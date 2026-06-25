param(
    [string]$Location = "eastus2",
    [string]$EnvironmentName = "dev"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "LLM observability Azure preflight" -ForegroundColor Cyan
Write-Host "Environment: $EnvironmentName"
Write-Host "Location:    $Location"

if (-not $env:AZURE_CONFIG_DIR) {
    $env:AZURE_CONFIG_DIR = Join-Path $repoRoot ".azure-local"
}

Write-Host "Azure CLI config: $env:AZURE_CONFIG_DIR"

function Test-Command {
    param([string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name is not installed or not available on PATH."
    }
}

Test-Command "az"
Test-Command "docker"
Test-Command "git"

Write-Host "Checking Azure CLI version..."
az version --output table

Write-Host "Compiling Bicep templates..."
az bicep build --file infra/bicep/foundation.bicep --stdout | Out-Null
az bicep build --file infra/bicep/app.bicep --stdout | Out-Null
az bicep build-params --file infra/bicep/foundation.dev.bicepparam --stdout | Out-Null

Write-Host "Checking Docker Compose configuration..."
$env:DOCKER_CONFIG = Join-Path $repoRoot ".docker-temp"
New-Item -ItemType Directory -Force -Path $env:DOCKER_CONFIG | Out-Null
docker compose config | Out-Null

Write-Host "Checking Azure login..."
$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$accountJson = & az account show --output json 2>$null
$accountExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference

if ($accountExitCode -ne 0 -or -not $accountJson) {
    Write-Warning "Azure CLI is not logged in for AZURE_CONFIG_DIR=$env:AZURE_CONFIG_DIR."
    Write-Host "Run this before real deployment:"
    Write-Host "  `$env:AZURE_CONFIG_DIR=`"$env:AZURE_CONFIG_DIR`""
    Write-Host "  az login"
    Write-Host "  az account set --subscription <subscription-id>"
    exit 2
}

$account = $accountJson | ConvertFrom-Json
Write-Host "Logged in subscription: $($account.name) [$($account.id)]"

$providers = @(
    "Microsoft.App",
    "Microsoft.ContainerRegistry",
    "Microsoft.KeyVault",
    "Microsoft.ManagedIdentity",
    "Microsoft.OperationalInsights",
    "Microsoft.CognitiveServices",
    "Microsoft.Monitor",
    "Microsoft.Dashboard"
)

Write-Host "Checking provider registration state..."
foreach ($provider in $providers) {
    $state = & az provider show --namespace $provider --query registrationState --output tsv
    Write-Host "  $provider`t$state"
}

Write-Host "Checking existing Azure Container Apps environments..."
$containerAppsEnvironmentsJson = & az containerapp env list `
    --query "[].{name:name,resourceGroup:resourceGroup,location:location}" `
    --output json

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Could not list Container Apps environments. The what-if step must validate subscription quota."
} else {
    $containerAppsEnvironments = @($containerAppsEnvironmentsJson | ConvertFrom-Json)
    Write-Host "  Existing environments: $($containerAppsEnvironments.Count)"

    foreach ($environment in $containerAppsEnvironments) {
        Write-Host "  $($environment.name)`t$($environment.resourceGroup)`t$($environment.location)"
    }

    if ($containerAppsEnvironments.Count -gt 0) {
        Write-Warning "Some subscriptions have a low global Container Apps environment quota. The foundation creates a dedicated environment, so confirm quota with what-if before deployment."
    }
}

Write-Host "Preflight complete. Next safe step is a subscription-scope what-if:"
Write-Host "az deployment sub what-if --location $Location --template-file infra/bicep/foundation.bicep --parameters location=$Location environmentName=$EnvironmentName"
