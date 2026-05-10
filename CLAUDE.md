# todo-backend

FastAPI backend for the Todo App.

## Stack

- **FastAPI** 0.111 — web framework
- **SQLAlchemy** 2.0 — ORM (DeclarativeBase style)
- **Alembic** — database migrations
- **PostgreSQL** 16 — database (SQLite for tests)
- **Pydantic** v2 — request/response validation

## Project structure

```
app/
  models/      — SQLAlchemy ORM models (source of DB schema)
  schemas/     — Pydantic models for request/response (hand-written to match todo-contracts)
  routers/     — FastAPI route handlers (thin — delegate to services/)
  services/    — Business logic (CRUD operations, filtering)
main.py        — FastAPI app, router mounts, CORS config
alembic/       — DB migrations (run after model changes)
```

## Schemas are derived from todo-contracts

The Pydantic schemas in `app/schemas/` are written to match `todo-contracts/openapi.yaml`. Do not invent new shapes — check the spec first. To regenerate them automatically: `make generate-schemas`.

## Running locally

Requires PostgreSQL running (use `todo-infra` Docker Compose or run postgres manually):

```bash
source .venv/bin/activate
make migrate       # run pending Alembic migrations
make dev           # starts uvicorn on :8000 with --reload
```

## Running tests

Tests use SQLite — no PostgreSQL required:

```bash
pytest tests/ -v
```

## Adding a migration

After changing a model in `app/models/`:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

## Known stubs

`app/routers/tags.py` — all endpoints return `501 Not Implemented`. The Tags feature is not complete:
- No `Tag` model exists yet
- No `tags` table in the DB
- No migration for tags
- See `specs/add-tags/` in `todo-meta` for the implementation spec
