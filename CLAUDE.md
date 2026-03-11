# VotoClaro v3

Strategic voting app for Peru 2026 elections.

## Architecture

- **Backend:** Python/FastAPI in `/backend`, virtualenv in `/backend/.venv`
- **Frontend:** Next.js/TypeScript in `/frontend`
- **Database:** PostgreSQL
- **Queue:** Redis for Celery task workers

## Running locally

### Backend

```bash
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend && npm run dev
```

### Tests

```bash
cd backend && source .venv/bin/activate && pytest
```

## Key algorithms

- D'Hondt method: `backend/app/services/dhondt.py`

## Task tracking

Uses beads for task tracking:

- `bd list` -- list tasks
- `bd show <id>` -- show task details
