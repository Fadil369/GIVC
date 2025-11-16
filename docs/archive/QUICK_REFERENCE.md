# GIVC Container Orchestration - Quick Reference Card

## 🚀 Quick Deployment Commands

### Docker Compose
```bash
# Development
docker-compose --profile dev up -d

# Production
docker-compose --profile production up -d

# With Monitoring
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### Kubernetes
```bash
# Deploy all
kubectl apply -f k8s/base/ -n givc

# Check status
kubectl get pods -n givc
kubectl get svc -n givc
```

### Helm
```bash
# Install
helm install givc ./helm/givc-chart -n givc --create-namespace

# Upgrade
helm upgrade givc ./helm/givc-chart -n givc

# Status
helm status givc -n givc
```

### Universal Script
```bash
# Docker Compose
./deploy-orchestrated.sh

# Kubernetes
ORCHESTRATOR=kubernetes ./deploy-orchestrated.sh

# Helm
USE_HELM=true ORCHESTRATOR=kubernetes ./deploy-orchestrated.sh
```

---

## 📊 Common Operations

### Check Status
```bash
# Docker Compose
docker-compose ps

# Kubernetes
kubectl get all -n givc

# Helm
helm list -n givc
```

### View Logs
```bash
# Docker Compose
docker-compose logs -f givc-app

# Kubernetes
kubectl logs -f deployment/givc-app -n givc

# Multiple pods
kubectl logs -l app=givc -n givc --tail=100
```

### Scale Services
```bash
# Docker Compose
docker-compose up -d --scale givc-app=5

# Kubernetes
kubectl scale deployment givc-app --replicas=5 -n givc

# Helm
helm upgrade givc ./helm/givc-chart --set frontend.replicaCount=5 -n givc
```

### Restart Services
```bash
# Docker Compose
docker-compose restart givc-app

# Kubernetes
kubectl rollout restart deployment/givc-app -n givc
```

---

## 🔍 Troubleshooting

### Check Pod Issues
```bash
kubectl describe pod <pod-name> -n givc
kubectl get events -n givc --sort-by='.lastTimestamp'
```

### Test Connectivity
```bash
# Internal
kubectl run -it --rm debug --image=curlimages/curl --restart=Never \
  -- curl http://givc-frontend.givc.svc.cluster.local

# Database
kubectl run -it --rm debug --image=postgres:15 --restart=Never \
  -- psql -h postgres -U givc -d givc_production
```

### Check Resources
```bash
kubectl top pods -n givc
kubectl top nodes
```

---

## 📈 Monitoring Access

- **Grafana:** http://localhost:3001 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Alertmanager:** http://localhost:9093

---

## 🔐 Security

### View Secrets
```bash
kubectl get secrets -n givc
kubectl describe secret givc-secrets -n givc
```

### Network Policies
```bash
kubectl get networkpolicies -n givc
kubectl describe networkpolicy givc-frontend-netpol -n givc
```

---

## 🔧 Configuration

### Update ConfigMap
```bash
kubectl edit configmap givc-config -n givc
kubectl rollout restart deployment/givc-app -n givc
```

### Update Secrets
```bash
kubectl create secret generic givc-secrets \
  --from-literal=key=value \
  --dry-run=client -o yaml | kubectl apply -n givc -f -
```

---

## 📦 Cleanup

### Docker Compose
```bash
docker-compose down
docker-compose down -v  # with volumes
```

### Kubernetes
```bash
kubectl delete -f k8s/base/ -n givc
kubectl delete namespace givc
```

### Helm
```bash
helm uninstall givc -n givc
kubectl delete namespace givc
```

---

## 📚 Documentation

- **Review:** CONTAINER_ORCHESTRATION_REVIEW.md
- **Guide:** ORCHESTRATION_GUIDE.md
- **Summary:** CLEANUP_ENHANCEMENTS_SUMMARY.md
- **Completion:** ENHANCEMENT_COMPLETION_REPORT.md

---

## 🆘 Need Help?

1. Check documentation
2. View logs: `kubectl logs -f <pod> -n givc`
3. Check events: `kubectl get events -n givc`
4. Create issue: https://github.com/fadil369/GIVC/issues

---

**Quick Reference v1.0** | GIVC Healthcare Platform
