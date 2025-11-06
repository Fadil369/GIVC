# GIVC Healthcare Platform - Container Orchestration Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Deployment Options](#deployment-options)
5. [Configuration](#configuration)
6. [Monitoring & Observability](#monitoring--observability)
7. [Scaling](#scaling)
8. [Security](#security)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Overview

This guide provides comprehensive instructions for deploying and managing the GIVC Healthcare Platform using container orchestration. The platform supports multiple orchestration engines:

- **Docker Compose** (Development & Small Scale)
- **Kubernetes** (Production & Enterprise)
- **Docker Swarm** (Mid-scale deployments)
- **Helm Charts** (Kubernetes package management)

### System Requirements

#### Minimum Requirements
- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB
- Docker 20.10+
- Docker Compose 2.0+

#### Recommended for Production
- CPU: 8+ cores
- RAM: 16+ GB
- Disk: 200+ GB SSD
- Kubernetes 1.24+
- Helm 3.0+

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                        │
│                     (Ingress/ALB/NLB)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌─────────▼────────┐
│   Frontend     │            │    Backend       │
│   (React)      │◄──────────►│   (Python)       │
│   Pods: 3-10   │            │   Pods: 2-8      │
└───────┬────────┘            └─────────┬────────┘
        │                               │
        └───────────────┬───────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌─────────▼────────┐
│   PostgreSQL   │            │     Redis        │
│   (Database)   │            │    (Cache)       │
└────────────────┘            └──────────────────┘
```

### Services

1. **Frontend (givc-app)**
   - React application
   - Nginx web server
   - Port: 80
   - Replicas: 3-10 (autoscaled)

2. **Backend (givc-backend)**
   - Python NPHIES API
   - FastAPI/Flask
   - Port: 8000
   - Replicas: 2-8 (autoscaled)

3. **PostgreSQL**
   - Primary database
   - Port: 5432
   - Persistent storage

4. **Redis**
   - Caching layer
   - Session storage
   - Port: 6379

---

## Quick Start

### Option 1: Docker Compose (Simplest)

```bash
# Clone repository
git clone https://github.com/fadil369/GIVC.git
cd GIVC

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
./deploy-orchestrated.sh

# Or manually:
docker-compose --profile production up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Kubernetes

```bash
# Deploy with kubectl
ORCHESTRATOR=kubernetes ./deploy-orchestrated.sh

# Or manually:
kubectl apply -f k8s/base/

# Check status
kubectl get pods -n givc
kubectl get services -n givc
```

### Option 3: Helm (Recommended for K8s)

```bash
# Deploy with Helm
USE_HELM=true ORCHESTRATOR=kubernetes ./deploy-orchestrated.sh

# Or manually:
helm install givc ./helm/givc-chart \
  --namespace givc \
  --create-namespace \
  --values ./helm/givc-chart/values.yaml

# Check status
helm status givc -n givc
```

---

## Deployment Options

### Development Environment

```bash
# Start with development profile
docker-compose --profile dev up -d

# Includes:
# - Hot reloading
# - Debug logging
# - Development databases
# - Source code volumes
```

### Staging Environment

```bash
# Deploy to staging
DEPLOYMENT_ENV=staging \
ORCHESTRATOR=kubernetes \
NAMESPACE=givc-staging \
./deploy-orchestrated.sh
```

### Production Environment

```bash
# Full production deployment
DEPLOYMENT_ENV=production \
ORCHESTRATOR=kubernetes \
USE_HELM=true \
./deploy-orchestrated.sh
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Environment
ENVIRONMENT=production
NODE_ENV=production

# NPHIES Configuration
NPHIES_BASE_URL=https://NPHIES.sa/api/fs/fhir
NPHIES_LICENSE=your_license
NPHIES_ORGANIZATION_ID=your_org_id
NPHIES_PROVIDER_ID=your_provider_id

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/givc
POSTGRES_DB=givc_production
POSTGRES_USER=givc
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_PASSWORD=secure_redis_password

# Security
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# Monitoring
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=secure_grafana_password
SLACK_WEBHOOK_URL=your_slack_webhook
```

### Kubernetes Secrets

```bash
# Create secrets
kubectl create secret generic givc-secrets \
  --from-literal=nphies-license=$NPHIES_LICENSE \
  --from-literal=nphies-org-id=$NPHIES_ORGANIZATION_ID \
  --from-literal=database-url=$DATABASE_URL \
  --from-literal=jwt-secret=$JWT_SECRET \
  -n givc

# Verify
kubectl get secrets -n givc
```

### Helm Values Customization

Edit `helm/givc-chart/values.yaml`:

```yaml
frontend:
  replicaCount: 5  # Increase replicas
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi

backend:
  image:
    tag: "v1.2.0"  # Specify version
  
ingress:
  hosts:
    - host: your-domain.com
      paths:
        - path: /
```

---

## Monitoring & Observability

### Start Monitoring Stack

```bash
# Start monitoring services
docker-compose -f docker-compose.monitoring.yml --profile monitoring up -d

# Access dashboards
# Grafana: http://localhost:3001
# Prometheus: http://localhost:9090
# Alertmanager: http://localhost:9093
```

### Available Metrics

1. **Application Metrics**
   - Request rate and latency
   - Error rates
   - API endpoint performance

2. **System Metrics**
   - CPU usage
   - Memory utilization
   - Disk I/O
   - Network traffic

3. **Container Metrics**
   - Container health
   - Restart counts
   - Resource consumption

4. **Business Metrics**
   - NPHIES API calls
   - Claims processed
   - Eligibility checks

### Grafana Dashboards

Pre-configured dashboards available at:
- `monitoring/grafana/dashboards/`

Import to Grafana:
1. Access Grafana (http://localhost:3001)
2. Login (admin/admin)
3. Import dashboard JSON files

### Alerting

Alerts are configured in:
- `monitoring/alerts/givc-alerts.yml`

Alert channels:
- Slack notifications
- Webhook to backend API
- Email (configure in alertmanager.yml)

---

## Scaling

### Manual Scaling

#### Docker Compose
```bash
docker-compose up -d --scale givc-app=5 --scale givc-backend=3
```

#### Kubernetes
```bash
kubectl scale deployment givc-app --replicas=5 -n givc
kubectl scale deployment givc-backend --replicas=3 -n givc
```

#### Helm
```bash
helm upgrade givc ./helm/givc-chart \
  --set frontend.replicaCount=5 \
  --set backend.replicaCount=3 \
  -n givc
```

### Auto-scaling (Kubernetes)

Horizontal Pod Autoscaler is pre-configured:

```yaml
# Frontend: 2-10 replicas
# Backend: 2-8 replicas
# Triggers:
#   - CPU > 70%
#   - Memory > 80%
```

Check autoscaler status:
```bash
kubectl get hpa -n givc
kubectl describe hpa givc-frontend-hpa -n givc
```

### Database Scaling

#### Read Replicas
```bash
# Add PostgreSQL read replica
helm upgrade givc ./helm/givc-chart \
  --set postgresql.replication.enabled=true \
  --set postgresql.replication.readReplicas=2
```

#### Connection Pooling
Configure in backend:
```python
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

---

## Security

### Security Best Practices

1. **Network Policies**
   - Enabled by default in Kubernetes
   - Restricts pod-to-pod communication
   - Located in `k8s/base/networkpolicy.yaml`

2. **Secret Management**
   - Never commit secrets to git
   - Use Kubernetes secrets or Vault
   - Rotate secrets regularly

3. **Image Security**
   - Use official base images
   - Scan for vulnerabilities
   - Run as non-root user

4. **TLS/SSL**
   - Configure cert-manager
   - Use Let's Encrypt
   - Force HTTPS

### Security Scanning

```bash
# Scan Docker images
docker scan givc-app:latest

# Check Kubernetes security
kubectl run --rm -it security-scan \
  --image=aquasec/trivy \
  --restart=Never \
  -- image givc-app:latest
```

### HIPAA Compliance

- All data encrypted at rest and in transit
- Audit logging enabled
- Access controls enforced
- Regular security assessments

---

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting

```bash
# Check pod status
kubectl get pods -n givc

# View pod logs
kubectl logs -f deployment/givc-app -n givc

# Describe pod for events
kubectl describe pod <pod-name> -n givc
```

#### 2. Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm debug \
  --image=postgres:15 \
  --restart=Never \
  -- psql -h postgres -U givc -d givc_production

# Check database logs
kubectl logs -f deployment/postgres -n givc
```

#### 3. Service Not Accessible

```bash
# Check service
kubectl get svc -n givc

# Test internal connectivity
kubectl run -it --rm debug \
  --image=curlimages/curl \
  --restart=Never \
  -- curl http://givc-frontend.givc.svc.cluster.local

# Check ingress
kubectl describe ingress givc-ingress -n givc
```

#### 4. High Memory Usage

```bash
# Check resource usage
kubectl top pods -n givc

# Increase memory limits
kubectl set resources deployment givc-app \
  --limits=memory=1Gi \
  -n givc
```

### Debug Mode

Enable debug logging:
```bash
# Docker Compose
LOG_LEVEL=DEBUG docker-compose up -d

# Kubernetes
kubectl set env deployment/givc-backend LOG_LEVEL=DEBUG -n givc
```

---

## Best Practices

### 1. Resource Management
- Always set resource requests and limits
- Monitor actual usage and adjust
- Use auto-scaling for variable loads

### 2. Health Checks
- Implement liveness probes
- Implement readiness probes
- Set appropriate timeouts

### 3. Logging
- Centralize logs (Loki/ELK)
- Use structured logging
- Include correlation IDs

### 4. Backup Strategy
```bash
# Automated database backup
kubectl create cronjob givc-backup \
  --image=postgres:15 \
  --schedule="0 2 * * *" \
  -- pg_dump -h postgres -U givc givc_production > backup.sql
```

### 5. Disaster Recovery
- Regular backup testing
- Document recovery procedures
- Maintain off-site backups

### 6. CI/CD Integration
```yaml
# Example GitHub Actions
- name: Deploy to Production
  run: |
    DEPLOYMENT_ENV=production \
    ORCHESTRATOR=kubernetes \
    USE_HELM=true \
    ./deploy-orchestrated.sh
```

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/fadil369/GIVC/issues
- Documentation: https://givc.thefadil.site/docs
- Email: dr.fadil@givc.thefadil.site

---

**Last Updated:** October 24, 2025  
**Version:** 1.0.0  
**Maintainer:** Dr. Al Fadil / BRAINSAIT LTD
