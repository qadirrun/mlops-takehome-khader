# K8s Load Balancing & Rollback Demo - Expected Output

---

## 📦 **SETUP**

### **Command 1: Deploy the application v1**
```bash
kubectl apply -f k8s/demo-deployment.yaml
```

**Expected Output:**
```
deployment.apps/iris-classifier created
service/iris-classifier created
horizontalpodautoscaler.autoscaling/iris-classifier-hpa created
```

---

### **Command 2: Wait for pods to be ready**
```bash
kubectl get pods -n iris-classifier -w
```

**Expected Output:**
```
NAME                               READY   STATUS              RESTARTS   AGE
iris-classifier-7d8f9b5c4d-abc12   0/1     ContainerCreating   0          2s
iris-classifier-7d8f9b5c4d-def34   0/1     ContainerCreating   0          2s
iris-classifier-7d8f9b5c4d-ghi56   0/1     ContainerCreating   0          2s
iris-classifier-7d8f9b5c4d-abc12   1/1     Running             0          5s
iris-classifier-7d8f9b5c4d-def34   1/1     Running             0          6s
iris-classifier-7d8f9b5c4d-ghi56   1/1     Running             0          7s
```

**✅ When to proceed:** All 3 pods show `1/1 Running` - Press **Ctrl+C**

---

### **Command 3: Create test pod**
```bash
kubectl apply -f k8s/test-pod.yaml
```

**Expected Output:**
```
pod/test-curl created
```

---

## 🔄 **LOAD BALANCING**

### **Command 4: Make 10 requests - watch traffic distributed**
```bash
kubectl exec -n iris-classifier test-curl -- sh -c "for i in 1 2 3 4 5 6 7 8 9 10; do echo '--- Request' \$i '---'; curl -s http://iris-classifier | grep 'Pod:'; done"
```

**Expected Output:**
```
--- Request 1 ---
<p>Pod: iris-classifier-7d8f9b5c4d-abc12</p>
--- Request 2 ---
<p>Pod: iris-classifier-7d8f9b5c4d-def34</p>
--- Request 3 ---
<p>Pod: iris-classifier-7d8f9b5c4d-ghi56</p>
--- Request 4 ---
<p>Pod: iris-classifier-7d8f9b5c4d-abc12</p>
--- Request 5 ---
<p>Pod: iris-classifier-7d8f9b5c4d-def34</p>
--- Request 6 ---
<p>Pod: iris-classifier-7d8f9b5c4d-ghi56</p>
--- Request 7 ---
<p>Pod: iris-classifier-7d8f9b5c4d-abc12</p>
--- Request 8 ---
<p>Pod: iris-classifier-7d8f9b5c4d-def34</p>
--- Request 9 ---
<p>Pod: iris-classifier-7d8f9b5c4d-ghi56</p>
--- Request 10 ---
<p>Pod: iris-classifier-7d8f9b5c4d-abc12</p>
```

**✅ What this shows:** Traffic is **round-robin distributed** across all 3 pods!

---

### **Command 5: Show the 3 pods handling requests**
```bash
kubectl get pods -n iris-classifier -l app=iris-classifier
```

**Expected Output:**
```
NAME                               READY   STATUS    RESTARTS   AGE
iris-classifier-7d8f9b5c4d-abc12   1/1     Running   0          2m30s
iris-classifier-7d8f9b5c4d-def34   1/1     Running   0          2m30s
iris-classifier-7d8f9b5c4d-ghi56   1/1     Running   0          2m30s
```

---

## 🚀 **ROLLING UPDATE**

### **Command 6: Check current version**
```bash
kubectl exec -n iris-classifier test-curl -- curl -s http://iris-classifier
```

**Expected Output:**
```html
<html><body><h1>Iris Classifier v1</h1><p>Pod: iris-classifier-7d8f9b5c4d-abc12</p><p>Version: 1.0.0</p></body></html>
```

**✅ Confirm:** You see **v1** and **Version: 1.0.0**

---

### **Command 7: Deploy v2 (rolling update)**
```bash
kubectl apply -f k8s/demo-deployment-v2.yaml
```

**Expected Output:**
```
deployment.apps/iris-classifier configured
```

---

### **Command 8: Watch pods update one by one**
```bash
kubectl get pods -n iris-classifier -w
```

**Expected Output:**
```
NAME                               READY   STATUS    RESTARTS   AGE
iris-classifier-7d8f9b5c4d-abc12   1/1     Running   0          3m
iris-classifier-7d8f9b5c4d-def34   1/1     Running   0          3m
iris-classifier-7d8f9b5c4d-ghi56   1/1     Running   0          3m
iris-classifier-6c9d8a7b5e-xyz11   0/1     Pending   0          0s
iris-classifier-6c9d8a7b5e-xyz11   0/1     ContainerCreating   0          1s
iris-classifier-6c9d8a7b5e-xyz11   1/1     Running             0          5s
iris-classifier-7d8f9b5c4d-abc12   1/1     Terminating         0          3m5s
iris-classifier-6c9d8a7b5e-uvw22   0/1     Pending             0          0s
iris-classifier-6c9d8a7b5e-uvw22   0/1     ContainerCreating   0          1s
iris-classifier-7d8f9b5c4d-abc12   0/1     Terminating         0          3m8s
iris-classifier-6c9d8a7b5e-uvw22   1/1     Running             0          5s
iris-classifier-7d8f9b5c4d-def34   1/1     Terminating         0          3m10s
iris-classifier-6c9d8a7b5e-rst33   0/1     Pending             0          0s
iris-classifier-6c9d8a7b5e-rst33   0/1     ContainerCreating   0          1s
iris-classifier-7d8f9b5c4d-def34   0/1     Terminating         0          3m13s
iris-classifier-6c9d8a7b5e-rst33   1/1     Running             0          5s
iris-classifier-7d8f9b5c4d-ghi56   1/1     Terminating         0          3m15s
iris-classifier-7d8f9b5c4d-ghi56   0/1     Terminating         0          3m18s
```

**✅ What this shows:** 
- New v2 pod starts → becomes Ready → Old v1 pod terminates
- **Zero downtime** - always at least 3 pods running!

**Press Ctrl+C when all old pods are terminated**

---

### **Command 9: Verify new version**
```bash
kubectl exec -n iris-classifier test-curl -- curl -s http://iris-classifier
```

**Expected Output:**
```html
<html><body><h1 style='color: blue;'>Iris Classifier v2 🚀</h1><p>Pod: iris-classifier-6c9d8a7b5e-xyz11</p><p>Version: 2.0.0</p><p>New Features: Enhanced Performance!</p></body></html>
```

**✅ Confirm:** You see **v2 🚀**, **Version: 2.0.0**, and **New Features**!

---

## ⏪ **ROLLBACK**

### **Command 10: Rollback to v1**
```bash
kubectl rollout undo deployment/iris-classifier -n iris-classifier
```

**Expected Output:**
```
deployment.apps/iris-classifier rolled back
```

---

### **Command 11: Watch rollback happen**
```bash
kubectl get pods -n iris-classifier -w
```

**Expected Output:**
```
NAME                               READY   STATUS    RESTARTS   AGE
iris-classifier-6c9d8a7b5e-xyz11   1/1     Running   0          2m
iris-classifier-6c9d8a7b5e-uvw22   1/1     Running   0          2m
iris-classifier-6c9d8a7b5e-rst33   1/1     Running   0          2m
iris-classifier-7d8f9b5c4d-jkl44   0/1     Pending   0          0s
iris-classifier-7d8f9b5c4d-jkl44   0/1     ContainerCreating   0          1s
iris-classifier-7d8f9b5c4d-jkl44   1/1     Running             0          5s
iris-classifier-6c9d8a7b5e-xyz11   1/1     Terminating         0          2m5s
iris-classifier-7d8f9b5c4d-mno55   0/1     Pending             0          0s
iris-classifier-7d8f9b5c4d-mno55   0/1     ContainerCreating   0          1s
iris-classifier-6c9d8a7b5e-xyz11   0/1     Terminating         0          2m8s
iris-classifier-7d8f9b5c4d-mno55   1/1     Running             0          5s
iris-classifier-6c9d8a7b5e-uvw22   1/1     Terminating         0          2m10s
iris-classifier-7d8f9b5c4d-pqr66   0/1     Pending             0          0s
iris-classifier-7d8f9b5c4d-pqr66   0/1     ContainerCreating   0          1s
iris-classifier-6c9d8a7b5e-uvw22   0/1     Terminating         0          2m13s
iris-classifier-7d8f9b5c4d-pqr66   1/1     Running             0          5s
iris-classifier-6c9d8a7b5e-rst33   1/1     Terminating         0          2m15s
iris-classifier-6c9d8a7b5e-rst33   0/1     Terminating         0          2m18s
```

**✅ What this shows:** Rolling back from v2 → v1 (same smooth process!)

**Press Ctrl+C when rollback completes**

---

### **Command 12: Verify we're back to v1**
```bash
kubectl exec -n iris-classifier test-curl -- curl -s http://iris-classifier
```

**Expected Output:**
```html
<html><body><h1>Iris Classifier v1</h1><p>Pod: iris-classifier-7d8f9b5c4d-jkl44</p><p>Version: 1.0.0</p></body></html>
```

**✅ Confirm:** Back to **v1** and **Version: 1.0.0** - Rollback successful! 🎉

---

### **Command 13: Show rollout history**
```bash
kubectl rollout history deployment/iris-classifier -n iris-classifier
```

**Expected Output:**
```
deployment.apps/iris-classifier
REVISION  CHANGE-CAUSE
2         <none>
3         <none>
```

**✅ What this shows:**
- **Revision 2** = v2 (the update we did)
- **Revision 3** = v1 (the rollback - back to v1)
- Current active revision is **3**

---

## 🎬 **Key Takeaways**

| Feature | What You Saw |
|---------|--------------|
| **Load Balancing** | Traffic distributed across 3 pods in round-robin |
| **Rolling Update** | Pods updated one-by-one with zero downtime |
| **Rollback** | Instant rollback to previous version (~30 seconds) |
| **High Availability** | Always 3+ pods running during updates |

---

## 🧹 **Cleanup**
```bash
kubectl delete -f k8s/demo-deployment.yaml
kubectl delete -f k8s/test-pod.yaml
```

**Expected Output:**
```
deployment.apps "iris-classifier" deleted
service "iris-classifier" deleted
horizontalpodautoscaler.autoscaling "iris-classifier-hpa" deleted
pod "test-curl" deleted
```

---

**🚀 Demo Complete!** You've successfully demonstrated K8s load balancing, rolling updates, and rollbacks!
