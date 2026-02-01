# Detect OS
UNAME_S := $(shell uname -s)

# Metadata
ENV ?=
PROJECT_NAME ?= $(shell sed -n 's/^name[[:space:]]*=[[:space:]]*"\(.*\)"/\1/p' pyproject.toml | head -n1)
PROJECT_VERSION ?= $(shell sed -n 's/^version[[:space:]]*=[[:space:]]*"\(.*\)"/\1/p' pyproject.toml | head -n1)
GIT_TAG ?= $(PROJECT_VERSION)

# Environment Files
ENV_FILE_BASE = .env
ENV_FILE_ENV = $(if $(ENV),$(ENV_FILE_BASE).$(ENV),)
# Define the priority order for environment files
ENV_FILE_PRIORITY = $(if $(ENV),$(ENV_FILE_BASE) $(ENV_FILE_ENV),$(ENV_FILE_BASE))

# Function to filter existing files
define filter_existing_files
$(foreach file,$(1),$(if $(wildcard $(file)),$(file),))
endef

# Determine which env files exist and should be used (preserving priority order)
USED_ENV_FILES := $(strip $(call filter_existing_files,$(ENV_FILE_PRIORITY)))

# Convert space-separated list to multiple --env-file arguments for docker-compose
ENV_FILE_ARGS := $(foreach file,$(USED_ENV_FILES),--env-file $(file))

# Docker
DOCKERFILE ?= $(if $(ENV),Dockerfile.$(ENV),Dockerfile)
IMAGE_NAME ?= $(PROJECT_NAME)
IMAGE_TAG ?= $(PROJECT_VERSION)$(if $(ENV),-$(ENV),)
IMAGE_PATH ?= $(IMAGE_NAME):$(IMAGE_TAG)
# COMPOSE_YAML logic:
# - If COMPOSE_YAML is explicitly set, use it
# - Else if ENV is set, use docker-compose.$(ENV).yaml
# - Otherwise, use docker-compose.yaml
COMPOSE_YAML ?= $(if $(ENV),docker-compose.$(ENV).yaml,docker-compose.yaml)

# ANSI Color Codes
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color
LINE = "$(GREEN)$(shell printf '%.0s-' {1..78})$(NC)"

# Paths
CWD_ABSOLUTE := $(shell pwd)
MAIN_MODULE = main
TESTS_SRC = tests
CHECK_SRC = src $(TESTS_SRC)

.PHONY: help version v lock env-vars \
	dev local migrate migrate-docker up up-db down restart build rebuild test-image dockle \
	format format-staged check lint check-all \
	test test-cov test-html \
	clean venv logs logs-bot logs-redis logs-postgres \
	git-tag bump-major bump-minor bump-patch bump-version

# Category: Helpers
help: ## 💡 Show this help message
	@echo $(LINE)
	@printf "$(GREEN)%-23s$(NC) %s\n" "Project" "$(PROJECT_NAME)"
	@printf "$(GREEN)%-23s$(NC) %s\n" "Version" "$(PROJECT_VERSION)"
	@printf "$(GREEN)%-23s$(NC) %s\n" "Environment" "$(if $(ENV),$(ENV),default)"
	@echo
	@echo "$(GREEN)Usage:$(NC) make $(YELLOW)<target>$(NC)"
	@echo $(LINE)
	@awk 'BEGIN {FS = ":.*?## "} \
		/^# Category:/ {printf "\n$(GREEN)  %s ↴$(NC)\n%s\n", substr($$0, 13), $(LINE)} \
		/^[a-zA-Z0-9_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@make env-vars

version: ## 🔎 Show project name and version (alias v)
	@echo "Project: $(PROJECT_NAME)"
	@echo "Version: $(PROJECT_VERSION)"

v: version

init: ## 💻 Initialize project
	@echo "💻 Initializing project..."
	@make version
	@echo "Setup env files:"
	@echo "  - create .env file"
	@if [ -f ".env" ]; then \
		echo "    file .env already exist. Skip"; \
	else \
		echo "    file .env created"; \
		cp env.example .env; \
	fi
	@echo "Setup husky hooks:"
	@echo "  - run npm install"
	@npm i >> /dev/null 2>&1
	@echo "    installation completed"
	@echo "Install dependencies:"
	@echo "  - run uv sync"
	@uv sync >> /dev/null 2>&1
	@echo "    sync completed"
	@echo "✅ Project initialized successfully!"

lock: ## 📦 Locking dependencies
	@echo "📦 Locking dependencies..."
	uv lock

env-vars: ## 📋 Display environment variables and their values
	@echo $(LINE)
	@echo "$(GREEN)Environment Variables ↴$(NC)"
	@echo
	@echo "$(GREEN)Usage:$(NC)$(YELLOW)<VARIABLE>$(NC)make <target>"
	@echo $(LINE)
	@echo
	@echo "$(GREEN)  Overridable ↴$(NC)"
	@echo $(LINE)
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "ENV" "$(if $(ENV),$(ENV),default)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "COMPOSE_YAML" "$(COMPOSE_YAML)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "DOCKERFILE" "$(DOCKERFILE)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "IMAGE_NAME" "$(IMAGE_NAME)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "IMAGE_TAG" "$(IMAGE_TAG)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "IMAGE_PATH" "$(IMAGE_PATH)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "GIT_TAG" "$(GIT_TAG)"
	@echo
	@echo "$(GREEN)  NOT Overridable ↴$(NC)"
	@echo $(LINE)
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "PROJECT_NAME" "$(PROJECT_NAME)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "PROJECT_VERSION" "$(PROJECT_VERSION)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "ENV_FILE_BASE" "$(ENV_FILE_BASE)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "ENV_FILE_ENV" "$(ENV_FILE_ENV)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "ENV_FILE_PRIORITY" "$(ENV_FILE_PRIORITY)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "USED_ENV_FILES" "$(USED_ENV_FILES)"
	@printf "$(YELLOW)  %-20s$(NC) %s\n" "ENV_FILE_ARGS" "$(ENV_FILE_ARGS)"
	@echo ""
	@if [ -n "$(ENV)" ] && [ -f "$(ENV_FILE_BASE)" ] && [ -f "$(ENV_FILE_ENV)" ]; then \
		echo "$(YELLOW)Differences between .env and .env.$(ENV):$(NC)"; \
		if command -v diff >/dev/null 2>&1; then \
			diff -u "$(ENV_FILE_BASE)" "$(ENV_FILE_ENV)" | grep -E '^[-+][^-\+]' || true; \
		else \
			echo "diff/grep command not available."; \
		fi; \
	fi
	@echo ""

# Category: Local Development
dev: ## 🏃‍ Run local bot development
	@echo "🏃‍ Running local bot development..."
	@$(MAKE) version
	@uv run python -m $(MAIN_MODULE)

local: ## 🏃‍ Run local development (🐳 with Pg & Redis on docker)
	@echo "🏃‍ Running local development (🐳 with Pg & Redis on docker)..."
	@make up-db
	@APP__REDIS__PORT=6380 APP__REDIS__HOST=localhost APP__DB__HOST=localhost \
		make dev

# Category: Database Management
migrate: ## ⬆️ Apply Alembic migrations to the database
	@echo "⬆️ Applying Alembic migrations..."
	alembic upgrade head
	@echo "✅ Alembic migrations applied successfully!"

migrate-docker: ## ⬆️ Apply Alembic migrations to the database in Docker
	@echo "⬆️ Applying Alembic migrations in Docker..."
	IMAGE_PATH=$(IMAGE_PATH) \
		docker-compose $(ENV_FILE_ARGS) -f $(COMPOSE_YAML) exec bot \
		alembic upgrade head
	@echo "✅ Alembic migrations applied successfully!"

# Category: Docker Management
up: ## 🐳 Up local Docker stack
	@echo "🐳 Up Docker stack..."
	IMAGE_PATH=$(IMAGE_PATH) \
		docker-compose $(ENV_FILE_ARGS) -f $(COMPOSE_YAML) up -d

up-db: ## 🐳 Up Postgres & Redis stack
	@echo "🐳 Up Postgres & Redis stack..."
	IMAGE_PATH=$(IMAGE_PATH) \
		docker-compose $(ENV_FILE_ARGS) -f $(COMPOSE_YAML) up -d postgres redis

down: ## 🛑 Stopping local Docker stack
	@echo "🛑 Stopping local Docker stack..."
	IMAGE_PATH=$(IMAGE_PATH) \
		docker-compose $(ENV_FILE_ARGS) -f $(COMPOSE_YAML) down

restart: ## 🟡 Restart the stack after changes
	@echo "🟡 Restart the stack after changes..."
	@make down
	@make up

logs: ## 📝 Show Docker logs
	@echo "📝 Showing Docker logs..."
	IMAGE_PATH=$(IMAGE_PATH) \
		docker-compose $(ENV_FILE_ARGS) -f $(COMPOSE_YAML) logs

logs-bot: ## 🤖 Show bot service logs
	@echo "🤖 Showing bot service logs..."
	IMAGE_PATH=$(IMAGE_PATH) \
		docker-compose $(ENV_FILE_ARGS) -f $(COMPOSE_YAML) logs bot

logs-redis: ## 🗄️ Show redis service logs
	@echo "🗄️ Showing redis service logs..."
	IMAGE_PATH=$(IMAGE_PATH) \
		docker-compose $(ENV_FILE_ARGS) -f $(COMPOSE_YAML) logs redis

logs-postgres: ## 🗄️ Show postgres service logs
	@echo "🗄️ Showing postgres service logs..."
	IMAGE_PATH=$(IMAGE_PATH) \
		docker-compose $(ENV_FILE_ARGS) -f $(COMPOSE_YAML) logs postgres

build: ## 🚀 Building docker image
	@echo "🚀 Building docker image..."
	@$(MAKE) lock
	docker build -f $(DOCKERFILE) -t $(IMAGE_PATH) .
	@echo "✅ Docker image $(IMAGE_PATH) built successfully!"

rebuild: ## 🚀 Building docker image (skip cache)
	@echo "🚀 Rebuilding docker image (skip cache)..."
	@$(MAKE) lock
	docker build -f $(DOCKERFILE) -t $(IMAGE_PATH) . --no-cache
	@echo "✅ Docker image $(IMAGE_PATH) rebuilt successfully!"

dockle: ## 🔍 Check docker image by Dockle
	@echo "🔍 Checking docker image by Dockle..."
	@if [ "$$(which dockle)" == "" ]; then \
		echo "Dockle is not installed. Please check installation instructions."; \
		exit 1; \
	fi
	@DOCKER_CONTENT_TRUST=1 dockle \
		--ignore CIS-DI-0006 \
		-af settings.py \
		$(IMAGE_PATH)
	@printf "✅ No issues found in %s image!\n" "$(IMAGE_PATH)"

test-image: ## 🔍 Check Docker image & project env in container
	@echo "🔍 Checking Docker image & project env in container..."
	@make version
	@docker run --rm \
		-e BOT_TOKEN=test \
		$(IMAGE_PATH) \
		python -c \
		"import sys; \
		print(f'Python version: {sys.version}'); \
		from src.bot import main; \
		print('✅ Main function imported successfully');"
	@$(MAKE) dockle

# Category: Code Quality
format: ## 💅 Format code with Ruff
	@echo "💅 Formatting code with Ruff..."
	uv run ruff format $(CHECK_SRC)
	uv run ruff check $(CHECK_SRC) --fix --exit-zero

format-staged: ## 💅 Format only staged Python files and update staged versions
	@echo "💅 Formatting only staged Python files..."
	@bash -c 'STAGED_FILES=$$(git diff --cached --name-only --diff-filter=ACMR | grep "\.py$$"); \
	if [ -n "$$STAGED_FILES" ]; then \
		for file in $$STAGED_FILES; do \
			if [ -f "$$file" ]; then \
				echo "Formatting $${file}..."; \
				uv run ruff format "$$file"; \
				uv run ruff check "$$file" --fix --exit-zero; \
				git add "$$file"; \
			fi; \
		done; \
	else \
		uv run ruff format .; \
		uv run ruff check . --fix --exit-zero; \
	fi'

check: ## 🔍 Linting code with Ruff...
	@echo "🔍 Linting code with Ruff..."
	uv run ruff check $(CHECK_SRC) --fix
	@echo

lint: ## 🧠 Running deep code analysis with Ty
	@echo "🧠 Running deep code analysis with Ty..."
	uv run ty check
	@echo

check-all: format check lint ## 🧠 Run format & all code quality checks
	@echo "✅ Code quality checks passed!"
	@echo

# Category: Architecture Validation
validate-deps: ## 🏗️ Validate Clean Architecture dependency rules
	@echo "🏗️ Validating Clean Architecture dependency rules..."
	uv run pytest -v tests/architecture/test_dependency_rule.py

# Category: Testing
test: ## 🧪 Run tests
	@echo "🧪 Running tests for $(PROJECT_NAME) $(PROJECT_VERSION)..."
	uv run pytest -v $(TESTS_SRC) --no-header

test-cov: ## 📊 Generating test coverage report
	@echo "📊 Generating test coverage report for $(PROJECT_NAME) $(PROJECT_VERSION)..."
	uv run pytest -v $(TESTS_SRC) --no-header --cov

test-html: ## 📊 Generating HTML test coverage report
	@echo "📊 Generating HTML test coverage report for $(PROJECT_NAME) $(PROJECT_VERSION)..."
	uv run pytest -v $(TESTS_SRC) --no-header --cov --cov-report=html
	@echo
	@echo "📄 See coverage report in htmlcov/index.html"

# Category: Utilities
clean: ## 🧹 Cleaning up environment cache
	@echo "🧹 Cleaning up environment cache..."
	rm -rf .ruff_cache
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.log" -exec rm -f {} +
	rm -fr .venv
	rm -rf node_modules
	@echo "✅ Cache cleaned up!"

venv: ## 🐍 Creating/recreating a virtual environment
	@echo "🐍 Creating/recreating a virtual environment..."
	uv venv .venv --clear

# Category: Versioning and Tagging
git-tag: ## 🏷️ Create a git tag for the current version (usage: make git-tag or GIT_TAG=x.y.z make git-tag)
	@echo "🏷️ Creating git tag v$(GIT_TAG)..."
	@git tag -a "v$(GIT_TAG)"
	@echo "✅ Git tag v$(GIT_TAG) created successfully!"
	@echo "💡 Don't forget to push the tag with: git push origin v$(GIT_TAG)"

bump-major: ## 🔼 Bump major version (x.0.0)
	@$(eval NEW_VERSION=$(shell echo $(PROJECT_VERSION) | awk -F. '{print ($$1+1) ".0.0"}'))
	@echo "🔼 Bumping major version from $(PROJECT_VERSION) to $(NEW_VERSION)"
	sed -i.bak 's/version = "[0-9]*\.[0-9]*\.[0-9]*"/version = "$(NEW_VERSION)"/' pyproject.toml
	sed -i.bak 's|!\[Version\](https://img.shields.io/badge/version-[0-9]*\.[0-9]*\.[0-9]*-blue\.svg)|![Version](https://img.shields.io/badge/version-$(NEW_VERSION)-blue.svg)|' README.md
	@echo "✅ Version bumped to $(NEW_VERSION), don't forget to commit the changes!"

bump-minor: ## 🔼 Bump minor version (x.y.0)
	@$(eval NEW_VERSION=$(shell echo $(PROJECT_VERSION) | awk -F. '{print $$1 "." ($$2+1) ".0"}'))
	@echo "🔼 Bumping minor version from $(PROJECT_VERSION) to $(NEW_VERSION)"
	sed -i.bak 's/version = "[0-9]*\.[0-9]*\.[0-9]*"/version = "$(NEW_VERSION)"/' pyproject.toml
	sed -i.bak 's|!\[Version\](https://img.shields.io/badge/version-[0-9]*\.[0-9]*\.[0-9]*-blue\.svg)|![Version](https://img.shields.io/badge/version-$(NEW_VERSION)-blue.svg)|' README.md
	@echo "✅ Version bumped to $(NEW_VERSION), don't forget to commit the changes!"

bump-patch: ## 🔼 Bump patch version (x.y.z)
	@$(eval NEW_VERSION=$(shell echo $(PROJECT_VERSION) | awk -F. '{print $$1 "." $$2 "." ($$3+1)}'))
	@echo "🔼 Bumping patch version from $(PROJECT_VERSION) to $(NEW_VERSION)"
	sed -i.bak 's/version = "[0-9]*\.[0-9]*\.[0-9]*"/version = "$(NEW_VERSION)"/' pyproject.toml
	sed -i.bak 's|!\[Version\](https://img.shields.io/badge/version-[0-9]*\.[0-9]*\.[0-9]*-blue\.svg)|![Version](https://img.shields.io/badge/version-$(NEW_VERSION)-blue.svg)|' README.md
	@echo "✅ Version bumped to $(NEW_VERSION), don't forget to commit the changes!"

bump-version: ## 🔼 Bump version to specific value (usage: make bump-version VERSION=2.1.0)
	@if [ -z "$(VERSION)" ]; then \
		echo "$(RED)❌ Error: VERSION is required$(NC)" >&2; \
		echo "$(YELLOW)ℹ️  Usage: make bump-version VERSION=2.1.0$(NC)" >&2; \
		exit 1; \
	fi
	@echo "🔼 Bumping version to $(VERSION)"
	sed -i.bak 's/version = "[0-9]*\.[0-9]*\.[0-9]*"/version = "$(VERSION)"/' pyproject.toml
	sed -i.bak 's|!\[Version\](https://img.shields.io/badge/version-[0-9]*\.[0-9]*\.[0-9]*-blue\.svg)|![Version](https://img.shields.io/badge/version-$(VERSION)-blue.svg)|' README.md
	@echo "✅ Version bumped to $(VERSION), don't forget to commit the changes!"
