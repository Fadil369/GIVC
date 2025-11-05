#!/bin/bash

# ========================================================================
# VPS Deployment Script for GIVC Ultrathink Platform
# ========================================================================
# Deploy FastAPI backend to Docker on your Hostinger VPS
#
# Usage: ./deploy-vps.sh
# Run this on your VPS via SSH
#
# Author: GIVC Platform Team
# ========================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Functions
print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ========================================================================
# Header
# ========================================================================

clear
echo -e "${CYAN}"
cat << 'EOF'
   _____ _______      ______
  / ____|_   _\ \    / / __ \
 | |  __  | |  \ \  / / |  | |
 | | |_ | | |   \ \/ /| |  | |
 | |__| |_| |_   \  / | |__| |
  \_____|_____|   \/   \____/

  Ultrathink AI Platform
  VPS Deployment
EOF
echo -e "${NC}\n"

# ========================================================================
# Check Prerequisites
# ========================================================================

print_header "Checking Prerequisites"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_warning "This script should be run as root or with sudo"
   print_info "Re-running with sudo..."
   exec sudo "$0" "$@"
fi

# Check OS
if [ ! -f /etc/os-release ]; then
    print_error "Cannot detect OS. This script requires Linux."
    exit 1
fi

print_success "Running on: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_warning "Docker not found. Installing..."

    # Install Docker
    apt-get update
    apt-get install -y ca-certificates curl gnupg lsb-release

    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Setup repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    print_success "Docker installed successfully"
else
    print_success "Docker found: $(docker --version)"
fi

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    print_warning "Docker Compose plugin not found. Installing..."
    apt-get update
    apt-get install -y docker-compose-plugin
    print_success "Docker Compose installed"
else
    print_success "Docker Compose found: $(docker compose version)"
fi

# Start Docker service
systemctl enable docker
systemctl start docker

# ========================================================================
# Setup Project
# ========================================================================

print_header "Setting Up Project"

# Set project directory
PROJECT_DIR="/opt/GIVC"
print_info "Project directory: $PROJECT_DIR"

# Clone or update repository
if [ -d "$PROJECT_DIR" ]; then
    print_info "Project directory exists. Updating..."
    cd "$PROJECT_DIR"

    # Stash any local changes
    if command -v git &> /dev/null; then
        git stash
        git pull origin main
        print_success "Repository updated"
    fi
else
    print_info "Cloning repository..."

    # Install git if not present
    if ! command -v git &> /dev/null; then
        apt-get install -y git
    fi

    cd /opt
    git clone https://github.com/Fadil369/GIVC.git
    cd GIVC
    print_success "Repository cloned"
fi

# ========================================================================
# Configure Environment
# ========================================================================

print_header "Configuring Environment"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_info "Creating .env file..."

    # Generate random secrets
    API_SECRET=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -hex 16)

    cat > .env << EOF
# Environment
ENVIRONMENT=production

# Security
API_SECRET_KEY=$API_SECRET
JWT_SECRET=$JWT_SECRET

# Database
DATABASE_URL=postgresql://givc:$DB_PASSWORD@postgres:5432/ultrathink
POSTGRES_USER=givc
POSTGRES_PASSWORD=$DB_PASSWORD
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

    chmod 600 .env
    print_success "Environment file created with secure random secrets"
else
    print_success "Environment file already exists"
fi

# Create necessary directories
mkdir -p models logs database/migrations
print_success "Directories created"

# ========================================================================
# Deploy Application
# ========================================================================

print_header "Deploying Application"

# Stop existing containers
if docker compose ps | grep -q "givc"; then
    print_info "Stopping existing containers..."
    docker compose down
fi

# Build and start containers
print_info "Building Docker images..."
docker compose build api postgres

print_info "Starting containers..."
docker compose up -d api postgres redis

# Wait for services to be healthy
print_info "Waiting for services to start..."
sleep 10

# Check container status
print_info "Container status:"
docker compose ps

# ========================================================================
# Database Migration
# ========================================================================

print_header "Database Migration"

# Wait for PostgreSQL
print_info "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U givc > /dev/null 2>&1; then
        print_success "PostgreSQL is ready"
        break
    fi
    echo -n "."
    sleep 2
done

# Run migrations
print_info "Running database migrations..."
if docker compose exec -T api alembic upgrade head; then
    print_success "Migrations completed"
else
    print_warning "Migration failed or not configured. Continuing..."
fi

# ========================================================================
# Health Check
# ========================================================================

print_header "Health Check"

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

# Test API health
print_info "Testing API health..."
sleep 5

if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    print_success "API is healthy!"
else
    print_error "API health check failed"
    print_info "Checking logs..."
    docker compose logs --tail=50 api
    exit 1
fi

# ========================================================================
# Setup Firewall (Optional)
# ========================================================================

print_header "Firewall Configuration"

if command -v ufw &> /dev/null; then
    print_info "Configuring UFW firewall..."

    # Allow SSH
    ufw allow 22/tcp

    # Allow HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp

    # Allow API port (if exposing directly)
    # ufw allow 8000/tcp

    # Enable firewall
    echo "y" | ufw enable

    print_success "Firewall configured"
else
    print_info "UFW not found. Install with: apt install ufw"
fi

# ========================================================================
# Summary
# ========================================================================

print_header "Deployment Summary"

echo ""
print_success "🎉 Deployment completed successfully!"
echo ""
print_info "Application Details:"
echo "  • API URL (internal): http://localhost:8000"
echo "  • API URL (external): http://$SERVER_IP:8000"
echo "  • Health Check: http://$SERVER_IP:8000/api/health"
echo "  • API Documentation: http://$SERVER_IP:8000/docs"
echo "  • Database: PostgreSQL on port 5432"
echo "  • Redis: Cache on port 6379"
echo ""
print_info "Container Status:"
docker compose ps
echo ""
print_info "Next Steps:"
echo "  1. Setup domain DNS pointing to: $SERVER_IP"
echo "  2. Install Nginx reverse proxy (optional)"
echo "  3. Setup SSL with Let's Encrypt"
echo "  4. Deploy frontend to Cloudflare Pages"
echo "  5. Update CORS settings in FastAPI"
echo ""
print_info "Useful Commands:"
echo "  • View logs: docker compose logs -f"
echo "  • Restart API: docker compose restart api"
echo "  • Stop all: docker compose down"
echo "  • Database backup: docker compose exec postgres pg_dump -U givc ultrathink > backup.sql"
echo ""

# ========================================================================
# SSL Setup (Optional)
# ========================================================================

echo ""
read -p "Would you like to setup SSL with Let's Encrypt? (y/n): " SETUP_SSL

if [[ "$SETUP_SSL" == "y" ]]; then
    print_header "SSL Setup"

    # Install Certbot
    if ! command -v certbot &> /dev/null; then
        print_info "Installing Certbot..."
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
    fi

    # Get domain
    read -p "Enter your domain (e.g., api.your-domain.com): " DOMAIN
    read -p "Enter your email: " EMAIL

    # Install Nginx if not present
    if ! command -v nginx &> /dev/null; then
        print_info "Installing Nginx..."
        apt-get install -y nginx
    fi

    # Create Nginx config
    cat > /etc/nginx/sites-available/givc << NGINXEOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINXEOF

    # Enable site
    ln -sf /etc/nginx/sites-available/givc /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx

    # Get SSL certificate
    certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive

    print_success "SSL certificate installed for $DOMAIN"
    print_success "Your API is now available at: https://$DOMAIN"

    # Setup auto-renewal
    (crontab -l 2>/dev/null; echo "0 0 * * * certbot renew --quiet") | crontab -
    print_success "Auto-renewal configured"
fi

# ========================================================================
# Completion
# ========================================================================

print_header "All Done!"

echo ""
print_success "Your GIVC Ultrathink Platform is now running!"
echo ""
print_info "Monitor your deployment:"
echo "  docker compose logs -f api"
echo ""
print_info "For support, check:"
echo "  • DOCKER_VPS_DEPLOYMENT.md"
echo "  • CLOUDFLARE_DEPLOYMENT.md"
echo  ""

exit 0
