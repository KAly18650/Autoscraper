# PowerShell equivalent of docker_shell.sh for local development
# Usage: From the project root run `./docker_shell.ps1`

$ErrorActionPreference = "Stop"

# Resolve important paths
$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptDir
$secretsDir  = Join-Path (Split-Path $projectRoot -Parent) "secrets"
$envFile     = Join-Path $projectRoot ".env"
$imageName   = "autoscraper-agents"

Write-Host "[docker_shell] Building image: $imageName"
docker build -t $imageName $projectRoot

if (-not (Test-Path $secretsDir)) {
    Write-Warning "[docker_shell] WARNING: secrets directory not found at $secretsDir"
}

if (-not (Test-Path $envFile)) {
    throw "[docker_shell] Unable to find .env file at $envFile"
}

$resolvedSecrets = (Resolve-Path $secretsDir -ErrorAction SilentlyContinue)?.Path
if (-not $resolvedSecrets) {
    $resolvedSecrets = $secretsDir
}

$resolvedEnvFile = (Resolve-Path $envFile).Path

Write-Host "[docker_shell] Running container with env from .env and secrets mounted at /secrets"

$dockerArgs = @(
    "run",
    "--env-file", $resolvedEnvFile,
    "-v", "${resolvedSecrets}:/secrets:ro",
    "-p", "8000:8000",
    $imageName
)

docker @dockerArgs
