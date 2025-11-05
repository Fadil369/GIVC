# 🐳 Docker VPS Deployment Guide - Hostinger/Ubuntu

## Overview

Deploy GIVC Ultrathink Platform to your own VPS using Docker containers.

**Architecture:**
```
Your Hostinger VPS (Ubuntu + Docker)
├── Docker Container: FastAPI Backend (Port 8000)
├── Nginx Reverse Proxy (Ports 80/443)
├── PostgreSQL Database (Docker or Managed)
├── SSL Certificate (Let's Encrypt)
└── Cloudflare Pages: React Frontend (Global CDN)
```

**Advantages:**
- ✅ Full control over infrastructure
- ✅ No monthly service fees (just VPS cost)
- ✅ Better performance (dedicated resources)
- ✅ Easy scaling (just upgrade VPS)
- ✅ Perfect for production

---

## 📋 Prerequisites

### VPS Requirements
- Ubuntu 20.04+ or 22.04 LTS
- Docker installed
- Docker Compose installed
- Domain name pointed to VPS IP
- Minimum: 2GB RAM, 2 vCPU, 20GB storage

### Check Your VPS
```bash
# SSH into your VPS
ssh root@your-vps-ip

# Check Docker
docker --version
docker-compose --version

# Check resources
free -h
df -h
```

---

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Clone Repository on VPS

```bash
# SSH into VPS
ssh root@your-vps-ip

# Clone repository
cd /opt
git clone https://github.com/Fadil369/GIVC.git
cd GIVC
```

### Step 2: Configure Environment

```bash
# Create .env file
cat > .env << 'EOF'
# Application
ENVIRONMENT=production
API_SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET=your-jwt-secret-key-change-this

# Database
DATABASE_URL=postgresql://givc:secure-password@postgres:5432/ultrathink
POSTGRES_USER=givc
POSTGRES_PASSWORD=secure-password
POSTGRES_DB=ultrathink

# Ultrathink AI
ULTRATHINK_ENABLED=true
SECURITY_MIDDLEWARE_ENABLED=true
ML_MODEL_PATH=/app/models

# Rate Limiting
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_STRICT=10

# Monitoring
PROMETHEUS_ENABLED=true
LOG_LEVEL=INFO
EOF

# Secure the .env file
chmod 600 .env
```

### Step 3: Deploy with Docker Compose

```bash
# Build and start containers
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**That's it! Your backend is now running on port 8000.**

---

## 📦 Docker Configuration Files

### Dockerfile (Already in Repo)

```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/models /app/logs

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "fastapi_app_ultrathink:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  # FastAPI Backend
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: givc-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - API_SECRET_KEY=${API_SECRET_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - ULTRATHINK_ENABLED=${ULTRATHINK_ENABLED}
      - SECURITY_MIDDLEWARE_ENABLED=${SECURITY_MIDDLEWARE_ENABLED}
      - ML_MODEL_PATH=${ML_MODEL_PATH}
      - RATE_LIMIT_DEFAULT=${RATE_LIMIT_DEFAULT}
      - RATE_LIMIT_STRICT=${RATE_LIMIT_STRICT}
      - PROMETHEUS_ENABLED=${PROMETHEUS_ENABLED}
      - LOG_LEVEL=${LOG_LEVEL}
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    depends_on:
      - postgres
    networks:
      - givc-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: givc-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - givc-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx Reverse Proxy (Optional - for SSL)
  nginx:
    image: nginx:alpine
    container_name: givc-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - api
    networks:
      - givc-network

  # Redis (Optional - for caching)
  redis:
    image: redis:7-alpine
    container_name: givc-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - givc-network
    command: redis-server --appendonly yes

volumes:
  postgres-data:
  redis-data:

networks:
  givc-network:
    driver: bridge
```

---

## 🔧 Nginx Configuration

### Create Nginx Config

```bash
# Create nginx directory
mkdir -p nginx

# Create nginx.conf
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;

    server {
        listen 80;
        server_name api.your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.your-domain.com;

        # SSL Configuration (Let's Encrypt)
        ssl_certificate /etc/letsencrypt/live/api.your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/api.your-domain.com/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Proxy to FastAPI
        location / {
            limit_req zone=api_limit burst=20 nodelay;

            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint (no rate limit)
        location /api/health {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
        }

        # API documentation
        location /docs {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
        }
    }
}
EOF
```

---

## 🔒 SSL Certificate Setup (Let's Encrypt)

### Option 1: Certbot (Recommended)

```bash
# Install Certbot
apt update
apt install -y certbot

# Stop nginx if running
docker-compose stop nginx

# Get certificate
certbot certonly --standalone \
  -d api.your-domain.com \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive

# Start nginx
docker-compose up -d nginx

# Auto-renewal (add to crontab)
echo "0 0 * * * certbot renew --quiet && docker-compose restart nginx" | crontab -
```

### Option 2: Cloudflare SSL (Easiest)

If using Cloudflare DNS:
1. Cloudflare will handle SSL automatically
2. Set SSL mode to "Full" in Cloudflare dashboard
3. No need for Let's Encrypt

---

## 🗄️ Database Migration

```bash
# Run migrations inside container
docker-compose exec api alembic upgrade head

# Or manually
docker-compose exec api bash
alembic upgrade head
exit
```

---

## 📊 Monitoring & Management

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 api
```

### Check Status

```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# API health
curl http://localhost:8000/api/health
curl https://api.your-domain.com/api/health
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api

# Rebuild and restart
docker-compose up -d --build api
```

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U givc ultrathink > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U givc ultrathink < backup_20241105.sql
```

---

## 🚀 Complete Deployment Script

Create `deploy-vps.sh`:

```bash
#!/bin/bash

set -e

echo "🚀 Deploying GIVC Ultrathink to VPS..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if running on VPS
if [ ! -f /etc/os-release ]; then
    echo "Error: Not running on Linux VPS"
    exit 1
fi

# Update system
echo -e "${BLUE}Updating system...${NC}"
apt update && apt upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Clone or update repository
if [ -d "/opt/GIVC" ]; then
    echo -e "${BLUE}Updating repository...${NC}"
    cd /opt/GIVC
    git pull
else
    echo -e "${BLUE}Cloning repository...${NC}"
    cd /opt
    git clone https://github.com/Fadil369/GIVC.git
    cd GIVC
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file...${NC}"
    cat > .env << 'ENVEOF'
ENVIRONMENT=production
API_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
DATABASE_URL=postgresql://givc:$(openssl rand -hex 16)@postgres:5432/ultrathink
POSTGRES_USER=givc
POSTGRES_PASSWORD=$(openssl rand -hex 16)
POSTGRES_DB=ultrathink
ULTRATHINK_ENABLED=true
SECURITY_MIDDLEWARE_ENABLED=true
ENVEOF
    chmod 600 .env
fi

# Build and start
echo -e "${BLUE}Building and starting containers...${NC}"
docker-compose up -d --build

# Wait for services
echo -e "${BLUE}Waiting for services to start...${NC}"
sleep 10

# Run migrations
echo -e "${BLUE}Running database migrations...${NC}"
docker-compose exec -T api alembic upgrade head

# Check health
echo -e "${BLUE}Checking health...${NC}"
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "API running at: http://$(hostname -I | awk '{print $1}'):8000"
    echo -e "Health check: http://$(hostname -I | awk '{print $1}'):8000/api/health"
    echo -e "Documentation: http://$(hostname -I | awk '{print $1}'):8000/docs"
else
    echo "❌ Health check failed. Check logs:"
    docker-compose logs api
    exit 1
fi

# Setup SSL (optional)
read -p "Setup SSL with Let's Encrypt? (y/n): " SETUP_SSL
if [ "$SETUP_SSL" = "y" ]; then
    read -p "Enter your domain (e.g., api.your-domain.com): " DOMAIN
    read -p "Enter your email: " EMAIL

    apt install -y certbot
    docker-compose stop nginx
    certbot certonly --standalone -d $DOMAIN --email $EMAIL --agree-tos --non-interactive
    docker-compose up -d nginx

    echo -e "${GREEN}✅ SSL configured for $DOMAIN${NC}"
fi

echo -e "${GREEN}🎉 Deployment complete!${NC}"
```

Make executable:
```bash
chmod +x deploy-vps.sh
```

---

## 🌐 Frontend Deployment (Cloudflare Pages)

Your frontend still goes to Cloudflare Pages:

```bash
# Build frontend locally or on VPS
cd frontend
npm install
npm run build

# Deploy to Cloudflare
wrangler pages deploy build --project-name=givc-ultrathink

# Set environment variable in Cloudflare dashboard:
# REACT_APP_API_URL=https://api.your-domain.com
```

---

## 🔧 Domain Configuration

### DNS Settings (Cloudflare)

```
Type    Name                Value               Proxy
A       api                 YOUR_VPS_IP         ✅ Proxied
CNAME   www                 givc.pages.dev      ✅ Proxied
```

### Update CORS in FastAPI

```python
# fastapi_app_ultrathink.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://givc-ultrathink.pages.dev",
        "https://your-domain.com",
        "https://www.your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📈 Scaling & Optimization

### Increase Workers

```yaml
# docker-compose.yml
services:
  api:
    command: uvicorn fastapi_app_ultrathink:app --host 0.0.0.0 --port 8000 --workers 8
```

### Enable Caching

```bash
# Add Redis to docker-compose
# Update FastAPI to use Redis for caching
```

### Monitor Resources

```bash
# Install monitoring
docker run -d \
  --name=grafana \
  -p 3000:3000 \
  grafana/grafana

docker run -d \
  --name=prometheus \
  -p 9090:9090 \
  prom/prometheus
```

---

## 💰 Cost Estimate

**Hostinger VPS + Cloudflare:**
- VPS (2GB RAM): $4-8/month
- Domain: $10-15/year
- Cloudflare Pages: FREE
- Cloudflare CDN: FREE
- SSL Certificate: FREE (Let's Encrypt)

**Total: ~$5-10/month** (vs $20-50 on managed platforms)

---

## ✅ Deployment Checklist

- [ ] VPS accessible via SSH
- [ ] Docker and Docker Compose installed
- [ ] Repository cloned to `/opt/GIVC`
- [ ] `.env` file configured with secrets
- [ ] Containers running: `docker-compose ps`
- [ ] Database migrations completed
- [ ] API health check passing
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed
- [ ] Domain DNS configured
- [ ] Frontend deployed to Cloudflare Pages
- [ ] CORS settings updated
- [ ] Monitoring enabled

---

## 🆘 Troubleshooting

### Container won't start
```bash
docker-compose logs api
docker-compose down && docker-compose up -d --build
```

### Database connection failed
```bash
docker-compose logs postgres
docker-compose exec postgres psql -U givc -d ultrathink
```

### Port already in use
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Out of disk space
```bash
docker system prune -a
docker volume prune
```

---

**Your deployment is now production-ready!** 🎉

Frontend: Cloudflare Pages (Global CDN)
Backend: Your VPS (Full control)
Database: Docker PostgreSQL (Persistent)
SSL: Let's Encrypt (Free)
