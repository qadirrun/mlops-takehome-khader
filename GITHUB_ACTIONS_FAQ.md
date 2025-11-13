# ❓ GitHub Actions - FAQ & Troubleshooting

## ❓ Frequently Asked Questions

### Q: How do I view workflow logs?
**A:** 
```bash
# Via GitHub UI: Actions tab → Click run → View logs
# Via CLI:
gh run view <run-id> --log
```

### Q: How do I trigger a workflow manually?
**A:**
```bash
# Via GitHub UI: Actions → Workflow → Run workflow
# Via CLI:
gh workflow run promote-prod.yml -f model_name=iris-logistic-regression
```

### Q: How do I re-run a failed workflow?
**A:**
```bash
gh run rerun <run-id>
```

### Q: How do I cancel a running workflow?
**A:**
```bash
gh run cancel <run-id>
```

### Q: How do I add a new secret?
**A:**
```bash
gh secret set SECRET_NAME --body "secret-value"
```

### Q: How do I list all secrets?
**A:**
```bash
gh secret list
```

### Q: How do I delete a secret?
**A:**
```bash
gh secret delete SECRET_NAME
```

### Q: How long do artifacts stay?
**A:** Default 90 days. Configure in workflow:
```yaml
- uses: actions/upload-artifact@v3
  with:
    retention-days: 30
```

### Q: Can I run workflows on schedule?
**A:** Yes, use cron:
```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly Sunday
```

### Q: How do I add approval gates?
**A:** Create environment in Settings → Environments, then:
```yaml
jobs:
  deploy:
    environment: production
```

---

## 🐛 Troubleshooting

### Problem: Workflow doesn't trigger
**Solution:**
```bash
# Check if workflow is enabled
gh workflow list

# Enable if disabled
gh workflow enable ci.yml

# Check syntax
gh workflow view ci.yml
```

### Problem: Docker push fails
**Solution:**
```bash
# Verify credentials
docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD

# Check token has push permissions
# Regenerate token at: https://hub.docker.com/settings/security
```

### Problem: Tests fail in CI but pass locally
**Solution:**
```bash
# Check Python version matches
python --version

# Install exact dependencies
pip install -r requirements.txt

# Run tests with same flags
pytest tests/ -v --tb=short
```

### Problem: Slack notification fails
**Solution:**
```bash
# Test webhook manually
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' \
  YOUR_SLACK_WEBHOOK_URL

# Verify webhook URL in secrets
gh secret list
```

### Problem: Canary deployment fails
**Solution:**
```bash
# Check PROD_API_URL secret
gh secret list

# View deployment logs
gh run view <run-id> --log

# Check if API is running
curl http://localhost:8000/healthz
```

### Problem: GitHub Actions quota exceeded
**Solution:**
- Free tier: 2,000 minutes/month
- Upgrade to Pro/Team for more minutes
- Optimize workflow to run faster
- Use caching to speed up builds

### Problem: Artifact too large
**Solution:**
```yaml
# Reduce retention days
retention-days: 7

# Exclude unnecessary files
- uses: actions/upload-artifact@v3
  with:
    path: |
      artifacts/
      !artifacts/temp/
```

### Problem: Workflow times out
**Solution:**
```yaml
# Increase timeout (default 360 min)
jobs:
  build:
    timeout-minutes: 600
```

### Problem: Permission denied errors
**Solution:**
```bash
# Check GitHub token permissions
# Settings → Developer settings → Personal access tokens

# Regenerate token with correct scopes:
# - repo (full control)
# - workflow (GitHub Actions)
```

---

## 🔍 Debugging Tips

### Enable debug logging
```bash
gh run view <run-id> --log --verbose
```

### Print environment variables
```yaml
- name: Debug environment
  run: env | sort
```

### Print GitHub context
```yaml
- name: Debug context
  run: echo "${{ toJson(github) }}"
```

### Test workflow locally
```bash
# Install act
brew install act

# Run workflow locally
act -j job-name
```

### Check workflow syntax
```bash
gh workflow view ci.yml
```

---

## 📊 Monitoring

### View all runs
```bash
gh run list --limit 50
```

### Filter by status
```bash
gh run list --status success
gh run list --status failure
gh run list --status in_progress
```

### Watch live
```bash
gh run watch <run-id>
```

### Get run summary
```bash
gh run view <run-id>
```

---

## 🚀 Performance Tips

✅ Use caching for dependencies  
✅ Use matrix for parallel testing  
✅ Use conditional steps to skip unnecessary jobs  
✅ Use concurrency to prevent duplicate runs  
✅ Optimize Docker image size  
✅ Use smaller base images (alpine)  
✅ Cache Docker layers  
✅ Parallelize jobs when possible  

---

## 📈 Best Practices

✅ Use secrets for sensitive data  
✅ Add approval gates for production  
✅ Monitor workflow runs regularly  
✅ Set retention policies for artifacts  
✅ Use status badges in README  
✅ Add notifications for failures  
✅ Document workflow steps  
✅ Test workflows locally with act  
✅ Use concurrency control  
✅ Version your actions  

---

## 🔗 Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub CLI Docs](https://cli.github.com/manual/)
- [Actions Marketplace](https://github.com/marketplace?type=actions)
- [act - Run workflows locally](https://github.com/nektos/act)

