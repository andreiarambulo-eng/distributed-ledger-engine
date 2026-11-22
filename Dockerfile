# Multi-stage Dockerfile leveraging uv for fast, reproducible builds
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ -f uv.lock ]; then uv sync --frozen --no-dev --no-install-project; else uv sync --no-dev --no-install-project; fi

# Test stage: same Python 3.12 as production, plus dev deps, tests and .env.test.
# Build/run with: docker compose run --rm --build test
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS test

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY src ./src
COPY tests ./tests
COPY .env.test ./

CMD ["sh", "-c", "ruff check src tests && ruff format --check src tests && pytest"]

# Runtime stage (last, so a plain `docker build .` still produces the production image)
FROM python:3.12-slim-bookworm AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src /app/src

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
