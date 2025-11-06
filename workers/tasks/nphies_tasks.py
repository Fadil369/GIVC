"""
Celery Tasks for ClaimLinc-GIVC
NPHIES integration tasks with idempotency and DLQ handling
"""

from celery import Task
from workers.celery_app import app
from typing import Dict, Any, Optional
import logging
import hashlib
import json
from datetime import datetime
import asyncio

# Teams integration
from integrations.teams.event_aggregator import send_teams_notification
from integrations.teams.models import TeamsEvent, EventType, TeamsPriority, StakeholderGroup

logger = logging.getLogger(__name__)


class IdempotentTask(Task):
    """
    Base task with idempotency support
    Prevents duplicate task execution using idempotency keys
    """
    
    def apply_async(self, args=None, kwargs=None, **options):
        """Override to inject idempotency key"""
        if kwargs is None:
            kwargs = {}
        
        # Generate idempotency key from task name + args
        if 'idempotency_key' not in kwargs:
            task_data = f"{self.name}:{str(args)}:{str(kwargs)}"
            kwargs['idempotency_key'] = hashlib.sha256(task_data.encode()).hexdigest()
        
        # Add correlation ID if not present
        if 'correlation_id' not in kwargs:
            from uuid import uuid4
            kwargs['correlation_id'] = str(uuid4())
        
        return super().apply_async(args, kwargs, **options)
    
    def __call__(self, *args, **kwargs):
        """Check idempotency before execution"""
        idempotency_key = kwargs.get('idempotency_key')
        correlation_id = kwargs.get('correlation_id')
        
        if idempotency_key:
            # Check if task already executed
            from config.security.vault_client import get_vault_client
            vault = get_vault_client()
            
            try:
                # Check Redis for idempotency key
                result = self.backend.get(f"idem:{idempotency_key}")
                if result:
                    logger.info(
                        f"Task {self.name} skipped (idempotent): {idempotency_key} "
                        f"[{correlation_id}]"
                    )
                    return json.loads(result)
            except Exception as e:
                logger.warning(f"Idempotency check failed: {e}")
        
        # Execute task
        result = super().__call__(*args, **kwargs)
        
        # Store idempotency result
        if idempotency_key:
            try:
                self.backend.set(
                    f"idem:{idempotency_key}",
                    json.dumps(result),
                    ex=86400  # 24 hours
                )
            except Exception as e:
                logger.warning(f"Failed to store idempotency result: {e}")
        
        return result


@app.task(
    base=IdempotentTask,
    bind=True,
    name='tasks.nphies.check_eligibility',
    max_retries=5,
    default_retry_delay=60
)
def check_nphies_eligibility(
    self,
    patient_data: Dict[str, Any],
    payer_code: str,
    correlation_id: Optional[str] = None,
    idempotency_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check patient eligibility via NPHIES
    
    Args:
        patient_data: Patient demographic and insurance information
        payer_code: Insurance payer code (e.g., '7001071327' for Bupa)
        correlation_id: Request correlation ID for audit trail
        idempotency_key: Idempotency key (auto-generated if not provided)
    
    Returns:
        Eligibility response with coverage details
    """
    try:
        logger.info(
            f"Checking NPHIES eligibility for patient {patient_data.get('member_id')} "
            f"with payer {payer_code} [{correlation_id}]"
        )
        
        # Import NPHIES client (lazy load)
        from nphies_sim.client import NPHIESClient
        
        client = NPHIESClient()
        
        # Build FHIR EligibilityRequest
        eligibility_request = client.build_eligibility_request(
            patient_data=patient_data,
            payer_code=payer_code,
            correlation_id=correlation_id
        )
        
        # Submit to NPHIES
        response = client.submit_eligibility_request(eligibility_request)
        
        # Log audit event
        logger.info(
            f"NPHIES eligibility check completed: {response.get('status')} [{correlation_id}]"
        )
        
        return {
            'status': 'success',
            'correlation_id': correlation_id,
            'eligibility_response': response,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        logger.error(
            f"NPHIES eligibility check failed: {exc} [{correlation_id}]",
            exc_info=True
        )
        
        # Send Teams notification for API errors
        try:
            asyncio.create_task(send_teams_notification(TeamsEvent(
                event_type=EventType.NPHIES_API_ERROR,
                correlation_id=correlation_id or self.request.id,
                stakeholders=[StakeholderGroup.NPHIES_INTEGRATION, StakeholderGroup.SRE],
                priority=TeamsPriority.HIGH,
                data={
                    "error_type": "api",
                    "operation": "check_eligibility",
                    "error_message": str(exc),
                    "patient_id": patient_data.get('member_id'),
                    "payer": payer_code
                }
            )))
        except Exception as teams_error:
            logger.warning(f"Failed to send Teams notification: {teams_error}")
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=min(2 ** self.request.retries * 60, 600))


@app.task(
    base=IdempotentTask,
    bind=True,
    name='tasks.nphies.submit_claim',
    max_retries=5,
    default_retry_delay=120
)
def submit_nphies_claim(
    self,
    claim_data: Dict[str, Any],
    payer_code: str,
    correlation_id: Optional[str] = None,
    idempotency_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Submit claim to NPHIES
    
    Args:
        claim_data: Complete claim information (services, diagnoses, etc.)
        payer_code: Insurance payer code
        correlation_id: Request correlation ID for audit trail
        idempotency_key: Idempotency key (auto-generated if not provided)
    
    Returns:
        Claim submission response with claim reference
    """
    try:
        logger.info(
            f"Submitting NPHIES claim {claim_data.get('claim_id')} "
            f"to payer {payer_code} [{correlation_id}]"
        )
        
        # Import NPHIES client
        from nphies_sim.client import NPHIESClient
        
        client = NPHIESClient()
        
        # Build FHIR Claim Bundle
        claim_bundle = client.build_claim_bundle(
            claim_data=claim_data,
            payer_code=payer_code,
            correlation_id=correlation_id
        )
        
        # Submit to NPHIES
        response = client.submit_claim(claim_bundle)
        
        # Schedule polling task for async response
        if response.get('is_async'):
            poll_nphies_response.apply_async(
                kwargs={
                    'nphies_request_id': response['request_id'],
                    'correlation_id': correlation_id
                },
                countdown=300  # Poll after 5 minutes
            )
        
        logger.info(
            f"NPHIES claim submitted: {response.get('status')} [{correlation_id}]"
        )
        
        # Send Teams notification for successful submission
        try:
            asyncio.create_task(send_teams_notification(TeamsEvent(
                event_type=EventType.NPHIES_CLAIM_SUBMITTED,
                correlation_id=correlation_id or self.request.id,
                stakeholders=[
                    StakeholderGroup.NPHIES_INTEGRATION,
                    StakeholderGroup.PMO,
                    StakeholderGroup.COMPLIANCE
                ],
                priority=TeamsPriority.INFO,
                data={
                    "claim_id": claim_data.get('claim_id'),
                    "poll_id": response.get('request_id'),
                    "patient_id": claim_data.get('patient_id'),
                    "provider": claim_data.get('provider_name'),
                    "payer": payer_code,
                    "total_amount": f"{claim_data.get('total_amount', 0)} SAR",
                    "services": [
                        {"description": s.get('description'), "amount": f"{s.get('amount', 0)} SAR"}
                        for s in claim_data.get('services', [])
                    ]
                }
            )))
        except Exception as teams_error:
            logger.warning(f"Failed to send Teams notification: {teams_error}")
        
        return {
            'status': 'success',
            'correlation_id': correlation_id,
            'claim_response': response,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        logger.error(
            f"NPHIES claim submission failed: {exc} [{correlation_id}]",
            exc_info=True
        )
        
        # Send Teams notification for submission failures
        try:
            # Determine error type
            error_type = "api"
            if "certificate" in str(exc).lower():
                error_type = "certificate"
            elif "jwt" in str(exc).lower() or "token" in str(exc).lower():
                error_type = "jwt"
            elif "timeout" in str(exc).lower() or "connection" in str(exc).lower():
                error_type = "network"
            
            asyncio.create_task(send_teams_notification(TeamsEvent(
                event_type=EventType.NPHIES_API_ERROR,
                correlation_id=correlation_id or self.request.id,
                stakeholders=[StakeholderGroup.NPHIES_INTEGRATION, StakeholderGroup.SRE],
                priority=TeamsPriority.HIGH if error_type == "certificate" else TeamsPriority.MEDIUM,
                data={
                    "error_type": error_type,
                    "operation": "submit_claim",
                    "error_message": str(exc),
                    "claim_id": claim_data.get('claim_id'),
                    "patient_id": claim_data.get('patient_id'),
                    "payer": payer_code
                }
            )))
        except Exception as teams_error:
            logger.warning(f"Failed to send Teams notification: {teams_error}")
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=min(2 ** self.request.retries * 120, 1800))


@app.task(
    base=IdempotentTask,
    bind=True,
    name='tasks.nphies.poll_response',
    max_retries=20,
    default_retry_delay=300
)
def poll_nphies_response(
    self,
    nphies_request_id: str,
    correlation_id: Optional[str] = None,
    idempotency_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Poll NPHIES for async claim response
    
    Args:
        nphies_request_id: NPHIES request tracking ID
        correlation_id: Original request correlation ID
        idempotency_key: Idempotency key
    
    Returns:
        Final claim adjudication result
    """
    try:
        logger.info(
            f"Polling NPHIES for response to request {nphies_request_id} [{correlation_id}]"
        )
        
        from nphies_sim.client import NPHIESClient
        
        client = NPHIESClient()
        
        # Poll for response
        response = client.poll_response(nphies_request_id)
        
        if response.get('status') == 'pending':
            # Still processing, retry
            logger.info(f"NPHIES response pending, will retry [{correlation_id}]")
            raise self.retry(countdown=300)  # Retry in 5 minutes
        
        logger.info(
            f"NPHIES response received: {response.get('status')} [{correlation_id}]"
        )
        
        # Update claim status in database
        from api.main import update_claim_status
        update_claim_status(
            nphies_request_id=nphies_request_id,
            status=response['status'],
            adjudication=response.get('adjudication')
        )
        
        # Send Teams notification based on claim outcome
        try:
            adjudication = response.get('adjudication', {})
            claim_status = response.get('status', '').lower()
            
            if claim_status == 'approved' or 'approved' in claim_status:
                # Claim approved
                asyncio.create_task(send_teams_notification(TeamsEvent(
                    event_type=EventType.NPHIES_CLAIM_APPROVED,
                    correlation_id=correlation_id or self.request.id,
                    stakeholders=[
                        StakeholderGroup.NPHIES_INTEGRATION,
                        StakeholderGroup.PMO,
                        StakeholderGroup.COMPLIANCE
                    ],
                    priority=TeamsPriority.INFO,
                    data={
                        "claim_id": adjudication.get('claim_id'),
                        "approval_number": adjudication.get('approval_number'),
                        "patient_id": adjudication.get('patient_id'),
                        "payer": adjudication.get('payer'),
                        "approved_amount": f"{adjudication.get('approved_amount', 0)} SAR",
                        "net_amount": f"{adjudication.get('net_amount', 0)} SAR",
                        "patient_share": f"{adjudication.get('patient_share', 0)} SAR",
                        "payer_share": f"{adjudication.get('payer_share', 0)} SAR",
                        "notes": adjudication.get('notes')
                    }
                )))
            elif claim_status == 'rejected' or 'rejected' in claim_status or 'denied' in claim_status:
                # Claim rejected
                asyncio.create_task(send_teams_notification(TeamsEvent(
                    event_type=EventType.NPHIES_CLAIM_REJECTED,
                    correlation_id=correlation_id or self.request.id,
                    stakeholders=[
                        StakeholderGroup.NPHIES_INTEGRATION,
                        StakeholderGroup.PMO,
                        StakeholderGroup.COMPLIANCE
                    ],
                    priority=TeamsPriority.HIGH,
                    data={
                        "claim_id": adjudication.get('claim_id'),
                        "patient_id": adjudication.get('patient_id'),
                        "payer": adjudication.get('payer'),
                        "rejection_code": adjudication.get('rejection_code'),
                        "rejection_reason": adjudication.get('rejection_reason'),
                        "errors": adjudication.get('errors', [])
                    }
                )))
        except Exception as teams_error:
            logger.warning(f"Failed to send Teams notification: {teams_error}")
        
        return {
            'status': 'success',
            'correlation_id': correlation_id,
            'nphies_response': response,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        logger.error(
            f"NPHIES polling failed: {exc} [{correlation_id}]",
            exc_info=True
        )
        
        # Retry up to 20 times (100 minutes)
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=300)
        else:
            # Max retries exceeded, send to DLQ
            logger.error(
                f"NPHIES polling max retries exceeded for {nphies_request_id} [{correlation_id}]"
            )
            raise


@app.task(name='tasks.general.cleanup_expired_results')
def cleanup_expired_results():
    """
    Periodic task to cleanup expired task results from Redis
    Runs daily to maintain Redis memory usage
    """
    logger.info("Starting cleanup of expired task results")
    
    try:
        from celery.result import AsyncResult
        import redis
        
        # Connect to Redis
        r = redis.from_url(app.conf.result_backend, decode_responses=True)
        
        # Scan for expired keys
        cursor = 0
        deleted_count = 0
        
        while True:
            cursor, keys = r.scan(cursor, match="celery-task-meta-*", count=1000)
            
            for key in keys:
                ttl = r.ttl(key)
                if ttl == -1:  # No expiration set
                    r.expire(key, 86400)  # Set 24h expiration
                elif ttl < 0:  # Expired
                    r.delete(key)
                    deleted_count += 1
            
            if cursor == 0:
                break
        
        logger.info(f"Cleanup completed: {deleted_count} expired results removed")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}", exc_info=True)
        raise


@app.task(name='tasks.general.renew_vault_credentials')
def renew_vault_credentials():
    """
    Periodic task to renew Vault dynamic credentials
    Runs hourly to ensure workers have valid credentials
    """
    logger.info("Renewing Vault credentials")
    
    try:
        from config.security.vault_client import get_vault_client
        
        vault = get_vault_client()
        
        # Force re-authentication
        vault._authenticate()
        
        logger.info("Vault credentials renewed successfully")
        
        return {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Vault credential renewal failed: {e}", exc_info=True)
        raise


# Periodic task schedule
app.conf.beat_schedule = {
    'cleanup-expired-results': {
        'task': 'tasks.general.cleanup_expired_results',
        'schedule': 86400.0,  # Daily
    },
    'renew-vault-credentials': {
        'task': 'tasks.general.renew_vault_credentials',
        'schedule': 3600.0,  # Hourly
    },
}
