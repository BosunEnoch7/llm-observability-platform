# Azure OpenAI provider configuration

Set `LLM_PROVIDER=azure_openai`, then provide the Azure OpenAI endpoint and
deployment name. The application uses the deployment name for inference while
retaining `DEFAULT_MODEL` as the bounded model label used by telemetry.

## Recommended Azure authentication

Keep `AZURE_USE_MANAGED_IDENTITY=true`. Assign the workload's managed identity
the least-privileged Azure OpenAI inference role on the target resource. The
Azure Identity credential chain then obtains a token for Cognitive Services;
no long-lived secret is stored in the application or GitHub.

For local development, authenticate with the Azure CLI so
`DefaultAzureCredential` can use that identity. An API key is supported only as
a development fallback by setting `AZURE_USE_MANAGED_IDENTITY=false` and
`AZURE_OPENAI_API_KEY` in the untracked `.env` file.

## Operational controls

- The SDK's internal retry loop is disabled so platform retries are observable.
- `LLM_REQUEST_TIMEOUT_SECONDS` bounds each provider attempt.
- `LLM_MAX_RETRIES` and `LLM_RETRY_BACKOFF_SECONDS` control exponential retry.
- Provider failures are sanitized before reaching clients and logs.
- Prompts and credentials are never logged or attached to metric labels.
- Token prices are configuration because Azure pricing depends on deployment.

Validate the configured API version against the Azure OpenAI resource before a
production deployment. API availability can vary by model and Azure region.
