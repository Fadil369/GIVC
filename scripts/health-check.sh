#!/bin/bash

# GIVC Health Check Script
# Checks all services for availability and health

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🏥 GIVC Health Check"
echo "===================="
echo ""

check_service() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_code"; then
        echo -e "${GREEN}✓${NC} $name: OK"
        return 0
    else
        echo -e "${RED}✗${NC} $name: FAILED"
        return 1
    fi
}

check_docker() {
    local service=$1
    
    if docker-compose ps "$service" | grep -q "Up"; then
        echo -e "${GREEN}✓${NC} Docker: $service is running"
        return 0
    else
        echo -e "${RED}✗${NC} Docker: $service is not running"
        return 1
    fi
}

# Docker Services Check
echo "Docker Services:"
check_docker "backend" || true
check_docker "frontend" || true
check_docker "postgres" || true
check_docker "redis" || true
echo ""

# HTTP Endpoints Check
echo "HTTP Endpoints:"
check_service "Frontend" "http://localhost:3000" "200|301|302" || true
check_service "Backend API" "http://localhost:8000/health" "200" || true
check_service "BrainSAIT Platform" "http://localhost:8001/health" "200|404" || true
check_service "Agentic Workflow" "http://localhost:3000/api/health" "200|404" || true
echo ""

# Database Check
echo "Database:"
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} PostgreSQL: OK"
else
    echo -e "${RED}✗${NC} PostgreSQL: FAILED"
fi
echo ""

# Redis Check
echo "Cache:"
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo -e "${GREEN}✓${NC} Redis: OK"
else
    echo -e "${YELLOW}⚠${NC} Redis: Not available or not configured"
fi
echo ""

# Disk Space
echo "System Resources:"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✓${NC} Disk Usage: ${DISK_USAGE}%"
else
    echo -e "${RED}✗${NC} Disk Usage: ${DISK_USAGE}% (Critical)"
fi

# Memory
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ "$MEM_USAGE" -lt 90 ]; then
    echo -e "${GREEN}✓${NC} Memory Usage: ${MEM_USAGE}%"
else
    echo -e "${YELLOW}⚠${NC} Memory Usage: ${MEM_USAGE}% (High)"
fi

echo ""
echo "Health check completed!"
