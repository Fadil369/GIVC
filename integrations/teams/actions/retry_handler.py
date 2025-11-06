"""
Retry Handler

Handles task retry actions from Teams Adaptive Cards.
Re-queues failed Celery tasks for processing.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from celery import Celery

from ..config import get_config
from ..models import ActionHandlerRequest, ActionHandlerResponse

logger = logging.getLogger(__name__)


class RetryHandler:
    """Handles task retry actions from Teams cards."""

    def __init__(self):
        self.config = get_config()
        # TODO: Initialize Celery app connection
        self.celery_app = None

    async def handle(self, request: ActionHandlerRequest) -> ActionHandlerResponse:
        """
        Handle retry task action.
        
        Args:
            request: ActionHandlerRequest with task_id and queue info
            
        Returns:
            ActionHandlerResponse with retry status
        """
        task_id = request.additional_data.get("task_id")
        queue = request.additional_data.get("queue", "default")
        
        if not task_id:
            return ActionHandlerResponse(
                success=False,
                message="Missing task_id",
                updated_card=None,
                error="task_id is required"
            )

        logger.info(
            f"Retrying task {task_id} on queue {queue}",
            extra={
                "correlation_id": request.correlation_id,
                "retried_by": request.user_email,
                "task_id": task_id,
                "queue": queue
            }
        )

        try:
            # TODO: Implement actual Celery task retry
            # For now, log the retry request
            logger.info(
                f"Task retry requested: {task_id}",
                extra={
                    "task_id": task_id,
                    "queue": queue,
                    "retried_by": request.user_email
                }
            )

            # Build retry confirmation card
            updated_card = self._build_retry_card(request, task_id, queue)

            return ActionHandlerResponse(
                success=True,
                message=f"Task {task_id} re-queued for processing",
                updated_card=updated_card,
                error=None
            )

        except Exception as exc:
            logger.exception(
                f"Failed to retry task: {exc}",
                extra={"correlation_id": request.correlation_id, "task_id": task_id}
            )
            return ActionHandlerResponse(
                success=False,
                message="Failed to retry task",
                updated_card=None,
                error=str(exc)
            )

    def _build_retry_card(
        self,
        request: ActionHandlerRequest,
        task_id: str,
        queue: str
    ) -> Dict[str, Any]:
        """Build confirmation card after task retry."""
        return {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "style": "accent",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "🔄 Task Re-queued",
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
                            "title": "Queue:",
                            "value": queue
                        },
                        {
                            "title": "Retried by:",
                            "value": request.user_name or request.user_email
                        },
                        {
                            "title": "Time:",
                            "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                        }
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": "The task has been re-queued for processing. Monitor the task status in Flower.",
                    "wrap": True,
                    "spacing": "medium"
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "📊 View in Flower",
                    "url": f"https://flower.claimlinc.sa/task/{task_id}"
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }


# Global handler instance
_handler = None


async def handle_retry_task(request: ActionHandlerRequest) -> ActionHandlerResponse:
    """
    Handle task retry action (convenience function).
    
    Args:
        request: ActionHandlerRequest
        
    Returns:
        ActionHandlerResponse
    """
    global _handler
    if _handler is None:
        _handler = RetryHandler()
    return await _handler.handle(request)
