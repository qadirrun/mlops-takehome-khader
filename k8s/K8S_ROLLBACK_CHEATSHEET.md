# 🔄 Kubernetes Rollback Cheat Sheet

## 1️⃣ Rolling Update Rollback

**When to use:** Regular updates that failed

```bash
# Rollback to previous version
kubectl rollout undo deployment/iris-classifier -n iris-classifier

# Rollback to specific revision
kubectl rollout undo deployment/iris-classifier -n iris-classifier --to-revision=2

# View history
kubectl rollout history deployment/iris-classifier -n iris-classifier

# Monitor progress
kubectl rollout status deployment/iris-classifier -n iris-classifier
```

---

## 2️⃣ Blue-Green Rollback

**When to use:** Major release failed, need instant switch

```bash
# Switch traffic back to blue
kubectl patch service iris-classifier -n iris-classifier \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# Switch traffic back to green
kubectl patch service iris-classifier -n iris-classifier \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Scale down green
kubectl scale deployment iris-classifier-green --replicas=0 -n iris-classifier

# Check current version
kubectl get service iris-classifier -n iris-classifier -o jsonpath='{.spec.selector.version}'
```

---

## 3️⃣ Canary Rollback

**When to use:** Canary deployment showing errors

```bash
# Delete canary deployment
kubectl delete deployment iris-classifier-canary -n iris-classifier

# Delete canary ingress
kubectl delete ingress iris-classifier-canary-ingress -n iris-classifier

# Or scale to 0
kubectl scale deployment iris-classifier-canary --replicas=0 -n iris-classifier

# Reduce traffic to 0%
kubectl patch ingress iris-classifier-canary-ingress -n iris-classifier \
  -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"0"}}}'
```

---

## 4️⃣ Helm Rollback

**When to use:** Helm release broken

```bash
# View release history
helm history iris-classifier -n iris-classifier

# Rollback to previous release
helm rollback iris-classifier -n iris-classifier

# Rollback to specific release
helm rollback iris-classifier 2 -n iris-classifier

# Check status
helm status iris-classifier -n iris-classifier
```

---

## 5️⃣ Emergency Rollback

**When to use:** Critical issue, need immediate action

```bash
# Scale to 0 (stop all pods)
kubectl scale deployment iris-classifier --replicas=0 -n iris-classifier

# Wait 10 seconds
sleep 10

# Recreate from YAML
kubectl apply -f k8s/deployment.yaml

# Force delete stuck pod (if needed)
kubectl delete pod <pod-name> -n iris-classifier --grace-period=0 --force
```

---

## 📊 Monitoring Commands

```bash
# Watch pods
kubectl get pods -n iris-classifier -w

# View events
kubectl get events -n iris-classifier --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n iris-classifier

# View logs
kubectl logs -l app=iris-classifier -n iris-classifier -f

# Describe deployment
kubectl describe deployment iris-classifier -n iris-classifier
```

---

## ✅ Verification Checklist

After rollback, verify:

```bash
# 1. Pods are running
kubectl get pods -n iris-classifier

# 2. Service has endpoints
kubectl get endpoints iris-classifier -n iris-classifier

# 3. Endpoint responds
curl http://iris-classifier.example.com/healthz

# 4. No errors in logs
kubectl logs -l app=iris-classifier -n iris-classifier --tail=50

# 5. Metrics look good
kubectl top pods -n iris-classifier
```

---

## 🎯 Decision Matrix

| Issue | Strategy | Command |
|-------|----------|---------|
| Update failed | Rolling | `kubectl rollout undo` |
| New version broken | Blue-Green | `kubectl patch service` |
| Canary errors | Canary | `kubectl delete deployment` |
| Helm broken | Helm | `helm rollback` |
| Critical issue | Emergency | `kubectl scale --replicas=0` |

---

## 🔗 Scale Commands

```bash
# Scale to N replicas
kubectl scale deployment iris-classifier --replicas=5 -n iris-classifier

# Scale to 0 (stop)
kubectl scale deployment iris-classifier --replicas=0 -n iris-classifier

# Scale to 1 (single pod)
kubectl scale deployment iris-classifier --replicas=1 -n iris-classifier

# Get current replicas
kubectl get deployment iris-classifier -n iris-classifier -o jsonpath='{.spec.replicas}'
```

---

## 🚨 Pause/Resume

```bash
# Pause deployment (useful for canary)
kubectl rollout pause deployment/iris-classifier -n iris-classifier

# Resume deployment
kubectl rollout resume deployment/iris-classifier -n iris-classifier
```

---

## 📝 Common Issues

### Pods stuck in pending
```bash
kubectl describe pod <pod-name> -n iris-classifier
kubectl delete pod <pod-name> -n iris-classifier
```

### Rollback not working
```bash
kubectl rollout history deployment/iris-classifier -n iris-classifier
kubectl describe deployment iris-classifier -n iris-classifier
```

### Service not routing
```bash
kubectl get service iris-classifier -n iris-classifier -o yaml
kubectl get endpoints iris-classifier -n iris-classifier
```


