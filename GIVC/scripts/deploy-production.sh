#!/bin/bash

# GIVC Healthcare Platform - Production Deployment Script
# © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited

set -e

echo "🚀 GIVC Healthcare Platform - Production Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo -e "${RED}❌ Wrangler CLI not found. Please install it: npm install -g wrangler${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Wrangler CLI found${NC}"

# Check authentication
echo "📝 Checking Cloudflare authentication..."
if ! wrangler whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not authenticated. Running wrangler login...${NC}"
    wrangler login
fi

echo -e "${GREEN}✓ Authenticated${NC}"

# Step 1: Create D1 Database
echo ""
echo "📊 Step 1: Creating D1 Database..."
DB_OUTPUT=$(wrangler d1 create givc-healthcare-prod 2>&1 || true)
echo "$DB_OUTPUT"

if echo "$DB_OUTPUT" | grep -q "already exists"; then
    echo -e "${YELLOW}⚠️  Database already exists${NC}"
    DB_ID=$(wrangler d1 list | grep "givc-healthcare-prod" | awk '{print $2}' || echo "")
else
    DB_ID=$(echo "$DB_OUTPUT" | grep "database_id" | cut -d'"' -f2)
fi

if [ -z "$DB_ID" ]; then
    echo -e "${RED}❌ Failed to get database ID${NC}"
    echo "Please manually create the database and update wrangler.toml"
else
    echo -e "${GREEN}✓ Database ID: $DB_ID${NC}"
    
    # Update wrangler.toml with database ID
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/database_id = \"\"/database_id = \"$DB_ID\"/g" wrangler.toml
    else
        sed -i "s/database_id = \"\"/database_id = \"$DB_ID\"/g" wrangler.toml
    fi
    echo -e "${GREEN}✓ Updated wrangler.toml with database ID${NC}"
fi

# Step 2: Deploy Database Schema
echo ""
echo "📝 Step 2: Deploying Database Schema..."
if [ -f "workers/schema.sql" ]; then
    wrangler d1 execute givc-healthcare-prod --file=workers/schema.sql --remote
    echo -e "${GREEN}✓ Schema deployed successfully${NC}"
else
    echo -e "${RED}❌ schema.sql not found${NC}"
    exit 1
fi

# Step 3: Create KV Namespaces
echo ""
echo "🗄️  Step 3: Creating KV Namespaces..."

# Medical Metadata KV
KV_METADATA_OUTPUT=$(wrangler kv:namespace create "MEDICAL_METADATA" 2>&1 || true)
echo "$KV_METADATA_OUTPUT"
if echo "$KV_METADATA_OUTPUT" | grep -q "id"; then
    KV_METADATA_ID=$(echo "$KV_METADATA_OUTPUT" | grep "id" | cut -d'"' -f2)
    echo -e "${GREEN}✓ Medical Metadata KV ID: $KV_METADATA_ID${NC}"
    
    # Update wrangler.toml
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "0,/binding = \"MEDICAL_METADATA\"/{s/id = \"\"/id = \"$KV_METADATA_ID\"/;}" wrangler.toml
    else
        sed -i "0,/binding = \"MEDICAL_METADATA\"/{s/id = \"\"/id = \"$KV_METADATA_ID\"/;}" wrangler.toml
    fi
fi

# Audit Logs KV
KV_AUDIT_OUTPUT=$(wrangler kv:namespace create "AUDIT_LOGS" 2>&1 || true)
echo "$KV_AUDIT_OUTPUT"
if echo "$KV_AUDIT_OUTPUT" | grep -q "id"; then
    KV_AUDIT_ID=$(echo "$KV_AUDIT_OUTPUT" | grep "id" | cut -d'"' -f2)
    echo -e "${GREEN}✓ Audit Logs KV ID: $KV_AUDIT_ID${NC}"
    
    # Update wrangler.toml
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "0,/binding = \"AUDIT_LOGS\"/{s/id = \"\"/id = \"$KV_AUDIT_ID\"/;}" wrangler.toml
    else
        sed -i "0,/binding = \"AUDIT_LOGS\"/{s/id = \"\"/id = \"$KV_AUDIT_ID\"/;}" wrangler.toml
    fi
fi

# Step 4: Create R2 Bucket
echo ""
echo "📦 Step 4: Creating R2 Bucket..."
R2_OUTPUT=$(wrangler r2 bucket create givc-medical-files 2>&1 || true)
echo "$R2_OUTPUT"
if echo "$R2_OUTPUT" | grep -q "Created" || echo "$R2_OUTPUT" | grep -q "already exists"; then
    echo -e "${GREEN}✓ R2 bucket ready${NC}"
fi

# Step 5: Set Secrets
echo ""
echo "🔐 Step 5: Setting Secrets..."
echo -e "${YELLOW}You need to set the following secrets:${NC}"
echo "  1. JWT_SECRET - Secret key for JWT signing (min 32 characters)"
echo "  2. ENCRYPTION_KEY - Master encryption key (min 32 characters)"

read -p "Do you want to set secrets now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Enter JWT_SECRET (will be hidden):"
    read -s JWT_SECRET
    echo "$JWT_SECRET" | wrangler secret put JWT_SECRET
    
    echo "Enter ENCRYPTION_KEY (will be hidden):"
    read -s ENCRYPTION_KEY
    echo "$ENCRYPTION_KEY" | wrangler secret put ENCRYPTION_KEY
    
    echo -e "${GREEN}✓ Secrets set${NC}"
else
    echo -e "${YELLOW}⚠️  You can set secrets later using:${NC}"
    echo "  wrangler secret put JWT_SECRET"
    echo "  wrangler secret put ENCRYPTION_KEY"
fi

# Step 6: Deploy Workers
echo ""
echo "🚢 Step 6: Deploying Workers..."
wrangler deploy
echo -e "${GREEN}✓ Workers deployed${NC}"

# Step 7: Create Queue
echo ""
echo "📨 Step 7: Creating Queue..."
QUEUE_OUTPUT=$(wrangler queues create medical-processing-queue 2>&1 || true)
echo "$QUEUE_OUTPUT"
if echo "$QUEUE_OUTPUT" | grep -q "Created" || echo "$QUEUE_OUTPUT" | grep -q "already exists"; then
    echo -e "${GREEN}✓ Queue ready${NC}"
fi

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo "📋 Summary:"
echo "  ✓ D1 Database: givc-healthcare-prod"
echo "  ✓ KV Namespaces: MEDICAL_METADATA, AUDIT_LOGS"
echo "  ✓ R2 Bucket: givc-medical-files"
echo "  ✓ Queue: medical-processing-queue"
echo "  ✓ Workers: Deployed"
echo ""
echo "🔍 Next Steps:"
echo "  1. Verify deployment: wrangler tail"
echo "  2. Test API endpoints"
echo "  3. Configure DNS (if not already done)"
echo "  4. Set up monitoring"
echo ""
echo "🔗 Access your API at:"
echo "  https://givc.<your-subdomain>.workers.dev"
echo ""
echo "📖 Documentation:"
echo "  - DEPLOYMENT_GUIDE.md"
echo "  - QUICK_START.md"
echo ""
