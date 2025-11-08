# Permissions Microservice (FastAPI)

This service manages user permissions across multiple teams and resources. It intentionally includes a mix of patterns and some maintainability pitfalls to simulate real-world friction for review and refactoring exercises.

## Features
- Domain layer for permission evaluation
- Repository layer using PostgreSQL (mix of sync and async access patterns)
- Background sync worker pulling external role mappings
- Duplicate logic and inconsistent naming to mimic real-world tech debt

## Getting Started

### Prerequisites
- Python 3.11+
- Docker (optional) for running Postgres quickly

### Setup Postgres with Docker
```bash
# Starts a local postgres on port 5433 to avoid conflicts
docker run --name permsdb -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=perms -p 5433:5432 -d postgres:15
```

### Environment
Create a `.env` file in the project root:
```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/perms
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/perms
EXTERNAL_ROLES_URL=http://localhost:9999/mock-roles
```

### Install Dependencies
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

### Initialize DB
```bash
psql "host=localhost port=5433 dbname=perms user=postgres password=postgres" -f migrations/001_init.sql
```

### Run the service
```bash
uvicorn app.main:app --reload --port 8000
```

### Example Requests
```bash
# Create user
curl -X POST http://localhost:8000/users -H 'Content-Type: application/json' -d '{"userId": "u1", "name": "Alice"}'

# Create team and membership
curl -X POST http://localhost:8000/teams -H 'Content-Type: application/json' -d '{"team_id": "t1", "team_name": "Core"}'
curl -X POST http://localhost:8000/memberships -H 'Content-Type: application/json' -d '{"uid": "u1", "team_id": "t1", "role": "admin"}'

# Check permission
curl "http://localhost:8000/permissions/check?user_id=u1&resource_id=repo1&action=write"
```

## Notes
- There are intentional issues: duplicate permission logic across modules, inconsistent naming (user_id vs uid vs userId), mixed sync/async DB patterns, a silent except in the sync worker, a circular dependency risk between rules_engine and sync_worker, missing null checks in a path, and sparse docstrings.
- Use this as a practice target for code review and refactoring.
