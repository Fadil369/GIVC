# Microsoft Teams Integration - Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Environment Setup

- [ ] **Install Python Dependencies**
  ```powershell
  pip install celery[redis] asyncio aiohttp jinja2 pydantic psycopg2-binary redis alembic
  ```

- [ ] **Generate HMAC Secret Key**
  ```powershell
  openssl rand -hex 32
  # Save output for next step
  ```

- [ ] **Create `.env` File**
  ```powershell
  cp .env.example .env
  # Edit .env and set TEAMS_HMAC_SECRET_KEY
  ```

### 2. Vault Configuration

- [ ] **Store HMAC Secret in Vault**
  ```bash
  vault kv put secret/teams/config hmac_secret="<generated-secret>"
  ```

- [ ] **Prepare for Webhook URLs**
  ```bash
  # Create path (URLs will be added after Teams setup)
  vault kv put secret/teams/webhooks \
    security_eng="placeholder" \
    cloudops="placeholder" \
    runtime_eng="placeholder" \
    devops="placeholder" \
    sre="placeholder" \
    compliance="placeholder" \
    nphies_integration="placeholder" \
    pmo="placeholder"
  ```

### 3. Microsoft Teams Setup

- [ ] **Create 8 Teams Channels**
  - #security-alerts (Security Engineering)
  - #cloudops-alerts (CloudOps)
  - #runtime-alerts (Runtime Engineering)
  - #devops-alerts (DevOps)
  - #sre-alerts (SRE)
  - #compliance-notifications (Compliance Office)
  - #nphies-integration (NPHIES Integration)
  - #pmo-updates (PMO)

- [ ] **Add Workflows to Each Channel**
  1. Click **...** (More options) → **Workflows**
  2. Search "When a Teams webhook request is received"
  3. Click **Add workflow**
  4. Copy webhook URL
  5. Save to text file for batch Vault update

- [ ] **Update Vault with Real Webhook URLs**
  ```bash
  vault kv put secret/teams/webhooks \
    security_eng="https://prod-123.westus.logic.azure.com:443/workflows/..." \
    cloudops="https://prod-456.westus.logic.azure.com:443/workflows/..." \
    runtime_eng="https://prod-789.westus.logic.azure.com:443/workflows/..." \
    devops="https://prod-101.westus.logic.azure.com:443/workflows/..." \
    sre="https://prod-102.westus.logic.azure.com:443/workflows/..." \
    compliance="https://prod-103.westus.logic.azure.com:443/workflows/..." \
    nphies_integration="https://prod-104.westus.logic.azure.com:443/workflows/..." \
    pmo="https://prod-105.westus.logic.azure.com:443/workflows/..."
  ```

### 4. Database Migration

- [ ] **Backup Database**
  ```powershell
  pg_dump -U postgres brainsait_nphies > backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql
  ```

- [ ] **Run Migration**
  ```powershell
  cd c:\Users\rcmrejection3\OneDrive\Desktop\ClaimLinc-GIVC
  alembic upgrade head
  ```

- [ ] **Verify Migration**
  ```sql
  -- Check table exists
  \d teams_notifications
  
  -- Check indexes
  \di teams_notifications*
  
  -- Check view
  SELECT * FROM teams_notifications_unacknowledged_critical LIMIT 10;
  
  -- Check trigger
  SELECT tgname, tgtype FROM pg_trigger WHERE tgrelid = 'teams_notifications'::regclass;
  ```

### 5. Testing

- [ ] **Run Unit Tests**
  ```powershell
  pytest integrations/teams/tests/ -v --cov=integrations.teams --cov-report=html
  ```

- [ ] **Verify 38 Tests Pass**
  - Expected: 38 passed
  - Target coverage: >85%

- [ ] **Review Coverage Report**
  ```powershell
  start htmlcov/index.html
  ```

---

## 🚀 Deployment Steps

### 1. Code Deployment

- [ ] **Git Commit Changes**
  ```powershell
  git add workers/tasks/nphies_tasks.py
  git add database/migrations/versions/20251106_add_teams_notifications.py
  git add integrations/teams/
  git add .env.example
  git add docs/integration/
  
  git commit -m "feat: Complete Microsoft Teams integration

- Add 5 Teams notification points in nphies_tasks.py
- Create teams_notifications table with audit logging
- Add 38 unit test cases (templates, webhook, events, security)
- Configure 47 environment variables
- Total: 2,400+ lines across 9 files"
  ```

- [ ] **Push to Repository**
  ```powershell
  git push origin main
  ```

- [ ] **Deploy to Production**
  ```powershell
  # Example: SSH to server and pull latest
  ssh user@prod-server
  cd /opt/claimlinc-givc
  git pull origin main
  ```

### 2. Worker Restart

- [ ] **Restart Celery Workers**
  ```bash
  # SystemD
  systemctl restart celery-worker
  
  # Supervisor
  supervisorctl restart celery-worker:*
  
  # Manual
  pkill -f celery
  celery -A workers.celery_app worker --loglevel=info --concurrency=4
  ```

- [ ] **Verify Workers Started**
  ```bash
  # Check logs
  tail -f /var/log/celery/worker.log
  
  # Check Flower (if available)
  curl http://localhost:5555/api/workers
  ```

### 3. Redis & PostgreSQL

- [ ] **Verify Redis Connection**
  ```bash
  redis-cli ping
  # Expected: PONG
  
  redis-cli PSUBSCRIBE 'teams:events:*'
  # Keep open for monitoring
  ```

- [ ] **Verify PostgreSQL Connection**
  ```sql
  SELECT current_database(), current_user;
  # Expected: brainsait_nphies | celery_user
  ```

---

## ✓ Post-Deployment Verification

### 1. End-to-End Test

- [ ] **Trigger Test NPHIES Claim**
  ```python
  from workers.tasks.nphies_tasks import submit_nphies_claim
  
  result = submit_nphies_claim.delay(
      claim_data={
          "claim_id": "CLM-TEST-001",
          "patient_id": "PAT-12345",
          "provider_name": "Test Hospital",
          "total_amount": 1000.00,
          "services": [{"description": "Test Service", "amount": 1000.00}]
      },
      payer_code="7001071327",
      correlation_id="test-deploy-verification"
  )
  
  print(result.get(timeout=60))
  ```

- [ ] **Check Teams Channel**
  - Go to #nphies-integration channel
  - Verify Adaptive Card received
  - Check card displays claim details correctly

- [ ] **Check Audit Table**
  ```sql
  SELECT 
      correlation_id, 
      event_type, 
      priority, 
      status_code, 
      sent_at
  FROM teams_notifications
  WHERE correlation_id = 'test-deploy-verification';
  ```

- [ ] **Test Action Buttons** (Manual)
  - Click "Acknowledge" button
  - Verify modal appears
  - Submit acknowledgment
  - Check audit table updated:
    ```sql
    SELECT acknowledged_by, acknowledged_at, action_taken
    FROM teams_notifications
    WHERE correlation_id = 'test-deploy-verification';
    ```

### 2. Monitoring Setup

- [ ] **Configure Prometheus Metrics** (Optional)
  - Add metrics to webhook_sender.py
  - Deploy updated code
  - Verify metrics endpoint: `curl http://localhost:8000/metrics`

- [ ] **Import Grafana Dashboard** (Optional)
  - Create dashboard JSON
  - Import to Grafana
  - Configure data source

- [ ] **Configure Alertmanager Rules** (Optional)
  - Create alerting rules YAML
  - Deploy to Alertmanager
  - Test with synthetic failure

### 3. Operational Checks

- [ ] **Query Recent Notifications**
  ```sql
  SELECT 
      event_type,
      COUNT(*) AS total,
      COUNT(*) FILTER (WHERE status_code BETWEEN 200 AND 299) AS successful,
      COUNT(*) FILTER (WHERE status_code >= 400) AS failed
  FROM teams_notifications
  WHERE sent_at > NOW() - INTERVAL '1 hour'
  GROUP BY event_type;
  ```

- [ ] **Check Unacknowledged Critical**
  ```sql
  SELECT * FROM teams_notifications_unacknowledged_critical;
  ```

- [ ] **Monitor Worker Logs**
  ```bash
  tail -f /var/log/celery/worker.log | grep -i teams
  # Should see "Teams notification sent successfully" messages
  ```

---

## 🔧 Troubleshooting

### Issue: Notifications Not Arriving

**Diagnostics:**
```bash
# 1. Check Vault connection
vault status

# 2. Check webhook URLs in Vault
vault kv get secret/teams/webhooks

# 3. Check worker logs
tail -f /var/log/celery/worker.log | grep -E "(teams|Teams)"

# 4. Query audit table
psql -d brainsait_nphies -c "SELECT * FROM teams_notifications ORDER BY sent_at DESC LIMIT 10"
```

**Solutions:**
- Verify TEAMS_WEBHOOK_VAULT_PATH in .env matches Vault path
- Verify webhook URLs are not placeholders
- Check network connectivity to Teams (test with curl)
- Verify HMAC secret is correct

### Issue: Rate Limiting (429 Errors)

**Diagnostics:**
```sql
SELECT correlation_id, retry_count, status_code, error_message
FROM teams_notifications
WHERE status_code = 429
ORDER BY sent_at DESC
LIMIT 10;
```

**Solutions:**
- Lower TEAMS_RATE_LIMIT_REQUESTS in .env (default: 60)
- Increase TEAMS_RATE_LIMIT_PERIOD (default: 60 seconds)
- Implement notification batching for burst events

### Issue: HMAC Signature Failures

**Diagnostics:**
```bash
# Check if secret is set
vault kv get secret/teams/config

# Test signature generation
python -c "
import hmac
import hashlib
secret = 'your-secret-here'
payload = '{\"test\": \"data\"}'
sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
print(sig)
"
```

**Solutions:**
- Regenerate HMAC secret: `openssl rand -hex 32`
- Update Vault: `vault kv patch secret/teams/config hmac_secret="<new-secret>"`
- Update .env: `TEAMS_HMAC_SECRET_KEY=<new-secret>`
- Restart workers

### Issue: Database Migration Failed

**Diagnostics:**
```powershell
# Check current revision
alembic current

# Check migration history
alembic history

# Check PostgreSQL logs
docker logs postgres_container
```

**Solutions:**
- Restore backup: `psql -U postgres brainsait_nphies < backup_YYYYMMDD_HHMMSS.sql`
- Fix migration script errors
- Run migration again: `alembic upgrade head`

---

## 📊 Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Notification Delivery Rate | >99% | `SELECT (COUNT(*) FILTER (WHERE status_code < 400)::float / COUNT(*))*100 FROM teams_notifications WHERE sent_at > NOW() - INTERVAL '24 hours'` |
| Average Acknowledgment Time (Critical) | <5 min | `SELECT AVG(EXTRACT(EPOCH FROM (acknowledged_at - sent_at))/60) FROM teams_notifications WHERE priority = 'CRITICAL' AND acknowledged_at IS NOT NULL` |
| Test Coverage | >85% | `pytest --cov=integrations.teams --cov-report=term` |
| P95 Webhook Latency | <2 sec | Prometheus histogram: `teams_notification_send_duration_seconds` |
| Unacknowledged Critical Alerts | <10 | `SELECT COUNT(*) FROM teams_notifications_unacknowledged_critical` |

---

## 📚 Reference Documentation

- [Architecture](./TEAMS_INTEGRATION_ARCHITECTURE.md) - 68-page design document
- [Implementation Guide](./TEAMS_IMPLEMENTATION_COMPLETE.md) - Task-by-task breakdown
- [Quick Reference](./TEAMS_QUICK_REFERENCE.md) - Commands, queries, troubleshooting
- [Templates Guide](../../integrations/teams/templates/README.md) - Adaptive Card schemas
- [API Reference](../../integrations/teams/README.md) - Module documentation

---

## 🆘 Rollback Plan

If critical issues arise after deployment:

1. **Stop Workers**
   ```bash
   systemctl stop celery-worker
   ```

2. **Revert Code**
   ```powershell
   git revert HEAD
   git push origin main
   ```

3. **Revert Database Migration**
   ```powershell
   alembic downgrade -1
   ```

4. **Restore Backup** (if needed)
   ```powershell
   psql -U postgres brainsait_nphies < backup_YYYYMMDD_HHMMSS.sql
   ```

5. **Restart Workers**
   ```bash
   systemctl start celery-worker
   ```

---

## 📝 Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | __________ | ______ | __________ |
| DevOps Lead | __________ | ______ | __________ |
| Security Review | __________ | ______ | __________ |
| QA Lead | __________ | ______ | __________ |
| Product Owner | __________ | ______ | __________ |

---

**Last Updated**: 2024-01-06  
**Version**: 1.0.0  
**Status**: Ready for Production Deployment
