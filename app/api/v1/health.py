"""
Health Check API Routes
System and portal health monitoring
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import HealthCheckResponse, SystemHealthResponse
from app.core import log
import main


router = APIRouter()


@router.get("/", response_model=SystemHealthResponse)
async def system_health():
    """
    System-wide health check
    
    Checks health of all configured portals
    """
    try:
        result = await main.integration_service.health_check()
        
        portals_health = {}
        for portal, health_data in result.get('portals', {}).items():
            portals_health[portal] = HealthCheckResponse(**health_data)
        
        return SystemHealthResponse(
            overall_status=result.get('overall_status', 'unknown'),
            portals=portals_health,
            checked_at=result.get('checked_at', '')
        )
    
    except Exception as e:
        log.error(f"System health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portal/{portal}", response_model=HealthCheckResponse)
async def portal_health(portal: str):
    """
    Portal-specific health check
    
    Checks health of a specific portal
    """
    try:
        result = await main.integration_service.health_check(portal=portal)
        
        return HealthCheckResponse(**result)
    
    except Exception as e:
        log.error(f"Portal health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/branch/{branch}")
async def branch_health(branch: str):
    """
    Branch-specific health check
    
    Checks health of a specific hospital branch
    """
    try:
        connector = main.integration_service.connector_factory.get_connector('oases', branch)
        result = await connector.health_check()
        
        return result
    
    except Exception as e:
        log.error(f"Branch health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint
    
    Returns OK if server is responsive
    """
    return {"status": "ok", "message": "pong"}
