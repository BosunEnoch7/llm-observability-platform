# LLMServiceDown runbook

1. Confirm the target state in Prometheus under **Status > Targets**.
2. Check the `llm-service` container state and recent logs.
3. Call `/health/live` and `/health/ready` directly.
4. Check resource exhaustion, restart loops, and configuration errors.
5. Restore service, confirm successful scrapes, and document the incident.
