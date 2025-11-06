"""
Adaptive Card Builder

Builds Adaptive Cards from Jinja2 templates with dynamic data binding.
Supports Action.Execute patterns, conditional rendering, and template validation.
"""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from datetime import datetime

from .config import get_config
from .models import TeamsEvent, EventType, TeamsPriority, StakeholderGroup

logger = logging.getLogger(__name__)

# Convenience alias for backward compatibility
CardBuilder = None  # Will be set after class definition


class AdaptiveCardBuilder:
    """
    Builds Adaptive Cards from Jinja2 templates.
    
    Features:
    - Template-based card generation
    - Dynamic data binding with Jinja2
    - Priority-based styling
    - Timestamp formatting
    - Template caching
    """

    def __init__(self):
        self.config = get_config()
        self.template_dir = Path(self.config.template_dir)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['format_datetime'] = self._format_datetime
        self.env.filters['format_priority'] = self._format_priority
        self.env.filters['format_stakeholders'] = self._format_stakeholders

        # Template mapping
        self.template_map = {
            # Vault events
            EventType.VAULT_SEAL_DETECTED: "vault_security_event.json",
            EventType.VAULT_UNSEAL_FAILED: "vault_security_event.json",
            EventType.VAULT_AUDIT_DISABLED: "vault_security_event.json",
            EventType.VAULT_TOKEN_RENEWAL_FAILED: "vault_security_event.json",
            EventType.VAULT_SECRET_ROTATION_COMPLETE: "vault_security_event.json",
            EventType.VAULT_CERTIFICATE_EXPIRING: "vault_security_event.json",
            
            # Celery events
            EventType.CELERY_TASK_FAILURE: "celery_task_failure.json",
            EventType.CELERY_TASK_FAILED: "celery_task_failure.json",
            EventType.CELERY_TASK_RETRY: "celery_task_failure.json",
            EventType.CELERY_TASK_TIMEOUT: "celery_task_failure.json",
            EventType.CELERY_DLQ_THRESHOLD: "celery_task_failure.json",
            EventType.CELERY_WORKER_OFFLINE: "celery_task_failure.json",
            EventType.CELERY_QUEUE_BACKLOG: "celery_task_failure.json",
            EventType.CELERY_TASK_DLQ: "celery_task_failure.json",
            
            # NPHIES events
            EventType.NPHIES_ELIGIBILITY_SUCCESS: "nphies_eligibility.json",
            EventType.NPHIES_ELIGIBILITY_DENIED: "nphies_eligibility.json",
            EventType.NPHIES_ELIGIBILITY_FAILED: "nphies_eligibility.json",
            EventType.NPHIES_CLAIM_SUBMITTED: "nphies_claim_submission.json",
            EventType.NPHIES_CLAIM_APPROVED: "nphies_claim_approved.json",
            EventType.NPHIES_CLAIM_REJECTED: "nphies_claim_rejected.json",
            EventType.NPHIES_API_ERROR: "nphies_api_error.json",
            EventType.NPHIES_CERTIFICATE_INVALID: "nphies_api_error.json",
            EventType.NPHIES_JWT_EXPIRED: "nphies_api_error.json",
            EventType.NPHIES_JWT_ERROR: "nphies_api_error.json",
            
            # Follow-up events
            EventType.FOLLOW_UP_STATUS: "follow_up_status.json",

            # System events
            EventType.SYSTEM_RABBITMQ_NODE_DOWN: "system_alert.json",
            EventType.SYSTEM_POSTGRES_REPLICATION_LAG: "system_alert.json",
            EventType.RABBITMQ_NODE_DOWN: "system_alert.json",
            EventType.REDIS_REPLICA_LAGGING: "system_alert.json",
            EventType.POSTGRES_CONNECTION_EXHAUSTED: "system_alert.json",
            EventType.KUBERNETES_POD_CRASHLOOP: "system_alert.json",
            EventType.PROMETHEUS_ALERT_FIRING: "system_alert.json",
            EventType.BACKUP_FAILED: "system_alert.json",
        }

    def _format_datetime(self, dt: Any, format: str = "SHORT") -> str:
        """Format datetime for Adaptive Card display."""
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            except ValueError:
                return dt
        
        if not isinstance(dt, datetime):
            return str(dt)
        
        if format == "SHORT":
            return dt.strftime("%Y-%m-%d %H:%M UTC")
        elif format == "LONG":
            return dt.strftime("%B %d, %Y at %H:%M:%S UTC")
        else:
            return dt.isoformat()

    def _format_priority(self, priority: TeamsPriority) -> str:
        """Format priority with emoji and color."""
        priority_map = {
            TeamsPriority.CRITICAL: "🔴 Critical",
            TeamsPriority.HIGH: "🟠 High",
            TeamsPriority.MEDIUM: "🟡 Medium",
            TeamsPriority.LOW: "🟢 Low",
            TeamsPriority.INFO: "🔵 Info"
        }
        return priority_map.get(priority, str(priority.value).upper())

    def _format_stakeholders(self, stakeholders: list) -> str:
        """Format stakeholders list as comma-separated string."""
        friendly_names = {
            StakeholderGroup.SECURITY_ENG: "Security Engineering",
            StakeholderGroup.CLOUDOPS: "Cloud Operations",
            StakeholderGroup.RUNTIME_ENG: "Runtime Engineering",
            StakeholderGroup.DEVOPS: "DevOps",
            StakeholderGroup.SRE: "SRE",
            StakeholderGroup.COMPLIANCE: "Compliance Office",
            StakeholderGroup.NPHIES_INTEGRATION: "NPHIES Integration",
            StakeholderGroup.PMO: "PMO",
        }

        formatted = []
        for stakeholder in stakeholders:
            if hasattr(stakeholder, "value"):
                formatted.append(friendly_names.get(stakeholder, stakeholder.value))
            else:
                formatted.append(str(stakeholder))
        return ", ".join(formatted)

    def _get_priority_color(self, priority: TeamsPriority) -> str:
        """Get Adaptive Card container color for priority."""
        color_map = {
            TeamsPriority.CRITICAL: "attention",
            TeamsPriority.HIGH: "warning",
            TeamsPriority.MEDIUM: "accent",
            TeamsPriority.LOW: "good",
            TeamsPriority.INFO: "default"
        }
        return color_map.get(priority, "default")

    def _get_alert_icon(self, priority: TeamsPriority) -> str:
        """Get alert icon emoji for priority."""
        icon_map = {
            TeamsPriority.CRITICAL: "🚨",
            TeamsPriority.HIGH: "⚠️",
            TeamsPriority.MEDIUM: "ℹ️",
            TeamsPriority.LOW: "📝",
            TeamsPriority.INFO: "📢"
        }
        return icon_map.get(priority, "📢")

    def _enrich_data(self, event: TeamsEvent) -> Dict[str, Any]:
        """
        Enrich event data with additional context.
        
        Args:
            event: TeamsEvent object
            
        Returns:
            Enriched data dictionary for template rendering
        """
        enriched = {
            # Event metadata
            "event_type": event.event_type.value,
            "correlation_id": event.correlation_id,
            "timestamp": event.timestamp,
            "priority": event.priority,
            "priority_formatted": self._format_priority(event.priority),
            "priority_color": self._get_priority_color(event.priority),
            "alert_icon": self._get_alert_icon(event.priority),
            "stakeholders": event.stakeholders,
            "stakeholders_formatted": self._format_stakeholders(event.stakeholders),
            
            # Event-specific data
            **event.data,
            "data": event.data,
            "event": event,
            
            # URLs (from config or environment)
            "grafana_url": "https://grafana.claimlinc.sa",
            "flower_url": "https://flower.claimlinc.sa",
            "kibana_url": "https://kibana.claimlinc.sa",
            "nphies_portal_url": "https://portal.nphies.sa",
            "nphies_status_url": "https://status.nphies.sa",
            "nphies_docs_url": "https://docs.nphies.sa",
            "claimlinc_url": "https://claimlinc.sa",
            
            # Runbook URLs (template-specific)
            "vault_runbook_url": "https://docs.claimlinc.sa/runbooks/vault-seal-recovery",
            "celery_runbook_url": "https://docs.claimlinc.sa/runbooks/celery-task-recovery",
            "nphies_runbook_url": "https://docs.claimlinc.sa/runbooks/nphies-integration",
        }
        
        return enriched

    def build_card(self, event: TeamsEvent) -> Dict[str, Any]:
        """
        Build Adaptive Card from event.
        
        Args:
            event: TeamsEvent object
            
        Returns:
            Adaptive Card JSON payload as dictionary
            
        Raises:
            ValueError: If template not found for event type
            TemplateNotFound: If template file doesn't exist
        """
        # Get template name
        template_name = self.template_map.get(event.event_type)
        if not template_name:
            raise ValueError(f"No template found for event type: {event.event_type}")

        logger.debug(
            f"Building card from template: {template_name}",
            extra={"correlation_id": event.correlation_id}
        )

        try:
            # Load template
            template = self.env.get_template(template_name)
            
            # Enrich data
            data = self._enrich_data(event)
            
            # Render template
            rendered = template.render(**data)
            
            # Parse JSON
            card_payload = json.loads(rendered)
            
            # Validate basic structure
            if not isinstance(card_payload, dict):
                raise ValueError("Template must render to JSON object")
            
            if card_payload.get("type") != "message":
                # Wrap in message envelope if not already
                card_payload = {
                    "type": "message",
                    "attachments": [
                        {
                            "contentType": "application/vnd.microsoft.card.adaptive",
                            "content": card_payload
                        }
                    ]
                }
            
            logger.info(
                f"Successfully built Adaptive Card",
                extra={
                    "correlation_id": event.correlation_id,
                    "template": template_name,
                    "event_type": event.event_type.value
                }
            )
            
            return card_payload
            
        except TemplateNotFound:
            logger.error(
                f"Template not found: {template_name}",
                extra={"correlation_id": event.correlation_id}
            )
            # Return fallback generic card
            return self._build_fallback_card(event)
        except json.JSONDecodeError as exc:
            logger.error(
                f"Invalid JSON in template {template_name}: {exc}",
                extra={"correlation_id": event.correlation_id}
            )
            return self._build_fallback_card(event)
        except Exception as exc:
            logger.exception(
                f"Failed to build card from template {template_name}: {exc}",
                extra={"correlation_id": event.correlation_id}
            )
            return self._build_fallback_card(event)

    def _build_fallback_card(self, event: TeamsEvent) -> Dict[str, Any]:
        """
        Build a generic fallback card when template rendering fails.
        
        Args:
            event: TeamsEvent object
            
        Returns:
            Generic Adaptive Card JSON payload
        """
        logger.warning(
            f"Using fallback card for event",
            extra={"correlation_id": event.correlation_id}
        )
        
        return {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "version": "1.5",
                        "body": [
                            {
                                "type": "Container",
                                "style": self._get_priority_color(event.priority),
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"⚠️ {event.event_type.value.replace('_', ' ').title()}",
                                        "weight": "bolder",
                                        "size": "large"
                                    }
                                ]
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {
                                        "title": "Priority:",
                                        "value": self._format_priority(event.priority)
                                    },
                                    {
                                        "title": "Event Type:",
                                        "value": event.event_type.value
                                    },
                                    {
                                        "title": "Correlation ID:",
                                        "value": event.correlation_id
                                    },
                                    {
                                        "title": "Timestamp:",
                                        "value": self._format_datetime(event.timestamp)
                                    },
                                    {
                                        "title": "Stakeholders:",
                                        "value": self._format_stakeholders(event.stakeholders)
                                    }
                                ]
                            },
                            {
                                "type": "TextBlock",
                                "text": json.dumps(event.data, indent=2),
                                "wrap": True,
                                "fontType": "monospace",
                                "spacing": "medium"
                            }
                        ],
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
                    }
                }
            ]
        }


# Export alias for backward compatibility
CardBuilder = AdaptiveCardBuilder
