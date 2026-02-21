# fast-aiogentic Telegram Bot
# Multi-stage build for minimal image size

FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies (git needed for aiogram dev-3.x)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock README.md ./

# Create virtual environment and install dependencies
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
RUN uv sync --frozen --no-install-project

# Production stage
FROM python:3.13-slim

WORKDIR /app

# Install Node.js for npx (required for Context7 MCP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Copy application code
COPY src/ ./src/
COPY fastagent.config.yaml ./
COPY prompts/ ./prompts/

# Create non-root user
RUN useradd --create-home --shell /bin/bash botuser \
    && chown -R botuser:botuser /app
USER botuser

# Health check (aiohttp /health endpoint in webhook mode)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["python", "-m", "fast_aiogentic.main"]
