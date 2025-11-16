#!/bin/bash

# ========================================================================
# Complete VPS Deployment Script for GIVC Ultrathink Platform
# ========================================================================
# This script automates the entire deployment process:
# 1. Transfers files to VPS
# 2. Installs dependencies
# 3. Configures environment
# 4. Deploys FastAPI backend
# 5. Deploys frontend to Cloudflare Pages
# ========================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
VPS_IP="82.25.101.65"
VPS_USER="root"
VPS_PORT="22"
DEPLOY_DIR="/opt/GIVC"
APP_NAME="givc-ultrathink"

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
# Step 0: Pre-flight Checks
# ========================================================================

print_header "Pre-flight Checks"

# Check if running from correct directory
if [ ! -f "fastapi_app_ultrathink.py" ]; then
    print_error "This script must be run from the GIVC repository root directory"
    exit 1
fi
print_success "Running from correct directory"

# Check required commands
for cmd in ssh scp rsync wrangler; do
    if ! command -v $cmd &> /dev/null; then
        print_warning "$cmd not found. Some features may not work."
    else
        print_success "$cmd found"
    fi
done

# ========================================================================
# Step 1: Test SSH Connection
# ========================================================================

print_header "Testing SSH Connection"

print_info "Attempting to connect to $VPS_USER@$VPS_IP..."
if ssh -o ConnectTimeout=10 -o BatchMode=yes $VPS_USER@$VPS_IP "echo 'Connection successful'" 2>/dev/null; then
    print_success "SSH connection established"
else
    print_error "SSH connection failed"
    print_info "Please ensure:"
    echo "  1. SSH key is added: ssh-copy-id $VPS_USER@$VPS_IP"
    echo "  2. Or run: ssh $VPS_USER@$VPS_IP to setup authentication"
    echo ""
    read -p "Do you want to continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
fi

# ========================================================================
# Step 2: Prepare Deployment Package
# ========================================================================

print_header "Preparing Deployment Package"

# Create temporary directory for deployment
TEMP_DIR=$(mktemp -d)
print_info "Created temporary directory: $TEMP_DIR"

# Copy necessary files
print_info "Copying files to temporary directory..."

# Backend files
cp -r \
    fastapi_app_ultrathink.py \
    requirements.txt \
    Dockerfile.fastapi \
    docker-compose.yml \
    .env.example \
    auth/ \
    config/ \
    middleware/ \
    routers/ \
    services/ \
    database/ \
    models/ \
    utils/ \
    $TEMP_DIR/ 2>/dev/null || true

# Copy deployment scripts
cp deploy-vps.sh $TEMP_DIR/ 2>/dev/null || true

print_success "Files prepared for deployment"

# ========================================================================
# Step 3: Transfer Files to VPS
# ========================================================================

print_header "Transferring Files to VPS"

print_info "Creating deployment directory on VPS..."
ssh $VPS_USER@$VPS_IP "mkdir -p $DEPLOY_DIR && mkdir -p $DEPLOY_DIR/logs $DEPLOY_DIR/models $DEPLOY_DIR/database"

print_info "Transferring files via rsync..."
rsync -avz --progress \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='dist' \
    --exclude='build' \
    $TEMP_DIR/ $VPS_USER@$VPS_IP:$DEPLOY_DIR/

print_success "Files transferred successfully"

# Cleanup temp directory
rm -rf $TEMP_DIR

# ========================================================================
# Step 4: Setup Environment on VPS
# ========================================================================

print_header "Setting Up Environment on VPS"

ssh $VPS_USER@$VPS_IP bash << 'ENDSSH'
set -e

echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv git curl wget

echo "🐍 Creating Python virtual environment..."
cd /opt/GIVC
python3 -m venv venv
source venv/bin/activate

echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    # Generate secure secret key
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET/" .env
    echo "✅ .env file created with secure secret key"
else
    echo "✅ .env file already exists"
fi

echo "✅ Environment setup complete"
ENDSSH

print_success "Environment configured on VPS"

# ========================================================================
# Step 5: Setup Database (PostgreSQL)
# ========================================================================

print_header "Setting Up Database"

read -p "Do you want to setup PostgreSQL database? (y/n): " SETUP_DB

if [ "$SETUP_DB" = "y" ]; then
    ssh $VPS_USER@$VPS_IP bash << 'ENDSSH'
    set -e

    echo "🗄️  Installing PostgreSQL..."
    apt-get install -y postgresql postgresql-contrib

    systemctl start postgresql
    systemctl enable postgresql

    echo "📊 Creating database and user..."
    sudo -u postgres psql << 'EOSQL'
    CREATE DATABASE ultrathink;
    CREATE USER givc WITH PASSWORD 'givc123';
    GRANT ALL PRIVILEGES ON DATABASE ultrathink TO givc;
    ALTER DATABASE ultrathink OWNER TO givc;
    \q
EOSQL

    echo "✅ PostgreSQL setup complete"
ENDSSH

    print_success "Database configured"

    # Update .env with database URL
    ssh $VPS_USER@$VPS_IP "sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://givc:givc123@localhost:5432/ultrathink|' /opt/GIVC/.env"
fi

# ========================================================================
# Step 6: Deploy FastAPI Backend
# ========================================================================

print_header "Deploying FastAPI Backend"

ssh $VPS_USER@$VPS_IP bash << 'ENDSSH'
set -e

cd /opt/GIVC
source venv/bin/activate

echo "🚀 Starting FastAPI application..."

# Stop existing instance if running
pkill -f "uvicorn fastapi_app_ultrathink" || true
sleep 2

# Start FastAPI in background
nohup uvicorn fastapi_app_ultrathink:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    > logs/fastapi.log 2>&1 &

echo $! > /opt/GIVC/fastapi.pid

sleep 5

# Check if running
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ FastAPI is running successfully"
    echo "📝 PID: $(cat /opt/GIVC/fastapi.pid)"
else
    echo "❌ FastAPI failed to start. Check logs:"
    tail -50 logs/fastapi.log
    exit 1
fi
ENDSSH

print_success "FastAPI backend deployed and running"

# Get VPS IP for frontend
API_URL="http://$VPS_IP:8000"
print_info "Backend API URL: $API_URL"

# ========================================================================
# Step 7: Setup Nginx Reverse Proxy (Optional)
# ========================================================================

print_header "Nginx Configuration"

read -p "Do you want to setup Nginx reverse proxy? (y/n): " SETUP_NGINX

if [ "$SETUP_NGINX" = "y" ]; then
    ssh $VPS_USER@$VPS_IP bash << 'ENDSSH'
    set -e

    echo "📦 Installing Nginx..."
    apt-get install -y nginx

    echo "🔧 Configuring Nginx..."
    cat > /etc/nginx/sites-available/givc << 'NGINX_CONF'
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
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
}
NGINX_CONF

    ln -sf /etc/nginx/sites-available/givc /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default

    nginx -t && systemctl restart nginx
    systemctl enable nginx

    echo "✅ Nginx configured and running"
ENDSSH

    print_success "Nginx reverse proxy configured"
    API_URL="http://$VPS_IP"
fi

# ========================================================================
# Step 8: Build and Deploy Frontend
# ========================================================================

print_header "Deploying Frontend to Cloudflare Pages"

print_info "Building frontend..."

# Update API URL in frontend
if [ -f "src/config/api.js" ]; then
    sed -i.bak "s|API_BASE_URL:.*|API_BASE_URL: '$API_URL'|" src/config/api.js
fi

# Build frontend
if [ -f "package.json" ]; then
    print_info "Installing frontend dependencies..."
    npm install

    print_info "Building frontend for production..."
    npm run build

    print_success "Frontend built successfully"

    # Deploy to Cloudflare Pages
    read -p "Do you want to deploy frontend to Cloudflare Pages? (y/n): " DEPLOY_CF

    if [ "$DEPLOY_CF" = "y" ]; then
        print_info "Deploying to Cloudflare Pages..."

        # Set environment variable
        export REACT_APP_API_URL=$API_URL

        wrangler pages deploy dist --project-name=givc-ultrathink

        print_success "Frontend deployed to Cloudflare Pages"
    fi
else
    print_warning "No package.json found. Skipping frontend deployment."
fi

# ========================================================================
# Step 9: Configure Firewall
# ========================================================================

print_header "Configuring Firewall"

read -p "Do you want to configure UFW firewall? (y/n): " SETUP_FW

if [ "$SETUP_FW" = "y" ]; then
    ssh $VPS_USER@$VPS_IP bash << 'ENDSSH'
    set -e

    echo "🔥 Configuring UFW firewall..."
    apt-get install -y ufw

    # Allow SSH
    ufw allow 22/tcp

    # Allow HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp

    # Allow FastAPI port (if not using Nginx)
    ufw allow 8000/tcp

    # Enable firewall
    echo "y" | ufw enable

    ufw status

    echo "✅ Firewall configured"
ENDSSH

    print_success "Firewall configured"
fi

# ========================================================================
# Step 10: Final Verification
# ========================================================================

print_header "Final Verification"

print_info "Testing backend API..."
if curl -f http://$VPS_IP:8000/api/health > /dev/null 2>&1; then
    print_success "Backend API is responding"
else
    print_warning "Backend API may not be accessible from outside"
fi

print_info "Checking service status on VPS..."
ssh $VPS_USER@$VPS_IP "cd /opt/GIVC && source venv/bin/activate && ps aux | grep fastapi | grep -v grep"

# ========================================================================
# Summary
# ========================================================================

print_header "Deployment Summary"

echo ""
print_success "🎉 Deployment Complete!"
echo ""
print_info "Backend Deployment:"
echo "  • VPS IP: $VPS_IP"
echo "  • API URL: $API_URL"
echo "  • Health Check: $API_URL/api/health"
echo "  • API Docs: $API_URL/docs"
echo "  • Logs: /opt/GIVC/logs/fastapi.log"
echo ""
print_info "Frontend Deployment:"
echo "  • Build directory: ./dist"
echo "  • Cloudflare Pages: Check wrangler output above"
echo ""
print_info "Useful Commands:"
echo "  • View logs: ssh $VPS_USER@$VPS_IP 'tail -f /opt/GIVC/logs/fastapi.log'"
echo "  • Restart API: ssh $VPS_USER@$VPS_IP 'cd /opt/GIVC && pkill -f fastapi && source venv/bin/activate && nohup uvicorn fastapi_app_ultrathink:app --host 0.0.0.0 --port 8000 --workers 4 > logs/fastapi.log 2>&1 &'"
echo "  • Check status: ssh $VPS_USER@$VPS_IP 'ps aux | grep fastapi'"
echo ""
print_info "Next Steps:"
echo "  1. Test API: curl $API_URL/api/health"
echo "  2. Test frontend integration"
echo "  3. Configure SSL with Let's Encrypt (optional)"
echo "  4. Setup monitoring and backups"
echo ""

exit 0
