#!/bin/bash

# GIVC Platform - Cloudflare API Integration
# Purpose: Manage Cloudflare resources via API

set -e

# Load environment variables properly
if [ -f .env ]; then
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        # Export the variable
        export "$key=$value"
    done < <(grep -v '^#' .env | grep -v '^$')
fi

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

API_TOKEN="${CLOUDFLARE_API_TOKEN}"
ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID}"
TUNNEL_ID="${CLOUDFLARE_TUNNEL_ID}"

# Function to call Cloudflare API
cf_api() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "https://api.cloudflare.com/client/v4/${endpoint}" \
            -H "Authorization: Bearer ${API_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "https://api.cloudflare.com/client/v4/${endpoint}" \
            -H "Authorization: Bearer ${API_TOKEN}"
    fi
}

# Command dispatcher
case "${1:-help}" in
    verify)
        echo -e "${BLUE}🔐 Verifying Cloudflare API token...${NC}"
        response=$(cf_api "accounts/${ACCOUNT_ID}/tokens/verify")
        if echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if data.get('success') else 1)" 2>/dev/null; then
            echo -e "${GREEN}✅ Token is valid!${NC}"
            echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"  Status: {data.get('result', {}).get('status', 'unknown')}\")" 2>/dev/null || echo ""
        else
            echo -e "${RED}❌ Token validation failed${NC}"
            echo "$response"
        fi
        ;;
    
    zones)
        echo -e "${BLUE}🌐 Listing zones (domains)...${NC}"
        cf_api "zones" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  ✅ {z['name']} (ID: {z['id']})\") for z in data.get('result', [])]" 2>/dev/null || echo "No zones found"
        ;;
    
    tunnels)
        echo -e "${BLUE}🚇 Listing Cloudflare Tunnels...${NC}"
        cf_api "accounts/${ACCOUNT_ID}/cfd_tunnel" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  ✅ {t['name']} (ID: {t['id']})\") for t in data.get('result', [])]" 2>/dev/null || echo "No tunnels found"
        ;;
    
    tunnel-info)
        echo -e "${BLUE}📊 Getting tunnel information...${NC}"
        cf_api "accounts/${ACCOUNT_ID}/cfd_tunnel/${TUNNEL_ID}" | python3 -c "import sys, json; data=json.load(sys.stdin); result=data.get('result', {}); print(f\"  Name: {result.get('name')}\n  ID: {result.get('id')}\n  Created: {result.get('created_at')}\")" 2>/dev/null || echo "Unable to fetch tunnel info"
        ;;
    
    dns-records)
        if [ -z "$2" ]; then
            echo "Usage: $0 dns-records <zone_id>"
            exit 1
        fi
        echo -e "${BLUE}📋 Listing DNS records for zone $2...${NC}"
        cf_api "zones/$2/dns_records" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  {r['name']}: {r['type']} -> {r['content']}\") for r in data.get('result', [])]" 2>/dev/null || echo "No records found"
        ;;
    
    workers)
        echo -e "${BLUE}⚙️  Listing Workers scripts...${NC}"
        cf_api "accounts/${ACCOUNT_ID}/workers/scripts" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  ✅ {w['id']}\") for w in data.get('result', [])]" 2>/dev/null || echo "No workers found"
        ;;
    
    status)
        echo -e "${BLUE}📊 Platform Status Summary${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Account ID: ${ACCOUNT_ID}"
        echo "Tunnel ID:  ${TUNNEL_ID}"
        echo ""
        $0 verify
        echo ""
        $0 tunnels
        ;;
    
    help|*)
        cat << 'HELPEOF'
╔═══════════════════════════════════════════════════════════════╗
║         Cloudflare API Integration - GIVC Platform            ║
╚═══════════════════════════════════════════════════════════════╝

Usage: ./cloudflare-api.sh <command> [options]

Commands:
  verify           - Verify API token is valid
  status           - Show platform status summary
  zones            - List all zones (domains)
  tunnels          - List all Cloudflare Tunnels
  tunnel-info      - Get detailed tunnel information
  dns-records <id> - List DNS records for a zone
  workers          - List Cloudflare Workers scripts
  help             - Show this help message

Examples:
  ./cloudflare-api.sh verify
  ./cloudflare-api.sh status
  ./cloudflare-api.sh zones
  ./cloudflare-api.sh tunnels

Configuration:
  Credentials loaded from .env file:
    - CLOUDFLARE_API_TOKEN
    - CLOUDFLARE_ACCOUNT_ID
    - CLOUDFLARE_TUNNEL_ID

HELPEOF
        ;;
esac
