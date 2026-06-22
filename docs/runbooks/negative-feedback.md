# Negative feedback runbook

1. Confirm the feedback volume is large enough to be representative.
2. Break results down by bounded category, model, and prompt version.
3. Correlate the change with deployments, model changes, latency, and errors.
4. Sample detailed feedback only from the approved durable analytics store.
5. Roll back a prompt/model release or begin an offline evaluation as warranted.
6. Track remediation against a versioned evaluation dataset before re-release.
