"""
GIVC AI API Routes
AI validation, smart forms, error detection
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.models.schemas import (
    AIValidationRequest,
    AIValidationResponse,
    SmartFormRequest,
    SmartFormResponse
)
from app.core import log
import main


router = APIRouter()


@router.post("/validate", response_model=AIValidationResponse)
async def validate_claim(request: AIValidationRequest):
    """
    Validate claim with Ultrathink AI
    
    Performs intelligent validation and provides suggestions
    """
    log.info("AI validation request received")
    
    try:
        claim_data = request.claim.dict()
        
        result = await main.integration_service.givc_service.validate_claim_with_ai(claim_data)
        
        return AIValidationResponse(
            is_valid=result.get('is_valid', False),
            confidence=result.get('confidence', 0.0),
            errors=result.get('errors', []),
            warnings=result.get('warnings', []),
            suggestions=result.get('suggestions', []),
            ai_insights=result.get('ai_insights')
        )
    
    except Exception as e:
        log.error(f"AI validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-complete", response_model=SmartFormResponse)
async def smart_form_completion(request: SmartFormRequest):
    """
    Smart form completion
    
    Auto-fills form fields using AI and historical patterns
    """
    log.info("Smart form completion request received")
    
    try:
        result = await main.integration_service.givc_service.smart_form_completion(
            partial_data=request.partial_data,
            context=request.context
        )
        
        if result.get('success'):
            return SmartFormResponse(
                success=True,
                completed_data=result.get('completed_data', {}),
                suggestions=result.get('suggestions', []),
                fields_completed=result.get('fields_completed', 0)
            )
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Smart completion failed'))
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Smart form completion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-errors")
async def detect_errors(claim_data: Dict[str, Any]):
    """
    Automated error detection
    
    Identifies potential errors before submission
    """
    log.info("Error detection request received")
    
    try:
        result = await main.integration_service.givc_service.detect_errors(claim_data)
        
        return result
    
    except Exception as e:
        log.error(f"Error detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_claim(claim_data: Dict[str, Any]):
    """
    AI-powered claim optimization
    
    Suggests improvements for better reimbursement
    """
    log.info("Claim optimization request received")
    
    try:
        result = await main.integration_service.givc_service.optimize_claim(claim_data)
        
        return result
    
    except Exception as e:
        log.error(f"Claim optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_analytics(start_date: str = None, end_date: str = None):
    """
    Get AI analytics
    
    Retrieves performance metrics and insights
    """
    try:
        result = await main.integration_service.givc_service.get_analytics(
            start_date=start_date,
            end_date=end_date
        )
        
        return result
    
    except Exception as e:
        log.error(f"Get analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
