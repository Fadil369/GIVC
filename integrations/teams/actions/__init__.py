"""Action handlers for Teams Adaptive Card interactions."""

from .acknowledge_handler import handle_acknowledge
from .escalate_handler import handle_escalate
from .retry_handler import handle_retry_task
from .discard_handler import handle_discard_task

__all__ = [
    "handle_acknowledge",
    "handle_escalate",
    "handle_retry_task",
    "handle_discard_task",
]
