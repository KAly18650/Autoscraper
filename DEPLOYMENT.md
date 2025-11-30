# Deployment Guide

This guide covers deploying AutoScraper to Google Cloud Run for production use.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Setup](#local-setup)
3. [Google Cloud Setup](#google-cloud-setup)
4. [Deployment](#deployment)
5. [Post-Deployment](#post-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts & Tools

- ✅ **Google Cloud Account** with billing enabled
- ✅ **gcloud CLI** installed ([Install guide](https://cloud.google.com/sdk/docs/install))
- ✅ **Docker** installed ([Install guide](https://docs.docker.com/get-docker/))
- ✅ **Gemini API Key** ([Get one here](https://ai.google.dev/))

### Required GCP APIs

Enable these APIs in your GCP project:

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com
```

---

## Local Setup

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/autoscraper.git
cd autoscraper
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Gemini API Configuration
GEMINI_API_KEY="your_actual_gemini_api_key"

# Google Cloud Configuration
GCS_BUCKET_NAME="your-bucket-name"
GCP_PROJECT_ID="your-gcp-project-id"

# Cloud Run Configuration
CLOUD_RUN_REGION="us-central1"
CLOUD_RUN_SERVICE_NAME="autoscraper-agents-service"

# Local development only
GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

**⚠️ IMPORTANT:** Never commit `.env` to version control!

### 3. Test Locally

```bash
# Test environment configuration
python tests/test_env_integrations.py

# Test Playwright
python tests/test_playwright.py

# Run ADK Web locally
adk web
```

Access at: http://localhost:8000

---

## Google Cloud Setup

### 1. Set Project

```bash
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID
```

### 2. Create GCS Bucket

```bash
gsutil mb -p $PROJECT_ID -l us-central1 gs://your-bucket-name
```

### 3. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create autoscraper-sa \
  --display-name="AutoScraper Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:autoscraper-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Create key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=autoscraper-sa@$PROJECT_ID.iam.gserviceaccount.com
```

**⚠️ Keep `service-account-key.json` secure and never commit it!**

### 4. Store Secrets in Secret Manager

#### Gemini API Key

```bash
echo -n "your_gemini_api_key" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --project=$PROJECT_ID
```

#### Service Account Key

```bash
gcloud secrets create autoscraper-sa-key \
  --data-file=service-account-key.json \
  --project=$PROJECT_ID
```

#### Grant Cloud Run Access to Secrets

```bash
# Get Cloud Run service account
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

# Grant access
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding autoscraper-sa-key \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"
```

### 5. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create autoscraper-repo \
  --repository-format=docker \
  --location=us-central1 \
  --project=$PROJECT_ID
```

### 6. Configure Docker Authentication

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

---

## Deployment

### Option 1: Using Deployment Script (Recommended)

**Windows (PowerShell):**
```powershell
.\deploy_cloud_run.ps1
```

**Linux/Mac (Bash):**
```bash
./deploy_cloud_run.sh
```

The script will:
1. ✅ Load configuration from `.env`
2. ✅ Validate required variables
3. ✅ Build Docker image
4. ✅ Push to Artifact Registry
5. ✅ Deploy to Cloud Run

### Option 2: Manual Deployment

#### Build and Push Image

```bash
# Set variables from .env
export REGION="us-central1"
export IMAGE_PATH="$REGION-docker.pkg.dev/$PROJECT_ID/autoscraper-repo/autoscraper-agents:latest"

# Build
docker build -t $IMAGE_PATH .

# Push
docker push $IMAGE_PATH
```

#### Deploy to Cloud Run

```bash
gcloud run deploy autoscraper-agents-service \
  --image $IMAGE_PATH \
  --platform managed \
  --region us-central1 \
  --port 8000 \
  --memory 1Gi \
  --timeout 300 \
  --set-env-vars "GCS_BUCKET_NAME=your-bucket-name,GCP_PROJECT_ID=$PROJECT_ID,GOOGLE_APPLICATION_CREDENTIALS=/secrets/autoscraper-service-account.json" \
  --set-secrets='/secrets/autoscraper-service-account.json=autoscraper-sa-key:latest,GEMINI_API_KEY=gemini-api-key:latest' \
  --project $PROJECT_ID
```

#### Optional: Allow Unauthenticated Access

```bash
gcloud run services add-iam-policy-binding autoscraper-agents-service \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

**⚠️ WARNING:** Only do this for demos. For production, use authentication!

---

## Post-Deployment

### Get Service URL

```bash
gcloud run services describe autoscraper-agents-service \
  --region=us-central1 \
  --format='value(status.url)'
```

### Test Deployment

```bash
# Get the URL
SERVICE_URL=$(gcloud run services describe autoscraper-agents-service \
  --region=us-central1 \
  --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health
```

### View Logs

```bash
# Real-time logs
gcloud run logs tail autoscraper-agents-service --region=us-central1

# Recent logs
gcloud run logs read autoscraper-agents-service \
  --region=us-central1 \
  --limit=50
```

### Monitor Usage

```bash
# View metrics in Cloud Console
gcloud run services describe autoscraper-agents-service \
  --region=us-central1
```

---

## Updating Deployment

To redeploy after making changes:

```bash
# Using script
.\deploy_cloud_run.ps1

# Or manually
docker build -t $IMAGE_PATH .
docker push $IMAGE_PATH
# Cloud Run will auto-deploy the new image
```

---

## Troubleshooting

### Common Issues

#### ❌ "Permission denied" errors

**Solution:**
```bash
# Verify service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:autoscraper-sa@$PROJECT_ID.iam.gserviceaccount.com"
```

#### ❌ "Secret not found"

**Solution:**
```bash
# List secrets
gcloud secrets list --project=$PROJECT_ID

# Verify secret versions
gcloud secrets versions list gemini-api-key
gcloud secrets versions list autoscraper-sa-key
```

#### ❌ "Image not found"

**Solution:**
```bash
# Verify Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# List images
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/$PROJECT_ID/autoscraper-repo
```

#### ❌ "Container failed to start"

**Solution:**
```bash
# Check logs
gcloud run logs read autoscraper-agents-service \
  --region=us-central1 \
  --limit=100

# Common causes:
# - Missing environment variables
# - Incorrect secret references
# - Playwright not installed in container
```

#### ❌ "Timeout errors"

**Solution:**
```bash
# Increase timeout
gcloud run services update autoscraper-agents-service \
  --region=us-central1 \
  --timeout=600
```

### Debug Mode

Enable detailed logging:

```bash
gcloud run services update autoscraper-agents-service \
  --region=us-central1 \
  --set-env-vars="LOG_LEVEL=DEBUG"
```

---

## Cost Optimization

### Estimated Costs

| Resource | Usage | Est. Cost/Month |
|----------|-------|-----------------|
| Cloud Run | 100 requests/day | ~$1-5 |
| Cloud Storage | 1 GB | ~$0.02 |
| Secret Manager | 2 secrets | ~$0.12 |
| Artifact Registry | 1 GB | ~$0.10 |
| **Total** | | **~$1-6/month** |

### Optimization Tips

1. **Use Cloud Run's auto-scaling**: Only pay when requests are being processed
2. **Set min instances to 0**: No cost when idle
3. **Use lifecycle policies** for old container images
4. **Monitor with Cloud Monitoring**: Set up budget alerts

---

## Security Best Practices

✅ **DO:**
- Use Secret Manager for all credentials
- Restrict service account permissions (principle of least privilege)
- Enable authentication on Cloud Run
- Use VPC Service Controls for sensitive data
- Regularly rotate secrets
- Monitor access logs

❌ **DON'T:**
- Hardcode credentials in code or Dockerfile
- Commit `.env` or service account keys
- Use `--allow-unauthenticated` in production
- Grant overly permissive IAM roles
- Expose internal endpoints publicly

---

## Production Checklist

Before going to production:

- [ ] Secrets stored in Secret Manager
- [ ] Service account with minimal permissions
- [ ] Authentication enabled on Cloud Run
- [ ] Monitoring and alerting configured
- [ ] Budget alerts set up
- [ ] Backup strategy for GCS bucket
- [ ] Disaster recovery plan documented
- [ ] Security review completed
- [ ] Load testing performed
- [ ] Documentation updated

---

## Support

For deployment issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review Cloud Run logs
3. Run diagnostic tests locally
4. Open an issue on GitHub

---

**Last Updated:** 2024-11-30  
**Tested On:** Google Cloud Run, Python 3.12, Docker 24.0
