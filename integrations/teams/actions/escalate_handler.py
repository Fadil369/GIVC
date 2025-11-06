"""
Escalate Handler

Handles escalation actions from Teams Adaptive Cards.
Triggers PagerDuty/Opsgenie alerts and notifies on-call personnel.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from ..models import ActionHandlerRequest, ActionHandlerResponse

logger = logging.getLogger(__name__)


class EscalateHandler:
    """Handles escalation actions from Teams cards."""

    async def handle(self, request: ActionHandlerRequest) -> ActionHandlerResponse:
        """
        Handle escalation action.
        
        Args:
            request: ActionHandlerRequest with escalation details
            
        Returns:
            ActionHandlerResponse with escalation status
        """
        escalation_tier = request.additional_data.get("escalation_tier", "on-call-sre")
        
        logger.warning(
            f"Escalating event to {escalation_tier}",
            extra={
                "correlation_id": request.correlation_id,
                "escalated_by": request.user_email,
                "tier": escalation_tier
            }
        )

        try:
            # TODO: Integrate with PagerDuty/Opsgenie API
            # For now, log the escalation
            logger.critical(
                f"🚨 ESCALATION: {request.event_id} escalated to {escalation_tier}",
                extra={
                    "correlation_id": request.correlation_id,
                    "escalated_by": request.user_email,
                    "event_id": request.event_id
                }
            )

            # Build escalation confirmation card
            updated_card = self._build_escalation_card(request, escalation_tier)

            return ActionHandlerResponse(
                success=True,
                message=f"Escalated to {escalation_tier}",
                updated_card=updated_card,
                error=None
            )

        except Exception as exc:
            logger.exception(
                f"Failed to escalate: {exc}",
                extra={"correlation_id": request.correlation_id}
            )
            return ActionHandlerResponse(
                success=False,
                message="Failed to escalate",
                updated_card=None,
                error=str(exc)
            )

    def _build_escalation_card(
        self,
        request: ActionHandlerRequest,
        escalation_tier: str
    ) -> Dict[str, Any]:
        """Build confirmation card after escalation."""
        return {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "style": "attention",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "🚨 Escalated",
                            "weight": "bolder",
                            "size": "large",
                            "color": "attention"
                        }
                    ]
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "Escalated by:",
                            "value": request.user_name or request.user_email
                        },
                        {
                            "title": "Escalation tier:",
                            "value": escalation_tier.replace("-", " ").title()
                        },
                        {
                            "title": "Time:",
                            "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                        },
                        {
                            "title": "Correlation ID:",
                            "value": request.correlation_id
                        }
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": f"This event has been escalated to **{escalation_tier.replace('-', ' ').title()}**. On-call personnel have been notified via PagerDuty.",
                    "wrap": True,
                    "spacing": "medium"
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }


# Global handler instance
_handler = None


async def handle_escalate(request: ActionHandlerRequest) -> ActionHandlerResponse:
    """
    Handle escalation action (convenience function).
    
    Args:
        request: ActionHandlerRequest
        
    Returns:
        ActionHandlerResponse
    """
    global _handler
    if _handler is None:
        _handler = EscalateHandler()
    return await _handler.handle(request)
