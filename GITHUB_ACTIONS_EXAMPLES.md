# 📊 GitHub Actions Workflows - Visual Guide & Examples

## 🔄 Complete CI/CD Flow

```
Developer Push
    ↓
GitHub Actions CI
├─ Lint code (flake8, pylint)
├─ Run unit tests
├─ Train models
├─ Build Docker image
└─ Push to Docker Hub
    ↓
Auto Deploy Dev
├─ Pull Docker image
├─ Deploy to dev server
├─ Run smoke tests
└─ Notify Slack
    ↓
Manual Prod Promotion (workflow_dispatch)
├─ Canary Deployment (10% traffic)
│  ├─ Deploy canary
│  ├─ Run smoke tests
│  ├─ Monitor 5 minutes
│  └─ Create canary record
    ↓
├─ Full Production (100% traffic)
│  ├─ Deploy to production
│  ├─ Run smoke tests
│  ├─ Create GitHub release
│  └─ Notify Slack
```

---

## 📋 Workflow 1: CI Pipeline

**Trigger:** Push to main/develop, Pull Requests

**Example Output:**
```
✅ Lint with flake8 - PASSED
✅ Lint with pylint - PASSED
✅ Unit tests - Training - PASSED (23/23)
✅ Unit tests - API - PASSED (15/15)
✅ Train models - PASSED
✅ Build Docker image - PASSED
✅ Push to Docker Hub - PASSED
```

**View logs:**
```bash
gh run view <run-id> --log
```

---

## 🚀 Workflow 2: Deploy Dev

**Trigger:** Automatic after CI passes

**Example Output:**
```
✅ Pull Docker image
✅ Deploy to Dev
✅ Smoke test - /healthz - PASSED
✅ Smoke test - /predict - PASSED
✅ Notify Slack - PASSED

Slack Message:
┌─────────────────────────────────┐
│ Dev Deployment                  │
│ Status: success                 │
│ Commit: abc123def456            │
│ Triggered by: john-doe          │
└─────────────────────────────────┘
```

---

## 🎯 Workflow 3: Promote Prod

**Trigger:** Manual (workflow_dispatch)

**Example: Canary Deployment**
```bash
# Trigger via CLI
gh workflow run promote-prod.yml \
  -f model_name=iris-logistic-regression \
  -f canary_percentage=10

# Output:
✅ Deploy Canary (10% traffic)
✅ Smoke test - Canary /healthz - PASSED
✅ Smoke test - Canary /predict - PASSED
✅ Monitor canary (5 min) - PASSED
✅ Create canary record - PASSED

Slack Message:
┌─────────────────────────────────┐
│ Canary Deployment               │
│ Model: iris-logistic-regression │
│ Traffic: 10%                    │
│ Status: success                 │
│ Triggered by: john-doe          │
└─────────────────────────────────┘
```

**Example: Full Production**
```
✅ Deploy Full Prod (100% traffic)
✅ Smoke test - Prod /healthz - PASSED
✅ Smoke test - Prod /predict - PASSED
✅ Create release - PASSED
✅ Notify Slack - PASSED

GitHub Release Created:
Tag: prod-iris-logistic-regression-42
Release: Prod - iris-logistic-regression
```

---

## 🔍 Common Commands

### List all workflows
```bash
gh workflow list
```

### View workflow runs
```bash
gh run list --workflow=ci.yml
gh run list --workflow=deploy-dev.yml
gh run list --workflow=promote-prod.yml
```

### View specific run
```bash
gh run view <run-id>
gh run view <run-id> --log
```

### Watch live
```bash
gh run watch <run-id>
```

### Trigger workflow
```bash
gh workflow run promote-prod.yml \
  -f model_name=iris-logistic-regression \
  -f canary_percentage=10
```

### Re-run failed workflow
```bash
gh run rerun <run-id>
```

---

## 📊 Monitoring Dashboard

Create a GitHub Actions dashboard:

```bash
# View all recent runs
gh run list --limit 20

# Filter by status
gh run list --status success
gh run list --status failure
gh run list --status in_progress
```

---

## 🎬 Video Flow Sequence

For your video, show this sequence:

1. **Developer commits code**
   ```bash
   git commit -m "Update model"
   git push origin main
   ```

2. **CI Pipeline runs** (2-3 min)
   - Show linting
   - Show tests passing
   - Show model training
   - Show Docker build

3. **Dev deployment** (1 min)
   - Show smoke tests
   - Show Slack notification

4. **Manual prod promotion** (5 min)
   - Show workflow dispatch
   - Show canary deployment
   - Show monitoring
   - Show full promotion
   - Show GitHub release

---

## 📈 Success Metrics

Track in your video:
- ✅ All tests passing
- ✅ Build time: ~2-3 minutes
- ✅ Deployment time: ~1 minute
- ✅ Canary monitoring: 5 minutes
- ✅ Full promotion: ~1 minute
- ✅ Zero downtime deployments

