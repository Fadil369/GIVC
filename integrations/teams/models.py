"""
Pydantic Models for Teams Integration

Defines data models for events, notifications, card payloads, and audit records
to ensure type safety and validation throughout the Teams integration module.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from enum import Enum
import uuid


class TeamsPriority(str, Enum):
    """Priority levels for Teams notifications."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventType(str, Enum):
    """Supported event types for Teams notifications."""
    # Vault events
    VAULT_SEAL_DETECTED = "vault.seal.detected"
    VAULT_UNSEAL_FAILED = "vault.unseal.failed"
    VAULT_AUDIT_DISABLED = "vault.audit.disabled"
    VAULT_TOKEN_RENEWAL_FAILED = "vault.token.renewal.failed"
    VAULT_SECRET_ROTATION_COMPLETE = "vault.secret.rotation.complete"
    VAULT_CERTIFICATE_EXPIRING = "vault.certificate.expiring"
    
    # Celery events
    CELERY_TASK_FAILED = "celery.task.failed"
    CELERY_TASK_FAILURE = "celery.task.failure"  # Alias for template
    CELERY_TASK_RETRY = "celery.task.retry"
    CELERY_TASK_TIMEOUT = "celery.task.timeout"
    CELERY_TASK_DLQ = "celery.task.dlq"  # DLQ exhausted
    CELERY_DLQ_THRESHOLD = "celery.dlq.threshold"
    CELERY_WORKER_OFFLINE = "celery.worker.offline"
    CELERY_QUEUE_BACKLOG = "celery.queue.backlog"
    
    # NPHIES events
    NPHIES_ELIGIBILITY_SUCCESS = "nphies.eligibility.success"
    NPHIES_ELIGIBILITY_DENIED = "nphies.eligibility.denied"
    NPHIES_ELIGIBILITY_FAILED = "nphies.eligibility.failed"
    NPHIES_CLAIM_SUBMITTED = "nphies.claim.submitted"
    NPHIES_CLAIM_APPROVED = "nphies.claim.approved"
    NPHIES_CLAIM_REJECTED = "nphies.claim.rejected"
    NPHIES_API_ERROR = "nphies.api.error"
    NPHIES_CERTIFICATE_INVALID = "nphies.certificate.invalid"
    NPHIES_JWT_ERROR = "nphies.jwt.error"  # JWT validation error
    NPHIES_JWT_EXPIRED = "nphies.jwt.expired"
    
    # Follow-up events
    FOLLOW_UP_STATUS = "followup.batch.status"

    # System events
    SYSTEM_RABBITMQ_NODE_DOWN = "system.rabbitmq.node_down"  # Match template naming
    SYSTEM_POSTGRES_REPLICATION_LAG = "system.postgres.replication_lag"  # Match template naming
    RABBITMQ_NODE_DOWN = "rabbitmq.node.down"  # Alias
    REDIS_REPLICA_LAGGING = "redis.replica.lagging"
    POSTGRES_CONNECTION_EXHAUSTED = "postgres.connection.exhausted"
    KUBERNETES_POD_CRASHLOOP = "kubernetes.pod.crashloop"
    PROMETHEUS_ALERT_FIRING = "prometheus.alert.firing"
    BACKUP_FAILED = "backup.failed"


class StakeholderGroup(str, Enum):
    """Stakeholder groups for notification routing."""
    SECURITY_ENG = "Security Eng."
    CLOUDOPS = "CloudOps"
    RUNTIME_ENG = "Runtime Eng."
    DEVOPS = "DevOps"
    SRE = "SRE"
    COMPLIANCE = "Compliance Office"
    NPHIES_INTEGRATION = "NPHIES Integration"  # Match with code usage
    PMO = "PMO"


class TeamsEvent(BaseModel):
    """Base model for all Teams notification events."""
    event_type: EventType
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:8]}")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: TeamsPriority
    stakeholders: List[StakeholderGroup]
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, v):
        """Ensure correlation_id is not empty."""
        if not v or not v.strip():
            raise ValueError("correlation_id cannot be empty")
        return v
    
    @field_validator("stakeholders")
    @classmethod
    def validate_stakeholders(cls, v):
        """Ensure at least one stakeholder is specified."""
        if not v:
            raise ValueError("At least one stakeholder must be specified")
        return v


class AdaptiveCardAction(BaseModel):
    """Adaptive Card Action.Execute model."""
    type: Literal["Action.Execute"] = "Action.Execute"
    title: str
    verb: str
    data: Dict[str, Any] = Field(default_factory=dict)
    associatedInputs: Optional[str] = "auto"
    style: Optional[Literal["default", "positive", "destructive"]] = "default"


class AdaptiveCardFact(BaseModel):
    """Adaptive Card Fact model for FactSet."""
    title: str
    value: str


class TeamsNotification(BaseModel):
    """Model for a complete Teams notification."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event: TeamsEvent
    card_payload: Dict[str, Any]
    webhook_urls: List[str]
    sent_at: Optional[datetime] = None
    status_code: Optional[int] = None
    retry_count: int = 0
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v),
        }


class NotificationAuditRecord(BaseModel):
    """Audit record for Teams notification (persisted to PostgreSQL)."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    correlation_id: str
    event_type: str
    stakeholders: List[str]
    priority: str
    webhook_url: str
    card_payload: Dict[str, Any]
    sent_at: datetime
    status_code: Optional[int]
    retry_count: int
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v),
        }


class ActionHandlerRequest(BaseModel):
    """Model for incoming action handler requests from Teams."""
    action: str
    event_id: str
    correlation_id: str
    user_email: str
    user_name: Optional[str] = None
    additional_data: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        """Validate action is one of the supported actions."""
        valid_actions = ["acknowledge", "escalate", "retry_task", "discard_task", "poll_nphies"]
        if v not in valid_actions:
            raise ValueError(f"Unsupported action: {v}. Must be one of {valid_actions}")
        return v


class ActionHandlerResponse(BaseModel):
    """Response model for action handlers."""
    success: bool
    message: str
    updated_card: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
