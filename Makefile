.PHONY: install test lint up down smoke

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=85

lint:
	python -m ruff check app tests
	python -m ruff format --check app tests

up:
	docker compose up --build -d

down:
	docker compose down

smoke:
	powershell -ExecutionPolicy Bypass -File scripts/smoke-test.ps1
