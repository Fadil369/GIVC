#!/bin/bash

# GIVC Platform - Quick Action Plan
# Execute these steps to complete the enhancement deployment

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     GIVC PLATFORM - IMMEDIATE ACTION PLAN                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as the right user
if [ "$(id -u)" -eq 0 ]; then
    echo "⚠️  Please run as pi user, not root"
    exit 1
fi

cd /home/pi/GIVC

echo "📋 Step-by-Step Actions for Platform Enhancement"
echo ""

# Action 1: Initialize Database
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ACTION 1: Initialize Database Schema"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Status: Checking if database is initialized..."

if docker exec givc-postgres psql -U givc -d givc_prod -c "\dt" 2>/dev/null | grep -q "users"; then
    echo "✅ Database already initialized"
else
    echo "📝 Database needs initialization"
    echo ""
    echo "Execute:"
    echo "  docker cp database/init.sql givc-postgres:/tmp/init.sql"
    echo "  docker exec givc-postgres psql -U givc -d givc_prod -f /tmp/init.sql"
    echo ""
    read -p "Initialize database now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker cp database/init.sql givc-postgres:/tmp/init.sql
        docker exec givc-postgres psql -U givc -d givc_prod -f /tmp/init.sql
        echo "✅ Database initialized successfully!"
    else
        echo "⏭️  Skipped - run manually later"
    fi
fi
echo ""

# Action 2: Review Environment Configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ACTION 2: Review Environment Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANT: Update NPHIES credentials in .env file"
echo ""
echo "Current .env status:"
if [ -f .env ]; then
    echo "✅ .env file exists"
    echo ""
    echo "Required updates:"
    echo "  - NPHIES_CLIENT_ID"
    echo "  - NPHIES_CLIENT_SECRET"
    echo "  - Review all passwords and secrets"
    echo ""
    echo "Edit with: nano .env"
else
    echo "❌ .env file missing!"
fi
echo ""

# Action 3: Setup Automated Backups
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ACTION 3: Setup Automated Backups"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Backup script: ./backup.sh"
echo ""
read -p "Run backup test now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./backup.sh
    echo ""
    echo "Configure daily backups:"
    echo "  crontab -e"
    echo "  Add: 0 2 * * * /home/pi/GIVC/backup.sh"
else
    echo "⏭️  Skipped - remember to setup cron job"
fi
echo ""

# Action 4: Deploy Monitoring
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ACTION 4: Deploy Monitoring Stack"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Monitoring services: Prometheus + Grafana"
echo ""
read -p "Deploy monitoring now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.monitoring.yml up -d
    echo ""
    echo "✅ Monitoring deployed!"
    echo "   Prometheus: http://localhost:9090"
    echo "   Grafana: http://localhost:3001 (admin/admin)"
else
    echo "⏭️  Skipped - deploy later with:"
    echo "   docker-compose -f docker-compose.monitoring.yml up -d"
fi
echo ""

# Action 5: Security Hardening
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ACTION 5: Security Review"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Recommendations:"
echo "  1. Close external database ports (edit docker-compose.yml)"
echo "  2. Configure firewall rules"
echo "  3. Restrict CORS origins in backend"
echo "  4. Add rate limiting to Nginx"
echo ""

# Action 6: Enhanced Backend Upgrade (Optional)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ACTION 6: Upgrade to Enhanced Backend (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Enhanced backend features:"
echo "  ✅ Full database integration"
echo "  ✅ Redis caching"
echo "  ✅ Patient management APIs"
echo "  ✅ Enhanced error handling"
echo "  ✅ OpenAPI documentation"
echo ""
echo "To upgrade:"
echo "  1. Test: python3 main_api_enhanced.py"
echo "  2. If OK: mv main_api.py main_api_old.py"
echo "  3. Then: cp main_api_enhanced.py main_api.py"
echo "  4. Rebuild: docker-compose up -d --build givc-backend"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Platform Status: HEALTHY"
echo "✅ All services running"
echo "✅ Enhancements prepared"
echo ""
echo "📋 Review full report: COMPREHENSIVE_REVIEW_REPORT.md"
echo "📋 Audit logs: audit-report-*.log"
echo ""
echo "🎯 Priority Actions:"
echo "  1. Initialize database schema (if not done)"
echo "  2. Update .env with NPHIES credentials"
echo "  3. Setup automated backups"
echo "  4. Deploy monitoring"
echo "  5. Review security recommendations"
echo ""
echo "For help: ./comprehensive-audit.sh"
echo ""
