.PHONY: install test lint up down smoke

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest

lint:
	python -m ruff check app tests

up:
	docker compose up --build -d

down:
	docker compose down

smoke:
	powershell -ExecutionPolicy Bypass -File scripts/smoke-test.ps1
