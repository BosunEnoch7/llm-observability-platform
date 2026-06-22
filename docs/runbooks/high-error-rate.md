# LLMHighErrorRate runbook

1. Break errors down by HTTP status and model in Grafana or Prometheus.
2. Correlate the start time with deployments and configuration changes.
3. Inspect provider timeouts, throttling, authentication, and quota.
4. Reduce traffic, roll back, or fail over according to the failure mode.
5. Confirm recovery across at least one complete alert evaluation window.
