"""
Unit tests for Teams Adaptive Card templates
Tests template rendering, data validation, and action generation
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from integrations.teams.card_builder import CardBuilder
from integrations.teams.models import (
    TeamsEvent,
    EventType,
    TeamsPriority,
    StakeholderGroup
)


@pytest.fixture
def card_builder():
    """Fixture providing CardBuilder instance"""
    return CardBuilder()


@pytest.fixture
def base_event_data():
    """Fixture providing common event data"""
    return {
        "correlation_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc)
    }


class TestVaultSecurityEventTemplate:
    """Tests for vault_security_event.json template"""
    
    def test_vault_seal_detected_card(self, card_builder, base_event_data):
        """Test Vault seal detected event renders correctly"""
        event = TeamsEvent(
            event_type=EventType.VAULT_SEAL_DETECTED,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.SECURITY_ENG, StakeholderGroup.SRE],
            priority=TeamsPriority.CRITICAL,
            data={
                "node": "vault-prod-01",
                "cluster_id": "vault-prod-cluster",
                "sealed_at": "2025-11-06T14:30:00Z"
            }
        )
        
        card = card_builder.build_card(event)
        
        assert card["type"] == "message"
        assert card["attachments"][0]["contentType"] == "application/vnd.microsoft.card.adaptive"
        
        card_content = str(card)
        assert "vault-prod-01" in card_content
        assert base_event_data["correlation_id"] in card_content
        assert "Vault Seal Detected" in card_content or "vault.seal.detected" in card_content
    
    def test_vault_certificate_expiring_card(self, card_builder, base_event_data):
        """Test Vault certificate expiring event"""
        event = TeamsEvent(
            event_type=EventType.VAULT_CERTIFICATE_EXPIRING,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.SECURITY_ENG, StakeholderGroup.NPHIES_INTEGRATION],
            priority=TeamsPriority.HIGH,
            data={
                "node": "vault-prod-01",
                "certificate_expires": "2025-11-20T00:00:00Z"
            }
        )
        
        card = card_builder.build_card(event)
        card_content = str(card)
        
        assert "certificate" in card_content.lower()
        assert "expires" in card_content.lower()
        assert base_event_data["correlation_id"] in card_content


class TestCeleryTaskFailureTemplate:
    """Tests for celery_task_failure.json template"""
    
    def test_task_failure_with_retries(self, card_builder, base_event_data):
        """Test Celery task failure with retry count"""
        event = TeamsEvent(
            event_type=EventType.CELERY_TASK_FAILURE,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.RUNTIME_ENG, StakeholderGroup.SRE],
            priority=TeamsPriority.HIGH,
            data={
                "task_name": "nphies_tasks.submit_nphies_claim",
                "task_id": str(uuid4()),
                "retry_count": 3,
                "max_retries": 5,
                "queue": "nphies_submissions",
                "worker": "worker-01",
                "error": "Connection timeout to NPHIES API",
                "patient_id": "PAT-12345",
                "member_id": "MEM-67890",
                "payer": "TAWUNIYA"
            }
        )
        
        card = card_builder.build_card(event)
        card_content = str(card)
        
        assert "nphies_tasks.submit_nphies_claim" in card_content
        assert "Connection timeout" in card_content
        assert "PAT-12345" in card_content
        assert "TAWUNIYA" in card_content
    
    def test_task_dlq_exhausted_retries(self, card_builder, base_event_data):
        """Test task moved to DLQ after exhausting retries"""
        event = TeamsEvent(
            event_type=EventType.CELERY_TASK_DLQ,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.RUNTIME_ENG, StakeholderGroup.DEVOPS],
            priority=TeamsPriority.CRITICAL,
            data={
                "task_name": "nphies_tasks.poll_nphies_response",
                "task_id": str(uuid4()),
                "retry_count": 5,
                "max_retries": 5,
                "queue": "nphies_polling",
                "error": "Max retries exceeded"
            }
        )
        
        card = card_builder.build_card(event)
        card_content = str(card)
        
        assert "5/5" in card_content or "exhausted" in card_content.lower()
        assert base_event_data["correlation_id"] in card_content


class TestNPHIESClaimTemplates:
    """Tests for NPHIES claim templates"""
    
    def test_claim_submission_card(self, card_builder, base_event_data):
        """Test NPHIES claim submission notification"""
        event = TeamsEvent(
            event_type=EventType.NPHIES_CLAIM_SUBMITTED,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[
                StakeholderGroup.NPHIES_INTEGRATION,
                StakeholderGroup.PMO,
                StakeholderGroup.COMPLIANCE
            ],
            priority=TeamsPriority.INFO,
            data={
                "claim_id": "CLM-2025-001234",
                "poll_id": "POLL-ABCD1234",
                "patient_id": "PAT-567890",
                "provider": "Al Hayat Hospital - Riyadh",
                "payer": "TAWUNIYA",
                "total_amount": "5000.00 SAR",
                "services": [
                    {"description": "Consultation", "amount": "200.00 SAR"},
                    {"description": "Laboratory Tests", "amount": "800.00 SAR"},
                    {"description": "X-Ray", "amount": "500.00 SAR"}
                ]
            }
        )
        
        card = card_builder.build_card(event)
        card_content = str(card)
        
        assert "CLM-2025-001234" in card_content
        assert "POLL-ABCD1234" in card_content
        assert "Al Hayat Hospital" in card_content
        assert "5000.00 SAR" in card_content
        assert "Consultation" in card_content
    
    def test_claim_approved_card(self, card_builder, base_event_data):
        """Test NPHIES claim approved notification"""
        event = TeamsEvent(
            event_type=EventType.NPHIES_CLAIM_APPROVED,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.NPHIES_INTEGRATION, StakeholderGroup.PMO],
            priority=TeamsPriority.INFO,
            data={
                "claim_id": "CLM-2025-001234",
                "approval_number": "APR-2025-XYZ789",
                "patient_id": "PAT-567890",
                "payer": "TAWUNIYA",
                "approved_amount": "4500.00 SAR",
                "net_amount": "4000.00 SAR",
                "patient_share": "500.00 SAR",
                "payer_share": "4000.00 SAR",
                "notes": "Approved with standard coverage"
            }
        )
        
        card = card_builder.build_card(event)
        card_content = str(card)
        
        assert "CLM-2025-001234" in card_content
        assert "APR-2025-XYZ789" in card_content
        assert "4500.00 SAR" in card_content
        assert "Approved" in card_content
    
    def test_claim_rejected_card(self, card_builder, base_event_data):
        """Test NPHIES claim rejected notification"""
        event = TeamsEvent(
            event_type=EventType.NPHIES_CLAIM_REJECTED,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.NPHIES_INTEGRATION, StakeholderGroup.COMPLIANCE],
            priority=TeamsPriority.HIGH,
            data={
                "claim_id": "CLM-2025-001234",
                "patient_id": "PAT-567890",
                "payer": "TAWUNIYA",
                "rejection_code": "INV-001",
                "rejection_reason": "Invalid patient member ID format",
                "errors": [
                    {"field": "member_id", "message": "Must be 10 digits"},
                    {"field": "payer_nphies_id", "message": "Payer ID not found in registry"}
                ]
            }
        )
        
        card = card_builder.build_card(event)
        card_content = str(card)
        
        assert "CLM-2025-001234" in card_content
        assert "INV-001" in card_content
        assert "Invalid patient member ID" in card_content
        assert "Must be 10 digits" in card_content


class TestNPHIESAPIErrorTemplate:
    """Tests for nphies_api_error.json template"""
    
    def test_certificate_error(self, card_builder, base_event_data):
        """Test NPHIES certificate error notification"""
        event = TeamsEvent(
            event_type=EventType.NPHIES_CERTIFICATE_INVALID,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.SECURITY_ENG, StakeholderGroup.NPHIES_INTEGRATION],
            priority=TeamsPriority.CRITICAL,
            data={
                "error_type": "certificate",
                "http_status": 401,
                "operation": "submit_claim",
                "endpoint": "https://HSB.nphies.sa/Claim/$submit",
                "error_message": "mTLS certificate expired",
                "certificate_expired": True,
                "certificate_expires": "2025-10-15T00:00:00Z"
            }
        )
        
        card = card_builder.build_card(event)
        card_content = str(card)
        
        assert "certificate" in card_content.lower()
        assert "expired" in card_content.lower()
        assert "401" in card_content
    
    def test_jwt_error(self, card_builder, base_event_data):
        """Test NPHIES JWT error notification"""
        event = TeamsEvent(
            event_type=EventType.NPHIES_JWT_ERROR,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.NPHIES_INTEGRATION, StakeholderGroup.SRE],
            priority=TeamsPriority.HIGH,
            data={
                "error_type": "jwt",
                "http_status": 401,
                "operation": "authenticate",
                "error_message": "JWT signature verification failed",
                "jwt_error": "Invalid signing key"
            }
        )
        
        card = card_builder.build_card(event)
        card_content = str(card)
        
        assert "jwt" in card_content.lower() or "JWT" in card_content
        assert "signature" in card_content.lower()


class TestSystemAlertTemplate:
    """Tests for system_alert.json template"""
    
    def test_rabbitmq_node_down(self, card_builder, base_event_data):
        """Test RabbitMQ node down alert"""
        event = TeamsEvent(
            event_type=EventType.SYSTEM_RABBITMQ_NODE_DOWN,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.SRE, StakeholderGroup.CLOUDOPS],
            priority=TeamsPriority.CRITICAL,
            data={
                "service": "RabbitMQ",
                "node": "rabbitmq-prod-02",
                "message": "Node stopped responding to health checks",
                "healthy_nodes": 2,
                "metrics": {
                    "cluster_size": 3,
                    "queue_depth": 1247,
                    "memory_usage": "85%"
                }
            }
        )
        
        card = card_builder.build_card(event)
        card_content = str(card)
        
        assert "RabbitMQ" in card_content
        assert "rabbitmq-prod-02" in card_content
        assert "2" in card_content  # healthy_nodes
    
    def test_postgres_replication_lag(self, card_builder, base_event_data):
        """Test PostgreSQL replication lag alert"""
        event = TeamsEvent(
            event_type=EventType.SYSTEM_POSTGRES_REPLICATION_LAG,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.SRE, StakeholderGroup.DEVOPS],
            priority=TeamsPriority.MEDIUM,
            data={
                "service": "PostgreSQL",
                "node": "postgres-replica-01",
                "message": "Replication lag exceeds threshold",
                "lag_seconds": 120,
                "metrics": {
                    "lag_seconds": 120,
                    "wal_receive_lsn": "0/123456789",
                    "wal_replay_lsn": "0/123456789"
                }
            }
        )
        
        card = card_builder.build_card(event)
        card_content = str(card)
        
        assert "PostgreSQL" in card_content or "Postgres" in card_content
        assert "120" in card_content  # lag_seconds


class TestFollowUpTemplate:
    """Tests for follow_up_status.json template"""

    def test_follow_up_status_card(self, card_builder, base_event_data):
        """Ensure follow-up status card renders with portals and alerts."""
        event = TeamsEvent(
            event_type=EventType.FOLLOW_UP_STATUS,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.NPHIES_INTEGRATION, StakeholderGroup.PMO],
            priority=TeamsPriority.HIGH,
            data={
                "branch": "Riyadh",
                "status_display": "Passed Due",
                "status_raw": "Passed Due",
                "insurance_company": "MOH",
                "batch_no": "B123",
                "processor": "Dr. Mutasim",
                "rework_type": "Re-submission",
                "batch_type": "IP",
                "billing_month": "Oct",
                "billing_year": 2024,
                "due_date_display": "2024-10-15",
                "received_date_display": "2024-09-01",
                "resubmission_date_display": "2024-10-20",
                "billing_amount_display": "SAR 1,000,000.00",
                "approved_to_pay_display": "SAR 800,000.00",
                "final_rejection_display": "SAR 250,000.00",
                "final_rejection_percent_display": "25.0%",
                "recovery_amount_display": "SAR 50,000.00",
                "alerts": [
                    "Marked Passed Due – overdue by 5 day(s) (was due 2024-10-15)",
                    "Final rejection total SAR 250,000.00",
                ],
                "portal_resources": [
                    {"name": "MOH Claim Portal", "url": "https://portal.example/claims"},
                    {"name": "Remote Access", "description": "Remote desktop IP: 10.0.10.10"},
                ],
                "days_until_due": -5,
            },
        )

        card = card_builder.build_card(event)
        card_content = str(card)

        assert "Follow-up" in card_content
        assert "MOH Claim Portal" in card_content
        assert "Remote desktop IP" in card_content
        assert "Passed Due" in card_content
        assert base_event_data["correlation_id"] in card_content


class TestCardBuilderFeatures:
    """Tests for CardBuilder utility features"""
    
    def test_fallback_card_on_missing_template(self, card_builder, base_event_data):
        """Test fallback card generation when template is missing"""
        # Create event with non-existent event type (will use fallback)
        event = TeamsEvent(
            event_type=EventType.VAULT_SEAL_DETECTED,  # Valid type
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.SRE],
            priority=TeamsPriority.INFO,
            data={"test": "data"}
        )
        
        # Temporarily break template path to test fallback
        original_path = card_builder.template_dir
        card_builder.template_dir = "/nonexistent/path"
        
        try:
            card = card_builder.build_card(event)
            card_content = str(card)
            
            # Should contain fallback card elements
            assert base_event_data["correlation_id"] in card_content
            assert "vault.seal.detected" in card_content.lower()
        finally:
            # Restore original path
            card_builder.template_dir = original_path
    
    def test_priority_formatting(self, card_builder):
        """Test priority formatting filter"""
        assert "🔴" in card_builder._format_priority(TeamsPriority.CRITICAL)
        assert "Critical" in card_builder._format_priority(TeamsPriority.CRITICAL)
        assert "🟡" in card_builder._format_priority(TeamsPriority.MEDIUM)
    
    def test_stakeholder_formatting(self, card_builder):
        """Test stakeholder list formatting"""
        stakeholders = [
            StakeholderGroup.SECURITY_ENG,
            StakeholderGroup.SRE,
            StakeholderGroup.DEVOPS
        ]
        
        formatted = card_builder._format_stakeholders(stakeholders)
        
        assert "Security Engineering" in formatted
        assert "SRE" in formatted
        assert "DevOps" in formatted
        assert ", " in formatted  # Comma-separated
    
    def test_datetime_formatting(self, card_builder):
        """Test datetime formatting filter"""
        dt = datetime(2025, 11, 6, 14, 30, 0, tzinfo=timezone.utc)
        
        # Test different formats
        short = card_builder._format_datetime(dt, "SHORT")
        medium = card_builder._format_datetime(dt, "MEDIUM")
        long = card_builder._format_datetime(dt, "LONG")
        
        assert "Nov" in short or "11" in short
        assert "2025" in medium
        assert "November" in long or "2025" in long
    
    def test_priority_color_mapping(self, card_builder):
        """Test priority to color mapping"""
        assert card_builder._get_priority_color(TeamsPriority.CRITICAL) == "attention"
        assert card_builder._get_priority_color(TeamsPriority.HIGH) == "warning"
        assert card_builder._get_priority_color(TeamsPriority.MEDIUM) == "accent"
        assert card_builder._get_priority_color(TeamsPriority.LOW) == "good"
    
    def test_alert_icon_mapping(self, card_builder):
        """Test priority to alert icon mapping"""
        assert card_builder._get_alert_icon(TeamsPriority.CRITICAL) == "🚨"
        assert card_builder._get_alert_icon(TeamsPriority.HIGH) == "⚠️"
        assert card_builder._get_alert_icon(TeamsPriority.MEDIUM) == "ℹ️"
        assert card_builder._get_alert_icon(TeamsPriority.LOW) == "📝"


class TestActionGeneration:
    """Tests for Action.Execute button generation"""
    
    def test_acknowledge_action_always_present(self, card_builder, base_event_data):
        """Test that acknowledge action is present in all cards"""
        event = TeamsEvent(
            event_type=EventType.VAULT_SEAL_DETECTED,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.SRE],
            priority=TeamsPriority.CRITICAL,
            data={"node": "vault-01"}
        )
        
        card = card_builder.build_card(event)
        card_str = str(card)
        
        assert "acknowledge" in card_str.lower()
        assert base_event_data["correlation_id"] in card_str
    
    def test_escalate_action_for_high_priority(self, card_builder, base_event_data):
        """Test escalate action appears for high/critical priority"""
        event = TeamsEvent(
            event_type=EventType.NPHIES_API_ERROR,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.NPHIES_INTEGRATION],
            priority=TeamsPriority.CRITICAL,
            data={"error_type": "certificate", "error_message": "Certificate expired"}
        )
        
        card = card_builder.build_card(event)
        card_str = str(card)
        
        assert "escalate" in card_str.lower()
    
    def test_retry_discard_actions_for_task_failures(self, card_builder, base_event_data):
        """Test retry/discard actions for failed tasks"""
        event = TeamsEvent(
            event_type=EventType.CELERY_TASK_DLQ,
            correlation_id=base_event_data["correlation_id"],
            stakeholders=[StakeholderGroup.RUNTIME_ENG],
            priority=TeamsPriority.HIGH,
            data={
                "task_id": str(uuid4()),
                "task_name": "test_task",
                "retry_count": 5,
                "max_retries": 5,
                "error": "Max retries exceeded"
            }
        )
        
        card = card_builder.build_card(event)
        card_str = str(card)
        
        # Should have retry and discard actions for DLQ events
        assert "retry" in card_str.lower() or "Retry" in card_str
        assert "discard" in card_str.lower() or "Discard" in card_str


# Run tests with: pytest integrations/teams/tests/test_templates.py -v
