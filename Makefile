.PHONY: dev db backend frontend test migrate seed docker-up clean

dev: db backend frontend

db:
	docker-compose up -d db redis

backend:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && source .venv/bin/activate && pytest -v

migrate:
	cd backend && source .venv/bin/activate && alembic upgrade head

seed:
	cd backend && source .venv/bin/activate && python -m app.data.seed

docker-up:
	docker-compose up --build

clean:
	docker-compose down -v
