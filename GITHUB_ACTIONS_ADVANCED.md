# 🚀 GitHub Actions - Advanced Customization

## 1. Add Kubernetes Deployment

Add to `promote-prod.yml` after smoke tests:

```yaml
- name: Deploy to Kubernetes
  run: |
    echo "🚀 Deploying to Kubernetes..."
    kubectl set image deployment/iris-classifier \
      iris-classifier=${{ secrets.DOCKER_USERNAME }}/iris-classifier:latest \
      -n iris-classifier
    kubectl rollout status deployment/iris-classifier -n iris-classifier
```

---

## 2. Add Performance Testing

Create `.github/workflows/performance-test.yml`:

```yaml
name: Performance Test

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run load test
        run: |
          pip install locust
          locust -f tests/load_test.py --headless -u 100 -r 10 -t 60s
```

---

## 3. Add Security Scanning

Add to `ci.yml`:

```yaml
- name: Security scan with Bandit
  run: |
    pip install bandit
    bandit -r app/ train/ -f json -o bandit-report.json || true

- name: Upload security report
  uses: actions/upload-artifact@v3
  with:
    name: security-report
    path: bandit-report.json
```

---

## 4. Add Code Coverage Badge

Add to `ci.yml`:

```yaml
- name: Generate coverage badge
  run: |
    pip install coverage-badge
    coverage-badge -o coverage.svg -f

- name: Commit coverage badge
  run: |
    git config user.name "GitHub Actions"
    git config user.email "actions@github.com"
    git add coverage.svg
    git commit -m "Update coverage badge" || true
    git push
```

---

## 5. Add Scheduled Training

Create `.github/workflows/scheduled-training.yml`:

```yaml
name: Scheduled Training

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Train models
        run: python train/main_loop_models.py
      - name: Push artifacts
        run: |
          git add mlruns/ artifacts/
          git commit -m "Weekly model training" || true
          git push
```

---

## 6. Add Approval Gates

Create `.github/environments/production` with required reviewers:

```yaml
# In promote-prod.yml
jobs:
  canary-rollout:
    environment: production  # Requires approval
    runs-on: ubuntu-latest
```

---

## 7. Add Slack Notifications for Failures

Add to any workflow:

```yaml
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1.24.0
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "❌ Workflow Failed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Workflow Failed*\nJob: ${{ github.job }}\nRun: ${{ github.run_id }}"
            }
          }
        ]
      }
```

---

## 8. Add Matrix Testing

Add to `ci.yml`:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pytest tests/ -v
```

---

## 9. Add Artifact Retention

Add to workflows:

```yaml
- name: Upload artifacts
  uses: actions/upload-artifact@v3
  with:
    name: mlflow-artifacts
    path: mlruns/
    retention-days: 90  # Keep for 90 days
```

---

## 10. Add Conditional Steps

```yaml
- name: Deploy to prod
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: echo "Deploying to production"

- name: Deploy to staging
  if: github.ref == 'refs/heads/develop'
  run: echo "Deploying to staging"
```

---

## 11. Add Environment Variables

```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: iris-classifier
  PYTHON_VERSION: '3.12'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building ${{ env.IMAGE_NAME }}"
```

---

## 12. Add Caching

```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

- name: Install dependencies
  run: pip install -r requirements.txt
```

---

## 13. Add Artifact Download

```yaml
- name: Download previous artifacts
  uses: actions/download-artifact@v3
  with:
    name: mlflow-artifacts
    path: mlruns/
```

---

## 14. Add Workflow Status Badge

Add to README.md:

```markdown
![CI Status](https://github.com/YOUR_USERNAME/mlflow/actions/workflows/ci.yml/badge.svg)
![Deploy Status](https://github.com/YOUR_USERNAME/mlflow/actions/workflows/deploy-dev.yml/badge.svg)
```

---

## 15. Add Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This prevents multiple runs of the same workflow on the same branch.

