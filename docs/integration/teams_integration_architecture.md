# Microsoft Teams Integration Architecture for ClaimLinc-GIVC

**Version:** 1.0  
**Date:** 2025-01-XX  
**Owner:** Integration Team, DevOps, PMO  
**Status:** Design Phase

---

## 1. Executive Summary

This document specifies the Microsoft Teams integration architecture for ClaimLinc-GIVC to unify all stakeholders (Security Engineering, CloudOps, Runtime Engineering, DevOps, SRE, Compliance Office, Integration Team, PMO) in a centralized, real-time collaboration workspace.

### Key Objectives
- **Unified Collaboration**: Single Teams workspace for all stakeholders
- **Real-Time Notifications**: Vault events, Celery task status, NPHIES transactions, system alerts
- **Interactive Cards**: Adaptive Cards with Action.Execute for acknowledgment, escalation, remediation
- **Audit Compliance**: All notifications logged with correlation IDs for HIPAA/PDPL compliance
- **Secure Integration**: HMAC signature verification, TLS 1.3, Vault-managed secrets

---

## 2. Architecture Overview

### 2.1 Integration Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                   ClaimLinc-GIVC Platform                       │
├─────────────┬──────────────┬──────────────┬──────────────────┐
│ Vault       │ Celery Tasks │ NPHIES Client│ FastAPI Endpoints│
│ Events      │ (Workers)    │ (Sim/Real)   │ (Auth, Pipeline) │
└─────┬───────┴──────┬───────┴──────┬───────┴──────────────┬─────┘
      │              │              │                      │
      │              ▼              ▼                      │
      │     ┌─────────────────────────────┐               │
      │     │  Teams Event Aggregator     │               │
      │     │  (integrations/teams/)      │               │
      │     │  - Event normalization      │               │
      │     │  - Correlation ID tracking  │               │
      │     │  - Audit logging            │               │
      │     └──────────────┬──────────────┘               │
      │                    │                              │
      │                    ▼                              │
      │     ┌─────────────────────────────┐               │
      │     │  Adaptive Card Builder      │               │
      │     │  - Template engine          │               │
      │     │  - Action.Execute patterns  │               │
      │     │  - User-specific views      │               │
      │     └──────────────┬──────────────┘               │
      │                    │                              │
      │                    ▼                              │
      │     ┌─────────────────────────────┐               │
      │     │  Teams Webhook Sender       │               │
      │     │  - HMAC signing             │               │
      │     │  - Retry with exponential   │               │
      │     │    backoff                  │               │
      │     │  - Rate limiting            │               │
      │     └──────────────┬──────────────┘               │
      │                    │                              │
      │                    ▼                              │
┌─────┴────────────────────────────────────────────────────────┐
│               Microsoft Teams (via Workflows App)            │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Security Eng.│  │   CloudOps   │  │ Runtime Eng. │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   DevOps     │  │     SRE      │  │  Compliance  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ Integration  │  │     PMO      │                         │
│  │    Team      │  │              │                         │
│  └──────────────┘  └──────────────┘                         │
└────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Incoming Webhooks** | Teams Workflows App | Receive notifications from ClaimLinc-GIVC |
| **Adaptive Cards** | Adaptive Cards 1.5 | Rich interactive UI with Action.Execute |
| **Power Automate** | Custom Connector | Bi-directional integration (future) |
| **Webhook Security** | HMAC-SHA256 | Signature verification for outgoing webhooks |
| **Event Bus** | Redis Pub/Sub | Real-time event distribution |
| **Card Storage** | PostgreSQL | Card history and audit trail |
| **Secret Management** | HashiCorp Vault | Webhook URLs, signing keys |

---

## 3. Event Types and Stakeholder Mapping

### 3.1 Vault Security Events

| Event | Stakeholders | Priority | Example |
|-------|-------------|----------|---------|
| `vault.seal.detected` | Security Eng., SRE, CloudOps | **CRITICAL** | Vault node sealed unexpectedly |
| `vault.unseal.failed` | Security Eng., SRE | **HIGH** | Unseal operation failed after 3 attempts |
| `vault.audit.disabled` | Security Eng., Compliance | **CRITICAL** | Audit logging disabled on node |
| `vault.token.renewal.failed` | Runtime Eng., DevOps | **MEDIUM** | AppRole token renewal failed |
| `vault.secret.rotation.complete` | Security Eng., DevOps | **INFO** | Credentials rotated successfully |
| `vault.certificate.expiring` | Security Eng., Integration Team | **HIGH** | NPHIES mTLS cert expires in 7 days |

### 3.2 Celery Task Events

| Event | Stakeholders | Priority | Example |
|-------|-------------|----------|---------|
| `celery.task.failed` | Runtime Eng., DevOps, SRE | **HIGH** | NPHIES eligibility check failed after 5 retries |
| `celery.task.retry` | Runtime Eng., DevOps | **MEDIUM** | Task retry attempt 3/5 |
| `celery.task.timeout` | Runtime Eng., SRE | **HIGH** | Task exceeded 60s timeout |
| `celery.dlq.threshold` | Runtime Eng., DevOps, PMO | **HIGH** | DLQ contains >100 failed tasks |
| `celery.worker.offline` | Runtime Eng., SRE, CloudOps | **CRITICAL** | Worker node unresponsive |
| `celery.queue.backlog` | Runtime Eng., SRE, PMO | **MEDIUM** | Eligibility queue depth >500 |

### 3.3 NPHIES Integration Events

| Event | Stakeholders | Priority | Example |
|-------|-------------|----------|---------|
| `nphies.eligibility.success` | Integration Team, PMO | **INFO** | Eligibility verified for patient |
| `nphies.eligibility.denied` | Integration Team, Compliance | **MEDIUM** | Patient ineligible, notify provider |
| `nphies.claim.submitted` | Integration Team, PMO | **INFO** | Claim submitted, poll ID: 12345 |
| `nphies.claim.approved` | Integration Team, PMO | **INFO** | Claim approved, amount: 15000 SAR |
| `nphies.claim.rejected` | Integration Team, Compliance | **HIGH** | Claim rejected, reason: invalid ICD-10 |
| `nphies.api.error` | Integration Team, DevOps, SRE | **CRITICAL** | NPHIES API 503 error, circuit open |
| `nphies.certificate.invalid` | Security Eng., Integration Team | **CRITICAL** | mTLS certificate validation failed |
| `nphies.jwt.expired` | Security Eng., Integration Team | **HIGH** | JWT token expired, renewal failed |

### 3.4 System & Infrastructure Events

| Event | Stakeholders | Priority | Example |
|-------|-------------|----------|---------|
| `rabbitmq.node.down` | Runtime Eng., SRE, CloudOps | **CRITICAL** | RabbitMQ node 2 unreachable |
| `redis.replica.lagging` | Runtime Eng., SRE, CloudOps | **MEDIUM** | Redis replica 30s behind primary |
| `postgres.connection.exhausted` | Runtime Eng., SRE, CloudOps | **CRITICAL** | Connection pool at 100% capacity |
| `kubernetes.pod.crashloop` | DevOps, SRE, CloudOps | **CRITICAL** | FastAPI pod restarting continuously |
| `prometheus.alert.firing` | SRE, DevOps, CloudOps | **HIGH** | High memory usage on worker nodes |
| `backup.failed` | SRE, Compliance, PMO | **HIGH** | Nightly backup failed |

---

## 4. Adaptive Card Templates

### 4.1 Vault Security Event Card

**Use Case:** Notify Security Eng. of Vault seal event

```json
{
  "type": "AdaptiveCard",
  "version": "1.5",
  "body": [
    {
      "type": "Container",
      "style": "emphasis",
      "items": [
        {
          "type": "ColumnSet",
          "columns": [
            {
              "type": "Column",
              "width": "auto",
              "items": [
                {
                  "type": "Image",
                  "url": "https://cdn.example.com/icons/vault-critical.png",
                  "size": "medium",
                  "style": "person"
                }
              ]
            },
            {
              "type": "Column",
              "width": "stretch",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "🔒 Vault Node Sealed",
                  "weight": "bolder",
                  "size": "large",
                  "color": "attention"
                },
                {
                  "type": "TextBlock",
                  "text": "vault-node-2.prod.svc.cluster.local",
                  "isSubtle": true,
                  "spacing": "none"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "title": "Priority:",
          "value": "🔴 CRITICAL"
        },
        {
          "title": "Event Time:",
          "value": "{{DATE(2025-01-15T14:23:45Z, SHORT)}}"
        },
        {
          "title": "Correlation ID:",
          "value": "vault-seal-abc123"
        },
        {
          "title": "Stakeholders:",
          "value": "Security Eng., SRE, CloudOps"
        },
        {
          "title": "Auto-unseal:",
          "value": "Attempted, failed (Azure KV timeout)"
        }
      ]
    },
    {
      "type": "TextBlock",
      "text": "**Impact:** All write operations blocked. Read operations continue from standby nodes.",
      "wrap": true,
      "spacing": "medium"
    },
    {
      "type": "TextBlock",
      "text": "**Recommended Actions:**\n1. Verify Azure Key Vault connectivity\n2. Manual unseal via CLI if AKV unavailable\n3. Check audit logs for root cause",
      "wrap": true
    }
  ],
  "actions": [
    {
      "type": "Action.Execute",
      "title": "✅ Acknowledge",
      "verb": "acknowledge",
      "data": {
        "action": "acknowledge",
        "event_id": "vault-seal-abc123",
        "acknowledger": "{{USER_EMAIL}}"
      },
      "associatedInputs": "auto"
    },
    {
      "type": "Action.Execute",
      "title": "🚨 Escalate to On-Call",
      "verb": "escalate",
      "style": "positive",
      "data": {
        "action": "escalate",
        "event_id": "vault-seal-abc123",
        "escalation_tier": "on-call-sre"
      }
    },
    {
      "type": "Action.OpenUrl",
      "title": "📊 View Dashboard",
      "url": "https://grafana.claimlinc.sa/d/vault-health"
    },
    {
      "type": "Action.OpenUrl",
      "title": "📖 Runbook",
      "url": "https://docs.claimlinc.sa/runbooks/vault-seal-recovery"
    }
  ],
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
}
```

### 4.2 Celery Task Failure Card

**Use Case:** Notify Runtime Eng. of NPHIES task failure after retries

```json
{
  "type": "AdaptiveCard",
  "version": "1.5",
  "body": [
    {
      "type": "Container",
      "style": "warning",
      "items": [
        {
          "type": "TextBlock",
          "text": "⚠️ Celery Task Failed",
          "weight": "bolder",
          "size": "large"
        }
      ]
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "title": "Task Name:",
          "value": "check_nphies_eligibility"
        },
        {
          "title": "Task ID:",
          "value": "4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a"
        },
        {
          "title": "Correlation ID:",
          "value": "corr-elig-xyz789"
        },
        {
          "title": "Retry Attempts:",
          "value": "5/5 (exhausted)"
        },
        {
          "title": "Queue:",
          "value": "nphies_eligibility"
        },
        {
          "title": "Worker:",
          "value": "celery-worker-3.prod.svc"
        },
        {
          "title": "Error:",
          "value": "NPHIESClientError: Connection timeout after 30s"
        }
      ]
    },
    {
      "type": "TextBlock",
      "text": "**Patient Context:**",
      "weight": "bolder",
      "spacing": "medium"
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "title": "Patient ID:",
          "value": "P123456789"
        },
        {
          "title": "Member ID:",
          "value": "M987654321"
        },
        {
          "title": "Payer:",
          "value": "Saudi Payer (701)"
        }
      ]
    },
    {
      "type": "TextBlock",
      "text": "**Next Steps:** Task moved to Dead Letter Queue (DLQ). Manual intervention required.",
      "wrap": true,
      "color": "attention"
    }
  ],
  "actions": [
    {
      "type": "Action.Execute",
      "title": "🔄 Retry Task",
      "verb": "retry",
      "data": {
        "action": "retry_task",
        "task_id": "4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a",
        "queue": "nphies_eligibility"
      }
    },
    {
      "type": "Action.Execute",
      "title": "🗑️ Discard Task",
      "verb": "discard",
      "style": "destructive",
      "data": {
        "action": "discard_task",
        "task_id": "4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a"
      }
    },
    {
      "type": "Action.OpenUrl",
      "title": "📊 View Flower",
      "url": "https://flower.claimlinc.sa/task/4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a"
    },
    {
      "type": "Action.OpenUrl",
      "title": "📋 View Logs",
      "url": "https://kibana.claimlinc.sa/app/logs?correlation_id=corr-elig-xyz789"
    }
  ]
}
```

### 4.3 NPHIES Claim Submission Card

**Use Case:** Notify Integration Team of successful claim submission

```json
{
  "type": "AdaptiveCard",
  "version": "1.5",
  "body": [
    {
      "type": "Container",
      "style": "good",
      "items": [
        {
          "type": "TextBlock",
          "text": "✅ NPHIES Claim Submitted",
          "weight": "bolder",
          "size": "large",
          "color": "good"
        }
      ]
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "title": "Claim ID:",
          "value": "CLM-2025-001234"
        },
        {
          "title": "Poll ID:",
          "value": "POLL-ABC123XYZ"
        },
        {
          "title": "Submitted:",
          "value": "{{DATE(2025-01-15T14:30:00Z, SHORT)}}"
        },
        {
          "title": "Patient ID:",
          "value": "P123456789"
        },
        {
          "title": "Provider:",
          "value": "King Fahad Medical City (KFMC)"
        },
        {
          "title": "Payer:",
          "value": "Saudi Payer (701)"
        },
        {
          "title": "Total Amount:",
          "value": "15,000 SAR"
        }
      ]
    },
    {
      "type": "TextBlock",
      "text": "**Services:**",
      "weight": "bolder",
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "ColumnSet",
          "columns": [
            {
              "type": "Column",
              "width": "stretch",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "• Consultation (E/M 99213)",
                  "wrap": true
                }
              ]
            },
            {
              "type": "Column",
              "width": "auto",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "500 SAR",
                  "horizontalAlignment": "right"
                }
              ]
            }
          ]
        },
        {
          "type": "ColumnSet",
          "columns": [
            {
              "type": "Column",
              "width": "stretch",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "• Lab Tests (CBC, HbA1c)",
                  "wrap": true
                }
              ]
            },
            {
              "type": "Column",
              "width": "auto",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "1,500 SAR",
                  "horizontalAlignment": "right"
                }
              ]
            }
          ]
        },
        {
          "type": "ColumnSet",
          "columns": [
            {
              "type": "Column",
              "width": "stretch",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "• Medication (Metformin 1000mg)",
                  "wrap": true
                }
              ]
            },
            {
              "type": "Column",
              "width": "auto",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "3,000 SAR",
                  "horizontalAlignment": "right"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "TextBlock",
      "text": "**Status:** Polling for response every 60 seconds. Expected response in 5-10 minutes.",
      "wrap": true,
      "spacing": "medium",
      "isSubtle": true
    }
  ],
  "actions": [
    {
      "type": "Action.Execute",
      "title": "🔍 Poll Now",
      "verb": "poll",
      "data": {
        "action": "poll_nphies_response",
        "poll_id": "POLL-ABC123XYZ",
        "claim_id": "CLM-2025-001234"
      }
    },
    {
      "type": "Action.OpenUrl",
      "title": "📄 View Claim Details",
      "url": "https://claimlinc.sa/claims/CLM-2025-001234"
    },
    {
      "type": "Action.OpenUrl",
      "title": "📊 NPHIES Dashboard",
      "url": "https://portal.nphies.sa/claims/POLL-ABC123XYZ"
    }
  ]
}
```

---

## 5. Implementation Components

### 5.1 Directory Structure

```
integrations/teams/
├── __init__.py
├── config.py                      # Teams webhook URLs, secrets
├── webhook_sender.py              # HTTP client with retry/HMAC
├── event_aggregator.py            # Event normalization and routing
├── card_builder.py                # Adaptive Card template engine
├── actions/
│   ├── __init__.py
│   ├── acknowledge_handler.py     # Handle acknowledgment actions
│   ├── escalate_handler.py        # Handle escalation actions
│   ├── retry_handler.py           # Handle task retry actions
│   └── discard_handler.py         # Handle task discard actions
├── templates/
│   ├── vault_security_event.json
│   ├── celery_task_failure.json
│   ├── nphies_claim_submission.json
│   ├── nphies_claim_approved.json
│   ├── nphies_claim_rejected.json
│   ├── system_alert.json
│   └── compliance_notification.json
├── models.py                      # Pydantic models for events/cards
├── security.py                    # HMAC signature verification
└── tests/
    ├── test_webhook_sender.py
    ├── test_card_builder.py
    └── test_event_aggregator.py
```

### 5.2 Configuration Schema

```python
# integrations/teams/config.py
from pydantic import BaseSettings, HttpUrl, SecretStr
from typing import Dict

class TeamsConfig(BaseSettings):
    """Teams integration configuration."""
    
    # Webhook URLs (stored in Vault)
    webhook_url_security: HttpUrl
    webhook_url_runtime: HttpUrl
    webhook_url_integration: HttpUrl
    webhook_url_compliance: HttpUrl
    webhook_url_devops: HttpUrl
    webhook_url_general: HttpUrl
    
    # Security
    hmac_secret: SecretStr  # For outgoing webhook signature verification
    signing_key: SecretStr  # For signing our webhooks
    
    # Rate limiting
    max_requests_per_minute: int = 60
    max_burst_size: int = 10
    
    # Retry configuration
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    retry_timeout_seconds: int = 30
    
    # Card settings
    card_history_retention_days: int = 90
    enable_user_specific_views: bool = True
    
    # Redis for event bus
    redis_url: str = "redis://redis-primary.prod.svc.cluster.local:6379/3"
    redis_channel_prefix: str = "teams:events:"
    
    class Config:
        env_prefix = "TEAMS_"
        case_sensitive = False
```

---

## 6. Security & Compliance

### 6.1 HMAC Signature Verification

All incoming webhooks from Teams must include HMAC-SHA256 signature:

```python
import hmac
import hashlib
from typing import Optional

def verify_hmac_signature(
    payload: str,
    signature: str,
    secret: str
) -> bool:
    """Verify HMAC signature for incoming Teams webhook."""
    expected_signature = hmac.new(
        key=secret.encode('utf-8'),
        msg=payload.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

### 6.2 Audit Logging

Every Teams notification must be logged with:

```python
{
    "timestamp": "2025-01-15T14:23:45.123456Z",
    "correlation_id": "corr-vault-abc123",
    "event_type": "vault.seal.detected",
    "stakeholders": ["Security Eng.", "SRE", "CloudOps"],
    "webhook_url": "https://xxxxx.webhook.office.com/webhookb2/***REDACTED***",
    "card_id": "card-vault-seal-abc123",
    "sent_at": "2025-01-15T14:23:45.456789Z",
    "status_code": 200,
    "retry_count": 0,
    "acknowledged_by": null,
    "acknowledged_at": null
}
```

### 6.3 Compliance Matrix

| Requirement | Implementation | Verification |
|------------|----------------|--------------|
| **HIPAA §164.308(a)(5)(ii)(C)** | Audit logs with 6-year retention | PostgreSQL audit table |
| **HIPAA §164.312(e)(1)** | TLS 1.3 for webhook transmission | nginx config |
| **PDPL Art 14** | Consent tracking for notifications | User preferences table |
| **PDPL Art 17** | Right to opt-out of notifications | User settings API |
| **NPHIES IG v0.4.0** | Correlation IDs in all NPHIES events | Card metadata |

---

## 7. Integration with Existing Components

### 7.1 Celery Task Integration

**File:** `workers/tasks/nphies_tasks.py`

```python
from integrations.teams import send_teams_notification

@shared_task(bind=True, base=IdempotentTask, max_retries=5)
def check_nphies_eligibility(
    self,
    patient_id: str,
    member_id: str,
    payer_nphies_id: str,
    service_date: str
) -> dict:
    """Check patient eligibility via NPHIES."""
    correlation_id = f"corr-elig-{uuid.uuid4().hex[:8]}"
    
    try:
        # Existing eligibility check logic...
        result = nphies_client.check_eligibility(...)
        
        # Send success notification to Teams
        send_teams_notification(
            event_type="nphies.eligibility.success",
            correlation_id=correlation_id,
            data={
                "patient_id": patient_id,
                "member_id": member_id,
                "payer": payer_nphies_id,
                "status": "eligible",
                "coverage_start": result.get("coverageStart"),
                "coverage_end": result.get("coverageEnd")
            },
            stakeholders=["Integration Team", "PMO"]
        )
        
        return result
        
    except Exception as exc:
        logger.error(
            f"Eligibility check failed: {exc}",
            extra={"correlation_id": correlation_id}
        )
        
        # Send failure notification to Teams
        send_teams_notification(
            event_type="nphies.eligibility.failed",
            correlation_id=correlation_id,
            data={
                "patient_id": patient_id,
                "member_id": member_id,
                "error": str(exc),
                "retry_count": self.request.retries,
                "max_retries": self.max_retries
            },
            stakeholders=["Integration Team", "DevOps", "Runtime Eng."],
            priority="high"
        )
        
        raise self.retry(exc=exc, countdown=exponential_backoff(self.request.retries))
```

### 7.2 Vault Event Monitoring

**New File:** `config/security/vault_event_monitor.py`

```python
import hvac
from integrations.teams import send_teams_notification

def monitor_vault_seal_status():
    """Monitor Vault seal status and send Teams alerts."""
    client = hvac.Client(url=VAULT_ADDR)
    
    while True:
        try:
            health = client.sys.read_health_status(method="GET")
            
            if health.get("sealed"):
                send_teams_notification(
                    event_type="vault.seal.detected",
                    correlation_id=f"vault-seal-{uuid.uuid4().hex[:8]}",
                    data={
                        "node": socket.gethostname(),
                        "cluster_id": health.get("cluster_id"),
                        "sealed_at": datetime.utcnow().isoformat()
                    },
                    stakeholders=["Security Eng.", "SRE", "CloudOps"],
                    priority="critical"
                )
                
        except Exception as exc:
            logger.error(f"Vault health check failed: {exc}")
        
        time.sleep(30)  # Check every 30 seconds
```

---

## 8. Deployment and Testing

### 8.1 Deployment Steps

1. **Create Teams Webhook URLs**
   - Navigate to Teams channel → Workflows → "When a Teams webhook request is received"
   - Generate webhook URLs for each stakeholder group
   - Store URLs in Vault:
     ```bash
     vault kv put secret/teams/webhooks \
       security="https://prod-xxx.webhook.office.com/webhookb2/xxx-security" \
       runtime="https://prod-xxx.webhook.office.com/webhookb2/xxx-runtime" \
       integration="https://prod-xxx.webhook.office.com/webhookb2/xxx-integration" \
       compliance="https://prod-xxx.webhook.office.com/webhookb2/xxx-compliance" \
       devops="https://prod-xxx.webhook.office.com/webhookb2/xxx-devops" \
       general="https://prod-xxx.webhook.office.com/webhookb2/xxx-general"
     ```

2. **Install Python Dependencies**
   ```bash
   pip install aiohttp[speedups] pydantic redis jinja2
   ```

3. **Database Schema Migration**
   ```sql
   CREATE TABLE teams_notifications (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       correlation_id VARCHAR(255) NOT NULL UNIQUE,
       event_type VARCHAR(100) NOT NULL,
       stakeholders TEXT[] NOT NULL,
       priority VARCHAR(20) NOT NULL,
       webhook_url TEXT NOT NULL,
       card_payload JSONB NOT NULL,
       sent_at TIMESTAMPTZ NOT NULL,
       status_code INTEGER,
       retry_count INTEGER DEFAULT 0,
       acknowledged_by VARCHAR(255),
       acknowledged_at TIMESTAMPTZ,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );
   
   CREATE INDEX idx_teams_notifications_correlation_id ON teams_notifications(correlation_id);
   CREATE INDEX idx_teams_notifications_event_type ON teams_notifications(event_type);
   CREATE INDEX idx_teams_notifications_sent_at ON teams_notifications(sent_at DESC);
   ```

4. **Environment Configuration**
   ```bash
   export TEAMS_VAULT_PATH="secret/teams/webhooks"
   export TEAMS_REDIS_URL="redis://redis-primary.prod.svc:6379/3"
   export TEAMS_MAX_REQUESTS_PER_MINUTE=60
   ```

### 8.2 Testing Strategy

| Test Type | Tool | Scope |
|-----------|------|-------|
| **Unit Tests** | pytest | Card builder, event aggregator, HMAC verification |
| **Integration Tests** | pytest + Docker Compose | End-to-end webhook sending, Redis pub/sub |
| **Load Tests** | Locust | 100 notifications/minute sustained |
| **Security Tests** | OWASP ZAP | HMAC bypass, injection attacks |
| **Compliance Tests** | Manual audit | HIPAA/PDPL audit log verification |

---

## 9. Monitoring and Alerting

### 9.1 Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

teams_notifications_sent = Counter(
    'teams_notifications_sent_total',
    'Total Teams notifications sent',
    ['event_type', 'priority', 'status']
)

teams_webhook_latency = Histogram(
    'teams_webhook_latency_seconds',
    'Webhook request latency',
    ['webhook_group']
)

teams_retry_count = Counter(
    'teams_notification_retries_total',
    'Total notification retry attempts',
    ['event_type']
)

teams_acknowledgments = Counter(
    'teams_acknowledgments_total',
    'Total card acknowledgments',
    ['event_type', 'acknowledger_role']
)
```

### 9.2 Grafana Dashboard Panels

1. **Notification Volume by Event Type** (Bar chart)
2. **Webhook Latency P50/P95/P99** (Graph)
3. **Retry Rate by Event Type** (Heatmap)
4. **Acknowledgment Time (MTTA)** (Gauge)
5. **Failed Notifications (Last 24h)** (Stat panel)

---

## 10. Runbooks and Escalation

### 10.1 Common Issues

| Issue | Symptoms | Resolution |
|-------|----------|-----------|
| **Webhook 429 Rate Limit** | `status_code: 429` in logs | Reduce notification frequency, implement batching |
| **Webhook 401 Unauthorized** | `status_code: 401` in logs | Regenerate webhook URL in Teams Workflows |
| **Card Actions Not Working** | User clicks action, no response | Verify Action.Execute verb matches handler |
| **Duplicate Notifications** | Same event sent multiple times | Check Redis idempotency key TTL |
| **Missing Stakeholders** | Some stakeholders not receiving | Verify stakeholder mapping in `event_aggregator.py` |

### 10.2 Escalation Matrix

| Severity | Response Time | Escalation Path |
|----------|--------------|-----------------|
| **CRITICAL** | 5 minutes | Integration Team → DevOps → SRE On-Call |
| **HIGH** | 30 minutes | Integration Team → DevOps |
| **MEDIUM** | 2 hours | Integration Team → PMO |
| **LOW** | Next business day | Integration Team |

---

## 11. Future Enhancements

### 11.1 Phase 2 (Q2 2025)

- **Power Automate Custom Connector**: Bi-directional integration for user-initiated actions
- **Bot Framework Integration**: Conversational queries ("What's the status of claim CLM-2025-001234?")
- **User-Specific Views**: Personalized cards based on user role/permissions
- **Adaptive Card Refresh**: Auto-update cards when event status changes

### 11.2 Phase 3 (Q3 2025)

- **Microsoft Graph API**: Create calendar events for compliance deadlines
- **Teams Tabs**: Embedded ClaimLinc-GIVC dashboard in Teams
- **Proactive Notifications**: AI-driven anomaly detection alerts
- **Multi-language Support**: Arabic and English card templates

---

## 12. References

- [Microsoft Teams Webhooks Documentation](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
- [Adaptive Cards Schema Explorer](https://adaptivecards.io/explorer/)
- [Universal Action Model (Action.Execute)](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/universal-actions-for-adaptive-cards/overview)
- [Power Automate Connector Documentation](https://learn.microsoft.com/en-us/connectors/custom-connectors/)
- [HMAC Signature Verification](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-outgoing-webhook#create-outgoing-webhooks-1)

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-XX  
**Next Review:** Q2 2025  
**Approval:** Integration Team Lead, DevOps Manager, CISO
