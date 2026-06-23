# Azure deployment failure runbook

1. Identify whether foundation, image build, app deployment, or smoke test failed.
2. Review the GitHub Actions job and the corresponding Azure deployment operation.
3. Check provider registration, regional availability, quota, RBAC, and policy denials.
4. Confirm the ACR image tag exists and the managed identity has `AcrPull`.
5. For Azure OpenAI, verify account region, model deployment, quota, and RBAC.
6. Re-run a Bicep `what-if`; do not bypass policy or broaden roles casually.
7. Roll back to the previous immutable image tag when the app revision is unhealthy.
