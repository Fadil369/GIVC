#!/bin/bash

# ========================================================================
# Cloudflare Deployment Script for GIVC Ultrathink Platform
# ========================================================================
# This script automates the deployment of the frontend to Cloudflare Pages
# and provides instructions for backend deployment
#
# Author: GIVC Platform Team
# License: GPL-3.0
# ========================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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
cat << "EOF"
   _____ _______      ______
  / ____|_   _\ \    / / __ \
 | |  __  | |  \ \  / / |  | |
 | | |_ | | |   \ \/ /| |  | |
 | |__| |_| |_   \  / | |__| |
  \_____|_____|   \/   \____/

  Ultrathink AI Platform
  Cloudflare Deployment
EOF
echo -e "${NC}\n"

print_info "Deployment script for Cloudflare Pages + Workers"
print_info "Version: 2.0.0 | Date: $(date '+%Y-%m-%d')"

# ========================================================================
# Pre-flight Checks
# ========================================================================

print_header "Pre-flight Checks"

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    print_error "Wrangler CLI not found"
    print_info "Install with: npm install -g wrangler"
    exit 1
fi
print_success "Wrangler CLI found: $(wrangler --version)"

# Check if logged in to Cloudflare
if ! wrangler whoami &> /dev/null 2>&1; then
    print_warning "Not logged in to Cloudflare"
    print_info "Running: wrangler login"
    wrangler login
fi
print_success "Logged in to Cloudflare"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js not found"
    print_info "Install Node.js from: https://nodejs.org/"
    exit 1
fi
print_success "Node.js found: $(node --version)"

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git not found"
    exit 1
fi
print_success "Git found: $(git --version | head -1)"

# ========================================================================
# Configuration
# ========================================================================

print_header "Configuration"

# Project name
PROJECT_NAME="${PROJECT_NAME:-givc-ultrathink}"
print_info "Project name: $PROJECT_NAME"

# Ask for deployment type
echo ""
echo "Select deployment option:"
echo "  1) Deploy Frontend to Cloudflare Pages (Recommended)"
echo "  2) Deploy Workers only"
echo "  3) Full deployment (Pages + Workers)"
echo "  4) Preview deployment"
echo ""
read -p "Enter option (1-4): " DEPLOY_OPTION

# Ask for backend URL if not set
if [[ -z "$API_BACKEND_URL" ]]; then
    echo ""
    print_warning "Backend API URL not set"
    read -p "Enter your FastAPI backend URL (or press Enter to skip): " API_BACKEND_URL
    export API_BACKEND_URL
fi

if [[ -n "$API_BACKEND_URL" ]]; then
    print_success "Backend URL: $API_BACKEND_URL"
else
    print_warning "No backend URL provided. Workers will need manual configuration."
fi

# ========================================================================
# Frontend Build
# ========================================================================

if [[ "$DEPLOY_OPTION" == "1" ]] || [[ "$DEPLOY_OPTION" == "3" ]] || [[ "$DEPLOY_OPTION" == "4" ]]; then
    print_header "Building Frontend"

    # Check if frontend directory exists
    if [[ ! -d "frontend" ]]; then
        print_error "Frontend directory not found"
        exit 1
    fi

    cd frontend

    # Install dependencies
    print_info "Installing dependencies..."
    if npm install; then
        print_success "Dependencies installed"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi

    # Build frontend
    print_info "Building React application..."
    if npm run build; then
        print_success "Frontend build successful"
    else
        print_error "Frontend build failed"
        exit 1
    fi

    # Check build output
    if [[ -d "build" ]]; then
        BUILD_SIZE=$(du -sh build | cut -f1)
        print_success "Build output: frontend/build ($BUILD_SIZE)"
    else
        print_error "Build directory not found"
        exit 1
    fi

    cd ..
fi

# ========================================================================
# Deploy Frontend to Cloudflare Pages
# ========================================================================

if [[ "$DEPLOY_OPTION" == "1" ]] || [[ "$DEPLOY_OPTION" == "3" ]]; then
    print_header "Deploying to Cloudflare Pages"

    print_info "Project: $PROJECT_NAME"
    print_info "Source: frontend/build"

    # Deploy to Pages
    if wrangler pages deploy frontend/build --project-name="$PROJECT_NAME" --commit-dirty=true; then
        print_success "Frontend deployed successfully!"

        # Get deployment URL
        PAGES_URL="https://${PROJECT_NAME}.pages.dev"
        print_success "Deployment URL: $PAGES_URL"

        echo ""
        print_info "Next steps:"
        echo "  1. Visit: $PAGES_URL"
        echo "  2. Configure custom domain in Cloudflare dashboard"
        echo "  3. Set environment variables:"
        echo "     - REACT_APP_API_URL=$API_BACKEND_URL"
        echo "     - REACT_APP_ULTRATHINK_ENABLED=true"
    else
        print_error "Deployment failed"
        exit 1
    fi
fi

# ========================================================================
# Deploy Preview
# ========================================================================

if [[ "$DEPLOY_OPTION" == "4" ]]; then
    print_header "Deploying Preview"

    if wrangler pages deploy frontend/build --project-name="$PROJECT_NAME" --branch="preview" --commit-dirty=true; then
        print_success "Preview deployment successful!"
    else
        print_error "Preview deployment failed"
        exit 1
    fi
fi

# ========================================================================
# Deploy Workers
# ========================================================================

if [[ "$DEPLOY_OPTION" == "2" ]] || [[ "$DEPLOY_OPTION" == "3" ]]; then
    print_header "Deploying Workers"

    # Check if workers directory exists
    if [[ ! -d "workers" ]]; then
        print_warning "Workers directory not found. Creating basic worker..."
        mkdir -p workers

        cat > workers/router.js << 'WORKER_EOF'
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Health check
    if (url.pathname === '/api/health') {
      return new Response(JSON.stringify({ status: 'ok', worker: 'active' }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Proxy to backend
    if (url.pathname.startsWith('/api/') && env.API_BACKEND_URL) {
      const backendUrl = new URL(env.API_BACKEND_URL);
      backendUrl.pathname = url.pathname;
      backendUrl.search = url.search;

      return fetch(backendUrl.toString(), {
        method: request.method,
        headers: request.headers,
        body: request.body
      });
    }

    // Serve frontend from Pages
    return env.ASSETS.fetch(request);
  }
};
WORKER_EOF
        print_success "Created basic worker"
    fi

    # Deploy worker
    print_info "Deploying worker..."
    if wrangler deploy; then
        print_success "Worker deployed successfully!"
    else
        print_warning "Worker deployment failed. Check wrangler.toml configuration."
    fi
fi

# ========================================================================
# Backend Deployment Instructions
# ========================================================================

print_header "Backend Deployment"

print_warning "FastAPI backend must be deployed separately"
echo ""
echo "Choose a deployment platform:"
echo ""
echo "🚂 Railway (Easiest):"
echo "   npm install -g @railway/cli"
echo "   railway login"
echo "   railway init"
echo "   railway up"
echo ""
echo "🐳 Docker on VPS:"
echo "   docker build -t givc-ultrathink ."
echo "   docker run -d -p 8000:8000 givc-ultrathink"
echo ""
echo "☁️  Google Cloud Run:"
echo "   gcloud builds submit --tag gcr.io/PROJECT/givc"
echo "   gcloud run deploy --image gcr.io/PROJECT/givc"
echo ""
echo "⚡ AWS Lambda:"
echo "   pip install mangum"
echo "   zappa deploy production"
echo ""

if [[ -n "$API_BACKEND_URL" ]]; then
    print_info "Your configured backend: $API_BACKEND_URL"
else
    print_warning "Backend URL not configured yet"
fi

# ========================================================================
# Environment Variables Setup
# ========================================================================

print_header "Environment Variables"

echo "Set these in Cloudflare Pages dashboard:"
echo ""
echo "  Pages → Settings → Environment Variables → Production"
echo ""
echo "  REACT_APP_API_URL=$API_BACKEND_URL"
echo "  REACT_APP_ENVIRONMENT=production"
echo "  REACT_APP_ULTRATHINK_ENABLED=true"
echo "  REACT_APP_AI_VALIDATION=true"
echo "  REACT_APP_SMART_COMPLETION=true"
echo ""

echo "For Workers, set secrets with:"
echo ""
echo "  wrangler secret put API_SECRET_KEY"
echo "  wrangler secret put JWT_SECRET"
echo "  wrangler secret put DATABASE_URL"
echo ""

# ========================================================================
# Verification
# ========================================================================

print_header "Verification"

if [[ "$DEPLOY_OPTION" == "1" ]] || [[ "$DEPLOY_OPTION" == "3" ]]; then
    PAGES_URL="https://${PROJECT_NAME}.pages.dev"

    print_info "Testing deployment..."
    sleep 2

    if curl -s -o /dev/null -w "%{http_code}" "$PAGES_URL" | grep -q "200"; then
        print_success "Frontend is live: $PAGES_URL"
    else
        print_warning "Frontend may still be deploying. Check status in dashboard."
    fi
fi

# ========================================================================
# Summary
# ========================================================================

print_header "Deployment Summary"

echo ""
print_success "Deployment completed successfully!"
echo ""
print_info "Frontend: https://${PROJECT_NAME}.pages.dev"
if [[ -n "$API_BACKEND_URL" ]]; then
    print_info "Backend: $API_BACKEND_URL"
fi
echo ""
print_info "Next Steps:"
echo "  1. Configure custom domain (optional)"
echo "  2. Set environment variables in Pages dashboard"
echo "  3. Deploy FastAPI backend to your chosen platform"
echo "  4. Update CORS settings in FastAPI to allow Pages domain"
echo "  5. Test all Ultrathink AI features"
echo ""
print_info "Documentation:"
echo "  - Full guide: CLOUDFLARE_DEPLOYMENT.md"
echo "  - Architecture: ARCHITECTURE_ANALYSIS.md"
echo "  - API docs: https://${API_BACKEND_URL:-your-backend}/docs"
echo ""

# ========================================================================
# Monitoring
# ========================================================================

print_header "Monitoring & Analytics"

echo "Monitor your deployment:"
echo "  - Pages Analytics: https://dash.cloudflare.com/pages"
echo "  - Workers Analytics: https://dash.cloudflare.com/workers"
echo "  - Real-time logs: wrangler tail"
echo ""

# ========================================================================
# Completion
# ========================================================================

print_success "All done! 🎉"
echo ""
print_info "Your GIVC Ultrathink Platform is now on Cloudflare's global network"
echo ""

# Open dashboard if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    read -p "Open Cloudflare dashboard? (y/n): " OPEN_DASH
    if [[ "$OPEN_DASH" == "y" ]]; then
        open "https://dash.cloudflare.com/pages"
    fi
fi

exit 0
