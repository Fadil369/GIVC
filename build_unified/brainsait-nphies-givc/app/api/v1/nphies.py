"""
NPHIES-Specific API Routes
Eligibility, Prior Authorization, Communication
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import (
    EligibilityRequest,
    EligibilityResponse,
    PriorAuthRequest,
    PriorAuthResponse
)
from app.core import log
import main


router = APIRouter()


@router.post("/eligibility", response_model=EligibilityResponse)
async def check_eligibility(request: EligibilityRequest):
    """
    Check patient eligibility
    
    Verifies patient insurance coverage and eligibility for services
    """
    log.info(f"Eligibility check for patient: {request.patient_id}")
    
    try:
        result = await main.integration_service.check_eligibility(
            patient_id=request.patient_id,
            insurance_id=request.insurance_id,
            service_date=request.service_date
        )
        
        if result.get('success'):
            data = result.get('data', {})
            return EligibilityResponse(
                success=True,
                eligible=result.get('eligible', False),
                patient_id=request.patient_id,
                insurance_id=request.insurance_id,
                coverage_status=data.get('status'),
                coverage_period=data.get('period'),
                message="Eligibility check completed"
            )
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Eligibility check failed'))
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Eligibility check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prior-authorization", response_model=PriorAuthResponse)
async def create_prior_authorization(request: PriorAuthRequest):
    """
    Create prior authorization request
    
    Submits prior authorization for planned services with AI validation
    """
    log.info(f"Prior authorization request for patient: {request.patient_id}")
    
    try:
        services_data = [service.dict() for service in request.services]
        
        result = await main.integration_service.create_prior_authorization(
            patient_id=request.patient_id,
            insurance_id=request.insurance_id,
            services=services_data
        )
        
        if result.get('success'):
            return PriorAuthResponse(
                success=True,
                authorization_id=result.get('authorization_id'),
                status=result.get('status'),
                approved_services=result.get('approved_services'),
                validation=result.get('validation'),
                message="Prior authorization created successfully"
            )
        else:
            # Check if validation failed
            if result.get('stage') == 'validation':
                return PriorAuthResponse(
                    success=False,
                    validation=result.get('validation'),
                    message="Validation failed"
                )
            
            raise HTTPException(status_code=400, detail=result.get('error', 'Prior authorization failed'))
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Prior authorization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prior-authorization/{auth_id}")
async def get_prior_authorization_status(auth_id: str):
    """
    Get prior authorization status
    
    Retrieves current status of a prior authorization request
    """
    try:
        result = await main.integration_service.get_claim_status(
            claim_id=auth_id,
            portal='nphies'
        )
        
        return result
    
    except Exception as e:
        log.error(f"Get prior auth status failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/communication")
async def send_communication(claim_id: str, message: str, attachments: List[dict] = None):
    """
    Send communication
    
    Sends communication/attachment related to a claim
    """
    try:
        connector = main.integration_service.connector_factory.get_connector('nphies')
        
        result = await connector.send_communication(
            claim_id=claim_id,
            message=message,
            attachments=attachments
        )
        
        if result.get('success'):
            return {
                "success": True,
                "communication_id": result.get('communication_id'),
                "message": "Communication sent successfully"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Communication failed'))
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Send communication failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/poll/{bundle_id}")
async def poll_status(bundle_id: str):
    """
    Poll transaction bundle status
    
    Retrieves status of a transaction bundle
    """
    try:
        connector = main.integration_service.connector_factory.get_connector('nphies')
        
        result = await connector.poll_status(bundle_id)
        
        return result
    
    except Exception as e:
        log.error(f"Poll status failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
