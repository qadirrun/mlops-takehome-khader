# 🔄 Kubernetes & Helm Rollback Guide

## Overview

This guide covers rollback procedures for different deployment strategies and tools.

---

## 🚀 Rolling Update Rollback

### Automatic Rollback (On Failure)
Kubernetes automatically rolls back if pods fail health checks.

### Manual Rollback

#### View Rollout History
```bash
# See all revisions
kubectl rollout history deployment/iris-classifier -n iris-classifier

# See details of specific revision
kubectl rollout history deployment/iris-classifier -n iris-classifier --revision=2
```

#### Rollback to Previous Version
```bash
# Rollback to previous revision
kubectl rollout undo deployment/iris-classifier -n iris-classifier

# Rollback to specific revision
kubectl rollout undo deployment/iris-classifier -n iris-classifier --to-revision=2
```

#### Monitor Rollback Progress
```bash
# Watch rollback in real-time
kubectl rollout status deployment/iris-classifier -n iris-classifier

# Watch pods being replaced
kubectl get pods -n iris-classifier -w
```

#### Pause/Resume Rollout
```bash
# Pause deployment (useful for canary)
kubectl rollout pause deployment/iris-classifier -n iris-classifier

# Resume deployment
kubectl rollout resume deployment/iris-classifier -n iris-classifier
```

---

## 🔵🟢 Blue-Green Rollback

### Instant Rollback (Switch Traffic Back)

#### Option 1: Patch Service Selector
```bash
# Switch traffic back to blue
kubectl patch service iris-classifier \
  -n iris-classifier \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# Verify traffic switched
kubectl get service iris-classifier -n iris-classifier -o yaml | grep version
```

#### Option 2: Update Service YAML
```bash
# Edit service
kubectl edit service iris-classifier -n iris-classifier

# Change selector from:
#   version: green
# To:
#   version: blue

# Save and exit
```

#### Option 3: Scale Down Green
```bash
# Scale green deployment to 0
kubectl scale deployment iris-classifier-green \
  --replicas=0 \
  -n iris-classifier

# Scale blue deployment back up
kubectl scale deployment iris-classifier-blue \
  --replicas=2 \
  -n iris-classifier
```

### Verify Rollback
```bash
# Check which version is active
kubectl get service iris-classifier -n iris-classifier -o jsonpath='{.spec.selector.version}'

# Check pod versions
kubectl get pods -n iris-classifier -L version

# Test endpoint
curl http://iris-classifier.example.com/healthz
```

---

## 🐤 Canary Rollback

### Immediate Rollback

#### Delete Canary Deployment
```bash
# Delete canary deployment
kubectl delete deployment iris-classifier-canary -n iris-classifier

# Verify deletion
kubectl get deployments -n iris-classifier
```

#### Scale Down Canary
```bash
# Scale canary to 0 replicas
kubectl scale deployment iris-classifier-canary \
  --replicas=0 \
  -n iris-classifier

# Verify
kubectl get pods -n iris-classifier -L version
```

#### Reduce Canary Traffic to 0%
```bash
# Edit ingress
kubectl edit ingress iris-classifier-canary-ingress -n iris-classifier

# Change canary-weight from 10 to 0:
# nginx.ingress.kubernetes.io/canary-weight: "0"

# Save and exit
```

### Gradual Rollback (Reverse Canary)

```bash
# Reduce traffic gradually
# 10% → 5% → 2% → 0%

kubectl patch ingress iris-classifier-canary-ingress \
  -n iris-classifier \
  -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"5"}}}'

# Wait and monitor metrics
sleep 300

# Continue reducing
kubectl patch ingress iris-classifier-canary-ingress \
  -n iris-classifier \
  -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"0"}}}'
```

---

## 📦 Helm Rollback

### View Helm Release History
```bash
# List all releases
helm list -n iris-classifier

# View release history
helm history iris-classifier -n iris-classifier

# See details of specific release
helm history iris-classifier -n iris-classifier --max 10
```

### Rollback to Previous Release
```bash
# Rollback to previous release
helm rollback iris-classifier -n iris-classifier

# Rollback to specific release number
helm rollback iris-classifier 2 -n iris-classifier
```

### Verify Helm Rollback
```bash
# Check current release
helm status iris-classifier -n iris-classifier

# Get values of current release
helm get values iris-classifier -n iris-classifier

# Get manifest of current release
helm get manifest iris-classifier -n iris-classifier
```

---

## 🔍 Monitoring During Rollback

### Watch Pods
```bash
# Watch pods in real-time
kubectl get pods -n iris-classifier -w

# Watch specific deployment
kubectl get pods -n iris-classifier -l app=iris-classifier -w
```

### Check Events
```bash
# View recent events
kubectl get events -n iris-classifier --sort-by='.lastTimestamp'

# Watch events in real-time
kubectl get events -n iris-classifier -w
```

### Monitor Metrics
```bash
# Check CPU/Memory usage
kubectl top pods -n iris-classifier

# Check node resources
kubectl top nodes
```

### View Logs
```bash
# View logs of current pods
kubectl logs -l app=iris-classifier -n iris-classifier --tail=50

# Follow logs in real-time
kubectl logs -l app=iris-classifier -n iris-classifier -f

# View logs of specific pod
kubectl logs <pod-name> -n iris-classifier
```

---

## 🚨 Emergency Rollback

### Scale Down Problematic Deployment
```bash
# Immediately scale down to 0
kubectl scale deployment iris-classifier \
  --replicas=0 \
  -n iris-classifier

# Verify pods are terminating
kubectl get pods -n iris-classifier
```

### Delete and Recreate
```bash
# Delete deployment
kubectl delete deployment iris-classifier -n iris-classifier

# Recreate from YAML
kubectl apply -f k8s/deployment.yaml
```

### Force Delete Stuck Pods
```bash
# Force delete pod (use with caution!)
kubectl delete pod <pod-name> \
  -n iris-classifier \
  --grace-period=0 \
  --force
```

---

## 📊 Rollback Decision Matrix

| Scenario | Strategy | Command |
|----------|----------|---------|
| Regular update failed | Rolling | `kubectl rollout undo` |
| New version has bugs | Blue-Green | Patch service selector |
| Canary shows errors | Canary | Delete canary deployment |
| Helm release broken | Helm | `helm rollback` |
| Emergency situation | Emergency | Scale to 0, then recreate |

---

## ✅ Rollback Checklist

- [ ] Identify issue (error rate, latency, crashes)
- [ ] Choose rollback strategy
- [ ] Execute rollback command
- [ ] Monitor metrics (CPU, memory, errors)
- [ ] Check logs for errors
- [ ] Verify health checks passing
- [ ] Test endpoints
- [ ] Confirm traffic flowing correctly
- [ ] Document incident
- [ ] Post-mortem analysis

---

## 🔗 Related Commands

```bash
# Get deployment info
kubectl get deployment iris-classifier -n iris-classifier -o yaml

# Describe deployment
kubectl describe deployment iris-classifier -n iris-classifier

# Get pod details
kubectl describe pod <pod-name> -n iris-classifier

# Check resource usage
kubectl top pods -n iris-classifier
```


