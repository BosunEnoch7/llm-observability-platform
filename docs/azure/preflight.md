# Azure preflight

This stage verifies deployment readiness before creating cloud resources or
incurring cost.

## Why this stage exists

The repository contains Azure-ready infrastructure and a GitHub OIDC deployment
workflow. Actual deployment still requires an authorized Azure subscription,
registered providers, sufficient quota, RBAC, GitHub environment variables, and
cost approval.

Running preflight first prevents avoidable deployment failures and documents the
boundary between repository readiness and external cloud access.

## Local preflight

From the repository root:

```powershell
.\scripts\azure-preflight.ps1 -EnvironmentName dev -Location eastus2
```

The script performs read-only checks:

- Azure CLI availability;
- Bicep template compilation;
- Docker Compose configuration rendering;
- Azure login state;
- Azure resource provider registration state when logged in.

If the script exits with code `2`, Azure CLI is installed but not logged in for
the isolated project config. Log in before deployment:

```powershell
$env:AZURE_CONFIG_DIR="$PWD\.azure-local"
az login
az account set --subscription "<subscription-id>"
```

## Required GitHub environment variables

Create GitHub environments named `dev`, `staging`, and `prod`, then define:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

These are environment variables for OIDC identity selection, not client-secret
credentials.

## Required Azure permissions

The federated deployment identity needs permission to:

- create the target resource group;
- deploy Container Registry, Container Apps, Key Vault, Log Analytics, managed
  identity, Azure Monitor resources, Managed Grafana, and optionally Azure
  OpenAI;
- create role assignments for ACR pull, Key Vault secrets access, and Azure
  OpenAI access.

Role assignment creation usually requires `User Access Administrator` or `Role
Based Access Control Administrator` at the selected scope.

## What-if before deployment

After login and subscription selection, review the deployment plan:

```powershell
$env:AZURE_CONFIG_DIR="$PWD\.azure-local"
az deployment sub what-if `
  --location eastus2 `
  --template-file infra/bicep/foundation.bicep `
  --parameters location=eastus2 environmentName=dev
```

Do not continue if the what-if shows unexpected resource names, regions, role
assignments, or cost-bearing services.

## Status decision

- Preflight passes and what-if is approved: run the GitHub **Deploy to Azure**
  workflow for `dev`.
- Azure CLI is not logged in: pause and authenticate.
- RBAC, quota, policy, or provider registration blocks deployment: document the
  blocker in the project incident log and resolve it before retrying.
