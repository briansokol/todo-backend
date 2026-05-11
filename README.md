# todo-backend

FastAPI backend for the Todo App.

## Stack

- **FastAPI** 0.111
- **SQLAlchemy** 2.0 (DeclarativeBase)
- **Alembic** — database migrations
- **PostgreSQL** 16 (SQLite for tests)
- **Pydantic** v2

## Running locally

Requires PostgreSQL. The easiest way is via [todo-infra](https://github.com/briansokol/todo-infra):

```bash
# in todo-infra/
docker compose up postgres
```

Then start the backend:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make migrate   # run Alembic migrations
make dev       # uvicorn on :8000 with --reload
```

API docs available at http://localhost:8000/docs.

## Running tests

Tests use SQLite — no PostgreSQL needed:

```bash
pytest tests/ -v
```

## Project structure

```
app/
  models/      — SQLAlchemy ORM models (source of DB schema)
  schemas/     — Pydantic models matching todo-contracts/openapi.yaml
  routers/     — FastAPI route handlers (thin layer, delegates to services/)
  services/    — Business logic (CRUD, filtering)
main.py        — App entry point, router mounts, CORS config
alembic/       — DB migration scripts
```

## API schema

Pydantic schemas in `app/schemas/` are written to match `todo-contracts/openapi.yaml`. Always check the spec before adding new shapes. To regenerate schemas automatically:

```bash
make generate-schemas
```

## Adding a migration

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```
