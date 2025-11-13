# CI/CD Pipeline Guide

## Overview

This project uses GitHub Actions for automated CI/CD with the following workflow:

```
Push to main/develop
    ↓
CI Pipeline (Lint → Test → Train → Build Docker)
    ↓
Auto Deploy to Dev (on main merge)
    ↓
Manual Canary → Full Prod Promotion
```

---

## Workflows

### 1. **CI Pipeline** (`ci.yml`)
**Trigger**: Push to `main` or `develop`, Pull Requests

**Job 1: Lint & Test**
- ✅ Flake8 linting (code style)
- ✅ Pylint linting (code quality)
- ✅ Unit tests - Training module (≥1 test)
- ✅ Unit tests - API module (≥1 test)
- ✅ Code coverage reporting
- ✅ Train all 3 models
- ✅ Upload MLflow artifacts

**Job 2: Build & Push Docker**
- ✅ Set up Docker Buildx
- ✅ Login to Docker Hub
- ✅ Build Docker image
- ✅ Push to registry (on main push)
- ✅ Tag with commit SHA and latest

**Artifacts**:
- `mlflow-artifacts/` - MLflow tracking data
- Docker image in registry

---

### 2. **Auto Deploy to Dev** (`deploy-dev.yml`)
**Trigger**: Push to `main` branch (automatic)

**Steps**:
- ✅ Pull Docker image from registry
- ✅ Deploy to Dev environment
- ✅ Smoke test: `/healthz` endpoint
- ✅ Smoke test: `/predict` endpoint
- ✅ Notify Slack

**Smoke Tests**:
- `GET /healthz` - Returns 200 with status "ok"
- `POST /predict` - Returns 200 with prediction

**Environment Variables** (set in GitHub Secrets):
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password
- `DEV_API_URL` - Dev API URL
- `SLACK_WEBHOOK` - Slack notification webhook

---

### 3. **Promote to Prod** (`promote-prod.yml`)
**Trigger**: Manual workflow dispatch

**Inputs**:
- `model_name` - Which model to deploy
  - `iris-logistic-regression`
  - `iris-random-forest`
  - `iris-svm`
- `canary_percentage` - Traffic percentage (5, 10, 25, 50)

**Job 1: Canary Rollout**
- ✅ Pull Docker image
- ✅ Deploy canary (e.g., 10% traffic on port 8001)
- ✅ Smoke test: `/healthz` endpoint
- ✅ Smoke test: `/predict` endpoint
- ✅ Monitor for 5 minutes
- ✅ Create canary record

**Job 2: Full Promotion** (depends on canary success)
- ✅ Pull Docker image
- ✅ Deploy full prod (100% traffic on port 8000)
- ✅ Smoke test: `/healthz` endpoint
- ✅ Smoke test: `/predict` endpoint
- ✅ Create GitHub release
- ✅ Notify Slack

**Environment Variables**:
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password
- `PROD_API_URL` - Prod API URL
- `SLACK_WEBHOOK` - Slack notification webhook

---

## Setup Instructions

### 1. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

```
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
DEV_API_URL=http://localhost:8000
PROD_API_URL=http://localhost:8000
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 2. Configure Environments

Go to **Settings → Environments** and create:

- **development** - No approval needed
- **production** - Manual approval (requires 2 reviewers)

### 3. Set Branch Protection Rules

Go to **Settings → Branches** and add rules for `main`:

- ✅ Require status checks to pass (CI workflow)
- ✅ Require code reviews (1+ reviewers)
- ✅ Dismiss stale PR approvals
- ✅ Require branches to be up to date

---

## Usage Examples

### 1. Trigger CI Pipeline
```bash
# Push to main or develop
git push origin main

# Automatically:
# 1. Runs linting (flake8, pylint)
# 2. Runs unit tests (training + API)
# 3. Trains all 3 models
# 4. Builds and pushes Docker image
```

### 2. Auto Deploy to Dev
```bash
# Merge PR to main
# Automatically:
# 1. Pulls Docker image
# 2. Deploys to Dev
# 3. Runs smoke tests (/healthz, /predict)
# 4. Notifies Slack
```

### 3. Manual Canary → Full Prod Promotion
1. Go to **Actions** tab
2. Select **Promote Prod**
3. Click **Run workflow**
4. Fill in:
   - Model: `iris-logistic-regression`
   - Canary %: `10`
5. Click **Run workflow**

**What happens**:
- Job 1: Deploys canary (10% traffic on port 8001)
  - Smoke tests pass → proceeds to Job 2
- Job 2: Full promotion (100% traffic on port 8000)
  - Creates GitHub release
  - Notifies Slack

---

## Monitoring

### View Workflow Runs
- Go to **Actions** tab
- Click on workflow name
- View run history and logs

### Slack Notifications
All deployments send notifications to Slack with:
- Status (success/failure)
- Model name
- Environment
- Triggered by (user)

### Artifacts
Download artifacts from workflow runs:
- MLflow tracking data
- Deployment records
- Canary/rollback records

---

## Best Practices

1. **Always test in Dev first** - Let auto-deploy validate changes
2. **Start with small canary** - Use 10% traffic initially
3. **Monitor metrics** - Check logs before full rollout
4. **Document rollbacks** - Always provide reason
5. **Review releases** - Check GitHub releases for deployment history

---

## Troubleshooting

### CI Pipeline Fails
- Check test logs in Actions
- Verify dependencies in `requirements.txt`
- Ensure Python 3.12 compatibility

### Dev Deployment Fails
- Check `DEV_DEPLOY_URL` and `DEV_API_KEY` secrets
- Verify dev environment is running
- Check deployment logs

### Canary Deployment Fails
- Validate model exists: `mlflow models list`
- Check `PROD_DEPLOY_URL` and `PROD_API_KEY`
- Review canary percentage (start with 5%)

### Rollback Fails
- Ensure previous model version exists
- Check environment is accessible
- Verify API credentials

