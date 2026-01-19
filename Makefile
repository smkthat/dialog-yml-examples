.PHONY: help run format check lint check-all test test-cov test-html clean

# Detect OS
UNAME_S := $(shell uname -s)

# ANSI Color Codes
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

CWD := $(shell pwd)
MAIN_MODULE = main.py
CHECK_SRC = src tests

help: # 💡 Show this help message
	@echo "$(GREEN)spoetka-base$(NC)"
	@echo "-------------------------------------"
	@echo "Usage: make $(YELLOW)<target>$(NC)"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?# "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  $(YELLOW)%-18s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

run: ## 🤖 Start bot...
	@echo "🤖 Start bot..."
	uv run $(MAIN_MODULE)

format: ## 🧠 Format code with Ruff
	@echo "🔧 Formatting code with Ruff..."
	uv run ruff format $(CHECK_SRC)

check: ## 🧠 Run code quality checks with Ruff
	@echo "🔍 Linting code with Ruff..."
	uv run ruff check $(CHECK_SRC) --fix
	uv run ty check
	@echo

check-all: format check ## 🧠 Run format & all code quality checks
	@echo "✅ Code quality checks passed!"
	@echo

test: ## 🧪 Run all tests
	@echo "🧪 Running all tests..."
	uv run pytest -v --no-header -x $(PYTEST_ADDOPTS)


test-cov: ## 📊 Generating test coverage report
	@echo "📊 Generating test coverage report..."
	uv run pytest -v --no-header --cov=src $(PYTEST_ADDOPTS)

test-html: ## 📊 Generating HTML test coverage report
	@echo "📊 Generating HTML test coverage report..."
	uv run pytest -v --no-header --cov=src --cov-report=html $(PYTEST_ADDOPTS)
	@echo
	@echo "📄 See coverage report in htmlcov/index.html"

clean: ## 🧹 Clean artifacts & cache
	@echo "🧹 Cleaning artifacts & cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .ruff_cache/
	@echo "✅ Artifacts & cache cleaned up!"