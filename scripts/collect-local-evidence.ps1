param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$PrometheusUrl = "http://localhost:9090",
    [string]$OutputDirectory = "screenshots/evidence",
    [switch]$SkipPrometheus
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$outputPath = Join-Path $repoRoot $OutputDirectory
New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

function Save-Json {
    param(
        [string]$Path,
        [object]$Value
    )

    $json = $Value | ConvertTo-Json -Depth 20
    $encoding = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $json, $encoding)
}

function Invoke-Json {
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [string]$Body = ""
    )

    if ($Body) {
        return Invoke-RestMethod -Method $Method -Uri $Uri -ContentType "application/json" -Body $Body
    }

    return Invoke-RestMethod -Method $Method -Uri $Uri
}

Write-Host "Collecting local evidence into $outputPath" -ForegroundColor Cyan

$health = Invoke-Json "$BaseUrl/health/ready"
Save-Json (Join-Path $outputPath "health-ready.json") $health

$generationBody = @{
    prompt = "Explain why LLM observability matters for production operations."
    max_tokens = 64
} | ConvertTo-Json

$generation = Invoke-Json "$BaseUrl/v1/generate" "POST" $generationBody
Save-Json (Join-Path $outputPath "generation-response.json") $generation

$feedbackBody = @{
    inference_id = $generation.inference_id
    rating = 5
    helpful = $true
} | ConvertTo-Json

$feedback = Invoke-Json "$BaseUrl/v1/feedback" "POST" $feedbackBody
Save-Json (Join-Path $outputPath "feedback-response.json") $feedback

$metrics = Invoke-WebRequest "$BaseUrl/metrics" -UseBasicParsing
$encoding = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText((Join-Path $outputPath "metrics.txt"), $metrics.Content, $encoding)

$evidenceFiles = @(
    "health-ready.json",
    "generation-response.json",
    "feedback-response.json",
    "metrics.txt"
)

if (-not $SkipPrometheus) {
    $targets = Invoke-Json "$PrometheusUrl/api/v1/targets"
    Save-Json (Join-Path $outputPath "prometheus-targets.json") $targets

    $rules = Invoke-Json "$PrometheusUrl/api/v1/rules"
    Save-Json (Join-Path $outputPath "prometheus-rules.json") $rules

    $evidenceFiles += @(
        "prometheus-targets.json",
        "prometheus-rules.json"
    )
} else {
    Write-Warning "Skipping Prometheus evidence collection. Use full mode when Docker Compose is available."
}

$summary = [ordered]@{
    collected_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    base_url = $BaseUrl
    prometheus_url = $PrometheusUrl
    health_status = $health.status
    inference_id = $generation.inference_id
    generated_model = $generation.model
    prometheus_collected = -not $SkipPrometheus
    output_directory = $OutputDirectory
    evidence_files = $evidenceFiles
}

Save-Json (Join-Path $outputPath "summary.json") $summary

Write-Host "Evidence collection complete."
Write-Host "Summary: $OutputDirectory/summary.json"
