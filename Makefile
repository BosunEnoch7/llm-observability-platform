.PHONY: install test lint validate up down smoke evidence load failure-up azure-preflight azure-teardown-dry-run

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=85

lint:
	python -m ruff check app tests scripts
	python -m ruff format --check app tests scripts

validate: lint test
	python -m json.tool grafana/dashboards/llm-overview.json > /dev/null
	docker compose config > /dev/null

up:
	docker compose up --build -d

down:
	docker compose down

smoke:
	powershell -ExecutionPolicy Bypass -File scripts/smoke-test.ps1

evidence:
	powershell -ExecutionPolicy Bypass -File scripts/collect-local-evidence.ps1

load:
	python scripts/load_test.py --duration 30 --concurrency 5

failure-up:
	docker compose -f docker-compose.yml -f docker-compose.failure.yml up --build -d

azure-preflight:
	powershell -ExecutionPolicy Bypass -File scripts/azure-preflight.ps1 -EnvironmentName dev -Location eastus2

azure-teardown-dry-run:
	powershell -ExecutionPolicy Bypass -File scripts/azure-teardown.ps1 -EnvironmentName dev
