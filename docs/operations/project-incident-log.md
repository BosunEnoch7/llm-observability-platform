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
