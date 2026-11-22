# Project Memory

Milestone log, appended after each feature/fix branch is merged into `development`.
One entry per merge, at most 6 bullets: decisions and invariants, not command output.

## 2026-11-23 · feat/api-key-auth (#1, squash `49cb5f8`)

- Auth is `X-API-Key` checked against `API_KEYS` (comma-separated env, `SecretStr`); no
  `api_keys` table. Multiple keys allow zero-downtime rotation; rotating needs a restart.
- Fail closed: `Settings` refuses to start outside `ENVIRONMENT=local` without keys. Keys are
  compared with `hmac.compare_digest` across all entries; missing/wrong keys share one 401 body.
- `/api/v1` is split into a public router (health probes) and a protected router; new ledger
  routers go on the protected one. Domain errors map to HTTP in one table in `main.py`.
- Fixed template crash: Dishka must be set up in `create_app()`, not `lifespan` (Starlette
  rejects middleware after startup). Lifecycle tests drive the ASGI lifespan to cover it.
- Tests load committed `.env.test` via `APP_ENV_FILE`; `docker compose run --rm --build test`
  runs lint + tests on Python 3.12. Compose runs only the API against host Postgres/Redis.
- Open edge cases: readiness still checks Redis (to be removed); app connects as the Postgres
  superuser, which would bypass permission-based ledger immutability until a role is added.
