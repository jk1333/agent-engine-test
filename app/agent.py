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

from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import preload_memory_tool

from sub_agents.User_Requirement.agent import user_requirement_agent
from sub_agents.Recipe_Finder.agent import recipe_finder_agent
from sub_agents.Final.agent import final_agent
from google.adk.tools import FunctionTool, ToolContext
import uuid
import re
import tempfile
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

AGENT_AUTH_ID = "my_auth_001"

ROOT_AGENT_INSTR = """
You are a personalized recipe and dietary planning agent named Diatery_Planner. Your task is to assist users in finding recipes or generating dietary plans based on their requirements.

1. Parse the user's input to extract the following information and format it as JSON:
   - request_type: "recipe" or "diet_plan"
   - dietary_goals: e.g., "weight loss", "muscle gain", or null
   - cuisine: e.g., "Indian", "Italian", or null
   - diet_type: e.g., "vegetarian", "vegan", "high-protein", or null
   - ingredients: list of ingredients, e.g., ["chicken", "rice"], or null
   - allergies: list of allergies, e.g., ["nuts", "dairy"], or null
   - protein_goal: e.g., "high", "low", or null
   - conditions: list of health conditions, e.g., ["diabetes"], or null

   Example: For "I want the recipe of chicken biriyani", the JSON should be:
   ```json
   {
     "request_type": "recipe",
     "dietary_goals": null,
     "cuisine": "Indian",
     "diet_type": null,
     "ingredients": ["chicken", "rice"],
     "allergies": null,
     "protein_goal": null,
     "conditions": null
   }
   ```

2. Extract the search query from the user's input (e.g., "chicken biriyani" from "I want the recipe of chicken biriyani") and set it as a context variable named `query`.

3. Based on the request_type:
   - If request_type is "recipe":
     - Delegate the task to the `recipe_finder_agent` with the parsed JSON as the query.
     - The `recipe_finder_agent` will return a list of recipes. Format the response as follows and send it back to the client:
       ```
       Here is your requested recipe:

       **{recipe["title"]}**
       - **Ingredients**: {", ".join(recipe["ingredients"])}
       - **Protein Content**: {recipe["protein_content"]}
       - **Description**: {recipe["description"]}
       ```
       If no recipes are found, respond with:
       ```
       Sorry, I couldn't find a recipe. Please try a different request.
       ```
   - If request_type is "diet_plan":
     - Delegate the task to the appropriate sub-agent (e.g., `final_agent`) to generate a diet plan.
     - Format the diet plan response appropriately.

4. If the request_type cannot be determined or the input is unclear, ask the user for more details:
   ```
   I couldn't understand your request. Could you please provide more details? For example:
   * "Give me a recipe for chicken curry."
   * "I need a weekly diet plan for weight loss."
   * "I want a high-protein vegetarian meal."
   ```

5. If your says 'hello', response with what you can do in kind manner.

Ensure all responses are clear, concise, and helpful to the user.
Answer using user language.
"""

def get_access_token(tool_context: ToolContext, auth_id: str) -> str | None:
    #Find value of matched key
    auth_id_pattern = re.compile(f"temp:{re.escape(auth_id)}(_\\d+)?")
    state_dict = tool_context.state.to_dict()
    print(f"Available state keys: {list(state_dict.keys())}")
    for key, value in state_dict.items():
        if auth_id_pattern.match(key) and isinstance(value, str):
            return value
    return None

def upload_text_to_drive(tool_context: ToolContext, text_content: str) -> str:
    """Uploads the given text content to a file in Google Drive.

    Args:
        tool_context: The context object provided by the ADK framework.
        text_content: The string content to be saved in the text file.
    """
    filename = str(uuid.uuid4()) + ".txt"

    file_bytes = text_content.encode("utf-8")
    mime_type = "text/plain"

    try:
        # Use OAuth2 credentials from the tool_context        
        access_token = get_access_token(tool_context, AGENT_AUTH_ID)
        if not access_token:
            return (
                f"❌ Error: OAuth access token not found. "
                f"Ensure the agent is authorized in Gemini Enterprise with AUTH_ID='{AGENT_AUTH_ID}'. "
                "The user may need to click 'Authorize' in the Gemini Enterprise UI."
            )
        creds = Credentials(token=access_token)

        # creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build("drive", "v3", credentials=creds)

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(file_bytes)
            temp_file.flush()

            # By not specifying 'parents', the file is uploaded to the root "My Drive" folder.
            file_metadata = {"name": filename}
            media = MediaFileUpload(temp_file.name, mimetype=mime_type)
            uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id, name").execute()
            return f"✅ Successfully uploaded '{uploaded_file.get('name')}' to your Google Drive with File ID: {uploaded_file.get('id')}"

    except Exception as e:
        print(f"An unexpected error occurred during upload: {e}")
        return f"❌ An unexpected error occurred during upload: {e}"

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="A personalized recipe and dietary planning agent. Use 'upload_text_to_drive' to save the result",
    instruction=ROOT_AGENT_INSTR,
    sub_agents=[
        user_requirement_agent,
        recipe_finder_agent,
        final_agent,
    ],
    tools=[
        preload_memory_tool,
        FunctionTool(upload_text_to_drive)
        
    ]
)