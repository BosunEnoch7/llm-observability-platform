# Azure deployment

The Azure deployment is split into foundation and application stages. This
avoids referencing a private ACR image before the registry and image exist.

## Provisioned foundation

- resource group with environment tags;
- Azure Container Registry with the admin account disabled;
- user-assigned managed identity;
- RBAC-enabled Key Vault with purge protection;
- Log Analytics and Azure Container Apps environment;
- optional Azure OpenAI account with local authentication disabled;
- optional Azure Monitor workspace and Azure Managed Grafana;
- least-privilege ACR pull, Key Vault secrets user, and Azure OpenAI user roles.

Azure OpenAI model deployment is intentionally not automated yet because model
availability, versions, quota, and capacity vary by subscription and region.
The application defaults to the simulator until an approved deployment name is
provided.

## GitHub OIDC prerequisites

Create an Entra application or user-assigned identity with a federated GitHub
credential scoped to the repository and GitHub environment. Configure these as
GitHub environment variables, not secrets containing client credentials:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

Grant the deployment identity only the roles required to create the declared
resources and role assignments. Role-assignment creation generally requires
User Access Administrator or Role Based Access Control Administrator in
addition to resource deployment permissions. Scope access to the target
subscription or a pre-agreed resource hierarchy.

Create GitHub environments named `dev`, `staging`, and `prod`. Add reviewers and
deployment protection rules for production.

See [GitHub OIDC setup](github-oidc.md) for the bootstrap command and federated
credential subject format.

## Deploy through GitHub Actions

Run **Deploy to Azure** manually. Keep the provider set to `simulated` for the
first deployment. The workflow:

1. signs in through OIDC without a stored client secret;
2. deploys `infra/bicep/foundation.bicep` at subscription scope;
3. builds and pushes the commit-addressed container image;
4. deploys `infra/bicep/app.bicep` to the generated resource group;
5. verifies `/health/ready` over HTTPS.

Before selecting `azure_openai`, confirm that the account and an approved model
deployment exist, then supply the deployment name in the workflow input.

## Local template validation

Use an isolated CLI configuration if desired:

```powershell
$env:AZURE_CONFIG_DIR="$PWD/.azure-local"
az bicep build --file infra/bicep/foundation.bicep --stdout | Out-Null
az bicep build --file infra/bicep/app.bicep --stdout | Out-Null
az bicep build-params --file infra/bicep/foundation.dev.bicepparam --stdout | Out-Null
```

Template compilation does not validate subscription quota, provider
registration, Azure OpenAI regional availability, or deployment permissions.
Use `az deployment sub what-if` with the intended subscription before approval.

## Cost and teardown

Azure Managed Grafana, Azure OpenAI, Container Apps, Log Analytics, and retained
telemetry can incur charges. Review pricing, budgets, and retention before
deployment. Dev environments should have an explicit owner and teardown plan.

Purge-protected Key Vault cannot be immediately destroyed permanently. This is
intentional production protection, but it must be understood before test
deployments.
