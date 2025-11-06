"""
Acknowledge Handler

Handles acknowledgment actions from Teams Adaptive Cards.
Updates audit records and sends confirmation cards.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update

from ..config import get_config
from ..models import ActionHandlerRequest, ActionHandlerResponse, NotificationAuditRecord

logger = logging.getLogger(__name__)


class AcknowledgeHandler:
    """Handles acknowledgment actions from Teams cards."""

    def __init__(self):
        self.config = get_config()
        self.engine = create_async_engine(self.config.postgres_dsn)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def handle(self, request: ActionHandlerRequest) -> ActionHandlerResponse:
        """
        Handle acknowledgment action.
        
        Args:
            request: ActionHandlerRequest with correlation_id and user info
            
        Returns:
            ActionHandlerResponse with updated card
        """
        logger.info(
            f"Processing acknowledgment",
            extra={
                "correlation_id": request.correlation_id,
                "user": request.user_email
            }
        )

        try:
            # Update audit record
            async with self.async_session() as session:
                async with session.begin():
                    stmt = update(NotificationAuditRecord.__table__).where(
                        NotificationAuditRecord.__table__.c.correlation_id == request.correlation_id
                    ).values(
                        acknowledged_by=request.user_email,
                        acknowledged_at=datetime.utcnow()
                    )
                    result = await session.execute(stmt)
                    await session.commit()
                    
                    if result.rowcount == 0:
                        logger.warning(
                            f"No audit record found for correlation_id: {request.correlation_id}"
                        )

            # Build acknowledgment confirmation card
            updated_card = self._build_acknowledgment_card(request)

            return ActionHandlerResponse(
                success=True,
                message=f"Acknowledged by {request.user_name or request.user_email}",
                updated_card=updated_card,
                error=None
            )

        except Exception as exc:
            logger.exception(
                f"Failed to process acknowledgment: {exc}",
                extra={"correlation_id": request.correlation_id}
            )
            return ActionHandlerResponse(
                success=False,
                message="Failed to process acknowledgment",
                updated_card=None,
                error=str(exc)
            )

    def _build_acknowledgment_card(self, request: ActionHandlerRequest) -> Dict[str, Any]:
        """Build confirmation card after acknowledgment."""
        return {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "style": "good",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "✅ Acknowledged",
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
                            "title": "Acknowledged by:",
                            "value": request.user_name or request.user_email
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
                    "text": "This event has been acknowledged. Thank you for your response.",
                    "wrap": True,
                    "spacing": "medium"
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }


# Global handler instance
_handler = None


async def handle_acknowledge(request: ActionHandlerRequest) -> ActionHandlerResponse:
    """
    Handle acknowledgment action (convenience function).
    
    Args:
        request: ActionHandlerRequest
        
    Returns:
        ActionHandlerResponse
    """
    global _handler
    if _handler is None:
        _handler = AcknowledgeHandler()
    return await _handler.handle(request)
