.PHONY: up down logs shell migrate migration test format lint

up:
	docker compose -f docker-compose.dev.yml up -d --build
	docker compose -f docker-compose.dev.yml up --build

down:
	docker compose -f docker-compose.dev.yml down

logs:
	docker compose -f docker-compose.dev.yml logs -f

shell:
	docker compose -f docker-compose.dev.yml exec api bash

migrate:
	docker compose -f docker-compose.dev.yml exec api alembic upgrade head

migration:
	docker compose -f docker-compose.dev.yml exec api alembic revision --autogenerate -m "$(name)"
	docker compose -f docker-compose.dev.yml exec api alembic revision --autogenerate -m "initial migration"

test:
	docker compose -f docker-compose.dev.yml exec api pytest tests/ -v

format:
	docker compose -f docker-compose.dev.yml exec api ruff check --fix app/

lint:
	docker compose -f docker-compose.dev.yml exec api ruff check app/

worker-logs:
	docker compose -f docker-compose.dev.yml logs -f celery_worker

beat-logs:
	docker compose -f docker-compose.dev.yml logs -f celery_beat

floci-logs:
	docker compose -f docker-compose.dev.yml logs -f floci
