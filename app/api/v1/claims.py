"""
Claims API Routes
Claim submission and status endpoints
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ClaimSubmissionRequest,
    ClaimResponse,
    BatchClaimRequest,
    BatchClaimResponse,
    ClaimStatusRequest,
    ClaimStatusResponse
)
from app.core import log
from datetime import datetime
import main


router = APIRouter()


@router.post("/submit", response_model=ClaimResponse)
async def submit_claim(request: ClaimSubmissionRequest):
    """
    Submit a claim with AI validation
    
    Validates claim using GIVC AI and submits to selected portals based on strategy
    """
    log.info(f"Claim submission request with strategy: {request.strategy}")
    
    try:
        # Convert Pydantic models to dict
        claim_data = request.claim.dict()
        
        result = await main.integration_service.submit_claim(
            claim_data=claim_data,
            strategy=request.strategy,
            portals=[p.value for p in request.portals] if request.portals else None
        )
        
        return ClaimResponse(
            success=result.get('success', False),
            claim_id=result.get('results', {}).get('nphies', {}).get('claim_id'),
            status=result.get('results', {}).get('nphies', {}).get('status'),
            portals=result.get('portals', []),
            validation=result.get('validation'),
            optimization=result.get('optimization'),
            results=result.get('results'),
            message=result.get('message'),
            submitted_at=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        log.error(f"Claim submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchClaimResponse)
async def submit_batch(request: BatchClaimRequest):
    """
    Submit multiple claims in batch
    
    Processes multiple claims in parallel with AI validation
    """
    log.info(f"Batch submission request for {len(request.claims)} claims")
    
    try:
        claims_data = [claim.dict() for claim in request.claims]
        
        result = await main.integration_service.batch_submit(
            claims=claims_data,
            strategy=request.strategy
        )
        
        return BatchClaimResponse(
            success=result.get('success', False),
            total_claims=result.get('total_claims', 0),
            successful=result.get('successful', 0),
            failed=result.get('failed', 0),
            results=[
                ClaimResponse(**r) if isinstance(r, dict) else ClaimResponse(success=False, message=str(r))
                for r in result.get('results', [])
            ]
        )
    
    except Exception as e:
        log.error(f"Batch submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/status", response_model=ClaimStatusResponse)
async def get_claim_status(request: ClaimStatusRequest):
    """
    Get claim status
    
    Retrieves current status of a submitted claim
    """
    log.info(f"Status check for claim: {request.claim_id}")
    
    try:
        result = await main.integration_service.get_claim_status(
            claim_id=request.claim_id,
            portal=request.portal.value,
            branch=request.branch.value if request.branch else None
        )
        
        if result.get('success'):
            return ClaimStatusResponse(
                success=True,
                claim_id=request.claim_id,
                status=result.get('status'),
                outcome=result.get('outcome'),
                last_updated=result.get('last_updated'),
                details=result.get('data')
            )
        else:
            raise HTTPException(status_code=404, detail=result.get('error', 'Claim not found'))
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_claim_history(patient_id: str = None, date_from: str = None, date_to: str = None):
    """
    Get claim history
    
    Retrieves historical claims for a patient or date range
    """
    # TODO: Implement claim history from database
    return {
        "success": True,
        "claims": [],
        "message": "Claim history feature coming soon"
    }
