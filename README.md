# backend-template

This is a backend template that I use for personal creation of any fun backend projects and personal use. This is updated based on my own coding structures. This template is AI-assisted and generated for proper structuring, experimentation, and learning.

## Template Structure

```
project-name/
    .github/
        workflows/
            ci.yml
    src/
        app/
            api/              # Presentation: FastAPI routers and schemas
            core/
                config.py     # Settings via pydantic-settings
                di.py         # Dependency injection via Dishka
            domain/           # Core: Entities, exceptions, and repository protocols
            infrastructure/   # Adapters: DB queries, Redis, external APIs
            services/         # Application: Business logic and use cases
            main.py           # Entrypoint (FastAPI app or async worker)
    tests/
        conftest.py
        test_pipeline.py
    .env.example
    docker-compose.yml
    Dockerfile
    pyproject.toml
    README.md
```

## How It's Structured (Clean Architecture)

The codebase follows Clean Architecture principles so business logic stays completely decoupled from databases and web frameworks:

- **`domain/`:** The core. Contains pure entities, domain exceptions, and repository interfaces (`Protocol`). It has zero external dependencies—it doesn't care if you're using Postgres, Mongo, or FastAPI.
- **`services/`:** The application layer / use cases. Contains the business logic. It interacts only with domain interfaces and doesn't care how data is persisted.
- **`infrastructure/`:** The adapters. Implements the repository protocols defined in `domain/` using actual tools (psycopg 3, Redis, Elasticsearch, Mongo, etc.).
- **`api/`:** The presentation layer. FastAPI routers and Pydantic schemas. It validates incoming requests, calls services, and returns HTTP responses.
- **`core/`:** Cross-cutting concerns. App config (`config.py`) and Dishka dependency injection wiring (`di.py`) that binds everything together.

---

## Adapting for Your Project (API vs Microservice vs ScaledJob)

By default, the template includes a minimal FastAPI setup in `api/` and `main.py`. Because the core (`domain`, `services`, `infrastructure`, `core`) is entrypoint-agnostic, you can adapt it to your workload:

### 1. HTTP API Only
Keep everything as is:
- Put your routers and schemas in `src/app/api/`.
- Register them in `src/app/api/v1/router.py`.
- Run with `uv run uvicorn app.main:app --reload`.

### 2. Microservice / CronJob / KEDA ScaledJob (No HTTP)
If you are building an event consumer (Kafka, RabbitMQ, Redis streams), a Kubernetes CronJob, or a KEDA ScaledJob:
1. **Remove `src/app/api/`:** Delete the folder entirely (unless your cluster requires a tiny `/health` server for liveness probes).
2. **Clean up `src/app/core/di.py`:**
   - Remove `FastapiProvider()` from `create_container()`.
   - Remove `from dishka.integrations.fastapi import FastapiProvider`.
3. **Update `src/app/main.py`:** Replace FastAPI with your async runner:
   ```python
   import asyncio
   from app.core.di import create_container
   from app.services.your_service import YourService

   async def main():
       container = create_container()
       async with container() as scope:
           service = await scope.get(YourService)
           await service.process()  # Consumer loop, polling, or single batch execution
       await container.close()

   if __name__ == "__main__":
       asyncio.run(main())
   ```
4. **Trim `pyproject.toml` (Optional):**
   - Remove `fastapi` and `uvicorn` from `dependencies`.
5. **Update `Dockerfile` & `docker-compose.yml`:**
   - Change `CMD` from `uvicorn app.main:app ...` to `["python", "-m", "app.main"]`.

### 3. Both (API + Background Worker)
If a single repository needs to serve API traffic and also run background workers:
- Keep `src/app/api/` and `src/app/main.py` for the web server.
- Add a separate worker entrypoint (e.g. `src/app/worker.py`) for the background runner.
- Both entrypoints share the exact same `domain/`, `services/`, and `infrastructure/` code.
- In deployment, run the API container (`uvicorn app.main:app`) and the Worker/ScaledJob container (`python -m app.worker`) from the same Docker image.

---

## Quick Start

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Spin up local database and cache:
   ```bash
   docker compose up -d postgres redis
   ```

4. Run locally:
   ```bash
   # For API:
   uv run uvicorn app.main:app --reload

   # For Worker / Job:
   uv run python -m app.main
   ```

## Tests & Linting

```bash
uv run pytest
uv run ruff check .
```
