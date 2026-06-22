# Availability error-budget burn runbook

1. Confirm both burn-rate windows are above the alert threshold.
2. Break generation failures down by HTTP status, provider, and deployment.
3. Correlate the onset with releases, provider throttling, quota, and latency.
4. Inspect traces using the request or trace ID from a representative failure.
5. Roll back, reduce traffic, or activate the provider/model fallback as needed.
6. Confirm both alert windows recover before closing the incident.
7. Record budget consumed, customer impact, cause, and corrective actions.
