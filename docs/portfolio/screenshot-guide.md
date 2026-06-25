# Screenshot capture guide

This guide keeps final project evidence consistent.

## Local stack

Start the local platform:

```powershell
Copy-Item .env.example .env -ErrorAction SilentlyContinue
docker compose up --build -d
powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test.ps1
```

Collect machine-readable evidence:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\collect-local-evidence.ps1
```

For screenshot capture only, enable tracing and anonymous local Grafana Viewer
access with the evidence override:

```powershell
docker compose -f docker-compose.yml -f docker-compose.evidence.yml up -d --no-build
```

This override is intentionally separate from the default Compose configuration.
Restore the normal local security settings after capture:

```powershell
docker compose up -d --no-build --force-recreate llm-service grafana
```

Open:

- API docs: <http://localhost:8000/docs>
- Metrics: <http://localhost:8000/metrics>
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3000>
- Alertmanager: <http://localhost:9093>
- Jaeger: <http://localhost:16686>

Grafana local credentials are `admin` / `admin`.

## Recommended order

1. Capture API docs.
2. Capture health/readiness response.
3. Capture metrics after generating traffic.
4. Capture Prometheus targets.
5. Capture Prometheus alert rules.
6. Capture Grafana LLM overview dashboard.
7. Enable tracing, generate one request, then capture Jaeger.
8. Run the load/failure test and capture terminal output plus dashboard impact.
9. Capture GitHub Actions CI.
10. Capture Azure deployment workflow inputs.
11. After approved Azure deployment, capture Azure resources and deployed
    `/health/ready`.

## Naming convention

Save screenshots in the `screenshots/` folder using the names listed in
[the evidence checklist](evidence-checklist.md).

Save generated JSON/text evidence under `screenshots/evidence/`. See
[local evidence collection](local-evidence.md).

Do not include secrets, API keys, private prompts, subscription IDs, tenant IDs,
or personal access tokens in screenshots.

## Captured evidence status

The repository contains the completed local evidence set captured on June 25,
2026. The Azure resources screenshot remains intentionally absent because the
real deployment was blocked during `what-if` by the subscription's consumed
Container Apps environment quota.
