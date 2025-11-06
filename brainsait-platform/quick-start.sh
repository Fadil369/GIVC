#!/bin/bash

# 🚀 BrainSAIT Platform - Quick Start Script
# This script sets up and launches the entire unified platform

set -e

echo "🧠 BrainSAIT Platform - Quick Start"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose not found. Installing...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo -e "${GREEN}✅ Prerequisites checked${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your API keys before continuing!${NC}"
    echo ""
    read -p "Press Enter to open .env for editing (use nano)..."
    nano .env
fi

echo -e "${BLUE}🔧 Setting up environment...${NC}"

# Create necessary directories
mkdir -p nginx/conf.d nginx/ssl monitoring/grafana/dashboards monitoring/grafana/datasources

# Set execute permissions
chmod +x database/init-multi-db.sh

echo -e "${GREEN}✅ Environment setup complete${NC}"
echo ""

# Ask user what to deploy
echo -e "${BLUE}📦 What would you like to deploy?${NC}"
echo "1) Core services only (Database, Redis, OID Registry, MCP Gateway)"
echo "2) Core + All New Services (Template, Chat, Payment Engines)"
echo "3) Core + GIVC Healthcare Platform"
echo "4) Full stack (Everything)"
echo "5) Development mode (with hot reload)"
echo ""
read -p "Select option (1-5): " deploy_option

# Build and start services
echo ""
echo -e "${BLUE}🚀 Building and starting services...${NC}"
echo ""

case $deploy_option in
    1)
        docker compose -f docker-compose.unified.yml up -d postgres redis oid-registry mcp-gateway
        ;;
    2)
        docker compose -f docker-compose.unified.yml up -d postgres redis oid-registry mcp-gateway chat-engine template-engine payment-engine
        ;;
    3)
        docker compose -f docker-compose.unified.yml up -d postgres redis oid-registry mcp-gateway givc-app
        ;;
    4)
        docker compose -f docker-compose.unified.yml up -d
        ;;
    5)
        docker compose -f docker-compose.unified.yml up
        ;;
    *)
        echo -e "${YELLOW}Invalid option. Deploying core services...${NC}"
        docker compose -f docker-compose.unified.yml up -d postgres redis oid-registry mcp-gateway
        ;;
esac

# Wait for services to be ready
echo ""
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Health checks
echo ""
echo -e "${BLUE}🏥 Checking service health...${NC}"

services=(
    "http://localhost:8010/health:OID Registry"
    "http://localhost:8020/health:MCP Gateway"
    "http://localhost:8030/health:Template Engine"
    "http://localhost:8040/health:Chat Engine"
    "http://localhost:8050/health:Payment Engine"
)

for service in "${services[@]}"; do
    IFS=':' read -r url name <<< "$service"
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  $name is not responding (may still be starting)${NC}"
    fi
done

# Register initial agents
echo ""
echo -e "${BLUE}📝 Registering initial LINC agents...${NC}"
python3 scripts/register-agents.py

echo ""
echo -e "${GREEN}🎉 Platform is ready!${NC}"
echo ""
echo "================================"
echo "🌐 Service URLs:"
echo "================================"
echo "OID Registry:     http://localhost:8010"
echo "MCP Gateway:      http://localhost:8020"
echo "Template Engine:  http://localhost:8030"
echo "Chat Engine:      http://localhost:8040"
echo "Payment Engine:   http://localhost:8050"
echo "GIVC Healthcare:  http://localhost:3000"
echo "N8N Workflow:     http://localhost:5678"
echo "Orchestrator:     http://localhost:8000"
echo ""
echo "📚 Documentation:"
echo "OID Registry API:     http://localhost:8010/docs"
echo "MCP Gateway API:      http://localhost:8020/docs"
echo "Template Engine API:  http://localhost:8030/docs"
echo "Chat Engine API:      http://localhost:8040/docs"
echo "Payment Engine API:   http://localhost:8050/docs"
echo ""
echo "🔐 Credentials (from .env):"
echo "N8N:      admin / [see .env]"
echo "Database: brainsait / [see .env]"
echo ""
echo "📊 Monitoring:"
echo "View logs: docker compose -f docker-compose.unified.yml logs -f [service-name]"
echo "Stop all:  docker compose -f docker-compose.unified.yml down"
echo "Restart:   docker compose -f docker-compose.unified.yml restart [service-name]"
echo ""
echo -e "${GREEN}✨ Happy building!${NC}"
