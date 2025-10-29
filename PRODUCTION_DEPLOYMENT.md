# 🚀 GIVC Production Deployment Guide

**Last Updated:** October 29, 2025
**Status:** ✅ Production Ready

## 📋 Overview

This guide covers the complete production deployment of the GIVC Healthcare Intelligence Platform with integrated BrainSAIT services.

## 🏗️ Architecture

### Core Services
- **Frontend:** React/Vite application with PWA support
- **Backend API:** FastAPI/Node.js microservices
- **Database:** PostgreSQL with multi-tenant support
- **Cache:** Redis for session management
- **Message Queue:** RabbitMQ for async processing

### Integrated Platforms
1. **BrainSAIT Platform** - Microservices architecture
2. **BrainSAIT Agentic Workflow** - AI orchestration
3. **GIVC Core** - Healthcare intelligence

## 🔧 Pre-Deployment Checklist

### 1. System Requirements
- [ ] Docker Engine 20.10+
- [ ] Docker Compose 2.0+
- [ ] Node.js 18+ (for local development)
- [ ] Python 3.11+ (for services)
- [ ] 8GB RAM minimum (16GB recommended)
- [ ] 50GB disk space

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with production values
nano .env
```

### 3. Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/givc
REDIS_URL=redis://localhost:6379

# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Security
JWT_SECRET=your_secure_jwt_secret
SESSION_SECRET=your_secure_session_secret

# Service URLs
API_BASE_URL=https://api.yourdomain.com
FRONTEND_URL=https://app.yourdomain.com
```

## 🚀 Deployment Steps

### Step 1: Build Application
```bash
# Install dependencies
npm install

# Build for production
npm run build

# Verify build
ls -lh dist/
```

### Step 2: Deploy Core Services
```bash
# Start main GIVC services
docker-compose -f docker-compose.yml up -d

# Verify services
docker-compose ps
```

### Step 3: Deploy BrainSAIT Platform
```bash
# Navigate to brainsait-platform
cd brainsait-platform

# Start unified services
docker-compose -f docker-compose.unified.yml up -d

# Check status
docker-compose -f docker-compose.unified.yml ps
```

### Step 4: Deploy Agentic Workflow
```bash
# Navigate to agentic workflow
cd ../brainsait-agentic-workflow

# Start orchestrator
docker-compose up -d

# Verify
docker-compose logs orchestrator
```

### Step 5: Database Migration
```bash
# Run database migrations
docker-compose exec backend python manage.py migrate

# Create superuser (if needed)
docker-compose exec backend python manage.py createsuperuser

# Load initial data
docker-compose exec backend python manage.py loaddata initial_data.json
```

### Step 6: Service Health Checks
```bash
# Check all services
./scripts/health-check.sh

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8001/api/health  # BrainSAIT
curl http://localhost:3000/api/health  # Agentic Workflow
```

## 🔒 Security Hardening

### 1. SSL/TLS Configuration
```bash
# Generate SSL certificates (Let's Encrypt)
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./certificates/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./certificates/
```

### 2. Firewall Rules
```bash
# Allow only necessary ports
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 22/tcp    # SSH
sudo ufw enable
```

### 3. Docker Security
```bash
# Run containers as non-root
# Update docker-compose.yml with:
user: "1000:1000"

# Enable Docker security scanning
docker scan givc:latest
```

## 📊 Monitoring Setup

### 1. Application Monitoring
```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana
open http://localhost:3001
# Default: admin/admin
```

### 2. Log Aggregation
```bash
# View aggregated logs
docker-compose logs -f --tail=100

# Service-specific logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. Performance Metrics
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001
- **Node Exporter:** http://localhost:9100

## 🔄 Backup Strategy

### 1. Database Backup
```bash
# Create backup script
cat > backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U postgres givc > "$BACKUP_DIR/givc_$DATE.sql"
# Keep last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
EOF

chmod +x backup-db.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /home/pi/GIVC/backup-db.sh
```

### 2. File Backup
```bash
# Backup uploads and data
rsync -avz ./data/ /backups/givc-data/
rsync -avz ./uploads/ /backups/givc-uploads/
```

## 🔧 Maintenance

### Regular Tasks
1. **Daily**
   - Check service health
   - Review error logs
   - Monitor resource usage

2. **Weekly**
   - Verify backups
   - Update security patches
   - Review performance metrics

3. **Monthly**
   - Database optimization
   - Dependency updates
   - Security audit

### Update Procedure
```bash
# Pull latest changes
git pull origin main

# Update dependencies
npm install

# Rebuild
npm run build

# Restart services (zero-downtime)
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend
```

## 🐛 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs service-name

# Restart service
docker-compose restart service-name

# Full restart
docker-compose down && docker-compose up -d
```

#### Database Connection Issues
```bash
# Check database
docker-compose exec postgres psql -U postgres -c "\l"

# Reset database (⚠️ DANGER)
docker-compose down -v
docker-compose up -d
```

#### High Memory Usage
```bash
# Check container stats
docker stats

# Restart high-usage container
docker-compose restart <service>
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale specific services
docker-compose up -d --scale backend=3
docker-compose up -d --scale worker=5
```

### Load Balancing
- Use nginx as reverse proxy
- Configure in `nginx/conf.d/default.conf`
- Enable upstream load balancing

## 🔐 Access Control

### User Roles
1. **Admin** - Full system access
2. **Healthcare Provider** - Patient data, claims
3. **Support** - Limited dashboard access
4. **API User** - Programmatic access

### API Authentication
```bash
# Generate API key
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secure_password"}'
```

## 📞 Support

### Resources
- Documentation: `/docs`
- API Docs: `http://localhost:8000/docs`
- GitHub Issues: https://github.com/Fadil369/GIVC/issues

### Emergency Contacts
- Technical Lead: [Add contact]
- DevOps: [Add contact]
- Security: [Add contact]

## ✅ Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database migrations completed
- [ ] Backup scripts configured
- [ ] Monitoring dashboards setup
- [ ] Firewall rules applied
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated
- [ ] Team trained on deployment

---

**Deployment Date:** _____________
**Deployed By:** _____________
**Version:** 1.0.0
