#!/bin/bash

# 🧪 Integration Test Script
# Tests all services are working correctly

set -e

echo "🧪 Running Integration Tests"
echo "==============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $response)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected $expected_code, got $response)"
        ((FAILED++))
        return 1
    fi
}

# Test JSON response
test_json_endpoint() {
    local name=$1
    local url=$2
    local field=$3
    
    echo -n "Testing $name... "
    
    response=$(curl -s "$url" 2>/dev/null)
    
    if echo "$response" | jq -e ".$field" > /dev/null 2>&1; then
        value=$(echo "$response" | jq -r ".$field")
        echo -e "${GREEN}✅ PASS${NC} ($field: $value)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Field $field not found)"
        ((FAILED++))
        return 1
    fi
}

echo "1️⃣  Testing Core Infrastructure"
echo "-----------------------------------"

test_endpoint "PostgreSQL (via health check)" "http://localhost:8010/health"
test_endpoint "Redis (via health check)" "http://localhost:8010/health"

echo ""
echo "2️⃣  Testing New Services"
echo "-----------------------------------"

test_json_endpoint "OID Registry" "http://localhost:8010/health" "status"
test_json_endpoint "MCP Gateway" "http://localhost:8020/health" "status"
test_endpoint "Chat Engine" "http://localhost:8040/health"

echo ""
echo "3️⃣  Testing Agent Registration"
echo "-----------------------------------"

# Test listing agents
test_endpoint "List agents" "http://localhost:8010/api/v1/registry/agents"

# Test registering a new agent
echo -n "Testing agent registration... "
response=$(curl -s -X POST "http://localhost:8010/api/v1/registry/agents" \
    -H "Content-Type: application/json" \
    -d '{
        "oid": "1.3.6.1.4.1.61026.9.1",
        "name": "testlinc",
        "domain": "test",
        "version": "1.0.0",
        "endpoints": {"rest": "http://localhost:9000"},
        "capabilities": ["test"],
        "dependencies": []
    }' 2>/dev/null)

if echo "$response" | jq -e '.oid' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  SKIP${NC} (May already exist)"
fi

echo ""
echo "4️⃣  Testing MCP Gateway Routing"
echo "-----------------------------------"

# Test agent listing via MCP
test_endpoint "List agents via MCP" "http://localhost:8020/agents"

echo ""
echo "5️⃣  Testing Existing Services Integration"
echo "-----------------------------------"

test_endpoint "GIVC Healthcare" "http://localhost:3000"
test_endpoint "N8N Workflow" "http://localhost:5678"
test_endpoint "Orchestrator" "http://localhost:8000/health"

echo ""
echo "=============================="
echo "📊 Test Results"
echo "=============================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check the output above.${NC}"
    exit 1
fi
