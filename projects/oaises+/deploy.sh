#!/bin/bash

###############################################################################
# BrainSAIT RCM Deployment Script
# Deploys the application to production VM
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VM_HOST="82.25.101.65"
VM_USER="root"
VM_PASSWORD="Fadil12345678#"
APP_DIR="/opt/brainsait"
REPO_URL="https://github.com/yourusername/brainsait-rcm.git"  # Update with your repo

echo -e "${GREEN}===========================================\${NC}"
echo -e "${GREEN}  BrainSAIT RCM Deployment Script${NC}"
echo -e "${GREEN}===========================================\${NC}"
echo ""

# Function to print step
print_step() {
    echo -e "\n${YELLOW}>>> $1${NC}\n"
}

# Function to execute remote command
remote_exec() {
    sshpass -p "$VM_PASSWORD" ssh -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST} "$1"
}

# Function to copy files to remote
remote_copy() {
    sshpass -p "$VM_PASSWORD" scp -o StrictHostKeyChecking=no -r "$1" ${VM_USER}@${VM_HOST}:"$2"
}

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo -e "${RED}Error: sshpass is not installed${NC}"
    echo "Install it with: sudo apt-get install sshpass (Ubuntu/Debian) or brew install sshpass (macOS)"
    exit 1
fi

# Step 1: Check connection
print_step "Step 1: Testing connection to VM..."
if remote_exec "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ Connection successful${NC}"
else
    echo -e "${RED}✗ Connection failed${NC}"
    exit 1
fi

# Step 2: Install dependencies
print_step "Step 2: Installing system dependencies..."
remote_exec "apt-get update && apt-get install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl"

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Create application directory
print_step "Step 3: Creating application directory..."
remote_exec "mkdir -p ${APP_DIR} /var/log/brainsait"
echo -e "${GREEN}✓ Directory created${NC}"

# Step 4: Copy application files
print_step "Step 4: Copying application files..."
remote_copy "./" "${APP_DIR}/"
echo -e "${GREEN}✓ Files copied${NC}"

# Step 5: Set up environment file
print_step "Step 5: Setting up environment file..."
echo -e "${YELLOW}Please ensure .env.production is properly configured before continuing${NC}"
read -p "Press enter to continue..."
remote_copy ".env.production" "${APP_DIR}/.env"
echo -e "${GREEN}✓ Environment file copied${NC}"

# Step 6: Generate secrets
print_step "Step 6: Generating secure secrets..."
JWT_SECRET=$(openssl rand -base64 64)
ENCRYPTION_KEY=$(openssl rand -hex 32)

remote_exec "cd ${APP_DIR} && \
    sed -i 's/CHANGE_THIS_LONG_RANDOM_STRING_MINIMUM_64_CHARACTERS_GENERATED_WITH_OPENSSL/${JWT_SECRET}/g' .env && \
    sed -i 's/CHANGE_THIS_64_CHARACTER_HEX_STRING_GENERATED_WITH_OPENSSL/${ENCRYPTION_KEY}/g' .env"

echo -e "${GREEN}✓ Secrets generated${NC}"

# Step 7: Build and start Docker containers
print_step "Step 7: Building and starting Docker containers..."
remote_exec "cd ${APP_DIR} && docker-compose down && docker-compose up -d --build"
echo -e "${GREEN}✓ Docker containers started${NC}"

# Step 8: Configure Nginx
print_step "Step 8: Configuring Nginx..."
remote_copy "nginx.conf" "/etc/nginx/sites-available/brainsait"
remote_exec "ln -sf /etc/nginx/sites-available/brainsait /etc/nginx/sites-enabled/ && \
    nginx -t && \
    systemctl reload nginx"
echo -e "${GREEN}✓ Nginx configured${NC}"

# Step 9: Set up SSL certificate
print_step "Step 9: Setting up SSL certificate..."
read -p "Enter your domain name: " DOMAIN
remote_exec "certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos -m admin@${DOMAIN}"
echo -e "${GREEN}✓ SSL certificate installed${NC}"

# Step 10: Create initial admin user
print_step "Step 10: Creating initial admin user..."
read -p "Enter admin email: " ADMIN_EMAIL
read -sp "Enter admin password: " ADMIN_PASSWORD
echo ""

remote_exec "docker exec brainsait-api python -c \"
from auth.jwt_handler import hash_password
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import asyncio

async def create_admin():
    client = AsyncIOMotorClient('mongodb://brainsait_admin:changeme@mongodb:27017')
    db = client.brainsait

    hashed_password = hash_password('${ADMIN_PASSWORD}')

    await db.users.insert_one({
        'user_id': 'admin_001',
        'email': '${ADMIN_EMAIL}',
        'full_name': 'System Administrator',
        'role': 'SUPER_ADMIN',
        'hashed_password': hashed_password,
        'is_active': True,
        'is_verified': True,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
        'failed_login_attempts': 0
    })

    print('Admin user created successfully')

asyncio.run(create_admin())
\""

echo -e "${GREEN}✓ Admin user created${NC}"

# Step 11: Verify deployment
print_step "Step 11: Verifying deployment..."
sleep 10

if remote_exec "curl -f http://localhost:8000/health > /dev/null 2>&1"; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${RED}✗ API health check failed${NC}"
fi

if remote_exec "curl -f http://localhost:3000 > /dev/null 2>&1"; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${RED}✗ Frontend health check failed${NC}"
fi

# Final summary
echo -e "\n${GREEN}===========================================\${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}===========================================\${NC}"
echo -e "\nApplication URL: https://${DOMAIN}"
echo -e "API Documentation: https://${DOMAIN}/docs"
echo -e "Admin Email: ${ADMIN_EMAIL}"
echo -e "\n${YELLOW}Important Next Steps:${NC}"
echo -e "1. Update DNS records to point ${DOMAIN} to ${VM_HOST}"
echo -e "2. Configure firewall rules"
echo -e "3. Set up database backups"
echo -e "4. Configure monitoring and alerts"
echo -e "5. Review and update all environment variables"
echo -e "\n${GREEN}Deployment logs available at: /var/log/brainsait/${NC}\n"
