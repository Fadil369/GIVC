# Microsoft Teams Integration - Quick Reference

## 🚀 Quick Start

### 1. Run Database Migration
```bash
cd /path/to/ClaimLinc-GIVC
alembic upgrade head
```

### 2. Configure Environment
```bash
# Copy example and edit
cp .env.example .env

# Generate HMAC secret
openssl rand -hex 32

# Update .env with:
# - TEAMS_HMAC_SECRET_KEY=<generated-secret>
# - TEAMS_WEBHOOK_* URLs from Teams channels
```

### 3. Run Tests
```bash
# All tests
pytest integrations/teams/tests/ -v

# With coverage
pytest integrations/teams/tests/ -v --cov=integrations.teams --cov-report=html

# View coverage report
open htmlcov/index.html
```

### 4. Restart Workers
```bash
systemctl restart celery-worker
# or
supervisorctl restart celery-worker:*
```

---

## 📋 Teams Channel Setup

### Create 8 Teams Channels:

1. **Security Engineering** → #security-alerts
2. **CloudOps** → #cloudops-alerts  
3. **Runtime Engineering** → #runtime-alerts
4. **DevOps** → #devops-alerts
5. **SRE** → #sre-alerts
6. **Compliance** → #compliance-notifications
7. **NPHIES Integration** → #nphies-integration
8. **PMO** → #pmo-updates

### Add Workflow to Each Channel:

1. Click **...** (More options) → **Workflows**
2. Search "When a Teams webhook request is received"
3. Click **Add workflow**
4. Copy webhook URL
5. Store in Vault: `vault kv put secret/teams/webhooks <stakeholder>="<url>"`

---

## 🔍 Testing Commands

### Test NPHIES Claim Submission
```python
from workers.tasks.nphies_tasks import submit_nphies_claim

claim_data = {
    "claim_id": "CLM-TEST-001",
    "patient_id": "PAT-12345",
    "provider_name": "Al Hayat Hospital - Riyadh",
    "total_amount": 5000.00,
    "services": [
        {"description": "Consultation", "amount": 200.00},
        {"description": "X-Ray", "amount": 500.00}
    ]
}

result = submit_nphies_claim.delay(
    claim_data=claim_data,
    payer_code="7001071327",  # TAWUNIYA
    correlation_id="test-correlation-id"
)

print(result.get())
```

### Query Audit Logs
```sql
-- Recent notifications
SELECT correlation_id, event_type, priority, status_code, sent_at
FROM teams_notifications
ORDER BY sent_at DESC
LIMIT 10;

-- Unacknowledged critical
SELECT * FROM teams_notifications_unacknowledged_critical;

-- Delivery failures
SELECT event_type, COUNT(*) AS failures
FROM teams_notifications
WHERE status_code >= 400
GROUP BY event_type;
```

---

## 🔧 Troubleshooting

### Notifications Not Arriving

**Check 1: Webhook URL in Vault**
```bash
vault kv get secret/teams/webhooks
```

**Check 2: Worker Logs**
```bash
tail -f /var/log/celery/worker.log | grep -i teams
```

**Check 3: Audit Table**
```sql
SELECT * FROM teams_notifications 
WHERE sent_at > NOW() - INTERVAL '1 hour'
ORDER BY sent_at DESC;
```

### Rate Limiting (429 Errors)

**Check Retry Count:**
```sql
SELECT correlation_id, retry_count, status_code, error_message
FROM teams_notifications
WHERE status_code = 429
ORDER BY sent_at DESC;
```

**Adjust Rate Limit:**
```bash
# In .env
TEAMS_RATE_LIMIT_REQUESTS=30  # Lower from 60
TEAMS_RATE_LIMIT_PERIOD=60
```

### HMAC Signature Failures

**Regenerate Secret:**
```bash
openssl rand -hex 32
```

**Update Vault:**
```bash
vault kv patch secret/teams/config hmac_secret="<new-secret>"
```

---

## 📊 Monitoring Queries

### Notification Volume by Event Type (Last 24h)
```sql
SELECT 
    event_type,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status_code BETWEEN 200 AND 299) AS successful,
    COUNT(*) FILTER (WHERE status_code >= 400) AS failed,
    AVG(retry_count) AS avg_retries
FROM teams_notifications
WHERE sent_at > NOW() - INTERVAL '24 hours'
GROUP BY event_type
ORDER BY total DESC;
```

### Average Acknowledgment Time
```sql
SELECT 
    priority,
    COUNT(*) AS total_acknowledged,
    AVG(EXTRACT(EPOCH FROM (acknowledged_at - sent_at))/60) AS avg_ack_minutes,
    MAX(EXTRACT(EPOCH FROM (acknowledged_at - sent_at))/60) AS max_ack_minutes
FROM teams_notifications
WHERE acknowledged_at IS NOT NULL
GROUP BY priority
ORDER BY CASE priority
    WHEN 'CRITICAL' THEN 1
    WHEN 'HIGH' THEN 2
    WHEN 'MEDIUM' THEN 3
    WHEN 'LOW' THEN 4
END;
```

### Top 10 Unacknowledged Notifications
```sql
SELECT 
    correlation_id,
    event_type,
    priority,
    stakeholders,
    sent_at,
    EXTRACT(EPOCH FROM (NOW() - sent_at))/3600 AS age_hours
FROM teams_notifications
WHERE acknowledged_at IS NULL
    AND priority IN ('CRITICAL', 'HIGH')
    AND status_code BETWEEN 200 AND 299
ORDER BY sent_at ASC
LIMIT 10;
```

---

## 📝 Event Type Reference

| Event Type | Priority | Stakeholders |
|------------|----------|--------------|
| `vault.seal.detected` | CRITICAL | Security, SRE |
| `vault.certificate.expiring` | HIGH | Security, NPHIES Integration |
| `celery.task.failure` | HIGH | Runtime, SRE |
| `celery.task.dlq` | CRITICAL | Runtime, DevOps |
| `nphies.claim.submitted` | INFO | NPHIES Integration, PMO, Compliance |
| `nphies.claim.approved` | INFO | NPHIES Integration, PMO |
| `nphies.claim.rejected` | HIGH | NPHIES Integration, Compliance |
| `nphies.api.error` | HIGH/CRITICAL | NPHIES Integration, SRE |
| `system.rabbitmq.node_down` | CRITICAL | SRE, CloudOps |
| `system.postgres.replication_lag` | MEDIUM | SRE, DevOps |

---

## 🔐 Security Checklist

- [x] HMAC-SHA256 signing on all webhooks
- [x] Webhook URLs stored in Vault (not .env)
- [x] TLS 1.3 for all HTTP requests
- [x] Constant-time signature comparison
- [x] Rate limiting (60 req/min default)
- [x] Audit logging with 90-day retention
- [x] No sensitive data in card payloads
- [x] Correlation IDs for tracing

---

## 📚 Documentation Links

- [Architecture](./TEAMS_INTEGRATION_ARCHITECTURE.md)
- [Templates Guide](../integrations/teams/templates/README.md)
- [API Reference](../integrations/teams/README.md)
- [Deployment Guide](./TEAMS_DEPLOYMENT_GUIDE.md)
- [Runbooks](../../docs/runbooks/)

---

## 🆘 Support

**Issues?** Check:
1. Worker logs: `/var/log/celery/worker.log`
2. Audit table: `teams_notifications`
3. Redis pub/sub: `redis-cli PSUBSCRIBE 'teams:events:*'`
4. Vault connectivity: `vault status`

**Still stuck?** Create issue with:
- Correlation ID
- Event type
- Error message from `teams_notifications` table
- Worker log excerpt
