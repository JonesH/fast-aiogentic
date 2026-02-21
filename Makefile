.PHONY: help install dev test lint typecheck format check clean build docker run gh-sync

# Default target
help:
	@echo "fast-aiogentic - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install    Install dependencies"
	@echo "  make dev        Install with dev dependencies"
	@echo ""
	@echo "Quality:"
	@echo "  make test       Run tests with coverage"
	@echo "  make lint       Run ruff linter"
	@echo "  make typecheck  Run ty type checker"
	@echo "  make format     Format code with ruff"
	@echo "  make check      Run all checks (lint, typecheck, test)"
	@echo ""
	@echo "Build:"
	@echo "  make build      Build package"
	@echo "  make clean      Remove build artifacts"

	@echo ""
	@echo "Docker:"
	@echo "  make docker     Build Docker image"
	@echo "  make run        Run with Docker Compose"
	@echo ""
	@echo "Deployment:"
	@echo "  make gh-sync    Sync .env to GitHub secrets/variables"


# Setup
install:
	uv sync

dev:
	uv sync --all-extras

# Quality checks
test:
	uv run pytest --cov --cov-report=term-missing

lint:
	uv run ruff check src/ tests/

typecheck:
	uv run ty check src/

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

check: lint typecheck test

# Build
build:
	uv build

clean:
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true


# Docker
docker:
	docker build -t fast-aiogentic:latest .

run:
	docker-compose up --build

# GitHub Secrets/Variables Sync
# Syncs .env to GitHub: *SECRET*|*PASSWORD*|*KEY*|*TOKEN*|SSH_* → secrets, rest → variables
gh-sync:
	@if [ ! -f .env ]; then echo "Error: .env file not found. Copy .env.example to .env first."; exit 1; fi
	@echo "Syncing .env to GitHub secrets and variables..."
	@while IFS='=' read -r key value; do \
		if [ -z "$$key" ] || [ "$${key#\#}" != "$$key" ]; then continue; fi; \
		case "$$key" in \
			*SECRET*|*PASSWORD*|*KEY*|*TOKEN*|SSH_*) \
				echo "  → secret: $$key"; \
				gh secret set "$$key" -b "$$value" 2>/dev/null || echo "    ⚠ failed (check gh auth)";; \
			*) \
				echo "  → variable: $$key"; \
				gh variable set "$$key" -b "$$value" 2>/dev/null || echo "    ⚠ failed (check gh auth)";; \
		esac; \
	done < .env
	@echo "✓ Done syncing to GitHub"
