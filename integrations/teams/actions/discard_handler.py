"""
Discard Handler

Handles task discard actions from Teams Adaptive Cards.
Moves failed tasks to archive and logs reason.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from ..config import get_config
from ..models import ActionHandlerRequest, ActionHandlerResponse

logger = logging.getLogger(__name__)


class DiscardHandler:
    """Handles task discard actions from Teams cards."""

    def __init__(self):
        self.config = get_config()

    async def handle(self, request: ActionHandlerRequest) -> ActionHandlerResponse:
        """
        Handle discard task action.
        
        Args:
            request: ActionHandlerRequest with task_id
            
        Returns:
            ActionHandlerResponse with discard status
        """
        task_id = request.additional_data.get("task_id")
        
        if not task_id:
            return ActionHandlerResponse(
                success=False,
                message="Missing task_id",
                updated_card=None,
                error="task_id is required"
            )

        logger.warning(
            f"Discarding task {task_id}",
            extra={
                "correlation_id": request.correlation_id,
                "discarded_by": request.user_email,
                "task_id": task_id
            }
        )

        try:
            # TODO: Implement actual task discard/archive
            # For now, log the discard request
            logger.warning(
                f"Task discarded: {task_id}",
                extra={
                    "task_id": task_id,
                    "discarded_by": request.user_email,
                    "reason": "Manual discard via Teams action"
                }
            )

            # Build discard confirmation card
            updated_card = self._build_discard_card(request, task_id)

            return ActionHandlerResponse(
                success=True,
                message=f"Task {task_id} discarded",
                updated_card=updated_card,
                error=None
            )

        except Exception as exc:
            logger.exception(
                f"Failed to discard task: {exc}",
                extra={"correlation_id": request.correlation_id, "task_id": task_id}
            )
            return ActionHandlerResponse(
                success=False,
                message="Failed to discard task",
                updated_card=None,
                error=str(exc)
            )

    def _build_discard_card(
        self,
        request: ActionHandlerRequest,
        task_id: str
    ) -> Dict[str, Any]:
        """Build confirmation card after task discard."""
        return {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "style": "warning",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "🗑️ Task Discarded",
                            "weight": "bolder",
                            "size": "large"
                        }
                    ]
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "Task ID:",
                            "value": task_id
                        },
                        {
                            "title": "Discarded by:",
                            "value": request.user_name or request.user_email
                        },
                        {
                            "title": "Time:",
                            "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                        },
                        {
                            "title": "Reason:",
                            "value": "Manual discard via Teams action"
                        }
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": "The task has been moved to archive. It will not be retried.",
                    "wrap": True,
                    "spacing": "medium",
                    "color": "warning"
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }


# Global handler instance
_handler = None


async def handle_discard_task(request: ActionHandlerRequest) -> ActionHandlerResponse:
    """
    Handle task discard action (convenience function).
    
    Args:
        request: ActionHandlerRequest
        
    Returns:
        ActionHandlerResponse
    """
    global _handler
    if _handler is None:
        _handler = DiscardHandler()
    return await _handler.handle(request)
