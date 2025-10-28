# BrainSAIT RCM - Production Deployment Guide

## 📋 Overview

This guide covers the complete deployment process for the BrainSAIT Healthcare Revenue Cycle Management system to your production VM.

**Production Server:**
- IP: `82.25.101.65`
- User: `root`
- OS: Ubuntu/Debian (recommended)

## 🔧 Prerequisites

### Local Machine
- Git
- Docker & Docker Compose (for local testing)
- SSH access
- `sshpass` (for automated deployment)

### Production Server
- Ubuntu 20.04 or later / Debian 11 or later
- 4GB+ RAM
- 50GB+ disk space
- Root or sudo access

## 🚀 Quick Deployment

### Option 1: Automated Deployment Script

```bash
# Make the deploy script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

The script will:
1. Install all dependencies
2. Copy application files
3. Generate secure secrets
4. Build and start Docker containers
5. Configure Nginx
6. Set up SSL certificates
7. Create initial admin user

### Option 2: Manual Deployment

Follow the detailed steps below for manual deployment.

## 📝 Detailed Manual Deployment Steps

### Step 1: Prepare Production Server

```bash
# SSH into the server
ssh root@82.25.101.65

# Update system
apt-get update && apt-get upgrade -y

# Install required packages
apt-get install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    ufw
```

### Step 2: Configure Firewall

```bash
# Allow SSH, HTTP, and HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

### Step 3: Clone Repository

```bash
# Create application directory
mkdir -p /opt/brainsait
cd /opt/brainsait

# Clone repository (or upload files via SCP)
git clone https://github.com/yourusername/brainsait-rcm.git .

# Or upload via SCP from local machine:
# scp -r ./ root@82.25.101.65:/opt/brainsait/
```

### Step 4: Configure Environment Variables

```bash
# Copy production environment template
cp .env.production .env

# Generate secure secrets
JWT_SECRET=$(openssl rand -base64 64)
ENCRYPTION_KEY=$(openssl rand -hex 32)
MONGO_PASSWORD=$(openssl rand -base64 32)

# Update .env file with generated secrets
sed -i "s/CHANGE_THIS_LONG_RANDOM_STRING_MINIMUM_64_CHARACTERS_GENERATED_WITH_OPENSSL/${JWT_SECRET}/g" .env
sed -i "s/CHANGE_THIS_64_CHARACTER_HEX_STRING_GENERATED_WITH_OPENSSL/${ENCRYPTION_KEY}/g" .env
sed -i "s/CHANGE_STRONG_PASSWORD_HERE/${MONGO_PASSWORD}/g" .env

# Edit .env and update remaining values:
nano .env
```

**Required updates in `.env`:**
- `NPHIES_API_KEY`: Your NPHIES API key
- `SMTP_USER` and `SMTP_PASSWORD`: Email credentials
- Domain names (replace `yourdomain.com`)
- OASIS+ credentials

### Step 5: Build and Start Docker Containers

```bash
cd /opt/brainsait

# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 6: Configure Nginx

```bash
# Copy Nginx configuration
cp nginx.conf /etc/nginx/sites-available/brainsait

# Update domain name in the config
sed -i 's/yourdomain.com/your-actual-domain.com/g' /etc/nginx/sites-available/brainsait

# Enable site
ln -sf /etc/nginx/sites-available/brainsait /etc/nginx/sites-enabled/

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Test configuration
nginx -t

# Reload Nginx
systemctl reload nginx
```

### Step 7: Set Up SSL Certificate

```bash
# Install SSL certificate with Let's Encrypt
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal:
certbot renew --dry-run
```

### Step 8: Create Initial Admin User

```bash
# Access the API container
docker exec -it brainsait-api python3

# Run Python script to create admin user
```

```python
import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from auth.jwt_handler import hash_password

async def create_admin():
    client = AsyncIOMotorClient("mongodb://brainsait_admin:YOUR_MONGO_PASSWORD@mongodb:27017")
    db = client.brainsait

    hashed_password = hash_password("YourSecurePassword123!")

    await db.users.insert_one({
        "user_id": "admin_001",
        "email": "admin@brainsait.com",
        "full_name": "System Administrator",
        "role": "SUPER_ADMIN",
        "hashed_password": hashed_password,
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "failed_login_attempts": 0
    })

    print("Admin user created successfully")
    client.close()

asyncio.run(create_admin())
```

### Step 9: Verify Deployment

```bash
# Check API health
curl http://localhost:8000/health

# Check Frontend
curl http://localhost:3000

# Check containers
docker-compose ps

# Check logs
docker-compose logs api
docker-compose logs web
docker-compose logs mongodb
```

### Step 10: Set Up Monitoring and Logging

```bash
# Create log rotation
cat > /etc/logrotate.d/brainsait <<EOF
/var/log/brainsait/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 root root
}
EOF

# Set up log directory
mkdir -p /var/log/brainsait
chmod 755 /var/log/brainsait
```

## 🔒 Security Checklist

- [ ] Strong passwords set for all services
- [ ] JWT_SECRET is random and secure (64+ characters)
- [ ] ENCRYPTION_KEY is random and secure (64+ characters)
- [ ] MongoDB password changed from default
- [ ] Firewall configured (UFW enabled)
- [ ] SSL certificate installed
- [ ] Security headers configured in Nginx
- [ ] Rate limiting enabled
- [ ] Admin user created with strong password
- [ ] All default credentials changed
- [ ] OASIS+ credentials secured
- [ ] SMTP credentials secured
- [ ] NPHIES API key secured

## 🔄 Maintenance Tasks

### Backup Database

```bash
# Create backup script
cat > /opt/brainsait/backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/brainsait/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker exec brainsait-mongodb mongodump \
    --uri="mongodb://brainsait_admin:YOUR_PASSWORD@localhost:27017/brainsait?authSource=admin" \
    --out=/tmp/backup_${DATE}

docker cp brainsait-mongodb:/tmp/backup_${DATE} ${BACKUP_DIR}/

# Keep only last 7 days
find ${BACKUP_DIR} -type d -mtime +7 -exec rm -rf {} \;
EOF

chmod +x /opt/brainsait/backup.sh

# Add to cron (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/brainsait/backup.sh") | crontab -
```

### Update Application

```bash
cd /opt/brainsait

# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f web

# Nginx logs
tail -f /var/log/nginx/brainsait-access.log
tail -f /var/log/nginx/brainsait-error.log
```

## 🐛 Troubleshooting

### API Container Won't Start

```bash
# Check logs
docker-compose logs api

# Common issues:
# 1. MongoDB not ready - wait a few seconds and restart
# 2. Missing dependencies - rebuild image
# 3. Port conflict - check if port 8000 is in use

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Frontend Container Won't Start

```bash
# Check logs
docker-compose logs web

# Rebuild
cd /opt/brainsait/apps/web
docker-compose build web
docker-compose up -d web
```

### Database Connection Issues

```bash
# Check MongoDB status
docker-compose ps mongodb
docker-compose logs mongodb

# Test connection
docker exec brainsait-mongodb mongosh \
    -u brainsait_admin \
    -p YOUR_PASSWORD \
    --authenticationDatabase admin \
    brainsait
```

### SSL Certificate Issues

```bash
# Renew certificate
certbot renew

# Force renewal
certbot renew --force-renewal

# Check certificate
certbot certificates
```

## 📊 Monitoring

### Health Checks

```bash
# API Health
curl https://yourdomain.com/health

# Database
docker exec brainsait-mongodb mongosh --eval "db.runCommand({ ping: 1 })"

# Container status
docker-compose ps
```

### Performance Monitoring

```bash
# Container stats
docker stats

# Disk usage
df -h
docker system df

# Memory usage
free -m
```

## 🔗 Useful URLs

- **Application**: https://yourdomain.com
- **API Documentation**: https://yourdomain.com/docs
- **API ReDoc**: https://yourdomain.com/redoc
- **Health Check**: https://yourdomain.com/health

## 📞 Support

For issues or questions:
- Email: support@brainsait.com
- Create an issue in the repository
- Check the documentation: /docs

## 📌 Important Notes

1. **Backup Regularly**: Set up automated database backups
2. **Monitor Logs**: Check logs regularly for errors
3. **Update Dependencies**: Keep Docker images and system packages updated
4. **Security Updates**: Apply security patches promptly
5. **Resource Monitoring**: Monitor CPU, memory, and disk usage
6. **SSL Renewal**: Certbot auto-renewal is configured, but verify it works

## 🎯 Post-Deployment Checklist

- [ ] Application is accessible via HTTPS
- [ ] API returns healthy status
- [ ] Can log in with admin credentials
- [ ] Database is running and accepting connections
- [ ] Redis is running
- [ ] Nginx is properly configured
- [ ] SSL certificate is valid
- [ ] Logs are being written
- [ ] Backup script is set up
- [ ] Firewall is configured
- [ ] DNS is pointing to server
- [ ] Email notifications work (test SMTP)
- [ ] NPHIES integration is configured
- [ ] OASIS+ integration is configured

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Maintainer**: BrainSAIT Development Team
