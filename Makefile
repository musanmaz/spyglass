.PHONY: dev prod down logs migrate seed test lint clean

dev:
	docker compose -f docker-compose.dev.yml up --build

prod:
	docker compose up -d --build

down:
	docker compose down
	docker compose -f docker-compose.dev.yml down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python scripts/seed_db.py

test-backend:
	cd backend && pytest --cov=app --cov-report=html -v

test-frontend:
	cd frontend && npm run test

test: test-backend test-frontend

lint-backend:
	cd backend && ruff check app/ && mypy app/

lint-frontend:
	cd frontend && npm run lint

lint: lint-backend lint-frontend

clean:
	docker compose down -v
	docker compose -f docker-compose.dev.yml down -v
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
