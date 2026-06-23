# Azure teardown and cost control

This project can create cost-bearing Azure resources. Every cloud test should
have an owner, budget expectation, and teardown plan before deployment starts.

## Cost-bearing resources

The foundation deployment can create:

- Azure Container Registry;
- Azure Container Apps and Log Analytics;
- Azure Managed Grafana;
- Azure Monitor workspace;
- Azure OpenAI, when explicitly enabled;
- retained logs and metrics.

Costs vary by region, usage, retention, and SKU. Review Azure pricing before
running production-like tests.

## Safe teardown script

The teardown script defaults to dry-run behavior. It lists resources but does
not delete anything unless `-ConfirmDelete` is provided.

```powershell
$env:AZURE_CONFIG_DIR="$PWD\.azure-local"
.\scripts\azure-teardown.ps1 -EnvironmentName dev
```

To delete the dev resource group:

```powershell
.\scripts\azure-teardown.ps1 -EnvironmentName dev -ConfirmDelete
```

The script submits resource group deletion with `--no-wait`. Check completion:

```powershell
az group exists --name llmobs-dev-rg
```

## Key Vault purge protection

The Bicep template enables Key Vault purge protection to model production-safe
secret handling. This means a deleted vault may remain recoverable and may not
be immediately purgeable.

Do not disable purge protection just to make demos easier. Instead:

- use short-lived dev environments;
- choose deterministic names carefully;
- understand retention before creating test vaults;
- document teardown status in the incident/blocker log.

If policy allows purge and the vault is soft-deleted, the script supports:

```powershell
.\scripts\azure-teardown.ps1 -EnvironmentName dev -ConfirmDelete -PurgeSoftDeletedKeyVault
```

Purge may still fail if purge protection or policy prevents it.

## Production safety

For `staging` and `prod`, teardown should require explicit approval and rollback
planning. Never delete shared or production resource groups from a personal
terminal without an approved change record.
