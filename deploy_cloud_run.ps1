$ErrorActionPreference = "Stop"

# --- Load Configuration from .env file --- #
Write-Host "Loading configuration from .env file..." -ForegroundColor Cyan

if (-Not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and fill in your configuration." -ForegroundColor Yellow
    exit 1
}

# Read .env file and set environment variables
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)\s*=\s*"?([^"]*)"?\s*$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$key" -Value $value
    }
}

# Validate required variables
$required_vars = @("GCP_PROJECT_ID", "GCS_BUCKET_NAME", "CLOUD_RUN_REGION", "CLOUD_RUN_SERVICE_NAME")
$missing_vars = @()

foreach ($var in $required_vars) {
    if (-Not (Test-Path "env:$var")) {
        $missing_vars += $var
    }
}

if ($missing_vars.Count -gt 0) {
    Write-Host "ERROR: Missing required environment variables in .env file:" -ForegroundColor Red
    $missing_vars | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    exit 1
}

# Set configuration from environment variables
$PROJECT_ID  = $env:GCP_PROJECT_ID
$BUCKET_NAME = $env:GCS_BUCKET_NAME
$REGION      = $env:CLOUD_RUN_REGION
$SERVICE_NAME = $env:CLOUD_RUN_SERVICE_NAME

Write-Host "Configuration loaded successfully:" -ForegroundColor Green
Write-Host "  Project ID: $PROJECT_ID"
Write-Host "  Bucket: $BUCKET_NAME"
Write-Host "  Region: $REGION"
Write-Host "  Service: $SERVICE_NAME"
Write-Host ""
# --- End Configuration --- #

$IMAGE_PATH = "$REGION-docker.pkg.dev/$PROJECT_ID/autoscraper-repo/autoscraper-agents:latest"

Write-Host "--- Step 1: Building Docker image ---" -ForegroundColor Cyan
docker build -t $IMAGE_PATH .

Write-Host "--- Step 2: Pushing image to Artifact Registry ---" -ForegroundColor Cyan
docker push $IMAGE_PATH

Write-Host "--- Step 3: Deploying to Cloud Run ---" -ForegroundColor Cyan
Write-Host "Service: $SERVICE_NAME in project $PROJECT_ID"

gcloud run deploy $SERVICE_NAME `
  --image $IMAGE_PATH `
  --platform managed `
  --region $REGION `
  --port 8000 `
  --memory 1Gi `
  --set-env-vars "GCS_BUCKET_NAME=$BUCKET_NAME,GCP_PROJECT_ID=$PROJECT_ID,GOOGLE_APPLICATION_CREDENTIALS=/secrets/autoscraper-service-account.json" `
  --set-secrets='/secrets/autoscraper-service-account.json=autoscraper-sa-key:latest,GEMINI_API_KEY=gemini-api-key:latest' `
  --project $PROJECT_ID

Write-Host "--- Deployment finished. Check Cloud Run console for status and URL. ---" -ForegroundColor Green

# Uncomment to allow unauthenticated access:
# --allow-unauthenticated `