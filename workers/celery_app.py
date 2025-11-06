"""
Celery Application Instance for ClaimLinc-GIVC
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure, worker_ready
import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)

# Create Celery app
app = Celery('claimlinc')

# Load configuration
app.config_from_object('config.celery_config')

# Auto-discover tasks from workers.tasks package
app.autodiscover_tasks(['workers.tasks'])


@worker_ready.connect
def on_worker_ready(sender=None, **kwargs):
    """Initialize worker on startup"""
    logger.info(f"Celery worker ready: {sender.hostname}")
    
    # Verify Vault connectivity
    try:
        from config.security.vault_client import get_vault_client
        vault = get_vault_client()
        logger.info("Vault client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Vault client: {e}")
        raise


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """
    Pre-task execution hook
    - Add correlation ID for audit trail
    - Log task start
    """
    correlation_id = kwargs.get('correlation_id') if kwargs else None
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
        if kwargs:
            kwargs['correlation_id'] = correlation_id
    
    logger.info(
        f"Task started: {task.name}[{task_id}] - Correlation ID: {correlation_id}",
        extra={'correlation_id': correlation_id, 'task_id': task_id, 'task_name': task.name}
    )


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **extra):
    """
    Post-task execution hook
    - Log task completion
    - Record metrics
    """
    correlation_id = kwargs.get('correlation_id') if kwargs else None
    
    logger.info(
        f"Task completed: {task.name}[{task_id}] - State: {state}",
        extra={
            'correlation_id': correlation_id,
            'task_id': task_id,
            'task_name': task.name,
            'state': state
        }
    )


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, 
                        kwargs=None, traceback=None, einfo=None, **extra):
    """
    Task failure hook
    - Log failure with full traceback
    - Send alert to monitoring system
    - Write to DLQ if max retries exceeded
    """
    correlation_id = kwargs.get('correlation_id') if kwargs else None
    
    logger.error(
        f"Task failed: {sender.name}[{task_id}] - Exception: {exception}",
        extra={
            'correlation_id': correlation_id,
            'task_id': task_id,
            'task_name': sender.name,
            'exception': str(exception)
        },
        exc_info=einfo
    )
    
    # Send alert to monitoring system
    try:
        import requests
        alert_webhook = "https://monitoring.claimlinc.local/api/alerts"
        
        requests.post(
            alert_webhook,
            json={
                'event': 'celery_task_failure',
                'task_name': sender.name,
                'task_id': task_id,
                'correlation_id': correlation_id,
                'exception': str(exception),
                'traceback': str(traceback),
                'timestamp': __import__('datetime').datetime.utcnow().isoformat()
            },
            timeout=5
        )
    except Exception as e:
        logger.warning(f"Failed to send failure alert: {e}")


if __name__ == '__main__':
    app.start()
