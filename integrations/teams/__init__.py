"""
Microsoft Teams Integration Module for ClaimLinc-GIVC

This module provides real-time notification capabilities to Microsoft Teams
using Workflows app (Incoming Webhooks) and Adaptive Cards for stakeholder
collaboration across Security Eng., CloudOps, Runtime Eng., DevOps, SRE,
Compliance Office, Integration Team, and PMO.

Key Features:
- Event aggregation and normalization
- Adaptive Card template engine with Action.Execute
- HMAC signature verification for security
- Retry logic with exponential backoff
- Audit logging for HIPAA/PDPL compliance
- Redis pub/sub for event distribution

Usage:
    from integrations.teams import send_teams_notification

    send_teams_notification(
        event_type="vault.seal.detected",
        correlation_id="vault-seal-abc123",
        data={"node": "vault-node-2", "sealed_at": "2025-01-15T14:23:45Z"},
        stakeholders=["Security Eng.", "SRE", "CloudOps"],
        priority="critical"
    )
"""

from .event_aggregator import send_teams_notification, TeamsPriority
from .card_builder import AdaptiveCardBuilder
from .webhook_sender import TeamsWebhookSender
from .config import TeamsConfig

__all__ = [
    "send_teams_notification",
    "TeamsPriority",
    "AdaptiveCardBuilder",
    "TeamsWebhookSender",
    "TeamsConfig",
]

__version__ = "1.0.0"
