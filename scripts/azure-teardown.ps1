param(
    [string]$WorkloadName = "llmobs",

    [ValidateSet("dev", "staging", "prod")]
    [string]$EnvironmentName = "dev",

    [switch]$ConfirmDelete,

    [switch]$PurgeSoftDeletedKeyVault
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (-not $env:AZURE_CONFIG_DIR) {
    $env:AZURE_CONFIG_DIR = Join-Path $repoRoot ".azure-local"
}

$resourceGroupName = "$WorkloadName-$EnvironmentName-rg"

Write-Host "LLM observability Azure teardown" -ForegroundColor Cyan
Write-Host "Resource group: $resourceGroupName"
Write-Host "Azure config:   $env:AZURE_CONFIG_DIR"

$accountJson = & az account show --output json 2>$null
if ($LASTEXITCODE -ne 0 -or -not $accountJson) {
    throw "Azure CLI is not logged in. Run: `$env:AZURE_CONFIG_DIR=`"$env:AZURE_CONFIG_DIR`"; az login"
}

$account = $accountJson | ConvertFrom-Json
Write-Host "Subscription:   $($account.name) [$($account.id)]"

$exists = & az group exists --name $resourceGroupName --output tsv
if ($exists -ne "true") {
    Write-Host "Resource group does not exist. Nothing to delete."
    exit 0
}

Write-Host ""
Write-Host "Resources currently in scope:"
& az resource list --resource-group $resourceGroupName --query "[].{name:name,type:type,location:location}" --output table

if (-not $ConfirmDelete) {
    Write-Host ""
    Write-Warning "Dry run only. Re-run with -ConfirmDelete to delete the resource group."
    Write-Host "Example:"
    Write-Host "  .\scripts\azure-teardown.ps1 -EnvironmentName $EnvironmentName -ConfirmDelete"
    exit 0
}

Write-Host ""
Write-Warning "Deleting resource group '$resourceGroupName'. This may take several minutes."
& az group delete --name $resourceGroupName --yes --no-wait

Write-Host "Delete submitted. Check status with:"
Write-Host "  az group exists --name $resourceGroupName"

if ($PurgeSoftDeletedKeyVault) {
    Write-Host ""
    Write-Warning "Key Vault purge was requested. Purge protection may prevent permanent deletion."
    $deletedVaults = & az keyvault list-deleted --query "[?starts_with(name, '$WorkloadName-$EnvironmentName-')].name" --output tsv
    foreach ($vaultName in $deletedVaults) {
        Write-Host "Attempting purge for deleted Key Vault: $vaultName"
        & az keyvault purge --name $vaultName
    }
}
