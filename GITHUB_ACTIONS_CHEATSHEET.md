# ⚡ GitHub Actions Cheat Sheet

## 🔐 Secrets Management

```bash
# Add secret
gh secret set SECRET_NAME --body "secret-value"

# List secrets
gh secret list

# Delete secret
gh secret delete SECRET_NAME

# Set from file
gh secret set SECRET_NAME < secret.txt
```

---

## 🔄 Workflow Management

```bash
# List workflows
gh workflow list

# Enable workflow
gh workflow enable ci.yml

# Disable workflow
gh workflow disable ci.yml

# View workflow
gh workflow view ci.yml
```

---

## ▶️ Run Management

```bash
# List runs
gh run list

# List runs for specific workflow
gh run list --workflow=ci.yml

# View run details
gh run view <run-id>

# View run logs
gh run view <run-id> --log

# Watch run live
gh run watch <run-id>

# Re-run workflow
gh run rerun <run-id>

# Cancel run
gh run cancel <run-id>

# Delete run
gh run delete <run-id>
```

---

## 🚀 Trigger Workflows

```bash
# Trigger workflow_dispatch
gh workflow run promote-prod.yml \
  -f model_name=iris-logistic-regression \
  -f canary_percentage=10

# Trigger with ref
gh workflow run ci.yml --ref main

# Trigger with inputs
gh workflow run deploy.yml \
  -f environment=production \
  -f version=1.0.0
```

---

## 📊 Filtering Runs

```bash
# By status
gh run list --status success
gh run list --status failure
gh run list --status in_progress

# By workflow
gh run list --workflow=ci.yml

# By actor
gh run list --actor=john-doe

# By branch
gh run list --branch=main

# Limit results
gh run list --limit 50
```

---

## 📝 Workflow Syntax

### Triggers
```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:  # Manual
    inputs:
      model_name:
        type: choice
        options: [model1, model2]
```

### Jobs
```yaml
jobs:
  job-name:
    runs-on: ubuntu-latest
    environment: production  # Approval gate
    steps:
      - uses: actions/checkout@v3
      - run: echo "Hello"
```

### Conditions
```yaml
if: github.ref == 'refs/heads/main'
if: github.event_name == 'push'
if: failure()
if: success()
if: always()
```

### Outputs
```yaml
- name: Set output
  id: step-id
  run: echo "output=value" >> $GITHUB_OUTPUT

- name: Use output
  run: echo ${{ steps.step-id.outputs.output }}
```

---

## 🔑 Common Variables

```yaml
${{ github.ref }}              # Branch/tag
${{ github.sha }}              # Commit hash
${{ github.actor }}            # User who triggered
${{ github.event_name }}       # Event type
${{ github.run_id }}           # Run ID
${{ github.run_number }}       # Run number
${{ github.workspace }}        # Working directory
${{ secrets.SECRET_NAME }}     # Secret value
${{ env.ENV_VAR }}             # Environment variable
${{ matrix.python-version }}   # Matrix variable
```

---

## 📦 Common Actions

```yaml
# Checkout code
- uses: actions/checkout@v3

# Setup Python
- uses: actions/setup-python@v4
  with:
    python-version: '3.12'

# Setup Docker
- uses: docker/setup-buildx-action@v2

# Login to Docker
- uses: docker/login-action@v2
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}

# Build and push Docker
- uses: docker/build-push-action@v4
  with:
    push: true
    tags: myimage:latest

# Upload artifact
- uses: actions/upload-artifact@v3
  with:
    name: artifact-name
    path: path/to/files

# Download artifact
- uses: actions/download-artifact@v3
  with:
    name: artifact-name

# Cache
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip

# Slack notification
- uses: slackapi/slack-github-action@v1.24.0
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🐛 Debugging

```bash
# Enable debug logging
gh run view <run-id> --log --verbose

# Check workflow syntax
gh workflow view ci.yml

# Test locally with act
act -j job-name

# View environment
- run: env | sort
```

---

## 📈 Best Practices

✅ Use secrets for sensitive data  
✅ Cache dependencies  
✅ Use matrix for multiple versions  
✅ Add approval gates for production  
✅ Use concurrency to prevent duplicates  
✅ Add status badges to README  
✅ Monitor workflow runs regularly  
✅ Set retention policies for artifacts  
✅ Use conditional steps  
✅ Add notifications for failures  

---

## 🔗 Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub CLI](https://cli.github.com/)
- [Actions Marketplace](https://github.com/marketplace?type=actions)

