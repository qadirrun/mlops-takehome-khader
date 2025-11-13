# 🎯 Kubernetes (K8s) - Complete Summary

## What is Kubernetes?

Kubernetes is a **container orchestration platform** that automates:
- **Deployment** - Automatically deploy containers
- **Scaling** - Add/remove containers based on load
- **Management** - Keep containers running, restart if failed
- **Updates** - Deploy new versions with zero downtime

Think of it as an intelligent system that manages your Docker containers across multiple machines.

---

## 🏗️ Your K8s Architecture

```
Internet Users
    ↓
DNS: iris-classifier.example.com
    ↓
Ingress (NGINX)
├─ TLS/SSL encryption
├─ Rate limiting (100 req/sec)
├─ CORS enabled
└─ Routes traffic
    ↓
Service (Load Balancer)
├─ Internal DNS name
├─ Port 80 → 8000
└─ Distributes traffic
    ↓
3 Pods (Replicas)
├─ Pod 1: iris-classifier:latest
├─ Pod 2: iris-classifier:latest
└─ Pod 3: iris-classifier:latest
    ↓
Auto-Scaling (HPA)
├─ Min: 2 pods
├─ Max: 10 pods
├─ CPU target: 70%
└─ Memory target: 80%
```

---

## 📁 Core Components

### 1. **Namespace** (namespace.yaml)
- **Purpose**: Isolation & security
- **Includes**:
  - Resource quotas (CPU, memory, pods)
  - Network policies (traffic control)
  - RBAC (permissions)
  - ConfigMap (configuration)
  - Secret (sensitive data)

### 2. **Deployment** (deployment.yaml)
- **Purpose**: Pod management
- **Features**:
  - 3 replicas (3 copies running)
  - Rolling update strategy
  - Health checks (startup, readiness, liveness)
  - Resource limits (CPU, memory)
  - Security context (non-root user)

### 3. **Service** (service.yaml)
- **Purpose**: Network access
- **Types**:
  - ClusterIP: Internal access
  - Headless: Direct pod access
  - Metrics: Prometheus scraping
- **HPA**: Auto-scales 2-10 pods

### 4. **Ingress** (ingress.yaml)
- **Purpose**: External access
- **Features**:
  - Domain: iris-classifier.example.com
  - TLS/SSL: Let's Encrypt
  - Rate limiting: 100 req/sec
  - CORS: Enabled
  - Paths: /, /api, /metrics

---

## 🚀 Deployment Strategies

### Rolling Update (Default)
```
Old Pod (v1.0) → Gradually replaced → New Pod (v1.1)
```
- **Downtime**: Zero
- **Speed**: Slow
- **Rollback**: Automatic
- **Use for**: Regular updates

### Blue-Green
```
Blue (v1.0) ACTIVE → Test Green (v1.1) → Switch traffic
```
- **Downtime**: Zero
- **Speed**: Fast
- **Rollback**: Instant
- **Use for**: Major releases

### Canary
```
Stable (90%) → Gradual shift → Canary (10%) → 100%
```
- **Downtime**: Zero
- **Speed**: Slow
- **Rollback**: Easy
- **Use for**: High-risk changes

---

## 🔧 Configuration

### ConfigMap (Non-sensitive)
```yaml
ENVIRONMENT: production
LOG_LEVEL: INFO
METRICS_ENABLED: true
HEALTH_CHECK_INTERVAL: 30
```

### Secret (Sensitive)
```yaml
MLFLOW_TRACKING_URI: http://mlflow-server:5000
MODEL_REGISTRY_URI: http://mlflow-server:5000
```

### Resource Limits (Per Pod)
```yaml
Requests:
  CPU: 100m (0.1 cores)
  Memory: 256Mi

Limits:
  CPU: 500m (0.5 cores)
  Memory: 512Mi
```

---

## 🏥 Health Checks

| Probe | Purpose | Interval | Action |
|-------|---------|----------|--------|
| Startup | Wait for app to start | 10s | Retry 30x |
| Readiness | Check if ready for traffic | 5s | Remove from service |
| Liveness | Check if alive | 10s | Restart pod |

---

## 📈 Auto-Scaling (HPA)

**Triggers:**
- CPU > 70% → Scale up
- Memory > 80% → Scale up
- CPU < 70% → Scale down
- Memory < 80% → Scale down

**Limits:**
- Minimum: 2 pods
- Maximum: 10 pods

---

## 🔐 Security Features

✅ Non-root user (UID 1000)
✅ No privilege escalation
✅ Read-only root filesystem
✅ Network policies
✅ RBAC (Role-Based Access Control)
✅ Secrets management
✅ TLS/SSL encryption
✅ Resource quotas

---

## 💻 Quick Commands

### Deploy
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### Check Status
```bash
kubectl get pods -n iris-classifier
kubectl get services -n iris-classifier
kubectl get hpa -n iris-classifier
```

### View Logs
```bash
kubectl logs -l app=iris-classifier -n iris-classifier
```

### Scale Manually
```bash
kubectl scale deployment iris-classifier --replicas=5 -n iris-classifier
```

### Rollback Commands
```bash
# Rolling Update Rollback
kubectl rollout undo deployment/iris-classifier -n iris-classifier

# Blue-Green Rollback (switch traffic)
kubectl patch service iris-classifier -n iris-classifier \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# Canary Rollback (delete canary)
kubectl delete deployment iris-classifier-canary -n iris-classifier

# Helm Rollback
helm rollback iris-classifier -n iris-classifier

# Emergency (scale to 0)
kubectl scale deployment iris-classifier --replicas=0 -n iris-classifier
```

---

## 📊 Monitoring

**Prometheus Integration:**
- Scrapes `/metrics-prometheus` endpoint
- Collects metrics from all pods
- Alerts on thresholds
- Grafana visualization

**Metrics Tracked:**
- Request rate (RPS)
- Error rate
- Latency (P95, P99)
- CPU usage
- Memory usage

---

## 🎯 When to Use Each Strategy

| Strategy | Use When |
|----------|----------|
| Rolling | Regular updates, non-critical |
| Blue-Green | Major releases, critical |
| Canary | High-risk, algorithm changes |

---

## � Rollback Procedures

### Rolling Update Rollback
```bash
kubectl rollout undo deployment/iris-classifier -n iris-classifier
kubectl rollout undo deployment/iris-classifier -n iris-classifier --to-revision=2
```

### Blue-Green Rollback
```bash
# Switch traffic back to blue
kubectl patch service iris-classifier -n iris-classifier \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Canary Rollback
```bash
# Delete canary deployment
kubectl delete deployment iris-classifier-canary -n iris-classifier
```

### Helm Rollback
```bash
helm rollback iris-classifier -n iris-classifier
helm rollback iris-classifier 2 -n iris-classifier  # Specific release
```

### Emergency Rollback
```bash
# Scale to 0 and recreate
kubectl scale deployment iris-classifier --replicas=0 -n iris-classifier
kubectl apply -f k8s/deployment.yaml
```

---

## �📚 Documentation Files

| File | Content |
|------|---------|
| `KUBERNETES_EXPLANATION.md` | Detailed explanation |
| `K8S_DEPLOYMENT_STRATEGIES_EXPLAINED.md` | Strategies guide |
| `K8S_QUICK_REFERENCE.md` | Quick reference |
| `K8S_ROLLBACK_GUIDE.md` | Detailed rollback procedures |
| `K8S_ROLLBACK_COMMANDS.md` | Rollback commands reference |
| `K8S_ROLLBACK_CHEATSHEET.md` | Quick rollback cheat sheet |
| `K8S_ROLLBACK_INDEX.md` | Rollback documentation index |
| `ROLLBACK_FEATURE_SUMMARY.md` | Feature overview |
| `ROLLBACK_IMPLEMENTATION_COMPLETE.md` | Implementation status |

---

## ✨ Key Takeaways

1. **Kubernetes automates** deployment, scaling, and management
2. **Your setup** has 3 replicas with auto-scaling (2-10 pods)
3. **Zero downtime** deployments with rolling/blue-green/canary
4. **Security** with RBAC, network policies, and secrets
5. **Monitoring** integrated with Prometheus & Grafana
6. **Production ready** with health checks and resource limits


