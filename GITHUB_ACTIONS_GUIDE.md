# 🚀 GitHub Actions Workflows Guide

## Overview

This project has 3 automated workflows:
1. **CI Pipeline** - Lint, test, train, build Docker image
2. **Deploy Dev** - Auto-deploy to dev on push to main
3. **Promote Prod** - Manual canary + full production rollout

---

## 📋 Prerequisites

### 1. GitHub Secrets Setup

Go to **Settings → Secrets and variables → Actions** and add:

```
DOCKER_USERNAME      = your-docker-username
DOCKER_PASSWORD      = your-docker-password (or token)
DEV_API_URL          = http://dev-api.example.com
PROD_API_URL         = http://prod-api.example.com
SLACK_WEBHOOK        = https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 2. GitHub Environments (Optional)

Create 2 environments for approval gates:
- **development** - Auto-deploy
- **production** - Requires manual approval

---

## 🔄 Workflow 1: CI Pipeline

**File:** `.github/workflows/ci.yml`

**Triggers:** Push to main/develop, Pull Requests

**Steps:**
```
1. Checkout code
2. Setup Python 3.12
3. Install dependencies
4. Lint with flake8 & pylint
5. Run unit tests (training + API)
6. Upload coverage to codecov
7. Train models
8. Upload MLflow artifacts
9. Build & push Docker image
```

**How to use:**
```bash
# Automatically runs on:
git push origin main
git push origin develop

# Or create a pull request
```

**View results:**
- Go to **Actions** tab in GitHub
- Click on the workflow run
- View logs for each step

---

## 🚀 Workflow 2: Deploy Dev

**File:** `.github/workflows/deploy-dev.yml`

**Triggers:** Push to main (automatic)

**Steps:**
```
1. Pull Docker image
2. Deploy to dev environment
3. Run smoke tests (/healthz, /predict)
4. Send Slack notification
```

**How to use:**
```bash
# Automatically runs after CI passes
git push origin main
```

**View results:**
- Check **Actions** tab
- Slack notification sent to configured webhook

---

## 🎯 Workflow 3: Promote Prod (Manual)

**File:** `.github/workflows/promote-prod.yml`

**Triggers:** Manual workflow dispatch

**Inputs:**
- Model name (iris-logistic-regression, iris-random-forest, iris-svm)
- Canary percentage (5%, 10%, 25%, 50%)

**Steps:**
```
Job 1: Canary Rollout
  1. Deploy canary (10% traffic)
  2. Run smoke tests
  3. Monitor for 5 minutes
  4. Create canary record

Job 2: Full Promotion
  1. Deploy to 100% traffic
  2. Run smoke tests
  3. Create GitHub release
  4. Send Slack notification
```

**How to use:**

### Option A: GitHub UI
1. Go to **Actions** tab
2. Select **Promote Prod** workflow
3. Click **Run workflow**
4. Select model and canary percentage
5. Click **Run workflow**

### Option B: GitHub CLI
```bash
gh workflow run promote-prod.yml \
  -f model_name=iris-logistic-regression \
  -f canary_percentage=10
```

---

## 📊 Monitoring Workflows

### View Workflow Status
```bash
# List all workflows
gh workflow list

# View specific workflow runs
gh run list --workflow=ci.yml

# View run details
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

### Workflow Badges

Add to README.md:
```markdown
[![CI](https://github.com/YOUR_USERNAME/mlflow/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/mlflow/actions/workflows/ci.yml)
[![Deploy Dev](https://github.com/YOUR_USERNAME/mlflow/actions/workflows/deploy-dev.yml/badge.svg)](https://github.com/YOUR_USERNAME/mlflow/actions/workflows/deploy-dev.yml)
[![Promote Prod](https://github.com/YOUR_USERNAME/mlflow/actions/workflows/promote-prod.yml/badge.svg)](https://github.com/YOUR_USERNAME/mlflow/actions/workflows/promote-prod.yml)
```

---

## 🔧 Customization

### Change Python Version
Edit `.github/workflows/ci.yml`:
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'  # Change here
```

### Add More Tests
```yaml
- name: Integration tests
  run: |
    pytest tests/integration/ -v
```

### Deploy to Kubernetes
Add step to promote-prod.yml:
```yaml
- name: Deploy to K8s
  run: |
    kubectl apply -f k8s/deployment.yaml
    kubectl rollout status deployment/iris-classifier
```

---

## ✅ Troubleshooting

| Issue | Solution |
|-------|----------|
| Docker push fails | Check DOCKER_USERNAME/PASSWORD secrets |
| Tests fail | Run locally: `pytest tests/ -v` |
| Slack notification fails | Verify SLACK_WEBHOOK URL |
| Canary deployment fails | Check PROD_API_URL secret |

---

## 📚 Next Steps

1. ✅ Add secrets to GitHub
2. ✅ Push code to trigger CI
3. ✅ Monitor workflow in Actions tab
4. ✅ Trigger manual prod promotion
5. ✅ Check Slack notifications

