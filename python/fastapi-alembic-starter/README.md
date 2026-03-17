# FastAPI + SQLAlchemy + Alembic

Step-by-step guide to set up a production-ready FastAPI project with SQLAlchemy 2.0 (async), Alembic migrations, and uv as package manager.

---

## 1. Initialize the project

```bash
uv init "<name or nothing>"
```

This creates `pyproject.toml`, `README.md`, `.python-version`, and a `main.py` placeholder.
Remove the placeholder:


## 2. Set the Python version

```bash
uv python pin 3.11
```

## 3. Add dependencies

### Core

```bash
uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg alembic pydantic-settings
```

| Package | Why |
|---|---|
| `fastapi` | Web framework |
| `uvicorn[standard]` | ASGI server with hot reload |
| `sqlalchemy[asyncio]` | ORM with async engine support |
| `asyncpg` | Async PostgreSQL driver |
| `alembic` | Database migrations |
| `pydantic-settings` | Env-based configuration via `.env` |

### Dev dependencies

```bash
uv add --dev pytest pytest-asyncio httpx ruff
```

| Package | Why |
|---|---|
| `pytest` + `pytest-asyncio` | Async test support |
| `httpx` | Async test client for FastAPI |
| `ruff` | Linter + formatter |

## 4. Create the project structure

```bash
mkdir -p src/{models,schemas,routes,services}
touch src/__init__.py
touch src/{main,config,database,dependencies}.py
touch src/models/__init__.py src/models/user.py
touch src/schemas/__init__.py src/schemas/user.py
touch src/routes/__init__.py src/routes/users.py
touch src/services/__init__.py src/services/user_service.py
```

Final layout:

```
my-api/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entrypoint
│   ├── config.py            # Settings from env
│   ├── database.py          # Engine & session factory
│   ├── dependencies.py      # get_db and other DI helpers
│   ├── models/
│   │   ├── __init__.py      # Base + model re-exports
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── users.py
│   └── services/
│       ├── __init__.py
│       └── user_service.py
├── alembic/                  # Created in step 6
├── tests/
├── pyproject.toml
├── .env
└── .env.example
```

## 5. Configure the app

### `.env.example`

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app_db
APP_ENV=development
DEBUG=true
SECRET_KEY=change-me
CORS_ORIGINS=["http://localhost:3000"]
```

```bash
cp .env.example .env
```

## 6. Set up Alembic

### Initialize

```bash
uv run alembic init alembic
```

This creates `alembic.ini` and `alembic/` with `env.py`, `script.py.mako`, and `versions/`.

### Edit `alembic.ini`

Comment out the default `sqlalchemy.url` line — we set it from code instead:

```ini
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

### Replace `alembic/env.py`

Replace the entire generated `env.py` with the code inside `kickoff/python/fastapi-alembic-starter/alembic/env.py`

> **Key point:** importing `src.models` loads `Base` with all registered models, so autogenerate can detect them.


## 7. Custom commands
From pyproject + cli folder
```bash
uv run run_dev
uv run db_generate "my_migration_name"
uv run db_migrate
```

Mirroring
```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Generate migration from models
uv run alembic revision --autogenerate -m "create users table"

# Review the generated file in alembic/versions/ before applying!

# Apply
uv run alembic upgrade head
```

## Useful References

- [FastAPI docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [uv docs](https://docs.astral.sh/uv/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)