# syntax=docker/dockerfile:1
# Kvell API Production Dockerfile
# Multi-stage build with uv for fast dependency installation

# ============================================================
# Stage 1: Build stage
# ============================================================
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (without dev dependencies)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy source code
COPY src ./src

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ============================================================
# Stage 2: Runtime stage
# ============================================================
FROM python:3.13-slim AS runtime

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code
COPY --from=builder /app/src ./src

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health/latest')" || exit 1

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
