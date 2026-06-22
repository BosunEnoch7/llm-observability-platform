# Safety event spike runbook

1. Confirm the increase by stage, category, action, model, and prompt version.
2. Check whether traffic composition or a prompt release changed recently.
3. Review only access-controlled safety records in the durable event store; do
   not retrieve prompt content from Prometheus labels or ordinary logs.
4. In monitor mode, decide whether to enable enforcement or upstream filtering.
5. In enforce mode, confirm blocked-request behavior and customer impact.
6. Escalate to the security/safety owner and preserve an auditable incident trail.
