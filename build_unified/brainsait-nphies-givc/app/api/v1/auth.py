"""
Authentication API Routes
Portal login/logout endpoints
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import LoginRequest, LoginResponse
from app.core import log
import main


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login to a portal
    
    Creates an authenticated session for the specified portal
    """
    log.info(f"Login request for portal: {request.portal}, branch: {request.branch}")
    
    try:
        connector = main.integration_service.connector_factory.get_connector(
            request.portal.value,
            request.branch.value if request.branch else None
        )
        
        result = await connector.login(request.username, request.password)
        
        if result.get('success'):
            return LoginResponse(
                success=True,
                session_id=result.get('session_id'),
                message=f"Successfully logged in to {request.portal}",
                expires_at=result.get('expires_at')
            )
        else:
            raise HTTPException(status_code=401, detail=result.get('error', 'Login failed'))
    
    except Exception as e:
        log.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(session_id: str):
    """
    Logout from a portal
    
    Invalidates the specified session
    """
    try:
        session = main.integration_service.connector_factory.get_connector(
            'nphies'
        ).session_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        portal = session['portal']
        connector = main.integration_service.connector_factory.get_connector(portal)
        
        success = await connector.logout(session_id)
        
        if success:
            return {"success": True, "message": "Logged out successfully"}
        else:
            raise HTTPException(status_code=500, detail="Logout failed")
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_sessions(portal: str = None):
    """
    List active sessions
    
    Returns all active sessions for the specified portal or all portals
    """
    try:
        sessions = main.integration_service.connector_factory.get_connector(
            'nphies'
        ).session_manager.list_sessions(portal)
        
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        }
    
    except Exception as e:
        log.error(f"List sessions failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
