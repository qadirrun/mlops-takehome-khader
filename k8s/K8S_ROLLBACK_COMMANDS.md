# 🔄 Kubernetes & Helm Rollback Commands

## Quick Reference

### Rolling Update Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/iris-classifier -n iris-classifier

# Rollback to specific revision
kubectl rollout undo deployment/iris-classifier -n iris-classifier --to-revision=2

# View rollout history
kubectl rollout history deployment/iris-classifier -n iris-classifier

# Monitor rollback progress
kubectl rollout status deployment/iris-classifier -n iris-classifier
```

### Blue-Green Rollback
```bash
# Switch traffic back to blue
kubectl patch service iris-classifier -n iris-classifier \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# Switch traffic back to green
kubectl patch service iris-classifier -n iris-classifier \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Scale down green deployment
kubectl scale deployment iris-classifier-green --replicas=0 -n iris-classifier

# Scale down blue deployment
kubectl scale deployment iris-classifier-blue --replicas=0 -n iris-classifier

# Check current active version
kubectl get service iris-classifier -n iris-classifier -o jsonpath='{.spec.selector.version}'
```

### Canary Rollback
```bash
# Delete canary deployment
kubectl delete deployment iris-classifier-canary -n iris-classifier

# Delete canary ingress
kubectl delete ingress iris-classifier-canary-ingress -n iris-classifier

# Scale canary to 0
kubectl scale deployment iris-classifier-canary --replicas=0 -n iris-classifier

# Reduce canary traffic to 0%
kubectl patch ingress iris-classifier-canary-ingress -n iris-classifier \
  -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"0"}}}'
```

### Helm Rollback
```bash
# View Helm release history
helm history iris-classifier -n iris-classifier

# Rollback to previous release
helm rollback iris-classifier -n iris-classifier

# Rollback to specific release
helm rollback iris-classifier 2 -n iris-classifier

# Check current release status
helm status iris-classifier -n iris-classifier

# Get values of current release
helm get values iris-classifier -n iris-classifier
```

### Emergency Rollback
```bash
# Scale deployment to 0 (stop all pods)
kubectl scale deployment iris-classifier --replicas=0 -n iris-classifier

# Recreate deployment from YAML
kubectl apply -f k8s/deployment.yaml

# Force delete stuck pod
kubectl delete pod <pod-name> -n iris-classifier --grace-period=0 --force
```

---

## Monitoring During Rollback

```bash
# Watch pods in real-time
kubectl get pods -n iris-classifier -w

# View recent events
kubectl get events -n iris-classifier --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n iris-classifier

# View logs
kubectl logs -l app=iris-classifier -n iris-classifier -f

# Describe deployment
kubectl describe deployment iris-classifier -n iris-classifier
```

---

## Pause/Resume Deployment

```bash
# Pause deployment (useful for canary)
kubectl rollout pause deployment/iris-classifier -n iris-classifier

# Resume deployment
kubectl rollout resume deployment/iris-classifier -n iris-classifier
```

---

## Scale Commands

```bash
# Scale to specific number of replicas
kubectl scale deployment iris-classifier --replicas=5 -n iris-classifier

# Scale to 0 (stop all)
kubectl scale deployment iris-classifier --replicas=0 -n iris-classifier

# Scale to 1 (single pod)
kubectl scale deployment iris-classifier --replicas=1 -n iris-classifier

# Check current replicas
kubectl get deployment iris-classifier -n iris-classifier -o jsonpath='{.spec.replicas}'
```

---

## Verify Rollback Success

```bash
# Check pod status
kubectl get pods -n iris-classifier

# Check deployment status
kubectl get deployment iris-classifier -n iris-classifier

# Check service endpoints
kubectl get endpoints iris-classifier -n iris-classifier

# Test endpoint
curl http://iris-classifier.example.com/healthz

# Check logs for errors
kubectl logs -l app=iris-classifier -n iris-classifier --tail=50
```

---

## Rollback Decision Tree

```
Issue detected?
├─ Regular update failed?
│  └─ Use: kubectl rollout undo
├─ Blue-Green deployment broken?
│  └─ Use: kubectl patch service (switch version)
├─ Canary showing errors?
│  └─ Use: kubectl delete deployment (canary)
├─ Helm release broken?
│  └─ Use: helm rollback
└─ Emergency situation?
   └─ Use: kubectl scale --replicas=0
```

---

## Common Issues & Solutions

### Pods stuck in pending
```bash
kubectl describe pod <pod-name> -n iris-classifier
kubectl delete pod <pod-name> -n iris-classifier
```

### Rollback not working
```bash
# Check rollout history
kubectl rollout history deployment/iris-classifier -n iris-classifier

# Check deployment status
kubectl describe deployment iris-classifier -n iris-classifier
```

### Service not routing traffic
```bash
# Check service selector
kubectl get service iris-classifier -n iris-classifier -o yaml

# Check endpoints
kubectl get endpoints iris-classifier -n iris-classifier
```


