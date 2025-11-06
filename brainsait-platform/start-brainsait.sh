#!/bin/bash
set -e

echo "🧠 BrainSAIT Platform - Smart Start"
echo "===================================="
echo ""

# Check for port conflicts
echo "📋 Checking for port conflicts..."
PORTS=(5432 6379 8010 8020 8030 8040 8050)
CONFLICTS=()

for port in "${PORTS[@]}"; do
    if sudo netstat -tulpn 2>/dev/null | grep -q ":$port "; then
        CONFLICTS+=($port)
    fi
done

if [ ${#CONFLICTS[@]} -gt 0 ]; then
    echo "⚠️  Port conflicts detected: ${CONFLICTS[*]}"
    echo ""
    echo "Options:"
    echo "1) Stop existing containers and start fresh"
    echo "2) Skip conflicting services"
    echo "3) Exit and resolve manually"
    read -p "Select option (1-3): " choice
    
    case $choice in
        1)
            echo "🛑 Stopping existing containers..."
            docker stop $(docker ps -q) 2>/dev/null || true
            sleep 3
            ;;
        2)
            echo "⏭️  Will skip conflicting services..."
            ;;
        3)
            echo "👋 Exiting..."
            exit 0
            ;;
    esac
fi

echo ""
echo "🚀 Starting BrainSAIT Platform..."
echo ""

# Start infrastructure
echo "📦 Starting infrastructure (PostgreSQL, Redis)..."
docker compose -f docker-compose.unified.yml up -d postgres redis

echo "⏳ Waiting for databases (15 seconds)..."
sleep 15

# Start core services
echo "📦 Starting core services (OID Registry, MCP Gateway)..."
docker compose -f docker-compose.unified.yml up -d oid-registry mcp-gateway

echo "⏳ Waiting for core services (10 seconds)..."
sleep 10

# Start application services
echo "📦 Starting application services (Template, Chat, Payment)..."
docker compose -f docker-compose.unified.yml up -d template-engine chat-engine payment-engine

echo "⏳ Waiting for services (10 seconds)..."
sleep 10

# Register agents
echo "📝 Registering LINC agents..."
python3 scripts/register-agents.py

echo ""
echo "✅ BrainSAIT Platform is running!"
echo ""
echo "🔗 Service URLs:"
echo "  OID Registry:    http://localhost:8010"
echo "  MCP Gateway:     http://localhost:8020"
echo "  Template Engine: http://localhost:8030"
echo "  Chat Engine:     http://localhost:8040"
echo "  Payment Engine:  http://localhost:8050"
echo ""
echo "📊 Check status: docker compose -f docker-compose.unified.yml ps"
echo "📋 View logs:    docker compose -f docker-compose.unified.yml logs -f"
echo ""
