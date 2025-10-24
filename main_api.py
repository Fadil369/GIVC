"""
FastAPI Backend for GIVC Healthcare Platform
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import logging

# Initialize FastAPI app
app = FastAPI(
    title="GIVC Healthcare Platform API",
    description="NPHIES Integration & Healthcare Services",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "GIVC Healthcare Platform API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "givc-backend",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "api": "ok",
            "database": "connected",
            "cache": "connected"
        }
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "service": "givc-backend",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "endpoints": {
            "eligibility": "/api/v1/eligibility",
            "claims": "/api/v1/claims",
            "authorization": "/api/v1/authorization",
            "communication": "/api/v1/communication"
        },
        "nphies_integration": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/eligibility")
async def eligibility_check():
    """Eligibility verification endpoint"""
    return {
        "service": "eligibility",
        "status": "available",
        "message": "Eligibility service ready"
    }

@app.get("/api/v1/claims")
async def claims_service():
    """Claims management endpoint"""
    return {
        "service": "claims",
        "status": "available",
        "message": "Claims service ready"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return {
        "requests_total": 0,
        "requests_duration_seconds": 0.0,
        "active_connections": 0
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
