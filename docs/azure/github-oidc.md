# GitHub OIDC setup

GitHub Actions deploys to Azure without a stored client secret. The workflow
uses short-lived tokens from GitHub OIDC and exchanges them for Azure access.

## What gets created

The bootstrap script can create or reuse:

- one Entra application registration;
- one service principal;
- federated credentials for GitHub environments `dev`, `staging`, and `prod`;
- a subscription-scope `Contributor` assignment for the deployment identity.

The Bicep templates create role assignments for managed identities. Depending
on the target scope and tenant policy, the deployment identity may also need
`User Access Administrator` or `Role Based Access Control Administrator`.

## Bootstrap command

After Azure login:

```powershell
$env:AZURE_CONFIG_DIR="$PWD\.azure-local"
az login
az account set --subscription "<subscription-id>"

.\scripts\azure-oidc-bootstrap.ps1 `
  -GitHubOrg "BosunEnoch7" `
  -GitHubRepo "llm-observability-platform" `
  -SubscriptionId "<subscription-id>"
```

To also set GitHub environment variables automatically, install and authenticate
GitHub CLI, then add `-SetGitHubVariables`:

```powershell
gh auth login
.\scripts\azure-oidc-bootstrap.ps1 `
  -GitHubOrg "BosunEnoch7" `
  -GitHubRepo "llm-observability-platform" `
  -SubscriptionId "<subscription-id>" `
  -SetGitHubVariables
```

## Required GitHub variables

Create GitHub environments named `dev`, `staging`, and `prod`. Each environment
needs:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

These are not client secrets. They identify the federated Azure identity the
workflow should request.

## Federated credential subject format

Each credential is scoped to one GitHub environment:

```text
repo:BosunEnoch7/llm-observability-platform:environment:dev
repo:BosunEnoch7/llm-observability-platform:environment:staging
repo:BosunEnoch7/llm-observability-platform:environment:prod
```

This keeps production deployment tied to the protected `prod` GitHub
environment instead of allowing any workflow context to deploy.

## Verification

After setup:

1. run `.\scripts\azure-preflight.ps1`;
2. run a Bicep `what-if`;
3. confirm GitHub environment variables exist;
4. trigger **Deploy to Azure** for `dev` with `llm_provider=simulated`.
