param(
    [Parameter(Mandatory = $true)]
    [string]$GitHubOrg,

    [Parameter(Mandatory = $true)]
    [string]$GitHubRepo,

    [string]$AppName = "llmobs-github-actions",

    [string]$SubscriptionId = "",

    [string[]]$Environments = @("dev", "staging", "prod"),

    [switch]$SetGitHubVariables
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (-not $env:AZURE_CONFIG_DIR) {
    $env:AZURE_CONFIG_DIR = Join-Path $repoRoot ".azure-local"
}

function Require-Command {
    param([string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name is not installed or not available on PATH."
    }
}

Require-Command "az"

if ($SetGitHubVariables) {
    Require-Command "gh"
}

$accountJson = & az account show --output json 2>$null
if ($LASTEXITCODE -ne 0 -or -not $accountJson) {
    throw "Azure CLI is not logged in. Run: `$env:AZURE_CONFIG_DIR=`"$env:AZURE_CONFIG_DIR`"; az login"
}

$account = $accountJson | ConvertFrom-Json
if ([string]::IsNullOrWhiteSpace($SubscriptionId)) {
    $SubscriptionId = $account.id
}

& az account set --subscription $SubscriptionId
$tenantId = (& az account show --query tenantId --output tsv)

Write-Host "Using tenant:       $tenantId"
Write-Host "Using subscription: $SubscriptionId"
Write-Host "GitHub repository:  $GitHubOrg/$GitHubRepo"
Write-Host "Application name:   $AppName"

$existingAppId = & az ad app list --display-name $AppName --query "[0].appId" --output tsv
if ([string]::IsNullOrWhiteSpace($existingAppId)) {
    Write-Host "Creating Entra application registration..."
    $appId = & az ad app create --display-name $AppName --query appId --output tsv
} else {
    Write-Host "Reusing existing Entra application registration..."
    $appId = $existingAppId
}

$spId = & az ad sp list --filter "appId eq '$appId'" --query "[0].id" --output tsv
if ([string]::IsNullOrWhiteSpace($spId)) {
    Write-Host "Creating service principal..."
    $spId = & az ad sp create --id $appId --query id --output tsv
}

foreach ($environment in $Environments) {
    $credentialName = "github-$environment"
    $subject = "repo:$GitHubOrg/$GitHubRepo:environment:$environment"
    $existingCredential = & az ad app federated-credential list `
        --id $appId `
        --query "[?name=='$credentialName'].name | [0]" `
        --output tsv

    if ([string]::IsNullOrWhiteSpace($existingCredential)) {
        Write-Host "Creating federated credential for GitHub environment '$environment'..."
        $credential = @{
            name = $credentialName
            issuer = "https://token.actions.githubusercontent.com"
            subject = $subject
            audiences = @("api://AzureADTokenExchange")
        } | ConvertTo-Json -Depth 5

        $tempFile = New-TemporaryFile
        try {
            Set-Content -Path $tempFile -Value $credential -Encoding utf8
            & az ad app federated-credential create --id $appId --parameters "@$tempFile" | Out-Null
        } finally {
            Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue
        }
    } else {
        Write-Host "Federated credential for '$environment' already exists."
    }
}

Write-Host "Assigning Contributor at subscription scope if missing..."
$scope = "/subscriptions/$SubscriptionId"
$existingContributor = & az role assignment list `
    --assignee $spId `
    --scope $scope `
    --role "Contributor" `
    --query "[0].id" `
    --output tsv

if ([string]::IsNullOrWhiteSpace($existingContributor)) {
    & az role assignment create --assignee $spId --role "Contributor" --scope $scope | Out-Null
} else {
    Write-Host "Contributor role assignment already exists."
}

Write-Host "Role assignment creation for Bicep RBAC resources may also require User Access Administrator or Role Based Access Control Administrator."

if ($SetGitHubVariables) {
    Write-Host "Writing GitHub environment variables with gh..."
    foreach ($environment in $Environments) {
        & gh variable set AZURE_CLIENT_ID --repo "$GitHubOrg/$GitHubRepo" --env $environment --body $appId
        & gh variable set AZURE_TENANT_ID --repo "$GitHubOrg/$GitHubRepo" --env $environment --body $tenantId
        & gh variable set AZURE_SUBSCRIPTION_ID --repo "$GitHubOrg/$GitHubRepo" --env $environment --body $SubscriptionId
    }
}

Write-Host ""
Write-Host "OIDC bootstrap complete."
Write-Host "Set these GitHub environment variables if not set automatically:"
Write-Host "  AZURE_CLIENT_ID=$appId"
Write-Host "  AZURE_TENANT_ID=$tenantId"
Write-Host "  AZURE_SUBSCRIPTION_ID=$SubscriptionId"
