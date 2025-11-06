#!/bin/bash

# GIVC Healthcare Platform - Comprehensive Audit Script
# Purpose: Review, audit, test, and identify improvements

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║       GIVC HEALTHCARE PLATFORM - COMPREHENSIVE AUDIT          ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

AUDIT_LOG="audit-report-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$AUDIT_LOG")
exec 2>&1

echo "📋 Audit started at: $(date)"
echo ""

# =================================================================
# SECTION 1: INFRASTRUCTURE AUDIT
# =================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 1: INFRASTRUCTURE AUDIT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "1.1 Docker Containers Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(NAMES|givc)"
echo ""

echo "1.2 Container Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $(docker ps --filter "name=givc" -q)
echo ""

echo "1.3 Container Health Checks:"
for container in $(docker ps --filter "name=givc" --format "{{.Names}}"); do
    health=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "no healthcheck")
    echo "  - $container: $health"
done
echo ""

echo "1.4 Disk Usage:"
df -h / | tail -1
echo "Docker volumes:"
docker volume ls --filter "name=givc" 
docker system df
echo ""

# =================================================================
# SECTION 2: SERVICE CONNECTIVITY AUDIT
# =================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 2: SERVICE CONNECTIVITY AUDIT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "2.1 Backend API Endpoints:"
endpoints=(
    "http://localhost:8000/"
    "http://localhost:8000/health"
    "http://localhost:8000/ready"
    "http://localhost:8000/api/v1/status"
    "http://localhost:8000/api/v1/eligibility"
    "http://localhost:8000/api/v1/claims"
    "http://localhost:8000/metrics"
)

for endpoint in "${endpoints[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint")
    if [ "$status" = "200" ]; then
        echo -e "  ${GREEN}✅ $endpoint - $status${NC}"
    else
        echo -e "  ${RED}❌ $endpoint - $status${NC}"
    fi
done
echo ""

echo "2.2 Frontend Access:"
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost/")
if [ "$frontend_status" = "200" ]; then
    echo -e "  ${GREEN}✅ Frontend accessible - $frontend_status${NC}"
else
    echo -e "  ${RED}❌ Frontend not accessible - $frontend_status${NC}"
fi
echo ""

echo "2.3 Nginx Proxy Tests:"
proxy_endpoints=(
    "http://localhost/health"
    "http://localhost/api/v1/status"
)

for endpoint in "${proxy_endpoints[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint")
    if [ "$status" = "200" ]; then
        echo -e "  ${GREEN}✅ $endpoint - $status${NC}"
    else
        echo -e "  ${RED}❌ $endpoint - $status${NC}"
    fi
done
echo ""

# =================================================================
# SECTION 3: DATABASE AUDIT
# =================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 3: DATABASE AUDIT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "3.1 PostgreSQL Connection:"
if docker exec givc-postgres pg_isready -U givc > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ PostgreSQL is ready${NC}"
else
    echo -e "  ${RED}❌ PostgreSQL not ready${NC}"
fi
echo ""

echo "3.2 Database Tables:"
docker exec givc-postgres psql -U givc -d givc_prod -c "\dt" 2>/dev/null || echo "  ⚠️  Unable to list tables (may not be initialized)"
echo ""

echo "3.3 Database Size:"
docker exec givc-postgres psql -U givc -d givc_prod -c "SELECT pg_size_pretty(pg_database_size('givc_prod'));" 2>/dev/null || echo "  Database size check skipped"
echo ""

echo "3.4 Active Connections:"
docker exec givc-postgres psql -U givc -d givc_prod -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE datname = 'givc_prod';" 2>/dev/null || echo "  Connection count check skipped"
echo ""

# =================================================================
# SECTION 4: CACHE (REDIS) AUDIT
# =================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 4: CACHE (REDIS) AUDIT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "4.1 Redis Connection:"
if docker exec givc-redis redis-cli -a redis_pass ping 2>/dev/null | grep -q "PONG"; then
    echo -e "  ${GREEN}✅ Redis is responding${NC}"
else
    echo -e "  ${RED}❌ Redis not responding${NC}"
fi
echo ""

echo "4.2 Redis Info:"
docker exec givc-redis redis-cli -a redis_pass INFO server 2>/dev/null | grep -E "(redis_version|os|process_id)" || echo "  Unable to get Redis info"
echo ""

echo "4.3 Redis Memory Usage:"
docker exec givc-redis redis-cli -a redis_pass INFO memory 2>/dev/null | grep -E "(used_memory_human|maxmemory)" || echo "  Unable to get memory info"
echo ""

echo "4.4 Redis Keys Count:"
docker exec givc-redis redis-cli -a redis_pass DBSIZE 2>/dev/null || echo "  Unable to count keys"
echo ""

# =================================================================
# SECTION 5: SECURITY AUDIT
# =================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 5: SECURITY AUDIT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "5.1 Container Security:"
for container in $(docker ps --filter "name=givc" --format "{{.Names}}"); do
    echo "  Container: $container"
    docker inspect --format='    - User: {{.Config.User}}' $container
    docker inspect --format='    - Privileged: {{.HostConfig.Privileged}}' $container
    docker inspect --format='    - ReadonlyRootfs: {{.HostConfig.ReadonlyRootfs}}' $container
done
echo ""

echo "5.2 Environment Variables (checking for secrets):"
echo "  ⚠️  Checking for exposed secrets..."
for container in $(docker ps --filter "name=givc" --format "{{.Names}}"); do
    echo "  Container: $container"
    env_vars=$(docker inspect --format='{{range .Config.Env}}{{println .}}{{end}}' $container | grep -E "(PASSWORD|SECRET|KEY|TOKEN)" | sed 's/=.*/=***REDACTED***/' || echo "    No sensitive vars found")
    echo "$env_vars"
done
echo ""

echo "5.3 Open Ports Audit:"
echo "  Checking exposed ports..."
docker ps --filter "name=givc" --format "table {{.Names}}\t{{.Ports}}"
echo ""

# =================================================================
# SECTION 6: NETWORK AUDIT
# =================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 6: NETWORK AUDIT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "6.1 Docker Networks:"
docker network ls | grep givc
echo ""

echo "6.2 Network Connectivity Between Services:"
echo "  Testing backend -> postgres..."
docker exec givc-backend nc -zv givc-postgres 5432 2>&1 | grep -q "succeeded" && echo -e "    ${GREEN}✅ Connected${NC}" || echo -e "    ${RED}❌ Failed${NC}"

echo "  Testing backend -> redis..."
docker exec givc-backend nc -zv givc-redis 6379 2>&1 | grep -q "succeeded" && echo -e "    ${GREEN}✅ Connected${NC}" || echo -e "    ${RED}❌ Failed${NC}"
echo ""

echo "6.3 DNS Resolution Test:"
docker exec givc-backend nslookup givc-postgres 2>/dev/null | grep "Address" || echo "  DNS test skipped"
echo ""

# =================================================================
# SECTION 7: PERFORMANCE AUDIT
# =================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 7: PERFORMANCE AUDIT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "7.1 API Response Times:"
for i in {1..5}; do
    time_taken=$(curl -s -o /dev/null -w "%{time_total}" "http://localhost:8000/health")
    echo "  Request $i: ${time_taken}s"
done
echo ""

echo "7.2 Backend Logs (last 10 lines):"
docker logs givc-backend --tail 10
echo ""

# =================================================================
# SECTION 8: CONFIGURATION AUDIT
# =================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 8: CONFIGURATION AUDIT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "8.1 Docker Compose Configuration:"
if [ -f "docker-compose.yml" ]; then
    echo -e "  ${GREEN}✅ docker-compose.yml exists${NC}"
    echo "  Services defined:"
    grep -E "^  [a-z-]+:" docker-compose.yml | sed 's/:$//' || echo "  Unable to parse services"
else
    echo -e "  ${RED}❌ docker-compose.yml not found${NC}"
fi
echo ""

echo "8.2 Nginx Configuration:"
if [ -f "nginx/nginx.conf" ]; then
    echo -e "  ${GREEN}✅ nginx.conf exists${NC}"
else
    echo -e "  ${YELLOW}⚠️  nginx.conf not found${NC}"
fi
echo ""

echo "8.3 Environment Files:"
[ -f ".env" ] && echo -e "  ${GREEN}✅ .env exists${NC}" || echo -e "  ${YELLOW}⚠️  .env not found (using defaults)${NC}"
[ -f ".env.example" ] && echo -e "  ${GREEN}✅ .env.example exists${NC}" || echo -e "  ${RED}❌ .env.example not found${NC}"
echo ""

# =================================================================
# SECTION 9: CODE QUALITY AUDIT
# =================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 9: CODE QUALITY AUDIT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "9.1 Python Backend:"
if [ -f "main_api.py" ]; then
    echo -e "  ${GREEN}✅ main_api.py exists${NC}"
    lines=$(wc -l < main_api.py)
    echo "  Lines of code: $lines"
else
    echo -e "  ${RED}❌ main_api.py not found${NC}"
fi
echo ""

echo "9.2 Dependencies:"
if [ -f "requirements.txt" ]; then
    echo -e "  ${GREEN}✅ requirements.txt exists${NC}"
    echo "  Packages: $(wc -l < requirements.txt)"
else
    echo -e "  ${RED}❌ requirements.txt not found${NC}"
fi
echo ""

# =================================================================
# SECTION 10: RECOMMENDATIONS
# =================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 10: RECOMMENDATIONS & ACTION ITEMS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

RECOMMENDATIONS=()

# Check for missing .env
if [ ! -f ".env" ]; then
    RECOMMENDATIONS+=("Create .env file from .env.example for proper configuration")
fi

# Check Redis auth in test script
if ! grep -q "redis_pass" test-deployment.sh 2>/dev/null; then
    RECOMMENDATIONS+=("Update test-deployment.sh to use Redis password authentication")
fi

# Check for database initialization
if ! docker exec givc-postgres psql -U givc -d givc_prod -c "\dt" 2>/dev/null | grep -q "rows"; then
    RECOMMENDATIONS+=("Initialize database schema - create tables and initial data")
fi

# Check for monitoring
if ! docker ps | grep -q "prometheus\|grafana"; then
    RECOMMENDATIONS+=("Consider adding monitoring (Prometheus/Grafana) for production readiness")
fi

# Check for backup strategy
if [ ! -f "backup.sh" ]; then
    RECOMMENDATIONS+=("Implement automated backup strategy for database and volumes")
fi

# Check for SSL/HTTPS locally
if ! grep -q "ssl_certificate" nginx/nginx.conf 2>/dev/null; then
    RECOMMENDATIONS+=("Consider implementing SSL/TLS for local development environment")
fi

# Check for logging strategy
if ! docker ps | grep -q "loki\|elasticsearch"; then
    RECOMMENDATIONS+=("Implement centralized logging solution for production")
fi

# Check for rate limiting
if ! grep -q "limit_req" nginx/nginx.conf 2>/dev/null; then
    RECOMMENDATIONS+=("Add rate limiting to Nginx for API protection")
fi

# Display recommendations
if [ ${#RECOMMENDATIONS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ No critical recommendations - system looks good!${NC}"
else
    echo -e "${YELLOW}Found ${#RECOMMENDATIONS[@]} recommendations:${NC}"
    for i in "${!RECOMMENDATIONS[@]}"; do
        echo -e "  $((i+1)). ${RECOMMENDATIONS[$i]}"
    done
fi
echo ""

# =================================================================
# SUMMARY
# =================================================================
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}AUDIT SUMMARY${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "📊 Audit completed at: $(date)"
echo "📝 Full report saved to: $AUDIT_LOG"
echo ""
echo "🎯 Next Steps:"
echo "  1. Review the recommendations above"
echo "  2. Run the enhancement script: ./enhance-platform.sh"
echo "  3. Implement database schema migrations"
echo "  4. Set up monitoring and alerting"
echo "  5. Configure automated backups"
echo ""
echo -e "${GREEN}✅ Audit Complete!${NC}"
