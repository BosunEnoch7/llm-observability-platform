# Load and failure testing

These exercises are intended for local or explicitly authorized test
environments. Never point the load generator at production without an approved
test plan, traffic limit, and rollback owner.

## Baseline load

Start the stack and generate five concurrent requests for 60 seconds:

```bash
docker compose up --build -d
python scripts/load_test.py --duration 60 --concurrency 5
```

The tool reports throughput, status counts, and p50/p95/p99 client latency. Use
Grafana to compare those observations with service-side histograms.

## Controlled failure injection

The overlay increases simulated latency and sets a 25% provider failure rate:

```bash
docker compose -f docker-compose.yml -f docker-compose.failure.yml up --build -d
python scripts/load_test.py --duration 120 --concurrency 10
```

Expected observations include provider retries, HTTP 503 responses after retry
exhaustion, higher p95 latency, error-budget burn, and eventually SLO alerts.
Restore the normal environment with:

```bash
docker compose down
docker compose up -d
```

Record the test parameters and screenshots in `screenshots/` when using the
exercise as portfolio or incident-readiness evidence.
