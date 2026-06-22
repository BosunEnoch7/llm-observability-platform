.PHONY: install test lint up down smoke load failure-up

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=85

lint:
	python -m ruff check app tests scripts
	python -m ruff format --check app tests scripts

up:
	docker compose up --build -d

down:
	docker compose down

smoke:
	powershell -ExecutionPolicy Bypass -File scripts/smoke-test.ps1

load:
	python scripts/load_test.py --duration 30 --concurrency 5

failure-up:
	docker compose -f docker-compose.yml -f docker-compose.failure.yml up --build -d
