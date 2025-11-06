#!/bin/bash

# GIVC Platform - Cloudflare Workers Deployment
# Purpose: Deploy and manage Workers scripts

set -e

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

API_TOKEN="${CLOUDFLARE_API_TOKEN}"
ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID}"

deploy_worker() {
    local worker_name="$1"
    local script_path="$2"
    
    if [ ! -f "$script_path" ]; then
        echo "❌ Script not found: $script_path"
        exit 1
    fi
    
    echo "🚀 Deploying worker: $worker_name"
    
    curl -s -X PUT \
        "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/workers/scripts/${worker_name}" \
        -H "Authorization: Bearer ${API_TOKEN}" \
        -H "Content-Type: application/javascript" \
        --data-binary "@${script_path}" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"
}

list_workers() {
    echo "📋 Listing Workers..."
    curl -s "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/workers/scripts" \
        -H "Authorization: Bearer ${API_TOKEN}" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  - {w['id']}\") for w in data.get('result', [])]"
}

case "${1:-help}" in
    deploy)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: $0 deploy <worker-name> <script-path>"
            exit 1
        fi
        deploy_worker "$2" "$3"
        ;;
    
    list)
        list_workers
        ;;
    
    *)
        cat << 'HELPEOF'
Cloudflare Workers Deployment Script

Usage: ./workers-deploy.sh <command> [options]

Commands:
  deploy <name> <path> - Deploy a Worker script
  list                 - List all Workers scripts

Examples:
  ./workers-deploy.sh deploy my-worker ./workers/api/index.js
  ./workers-deploy.sh list

HELPEOF
        ;;
esac
