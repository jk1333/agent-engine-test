# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# mypy: disable-error-code="attr-defined,arg-type"
import logging
import os
from typing import Any

import click
import google.auth
import vertexai
from google.adk.artifacts import GcsArtifactService
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
from vertexai._genai.types import AgentEngine, AgentEngineConfig
from vertexai.agent_engines.templates.adk import AdkApp

from app.agent import root_agent
from app.utils.deployment import (
    parse_env_vars,
    print_deployment_success,
    write_deployment_metadata,
)
from app.utils.gcs import create_bucket_if_not_exists
from app.utils.tracing import CloudTraceLoggingSpanExporter
from app.utils.typing import Feedback

import functools
from google.adk.sessions import DatabaseSessionService #VertexAiSessionService, InMemorySessionService
from google.adk.sessions import VertexAiSessionService

from google.adk.memory.base_memory_service import BaseMemoryService
from google.adk.memory.base_memory_service import SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from typing_extensions import override
from google.genai import types
from typing import Optional
from google.adk.sessions.session import Session

class CustomMemoryBankService(BaseMemoryService):
  """Implementation of the BaseMemoryService using Vertex AI Memory Bank."""

  def __init__(
      self,
      project: Optional[str] = None,
      location: Optional[str] = None,
      agent_engine_id: Optional[str] = None,
  ):
    self._project = project
    self._location = location
    self._agent_engine_id = agent_engine_id

  @override
  async def add_session_to_memory(self, session: Session):
    if not self._agent_engine_id:
      raise ValueError('Agent Engine ID is required for Memory Bank.')

    events = []
    for event in session.events:
      if self._should_filter_out_event(event.content):
        continue
      if event.content:
        events.append({
            'content': event.content.model_dump(exclude_none=True, mode='json')
        })
    if events:
      client = self._get_api_client()
      print(f"[CustomMemoryBankService] Generating memory...")
      operation = client.agent_engines.memories.generate(
          name='reasoningEngines/' + self._agent_engine_id,
          direct_contents_source={'events': events},
          scope={
              'app_name': session.app_name,
              'user_id': session.user_id,
          },
          config={'wait_for_completion': True},
      )
      print(f"[CustomMemoryBankService] {operation}")
    else:
      print('[CustomMemoryBankService] No events to add to memory.')

  @override
  async def search_memory(self, *, app_name: str, user_id: str, query: str):
    if not self._agent_engine_id:
      raise ValueError('Agent Engine ID is required for Memory Bank.')

    client = self._get_api_client()
    retrieved_memories_iterator = client.agent_engines.memories.retrieve(
        name='reasoningEngines/' + self._agent_engine_id,
        scope={
            'app_name': app_name,
            'user_id': user_id,
        },
        similarity_search_params={
            'search_query': query,
        },
    )

    print('Search memory response received.')

    memory_events = []
    for retrieved_memory in retrieved_memories_iterator:
      # TODO: add more complex error handling
      print('Retrieved memory: %s', retrieved_memory)
      memory_events.append(
          MemoryEntry(
              author='user',
              content=types.Content(
                  parts=[types.Part(text=retrieved_memory.memory.fact)],
                  role='user',
              ),
              timestamp=retrieved_memory.memory.update_time.isoformat(),
          )
      )
    return SearchMemoryResponse(memories=memory_events)
  
  def _get_api_client(self):
    return vertexai.Client(project=self._project, location=self._location)
  
  def _should_filter_out_event(self, content: types.Content) -> bool:
    """Returns whether the event should be filtered out."""
    if not content or not content.parts:
        return True
    for part in content.parts:
        if part.text or part.inline_data or part.file_data:
            return False
    return True

class AgentEngineApp(AdkApp):
    def set_up(self) -> None:
        """Set up logging and tracing for the agent engine app."""
        #Update memory_bank to point agent engine
        #self._tmpl_attrs["memory_service_builder"]._agent_engine_id = os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ID")
        import logging        
        super().set_up()
        logging.basicConfig(level=logging.INFO)
        logging_client = google_cloud_logging.Client()
        self.logger = logging_client.logger(__name__)
        provider = TracerProvider()
        processor = export.BatchSpanProcessor(
            CloudTraceLoggingSpanExporter(
                project_id=os.environ.get("GOOGLE_CLOUD_PROJECT")
            )
        )
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        self._tmpl_attrs["memory_service"] = CustomMemoryBankService(
            os.environ.get("GOOGLE_CLOUD_PROJECT"),
            os.environ.get("GOOGLE_CLOUD_LOCATION"),
            os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ID")
        )

    def register_feedback(self, feedback: dict[str, Any]) -> None:
        """Collect and log feedback."""
        feedback_obj = Feedback.model_validate(feedback)
        self.logger.log_struct(feedback_obj.model_dump(), severity="INFO")

    def register_operations(self) -> dict[str, list[str]]:
        """Registers the operations of the Agent.

        Extends the base operations to include feedback registration functionality.
        """
        operations = super().register_operations()
        operations[""] = operations.get("", []) + ["register_feedback"]
        return operations

@click.command()
@click.option(
    "--project",
    default=None,
    help="GCP project ID (defaults to application default credentials)",
)
@click.option(
    "--location",
    default="us-central1",
    help="GCP region (defaults to us-central1)",
)
@click.option(
    "--agent-name",
    default="agent-engine-test",
    help="Name for the agent engine",
)
@click.option(
    "--requirements-file",
    default=".requirements.txt",
    help="Path to requirements.txt file",
)
@click.option(
    "--extra-packages",
    multiple=True,
    default=["./app"],
    help="Additional packages to include",
)
@click.option(
    "--set-env-vars",
    default=None,
    help="Comma-separated list of environment variables in KEY=VALUE format",
)
@click.option(
    "--service-account",
    default=None,
    help="Service account email to use for the agent engine",
)
@click.option(
    "--db-url",
    default=None,
    help="Database URL for the agent engine",
)
def deploy_agent_engine_app(
    project: str | None,
    location: str,
    agent_name: str,
    requirements_file: str,
    extra_packages: tuple[str, ...],
    set_env_vars: str | None,
    service_account: str | None,
    db_url: str | None,
) -> AgentEngine:
    """Deploy the agent engine app to Vertex AI."""
    # Parse environment variables if provided

    env_vars = parse_env_vars(set_env_vars)

    if not project:
        _, project = google.auth.default()

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🤖 DEPLOYING AGENT TO VERTEX AI AGENT ENGINE 🤖         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    #get_localip()
    print(f"Connecting to: {db_url}")

    logging.basicConfig(level=logging.INFO)
    extra_packages_list = list(extra_packages)
    staging_bucket_uri = f"gs://{project}-agent-engine"
    artifacts_bucket_name = f"{project}-agent-engine-test-logs"
    create_bucket_if_not_exists(
        bucket_name=artifacts_bucket_name, project=project, location=location
    )
    create_bucket_if_not_exists(
        bucket_name=staging_bucket_uri, project=project, location=location
    )

    # Initialize vertexai client
    client = vertexai.Client(
        project=project,
        location=location,
    )

    # Set location for Gemini api, for memory, only us-central1 supports
    vertexai.init(project=project, location="us-central1")

    # Read requirements
    with open(requirements_file) as f:
        requirements = f.read().strip().split("\n")

    #Added following config for db based session and tracing
    if db_url == "VertexAiSessionService":
        #Following config for VAI Session console
        session_service = functools.partial(
            VertexAiSessionService,
            project=project,
            location=location
        )
    else:
        session_service = functools.partial(
            DatabaseSessionService,
            db_url=db_url
        )

    agent_engine = AgentEngineApp(
        agent=root_agent,
        artifact_service_builder=lambda: GcsArtifactService(
            bucket_name=artifacts_bucket_name
        ),
        session_service_builder = session_service,
        #memory_service_builder = functools.partial(
        #    CustomMemoryBankService,
        #    project=project,
        #    location=location,
        #),
        enable_tracing=True
    )

    # Set worker parallelism to 1
    env_vars["NUM_WORKERS"] = "1"

    # Common configuration for both create and update operations
    labels: dict[str, str] = {}

    config = AgentEngineConfig(
        display_name=agent_name,
        description="A base ReAct agent built with Google's Agent Development Kit (ADK)",
        extra_packages=extra_packages_list,
        env_vars=env_vars,
        service_account=service_account,
        requirements=requirements,
        staging_bucket=staging_bucket_uri,
        labels=labels,
    )

    agent_config = {
        "agent": agent_engine,
        "config": config,
    }
    logging.info(f"Agent config: {agent_config}")

    # Check if an agent with this name already exists
    existing_agents = list(client.agent_engines.list())
    logging.info(f"Existing agents: {existing_agents}")
    matching_agents = [
        agent
        for agent in existing_agents
        if agent.api_resource.display_name == agent_name
    ]

    if matching_agents:
        # Update the existing agent with new configuration
        logging.info(f"\n📝 Updating existing agent: {agent_name}")
        remote_agent = client.agent_engines.update(
            name=matching_agents[0].api_resource.name, **agent_config
        )
    else:
        # Create a new agent if none exists
        logging.info(f"\n🚀 Creating new agent: {agent_name}")
        remote_agent = client.agent_engines.create(**agent_config)

    write_deployment_metadata(remote_agent)
    print_deployment_success(remote_agent, location, project)

    return

if __name__ == "__main__":
    deploy_agent_engine_app()