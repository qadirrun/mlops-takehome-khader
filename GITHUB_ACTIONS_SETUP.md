# 🔧 GitHub Actions Setup - Step by Step

## Step 1: Create GitHub Repository

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/mlflow.git
git branch -M main
git push -u origin main
```

---

## Step 2: Add GitHub Secrets

### Via GitHub UI:
1. Go to your repo → **Settings**
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:

```
Name: DOCKER_USERNAME
Value: your-docker-hub-username

Name: DOCKER_PASSWORD
Value: your-docker-hub-token (NOT password!)
  → Get token: https://hub.docker.com/settings/security

Name: DEV_API_URL
Value: http://localhost:8000 (or your dev server)

Name: PROD_API_URL
Value: http://prod-api.example.com

Name: SLACK_WEBHOOK
Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
  → Get from: https://api.slack.com/messaging/webhooks
```

### Via GitHub CLI:
```bash
gh secret set DOCKER_USERNAME --body "your-username"
gh secret set DOCKER_PASSWORD --body "your-token"
gh secret set DEV_API_URL --body "http://localhost:8000"
gh secret set PROD_API_URL --body "http://prod-api.example.com"
gh secret set SLACK_WEBHOOK --body "https://hooks.slack.com/..."
```

---

## Step 3: Create Environments (Optional)

For approval gates on production:

1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Name: `production`
4. Add required reviewers (optional)
5. Repeat for `development`

---

## Step 4: Verify Workflows

Check that workflow files exist:
```bash
ls -la .github/workflows/
# Should show:
# - ci.yml
# - deploy-dev.yml
# - promote-prod.yml
```

---

## Step 5: Trigger First Workflow

```bash
# Push to main to trigger CI
git push origin main

# View in GitHub Actions tab
# Should see: CI workflow running
```

---

## Step 6: Monitor Workflow

### Via GitHub UI:
1. Go to **Actions** tab
2. Click on workflow run
3. View logs for each step

### Via GitHub CLI:
```bash
# List recent runs
gh run list

# View specific run
gh run view <run-id> --log

# Watch live
gh run watch <run-id>
```

---

## Step 7: Trigger Production Promotion

### Via GitHub UI:
1. Go to **Actions** tab
2. Select **Promote Prod** workflow
3. Click **Run workflow**
4. Select:
   - Model: `iris-logistic-regression`
   - Canary: `10`
5. Click **Run workflow**

### Via GitHub CLI:
```bash
gh workflow run promote-prod.yml \
  -f model_name=iris-logistic-regression \
  -f canary_percentage=10
```

---

## Step 8: Verify Slack Notifications

After workflow completes:
- Check your Slack channel
- Should see deployment status message

---

## ✅ Verification Checklist

- [ ] Repository created on GitHub
- [ ] All secrets added
- [ ] Workflow files in `.github/workflows/`
- [ ] First push triggers CI workflow
- [ ] Tests pass
- [ ] Docker image builds
- [ ] Dev deployment succeeds
- [ ] Slack notification received
- [ ] Manual prod promotion works

---

## 🚨 Troubleshooting

### Workflow doesn't trigger
```bash
# Check workflow syntax
gh workflow view ci.yml

# Re-enable workflow
gh workflow enable ci.yml
```

### Docker push fails
```bash
# Verify credentials
docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD

# Check token has push permissions
```

### Tests fail
```bash
# Run locally first
pytest tests/ -v

# Check Python version matches
python --version
```

### Slack notification fails
```bash
# Test webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' \
  YOUR_SLACK_WEBHOOK_URL
```

---

## 📚 Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [GitHub CLI](https://cli.github.com/)
- [Docker Hub Tokens](https://hub.docker.com/settings/security)
- [Slack Webhooks](https://api.slack.com/messaging/webhooks)

