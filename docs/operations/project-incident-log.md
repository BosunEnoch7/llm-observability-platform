# Project incident and blocker log

This document records blockers, issues, and incidents encountered while building
the LLM observability platform. It is intentionally kept as a living project
artifact so the final portfolio handoff can show not only what was built, but
how operational problems were handled.

Each entry should capture:

- date;
- phase or milestone;
- issue summary;
- impact;
- root cause or likely cause;
- treatment or workaround;
- prevention or follow-up action;
- final status.

## Incident handling standard

For this project, an issue is considered closed only when:

1. the immediate blocker is removed;
2. validation is rerun when the issue could affect code, infrastructure, or CI;
3. documentation or runbooks are updated when the issue teaches an operational
   lesson;
4. the remaining risk is clearly stated.

## Log

| Date | Phase | Issue | Impact | Treatment | Prevention / Follow-up | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-06-23 | Azure IaC | Azure CLI default profile path was not usable from the workspace. | Bicep validation could not reliably use the normal Azure CLI config. | Used an isolated local CLI config directory: `.azure-local/`. Added `.azure-local/` to `.gitignore`. | Keep local Azure CLI state out of source control and document isolated validation commands. | Closed |
| 2026-06-23 | Azure IaC | Bicep emitted warnings for ACR name length inference. | Template compilation succeeded, but warnings reduced confidence. | Reworked ACR name construction to use known-safe naming constraints instead of truncation. Recompiled Bicep templates. | Prefer deterministic resource names with explicit parameter constraints. | Closed |
| 2026-06-23 | Azure docs | README still said IaC would be added later after IaC had been added. | Documentation drift could confuse reviewers. | Updated README to state that the first Azure deployment path is now included. | Review README after every milestone that changes project scope. | Closed |
| 2026-06-23 | Validation | Running tests with the global Python interpreter failed because `prometheus_client` was missing. | Test collection failed even though the repository virtual environment had the dependency. | Reran tests with `.venv\Scripts\python.exe`; all 19 tests passed with 87% coverage. | Always validate with the project virtual environment or CI environment. | Closed |
| 2026-06-23 | Validation | Docker Compose emitted a warning because the default Docker config path was not readable. | Compose config validation still passed, but logs were noisy. | Used a workspace-local temporary Docker config for validation. | Keep validation commands isolated from machine-specific Docker state. | Closed |
| 2026-06-23 | Git workflow | Git staging initially failed because the sandbox could not write `.git/index.lock`. | Changes could not be committed from the restricted sandbox. | Requested approval for Git operations, then committed and pushed the Azure milestone. | Treat repository mutations as explicit Git operations requiring appropriate workspace permissions. | Closed |
| 2026-06-23 | Azure preflight | Azure CLI is installed but no account is logged in for the isolated project config. | Real Azure deployment cannot safely start yet. | Paused deployment and added a read-only Azure preflight script plus documentation. | Authenticate with `az login`, select the subscription, run provider/RBAC checks, and complete what-if before deployment. | Open |
| 2026-06-23 | Azure preflight | Initial preflight script treated unauthenticated `az account show` as a PowerShell hard error. | The script stopped before printing the intended login guidance. | Captured the Azure CLI exit code explicitly and converted the unauthenticated state into a controlled preflight result. | Test preflight scripts against both logged-in and logged-out states. | Closed |
| 2026-06-23 | Azure deployment readiness | GitHub Actions cannot deploy until Azure OIDC identity and GitHub environment variables exist. | Deployment workflow is ready but blocked from authenticating to Azure. | Added a GitHub OIDC setup guide and bootstrap script for Entra app, federated credentials, and GitHub variables. | Run the bootstrap after Azure login and record the resulting client, tenant, and subscription IDs in GitHub environment variables. | Open |
| 2026-06-23 | Azure cost control | Cloud deployment would create cost-bearing resources without a repeatable teardown path. | Risk of orphaned resources and unexpected cost after testing. | Added dry-run-first Azure teardown script and cost-control documentation. | Require teardown ownership before running cloud deployments. | Closed |
| 2026-06-23 | Portfolio evidence | Screenshots were documented, but machine-readable local evidence was not automated. | Reviewers would need to manually verify core endpoints and Prometheus state. | Added a local evidence collector for health, generation, feedback, metrics, Prometheus targets, and alert rules. | Run evidence collection before final screenshots and after observability changes. | Closed |
| 2026-06-23 | Git workflow | Initial push of the local evidence commit failed with a transient loose-object permission error. | Commit existed locally but was not immediately available on GitHub. | Ran `git fsck --full`, confirmed no repository corruption, then retried `git push` successfully. | If repeated, pause OneDrive sync or move active Git repos outside synced folders. | Closed |
| 2026-06-23 | Local evidence | Docker Engine pipe access was denied when starting the local Compose stack. | Local evidence collection could not run from the current sandbox. | Added Docker troubleshooting guidance and paused runtime evidence collection until Docker Desktop access is available. | Start Docker Desktop, verify `docker version`, then rerun `docker compose up --build -d` and `.\scripts\collect-local-evidence.ps1`. | Open |
| 2026-06-23 | Local evidence | Docker remained unavailable, but API-only evidence could still be collected from a direct FastAPI run. | Full Prometheus/Grafana evidence remains blocked, but application evidence can progress. | Added `-SkipPrometheus` mode to the evidence collector for direct app validation. | Use full collector once Docker is available to add Prometheus target/rule proof. | Closed |
| 2026-06-23 | Local evidence | Direct PowerShell script execution was blocked by execution policy. | The first API-only evidence collection command failed before running the collector. | Reran the collector with `powershell -ExecutionPolicy Bypass -File`, matching the Makefile pattern. | Use Makefile targets or explicit execution-policy bypass for local project scripts on Windows. | Closed |

## Final-project requirement

Before the project is marked complete, this log must be reviewed and expanded
with any additional incidents from:

- local development;
- tests and CI;
- Docker Compose;
- Prometheus, Grafana, and Alertmanager;
- Azure provisioning;
- Azure deployment;
- smoke tests;
- dashboard or alert validation.

The final README should summarize the most important operational lessons and
link back to this document as evidence of SRE practice.
