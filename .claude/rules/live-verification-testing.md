---
paths:
  - "tests/**"
---
# Live Verification & Concurrency Testing Rules
- **No Production Data & Environment Confirmation:** NEVER connect to or run tests against production databases or live production data. Before executing any test suite against a shared staging or persistent database (anything other than an isolated local test containers/Docker test instance), STOP and ask the user to explicitly confirm the target database host and name.
- **Real Disposable Datastores Only:** All integration and concurrency tests must run against disposable, isolated PostgreSQL and Redis instances (test containers or dedicated local test containers) seeded strictly with synthetic test fixtures; mocking database sessions, Redis clients, locks, or transaction boundaries is prohibited in these tests.
- **Scope of the No-Mock Rule:** API/unit tests may keep using mock repositories via `TestProvider` in `tests/conftest.py` (see CLAUDE.md); the real-datastore requirement applies only to integration and concurrency tests.
- **Test Isolation:** Every test case must reset synthetic PostgreSQL tables and flush Redis test keys cleanly between runs without relying on execution order.
- **Concurrency & Idempotency Verification:** Stress tests must execute true parallel coroutines (`asyncio.gather`) against contended records and explicitly assert invariant preservation (zero negative balances, zero deadlocks, and identical responses on duplicate idempotency keys—including when Redis cache is cold or unavailable).