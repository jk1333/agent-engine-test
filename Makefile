# ==============================================================================
# Installation & Setup
# ==============================================================================

# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev

# ==============================================================================
# Playground Targets
# ==============================================================================

# Launch local dev playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 Try asking: What's the weather in San Francisco?                         |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'app' folder to interact with your agent.          |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# ==============================================================================
# Backend Deployment Targets
# ==============================================================================

# Deploy the agent remotely
backend:
	# Export dependencies to requirements file using uv export.
	uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate > .requirements.txt 2>/dev/null || \
	uv export --no-hashes --no-header --no-dev --no-emit-project > .requirements.txt && uv run app/agent_engine_app.py --location="us-central1" --agent-name="agent-engine-test-dev" --db-url="VertexAiSessionService" --model-location="global"

CLIENT_ID := CLIENT_ID
CLIENT_SECRET := SECRET
AGENT_ENGINE_RESOURCE_NAME := FULL_RESOURCE_NAME

AUTH_ID_TO_USE := dietary_planner
GEMINI_ENTERPRISE_REGION := global
GEMINI_ENTERPRISE_APP_ID := agent-portal

ge-register:
	$(eval PROJECT_ID := $(shell gcloud config get-value project))
	$(eval PROJECT_NUMBER := $(shell gcloud projects describe $(PROJECT_ID) --format='value(projectNumber)'))
	$(eval ACCESS_TOKEN := $(shell gcloud auth print-access-token))
	@echo "1. Authorizations 등록 중..."
	curl -X POST \
		-H "Authorization: Bearer $(ACCESS_TOKEN)" \
		-H "Content-Type: application/json" \
		-H "X-Goog-User-Project: $(PROJECT_ID)" \
		"https://$(GEMINI_ENTERPRISE_REGION)-discoveryengine.googleapis.com/v1alpha/projects/$(PROJECT_ID)/locations/$(GEMINI_ENTERPRISE_REGION)/authorizations?authorizationId=$(AUTH_ID_TO_USE)" \
		-d '{"name": "projects/$(PROJECT_NUMBER)/locations/$(GEMINI_ENTERPRISE_REGION)/authorizations/$(AUTH_ID_TO_USE)", "serverSideOauth2": {"clientId": "$(CLIENT_ID)", "clientSecret": "$(CLIENT_SECRET)", "authorizationUri": "https://accounts.google.com/o/oauth2/v2/auth?client_id=$(CLIENT_ID)&redirect_uri=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fstatic%2Foauth%2Foauth.html&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform&include_granted_scopes=true&response_type=code&access_type=offline&prompt=consent", "tokenUri": "https://oauth2.googleapis.com/token"}}'

	@echo "\n2. Agent 등록 중..."
	curl -X POST \
		-H "Authorization: Bearer $(ACCESS_TOKEN)" \
		-H "Content-Type: application/json" \
		-H "X-Goog-User-Project: $(PROJECT_ID)" \
		"https://$(GEMINI_ENTERPRISE_REGION)-discoveryengine.googleapis.com/v1alpha/projects/$(PROJECT_ID)/locations/$(GEMINI_ENTERPRISE_REGION)/collections/default_collection/engines/$(GEMINI_ENTERPRISE_APP_ID)/assistants/default_assistant/agents" \
		-d '{"displayName": "Dietary Planner", "description": "Healthy life", "adk_agent_definition": { "provisioned_reasoning_engine": { "reasoning_engine": "$(AGENT_ENGINE_RESOURCE_NAME)" } }, "authorization_config": {"tool_authorizations": ["projects/$(PROJECT_NUMBER)/locations/$(GEMINI_ENTERPRISE_REGION)/authorizations/$(AUTH_ID_TO_USE)"]}}'

# ==============================================================================
# Infrastructure Setup
# ==============================================================================

# Set up development environment resources using Terraform
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

# ==============================================================================
# Testing & Code Quality
# ==============================================================================

# Run unit and integration tests
test:
	uv run pytest tests/unit && uv run pytest tests/integration

# Run code quality checks (codespell, ruff, mypy)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .