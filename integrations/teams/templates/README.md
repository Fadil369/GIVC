# Adaptive Card Templates

This directory contains Jinja2 templates for Microsoft Teams Adaptive Cards. Each template corresponds to specific event types and renders dynamic notification cards with contextual data.

## Template Files

### 1. `vault_security_event.json`

**Event Types:**

- `vault.seal.detected` - Vault node sealed (automatic or manual)
- `vault.unseal.complete` - Vault node unsealed successfully
- `vault.certificate.expiring` - NPHIES mTLS certificate expiring soon
- `vault.secret.rotation.complete` - Secret rotation completed
- `vault.audit.log.full` - Audit log storage threshold reached

**Data Fields:**

- `node` (str): Vault node hostname
- `cluster_id` (str): Vault cluster identifier
- `sealed_at` (datetime): Timestamp when node was sealed
- `auto_unseal_error` (str): Error message if auto-unseal failed
- `certificate_expires` (datetime): Certificate expiration timestamp

**Actions:**

- ✅ Acknowledge
- 🚨 Escalate to On-Call (critical/high only)
- 📊 View Dashboard (Grafana)
- 📖 Runbook

---

### 2. `celery_task_failure.json`

**Event Types:**

- `celery.task.failure` - Celery task failed with exception
- `celery.task.retry` - Task retry attempt
- `celery.task.dlq` - Task moved to Dead Letter Queue

**Data Fields:**

- `task_name` (str): Celery task name (e.g., `nphies_tasks.submit_nphies_claim`)
- `task_id` (str): Celery task UUID
- `retry_count` (int): Number of retry attempts
- `max_retries` (int): Maximum retry limit
- `queue` (str): Queue name (e.g., `nphies_submissions`)
- `worker` (str): Worker node hostname
- `error` (str): Exception message
- `patient_id` (str, optional): Patient identifier for context
- `member_id` (str, optional): Insurance member ID
- `payer` (str, optional): Insurance payer name

**Actions:**

- 🔄 Retry Task (if retry_count >= max_retries)
- 🗑️ Discard Task (if retry exhausted)
- ✅ Acknowledge
- 📊 View Flower (task details)
- 📋 View Logs (Kibana with correlation_id)

---

### 3. `nphies_claim_submission.json`

**Event Types:**

- `nphies.claim.submitted` - Claim submitted to NPHIES successfully

**Data Fields:**

- `claim_id` (str): Internal ClaimLinc claim ID
- `poll_id` (str): NPHIES polling identifier
- `patient_id` (str): Patient identifier
- `provider` (str): Healthcare provider name
- `payer` (str): Insurance payer name
- `total_amount` (str): Total claim amount (e.g., "5000.00 SAR")
- `services` (list): List of service dictionaries with `description` and `amount`

**Actions:**

- 🔍 Poll Now (trigger immediate NPHIES poll)
- 📄 View Claim Details (ClaimLinc UI)
- 📊 NPHIES Dashboard (NPHIES portal)

---

### 4. `nphies_claim_approved.json`

**Event Types:**

- `nphies.claim.approved` - NPHIES approved the claim

**Data Fields:**

- `claim_id` (str): Internal ClaimLinc claim ID
- `approval_number` (str): NPHIES approval reference number
- `patient_id` (str): Patient identifier
- `payer` (str): Insurance payer name
- `approved_amount` (str): Total approved amount
- `net_amount` (str): Net payment amount
- `patient_share` (str, optional): Patient co-payment amount
- `payer_share` (str, optional): Payer reimbursement amount
- `notes` (str, optional): Approval notes from NPHIES

**Actions:**

- ✅ Acknowledge
- 📄 View Claim Details
- 💳 Process Payment (ClaimLinc payment UI)

---

### 5. `nphies_claim_rejected.json`

**Event Types:**

- `nphies.claim.rejected` - NPHIES rejected the claim

**Data Fields:**

- `claim_id` (str): Internal ClaimLinc claim ID
- `patient_id` (str): Patient identifier
- `payer` (str): Insurance payer name
- `rejection_code` (str): NPHIES rejection code (e.g., `INV-001`)
- `rejection_reason` (str): Human-readable rejection reason
- `errors` (list): List of error dictionaries with `field` and `message`

**Actions:**

- ✅ Acknowledge
- 📝 Edit & Resubmit (ClaimLinc edit UI)
- 📄 View Claim Details
- 📚 Rejection Code Guide (NPHIES documentation)

---

### 6. `nphies_api_error.json`

**Event Types:**

- `nphies.api.error` - NPHIES API request failed
- `nphies.certificate.invalid` - mTLS certificate expired or invalid
- `nphies.jwt.error` - JWT token signing or validation failed
- `nphies.network.timeout` - Network timeout to NPHIES endpoints

**Data Fields:**

- `error_type` (str): Error category (`certificate`, `jwt`, `network`, `api`)
- `http_status` (int): HTTP status code (e.g., 401, 500, 503)
- `operation` (str): Operation name (e.g., `submit_claim`, `check_eligibility`)
- `endpoint` (str): NPHIES API endpoint URL
- `error_message` (str): Detailed error message
- `certificate_expires` (datetime, optional): Certificate expiration timestamp
- `certificate_expired` (bool, optional): True if certificate already expired
- `jwt_error` (str, optional): JWT-specific error message

**Actions:**

- ✅ Acknowledge
- 🚨 Escalate (to on-call-integration tier)
- 📋 View Logs (Kibana)
- 📊 NPHIES Status (NPHIES status page)
- 📖 API Docs (NPHIES API reference)

---

### 7. `system_alert.json`

**Event Types:**

- `system.rabbitmq.node_down` - RabbitMQ node unavailable
- `system.redis.connection_lost` - Redis connection lost
- `system.postgres.replication_lag` - PostgreSQL replication lag exceeded threshold
- `system.kubernetes.pod_crashlooping` - Kubernetes pod in CrashLoopBackOff

**Data Fields:**

- `service` (str): Service name (`RabbitMQ`, `Redis`, `PostgreSQL`, `Kubernetes`)
- `node` (str, optional): Node hostname
- `pod` (str, optional): Kubernetes pod name
- `namespace` (str, optional): Kubernetes namespace
- `message` (str): Alert message
- `metrics` (dict, optional): Key-value pairs of metric data
- `healthy_nodes` (int, optional): Number of healthy nodes in cluster
- `lag_seconds` (int, optional): Replication lag in seconds (PostgreSQL)
- `crash_count` (int, optional): Number of consecutive crashes (Kubernetes)
- `dashboard_id` (str, optional): Grafana dashboard ID
- `runbook_url` (str, optional): Runbook URL for this alert

**Actions:**

- ✅ Acknowledge
- 🚨 Escalate to On-Call (critical/high only)
- 📊 Grafana Dashboard
- 📋 View Logs (Kibana)
- 📖 Runbook (if available)

---

### 8. `follow_up_status.json`

**Event Types:**

- `followup.batch.status` – Daily worksheet follow-up alert for batches, reworks, and claim resubmissions

**Data Fields:**

- `branch` (str): Branch or facility name associated with the batch
- `insurance_company` (str): Insurance payer
- `batch_no` (str): Batch number or correlation identifier
- `status_display` (str): Human-readable status (e.g., "Passed Due", "Ready To Work")
- `due_date_display` (str): Formatted due date or "Not provided"
- `resubmission_date_display` (str): Formatted resubmission date, if any
- `billing_amount_display` (str): Formatted billing amount (e.g., `SAR 1,250,000.00`)
- `approved_to_pay_display` (str): Formatted approved-to-pay amount
- `final_rejection_display` (str): Formatted rejection total
- `final_rejection_percent_display` (str): Rejection percentage (e.g., `12.5%`)
- `recovery_amount_display` (str): Amount currently in recovery
- `alerts` (list[str]): Bullet list of attention items (overdue, pending submission, large rejection, etc.)
- `portal_resources` (list[dict]): Related portals/channels with `name`, optional `url`, and `description`
- `processor` (str): Team member responsible
- `rework_type` / `batch_type` (str, optional): Workflow metadata
- `days_until_due` (int, optional): Days remaining until due date (negative when overdue)

**Actions:**

- ✅ Acknowledge
- 🚨 Escalate (critical/high priority only)

The template surfaces worksheet context, highlights upcoming or overdue deadlines, and links the recipient to relevant operational portals pulled from the Accounts workbook.

---

## Jinja2 Variables

All templates have access to these common variables:

### Event Metadata
- `event_type` (EventType): Event type enum value (e.g., `vault.seal.detected`)
- `correlation_id` (str): Unique correlation ID for tracing
- `timestamp` (datetime): Event occurrence timestamp
- `priority` (TeamsPriority): Priority enum (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`)
- `priority_formatted` (str): Human-readable priority (e.g., "🔴 Critical")
- `priority_color` (str): Adaptive Card color (`attention`, `warning`, `accent`, `good`, `default`)
- `alert_icon` (str): Emoji icon based on priority (🚨, ⚠️, ℹ️, 📝, 📢)
- `stakeholders` (list[StakeholderGroup]): List of stakeholder groups
- `stakeholders_formatted` (str): Comma-separated stakeholder names

### URLs
- `grafana_url` (str): Grafana base URL (`https://grafana.claimlinc.sa`)
- `flower_url` (str): Flower (Celery monitoring) URL (`https://flower.claimlinc.sa`)
- `kibana_url` (str): Kibana (logging) URL (`https://kibana.claimlinc.sa`)
- `nphies_portal_url` (str): NPHIES portal URL (`https://portal.nphies.sa`)
- `nphies_status_url` (str): NPHIES status page (`https://status.nphies.sa`)
- `nphies_docs_url` (str): NPHIES documentation (`https://docs.nphies.sa`)
- `claimlinc_url` (str): ClaimLinc application URL (`https://claimlinc.sa`)
- `vault_runbook_url` (str): Vault runbook URL
- `celery_runbook_url` (str): Celery runbook URL
- `nphies_runbook_url` (str): NPHIES runbook URL

### Custom Filters
- `format_datetime(value, format='MEDIUM')` - Format datetime objects (`SHORT`, `MEDIUM`, `LONG`)
- `format_priority(value)` - Format TeamsPriority enum (e.g., "🔴 Critical")
- `format_stakeholders(value)` - Format stakeholder list (e.g., "SRE, DevOps, Security")

---

## Adaptive Card Actions

### Action.Execute Verbs
- `acknowledge` - Acknowledge notification (all templates)
- `escalate` - Escalate to on-call engineer (critical/high priority)
- `retry` - Retry failed Celery task (celery_task_failure.json)
- `discard` - Discard failed task (celery_task_failure.json)
- `poll` - Poll NPHIES response immediately (nphies_claim_submission.json)

### Action Data
All actions include:
```json
{
  "action": "verb_name",
  "event_id": "{{ correlation_id }}",
  "correlation_id": "{{ correlation_id }}",
  // Additional action-specific fields
}
```

---

## Template Rendering

Templates are rendered using `CardBuilder.build_card()`:

```python
from integrations.teams.models import TeamsEvent, EventType, TeamsPriority, StakeholderGroup
from integrations.teams.card_builder import CardBuilder

event = TeamsEvent(
    event_type=EventType.VAULT_SEAL_DETECTED,
    correlation_id="550e8400-e29b-41d4-a716-446655440000",
    stakeholders=[StakeholderGroup.SECURITY_ENG, StakeholderGroup.SRE],
    priority=TeamsPriority.CRITICAL,
    data={
        "node": "vault-prod-01",
        "cluster_id": "vault-prod-cluster",
        "sealed_at": "2025-11-06T14:30:00Z"
    }
)

card_builder = CardBuilder()
card_payload = card_builder.build_card(event)  # Returns dict ready for Teams webhook
```

---

## Validation


- All templates follow Adaptive Card Schema 1.5
- JSON structure validated (Jinja2 syntax causes linter errors - expected)
- Templates render fallback card if Jinja2 errors occur

- Card payload logged for debugging

---


## Development Notes


1. **Linter Errors**: VS Code JSON linter will report errors on Jinja2 syntax (`{% if %}`, `{{ variable }}`). This is expected and safe to ignore.

2. **Testing Templates**: Use `CardBuilder` unit tests to validate rendering:

   ```bash

   pytest integrations/teams/tests/test_card_builder.py -v
   ```

3. **Adding New Templates**:
   - Create JSON file in this directory

   - Add event type mapping in `CardBuilder._get_template_name()`
   - Add template-specific data fields documentation
   - Write unit test with sample data


4. **Conditional Rendering**: Use Jinja2 `{% if %}` blocks to show/hide sections based on available data:
   ```jinja2
   {% if data.patient_id %}
   {

     "title": "Patient ID:",
     "value": "{{ data.patient_id }}"
   }
   {% endif %}
   ```

5. **URL Parameters**: Embed correlation IDs and entity IDs in URLs for deep linking:
   ```jinja2

   "url": "{{ kibana_url }}/app/logs?correlation_id={{ correlation_id }}"
   ```

---

## References

- [Adaptive Cards Schema](https://adaptivecards.io/explorer/)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)
- [Universal Actions Model](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/universal-actions-for-adaptive-cards/)
- [Teams Workflows](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
