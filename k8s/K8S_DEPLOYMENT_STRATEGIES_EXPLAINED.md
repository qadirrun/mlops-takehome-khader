# 🚀 Kubernetes Deployment Strategies Explained

## Overview

Your project includes **3 deployment strategies** for different use cases:

---

## 1️⃣ **Rolling Update** (deployment.yaml)

### How It Works
```
Old Pod (v1.0)  →  Gradually replaced  →  New Pod (v1.1)
```

**Process:**
1. Start 1 new pod (v1.1)
2. Wait for it to be ready
3. Remove 1 old pod (v1.0)
4. Repeat until all pods updated

**Configuration:**
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Max 1 extra pod during update
    maxUnavailable: 0  # Never remove all pods
```

### Pros ✅
- Zero downtime
- Gradual rollout
- Simple to implement
- Automatic rollback on failure

### Cons ❌
- Slower deployment
- Both versions running simultaneously
- More resource usage

### When to Use
- Regular updates
- Non-critical changes
- When you need zero downtime

---

## 2️⃣ **Blue-Green Deployment** (blue-green.yaml)

### How It Works
```
BLUE (v1.0) - ACTIVE
    ↓
    Test GREEN (v1.1)
    ↓
    Switch traffic
    ↓
GREEN (v1.1) - ACTIVE
```

**Process:**
1. Blue deployment runs current version (v1.0)
2. Green deployment runs new version (v1.1)
3. Test green deployment thoroughly
4. Switch traffic from blue to green
5. Keep blue as rollback option

**Configuration:**
```yaml
Blue:
  replicas: 2
  image: iris-classifier:v1.0.0

Green:
  replicas: 0  # Standby
  image: iris-classifier:v1.1.0
```

### Pros ✅
- Zero downtime
- Easy rollback (switch back to blue)
- Full testing before switch
- No version mixing

### Cons ❌
- Double resource usage
- More complex setup
- Requires manual traffic switch

### When to Use
- Major version updates
- Critical deployments
- When rollback is important
- Full testing required

### Deployment Steps
```bash
# 1. Scale up green deployment
kubectl scale deployment iris-classifier-green --replicas=2

# 2. Test green deployment
curl http://iris-classifier-green/healthz

# 3. Switch traffic to green
kubectl patch service iris-classifier -p '{"spec":{"selector":{"version":"green"}}}'

# 4. Monitor green deployment
kubectl logs -l version=green

# 5. If issues, rollback to blue
kubectl patch service iris-classifier -p '{"spec":{"selector":{"version":"blue"}}}'
```

---

## 3️⃣ **Canary Deployment** (canary.yaml)

### How It Works
```
Stable (90% traffic) - v1.0
    ↓
    Gradual shift
    ↓
Canary (10% traffic) - v1.1
    ↓
    Monitor metrics
    ↓
Canary (100% traffic) - v1.1
```

**Process:**
1. Deploy canary version alongside stable
2. Route 10% traffic to canary
3. Monitor error rates, latency, etc.
4. Gradually increase traffic (10% → 50% → 100%)
5. Rollback if issues detected

**Configuration:**
```yaml
Stable:
  replicas: 3
  image: iris-classifier:v1.0.0

Canary:
  replicas: 1
  image: iris-classifier:v1.1.0
  
Ingress:
  canary: "true"
  canary-weight: "10"  # 10% traffic
```

### Pros ✅
- Minimal blast radius
- Early issue detection
- Gradual rollout
- Easy rollback
- Real user testing

### Cons ❌
- Complex monitoring required
- Slower deployment
- Version mixing
- More resource usage

### When to Use
- New features
- Algorithm changes
- When you want early detection
- High-risk changes

### Deployment Steps
```bash
# 1. Deploy canary version
kubectl apply -f k8s/canary.yaml

# 2. Route 10% traffic to canary
kubectl patch ingress iris-classifier-canary \
  -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"10"}}}'

# 3. Monitor metrics
kubectl logs -l version=canary

# 4. Increase traffic gradually
# 10% → 25% → 50% → 100%

# 5. If issues, rollback
kubectl delete deployment iris-classifier-canary
```

---

## 📊 Comparison Table

| Feature | Rolling | Blue-Green | Canary |
|---------|---------|-----------|--------|
| Downtime | ✅ Zero | ✅ Zero | ✅ Zero |
| Rollback Speed | ⚠️ Slow | ✅ Fast | ✅ Fast |
| Resource Usage | ✅ Low | ❌ High | ⚠️ Medium |
| Complexity | ✅ Simple | ⚠️ Medium | ❌ Complex |
| Testing | ⚠️ Limited | ✅ Full | ✅ Real Users |
| Risk | ⚠️ Medium | ✅ Low | ✅ Very Low |
| Deployment Speed | ⚠️ Slow | ✅ Fast | ⚠️ Slow |

---

## 🎯 Decision Guide

### Use Rolling Update if:
- Regular, non-critical updates
- Limited resources
- Simple changes
- Quick deployment needed

### Use Blue-Green if:
- Major version updates
- Critical deployments
- Full testing required
- Easy rollback important

### Use Canary if:
- High-risk changes
- Algorithm changes
- New features
- Early detection important

---

## 🔄 Rollback Procedures

### Rolling Update Rollback
```bash
kubectl rollout undo deployment/iris-classifier
```

### Blue-Green Rollback
```bash
# Switch traffic back to blue
kubectl patch service iris-classifier \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Canary Rollback
```bash
# Delete canary deployment
kubectl delete deployment iris-classifier-canary
```

---

## 📈 Monitoring During Deployment

Watch these metrics:
- **Error Rate** - Should stay < 5%
- **Latency (P95)** - Should stay < 1s
- **CPU Usage** - Should stay < 70%
- **Memory Usage** - Should stay < 80%
- **Pod Restarts** - Should be 0

```bash
# Monitor in real-time
kubectl top pods -n iris-classifier
kubectl get events -n iris-classifier --sort-by='.lastTimestamp'
```


