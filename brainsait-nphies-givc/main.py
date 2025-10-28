"""
Main FastAPI Application
BrainSAIT-NPHIES-GIVC Integration Platform
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core import log, setup_logging, settings, load_config_yaml
from app.services.integration import IntegrationService


# Global integration service
integration_service: IntegrationService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global integration_service
    
    # Startup
    log.info(f"Starting {settings.app_name}...")
    setup_logging(settings.log_level, settings.log_file)
    
    # Load configuration
    try:
        config = load_config_yaml()
        integration_service = IntegrationService(config)
        log.info("Integration service initialized successfully")
    except Exception as e:
        log.error(f"Failed to initialize integration service: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    log.info("Shutting down...")
    if integration_service:
        await integration_service.close()
    log.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Healthcare Claims Integration Platform",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    log.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# Import routers
from app.api.v1 import auth, claims, nphies, givc, health

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(claims.router, prefix="/api/v1/claims", tags=["Claims"])
app.include_router(nphies.router, prefix="/api/v1/nphies", tags=["NPHIES"])
app.include_router(givc.router, prefix="/api/v1/givc", tags=["GIVC AI"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.app_name,
        "version": "2.0.0",
        "status": "running",
        "features": {
            "nphies_integration": True,
            "givc_ai": True,
            "legacy_portals": True,
            "smart_routing": True
        }
    }


@app.get("/api/v1")
async def api_info():
    """API information"""
    return {
        "version": "1.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "claims": "/api/v1/claims",
            "nphies": "/api/v1/nphies",
            "givc": "/api/v1/givc",
            "health": "/api/v1/health"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
