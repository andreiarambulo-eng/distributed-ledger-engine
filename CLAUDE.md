# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This repo (`distributed-ledger-engine`) was just created from the author's personal `backend-template`. `pyproject.toml`, the README and `APP_NAME` still use the template's names. The only feature so far is the health-check vertical slice (`/api/v1/health/liveness`, `/api/v1/health/readiness`). Use it as the reference pattern for new features.

## Commands

Tooling is `uv` with Python 3.12. The package lives under `src/`. pytest finds it through `pythonpath = ["src"]`, and Docker finds it through `PYTHONPATH=/app/src`.

```bash
uv sync                                   # install deps (incl. dev group)
cp .env.example .env
docker compose up -d postgres redis       # local backing services
uv run uvicorn app.main:app --reload      # run API (docs at /docs)

uv run pytest                             # all tests
uv run pytest tests/test_pipeline.py::test_readiness_probe   # single test
uv run ruff check .                       # lint (E, F, I, UP, B, SIM; line length 100)
uv run ruff format .                      # CI runs `ruff format --check .`, so format before committing
```

CI (`.github/workflows/ci.yml`) runs `uv sync`, `ruff check`, `ruff format --check` and `pytest` on pushes and PRs to `main`.

## Architecture

Clean Architecture. Dependencies point inward: `api` → `services` → `domain` ← `infrastructure`, with `core/di.py` connecting them.

- `domain/` holds plain dataclass entities (frozen), `DomainError` subclasses, and repository interfaces written as `typing.Protocol`. It must not import FastAPI, psycopg, redis, or any other framework or driver.
- `services/` holds use-case classes. Their constructors take domain protocols and `Settings`, never concrete adapters.
- `infrastructure/` holds the concrete adapters that implement those protocols with psycopg 3, redis-py, motor or elasticsearch.
- `api/` holds FastAPI routers and Pydantic schemas. Endpoints map domain entities to response schemas explicitly; they never return dataclasses directly. New routers are registered in `api/v1/router.py`, which is mounted under `/api/v1`.
- `main.py` contains the `create_app()` factory. It maps `EntityNotFoundError` to 404 and any other `DomainError` to 400, using the body `{"error": {"code", "message"}}`. Services should raise domain exceptions and leave HTTP status codes to this layer.

### Dependency injection (Dishka)

`core/di.py` holds all of the wiring:
- `DatabaseProvider` creates **APP-scoped** singletons: `Settings`, the psycopg `AsyncConnectionPool`, Redis, the Motor client/DB and AsyncElasticsearch. It also provides a **REQUEST-scoped** `AsyncConnection` borrowed from the pool, so each request gets its own connection, which is returned to the pool when the request ends.
- `AppProvider` binds protocol → implementation and builds services, all at REQUEST scope. Adding a feature means adding providers here (e.g. `get_x_repo(...) -> XRepository` returning the concrete class, and `get_x_service(...)`).
- Endpoints receive dependencies through `@inject` and `FromDishka[ServiceType]`.
- `create_container(*extra_providers)` accepts extra providers, which lets the same core serve a non-HTTP worker entrypoint. The README describes how to drop `FastapiProvider` and run `python -m app.main` or a separate `app/worker.py`.

### Testing pattern

`tests/conftest.py` builds its own container from a `TestProvider` that swaps in mock repositories, then calls `setup_dishka` on a fresh `create_app()`. This works because `httpx.ASGITransport` does **not** run the app lifespan, so the real container (and its real DB connections) is never created. When you add services, add matching mock providers to `TestProvider`. `testcontainers[postgres,redis]` is available for integration tests against real backends. pytest-asyncio runs in `asyncio_mode = "auto"`.

## Commit messages

Conventional commits, following `.github/.gitmessage`: `<type>(<scope>): <imperative summary, ≤50 chars>`. Types: feat, fix, refactor, perf, test, docs, ci, chore. Common scopes: api, worker, db, redis, di, config, docker, tests. The body should explain why.
