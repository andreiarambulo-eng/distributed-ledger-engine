---
paths:
  - "src/app/infrastructure/**"
  - "src/app/domain/**"
  - "migrations/**"
---
# Datastore Access & Schema Rules
- **Schema & Keyspace Ownership:** Do NOT alter existing PostgreSQL table definitions, constraints, migrations, or Redis key schemas without explicit approval.
- **Source of Truth Separation:** PostgreSQL is the sole authoritative source of truth for balances, holds, and ledger entries; Redis may only be used for ephemeral caching, locks, or pre-flight idempotency—never as primary financial storage.
- **No Raw Credential Access:** Read datastore connection URLs exclusively from Pydantic `Settings`; never hardcode credentials or inspect `.env` files.
- **Precision & Immutability:** Map monetary columns strictly to Python `Decimal` (`NUMERIC`); never generate `UPDATE` or `DELETE` statements against append-only ledger entry tables.
- **Parameterized Queries & Key TTLs:** All SQL queries (`psycopg3` / `PyPika`) must use bound parameters, and every Redis key must define an explicit TTL.