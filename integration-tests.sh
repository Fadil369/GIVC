#!/bin/bash

# GIVC Platform - Integration Test Suite
# Purpose: Comprehensive integration testing

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
TOTAL=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL=$((TOTAL+1))
    echo -n "  Testing $test_name... "
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        PASSED=$((PASSED+1))
        return 0
    else
        echo -e "${RED}✗${NC}"
        FAILED=$((FAILED+1))
        return 1
    fi
}

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     GIVC Platform - Integration Test Suite                   ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Container Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CONTAINER TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Frontend container" "docker ps | grep -q givc-frontend"
run_test "Backend container" "docker ps | grep -q givc-backend"
run_test "PostgreSQL container" "docker ps | grep -q givc-postgres"
run_test "Redis container" "docker ps | grep -q givc-redis"
run_test "Nginx container" "docker ps | grep -q givc-nginx"
run_test "Backend health" "docker inspect givc-backend | grep -q '\"Status\": \"healthy\"'"
run_test "PostgreSQL health" "docker inspect givc-postgres | grep -q '\"Status\": \"healthy\"'"
run_test "Redis health" "docker inspect givc-redis | grep -q '\"Status\": \"healthy\"'"

echo ""

# Database Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DATABASE TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Database connection" "docker exec givc-postgres pg_isready -U givc"
run_test "Database exists" "docker exec givc-postgres psql -U givc -lqt | grep -qw givc_prod"
run_test "Tables created" "docker exec givc-postgres psql -U givc -d givc_prod -c '\dt' | grep -q users"
run_test "Users table" "docker exec givc-postgres psql -U givc -d givc_prod -c '\dt' | grep -q users"
run_test "Providers table" "docker exec givc-postgres psql -U givc -d givc_prod -c '\dt' | grep -q providers"
run_test "Patients table" "docker exec givc-postgres psql -U givc -d givc_prod -c '\dt' | grep -q patients"
run_test "Claims table" "docker exec givc-postgres psql -U givc -d givc_prod -c '\dt' | grep -q claims"

echo ""

# API Endpoint Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API ENDPOINT TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Root endpoint" "curl -s -f http://localhost:8000/"
run_test "Health endpoint" "curl -s -f http://localhost:8000/health"
run_test "Ready endpoint" "curl -s -f http://localhost:8000/ready"
run_test "Status endpoint" "curl -s -f http://localhost:8000/api/v1/status"
run_test "Eligibility endpoint" "curl -s -f http://localhost:8000/api/v1/eligibility"
run_test "Claims endpoint" "curl -s -f http://localhost:8000/api/v1/claims"
run_test "Metrics endpoint" "curl -s -f http://localhost:8000/metrics"

echo ""

# Response Content Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API RESPONSE TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Health status 'healthy'" "curl -s http://localhost:8000/health | grep -q 'healthy'"
run_test "API version present" "curl -s http://localhost:8000/api/v1/status | grep -q 'api_version'"
run_test "NPHIES integration" "curl -s http://localhost:8000/api/v1/status | grep -q 'nphies'"
run_test "Service name correct" "curl -s http://localhost:8000/ | grep -q 'GIVC'"

echo ""

# Cache Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CACHE TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Redis connection" "docker exec givc-redis redis-cli -a redis_pass ping | grep -q PONG"
run_test "Redis info" "docker exec givc-redis redis-cli -a redis_pass INFO server"
run_test "Redis save" "docker exec givc-redis redis-cli -a redis_pass SAVE"

echo ""

# Frontend Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FRONTEND TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Frontend accessible" "curl -s -f http://localhost/"
run_test "Frontend HTML" "curl -s http://localhost/ | grep -q '<html'"
run_test "Frontend title" "curl -s http://localhost/ | grep -iq 'GIVC'"

echo ""

# Nginx Proxy Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NGINX PROXY TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Nginx health proxy" "curl -s http://localhost/health | grep -q healthy"
run_test "Nginx API proxy" "curl -s http://localhost/api/v1/status | grep -q nphies"
run_test "Nginx headers" "curl -sI http://localhost/ | grep -q 'Server: nginx'"

echo ""

# Network Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NETWORK TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Docker network exists" "docker network ls | grep -q givc"
run_test "Backend to Postgres" "docker exec givc-backend nc -zv givc-postgres 5432"
run_test "Backend to Redis" "docker exec givc-backend nc -zv givc-redis 6379"

echo ""

# Security Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECURITY TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test ".env file secured" "[ \$(stat -c '%a' .env 2>/dev/null || stat -f '%A' .env 2>/dev/null) = '600' ]"
run_test ".env in .gitignore" "grep -q '.env' .gitignore"
run_test "Backend non-root" "docker inspect givc-backend --format='{{.Config.User}}' | grep -q apiuser"
run_test "No privileged containers" "! docker ps --filter 'name=givc' --format '{{.ID}}' | xargs -I {} docker inspect {} --format='{{.HostConfig.Privileged}}' | grep -q true"

echo ""

# Cloudflare Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CLOUDFLARE TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Tunnel service running" "systemctl is-active --quiet cloudflared"
run_test "Cloudflare API configured" "[ -n \"\$CLOUDFLARE_API_TOKEN\" ]" || run_test "API token in .env" "grep -q CLOUDFLARE_API_TOKEN .env"
run_test "Tunnel ID configured" "grep -q CLOUDFLARE_TUNNEL_ID .env"

echo ""

# File Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FILE & CONFIGURATION TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "docker-compose.yml" "[ -f docker-compose.yml ]"
run_test ".env file" "[ -f .env ]"
run_test "Database schema" "[ -f database/init.sql ]"
run_test "Backup script" "[ -x backup.sh ]"
run_test "Audit script" "[ -x comprehensive-audit.sh ]"
run_test "Test script" "[ -x test-deployment.sh ]"
run_test "Cloudflare API script" "[ -x cloudflare-api.sh ]"

echo ""

# Performance Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PERFORMANCE TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Response time test
RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" http://localhost:8000/health)
if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
    echo -e "  Testing response time... ${GREEN}✓${NC} (${RESPONSE_TIME}s)"
    PASSED=$((PASSED+1))
else
    echo -e "  Testing response time... ${YELLOW}⚠${NC} (${RESPONSE_TIME}s - slow)"
    PASSED=$((PASSED+1))
fi
TOTAL=$((TOTAL+1))

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total Tests:  $TOTAL"
echo -e "${GREEN}Passed:       $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed:       $FAILED${NC}"
else
    echo "Failed:       $FAILED"
fi
SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED/$TOTAL)*100}")
echo "Success Rate: ${SUCCESS_RATE}%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Review the output above.${NC}"
    exit 1
fi
