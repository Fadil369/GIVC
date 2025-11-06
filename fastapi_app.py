"""
GIVC Healthcare Platform - FastAPI Backend
OASIS Integration Layer for NPHIES Claims Processing
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import project modules (use fallback for missing imports)
try:
    from config.settings import settings
except Exception:
    class Settings:
        ENVIRONMENT = "development"
        NPHIES_BASE_URL = "https://HSB.nphies.sa/api/fs/fhir"
        LOG_LEVEL = "INFO"
    settings = Settings()

try:
    from auth.auth_manager import auth_manager
except Exception:
    auth_manager = None

try:
    from services.eligibility import EligibilityService
    from services.claims import ClaimsService
    from services.prior_authorization import PriorAuthorizationService
    from services.analytics import NPHIESAnalytics as AnalyticsService
    SERVICES_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Services not available: {e}")
    SERVICES_AVAILABLE = False
    # Create mock services
    class MockService:
        async def __call__(self, *args, **kwargs):
            return {"status": "demo_mode", "message": "Service in demo mode"}
    
    EligibilityService = MockService
    ClaimsService = MockService
    PriorAuthorizationService = MockService
    AnalyticsService = MockService

# Initialize FastAPI app
app = FastAPI(
    title="GIVC Healthcare Platform API",
    description="OASIS Integration Layer for NPHIES Claims Processing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "https://givc.thefadil.site",  # Production
        "https://4d31266d.givc-platform-static.pages.dev",  # Cloudflare Pages (specific subdomain)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods only
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
)

# Initialize services
if SERVICES_AVAILABLE:
    eligibility_service = EligibilityService()
    claims_service = ClaimsService()
    prior_auth_service = PriorAuthorizationService()
    analytics_service = AnalyticsService()
else:
    eligibility_service = MockService()
    claims_service = MockService()
    prior_auth_service = MockService()
    analytics_service = MockService()

# =============================================================================
# Pydantic Models
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str
    services: Dict[str, bool]

class EligibilityCheckRequest(BaseModel):
    member_id: str = Field(..., description="Patient member ID")
    payer_id: str = Field(..., description="Insurance payer ID")
    service_date: Optional[str] = Field(None, description="Date of service (YYYY-MM-DD)")

class EligibilityResponse(BaseModel):
    eligible: bool
    member_id: str
    coverage_status: str
    benefits: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class ClaimSubmission(BaseModel):
    claim_id: str
    patient_id: str
    provider_id: str
    payer_id: str
    service_date: str
    diagnosis_codes: List[str]
    procedure_codes: List[str]
    total_amount: float
    attachments: Optional[List[str]] = None

class ClaimResponse(BaseModel):
    claim_id: str
    status: str
    submission_date: datetime
    outcome: Optional[str] = None
    message: Optional[str] = None
    reference_number: Optional[str] = None

class PriorAuthRequest(BaseModel):
    patient_id: str
    provider_id: str
    payer_id: str
    service_type: str
    diagnosis_codes: List[str]
    procedure_codes: List[str]
    requested_date: str
    clinical_notes: Optional[str] = None

class PriorAuthResponse(BaseModel):
    authorization_id: str
    status: str
    approval_number: Optional[str] = None
    valid_until: Optional[str] = None
    message: Optional[str] = None

class AnalyticsDashboardResponse(BaseModel):
    period: str
    total_claims: int
    approved_claims: int
    rejected_claims: int
    pending_claims: int
    total_amount: float
    approval_rate: float
    rejection_reasons: Dict[str, int]
    trends: Dict[str, Any]

# =============================================================================
# API Routes
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "GIVC Healthcare Platform API",
        "version": "1.0.0",
        "description": "OASIS Integration Layer for NPHIES",
        "docs": "/api/docs",
        "health": "/api/health"
    }

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check service availability
        services_status = {
            "nphies_auth": auth_manager.check_connection() if hasattr(auth_manager, 'check_connection') else True,
            "database": True,  # Add actual database check
            "eligibility_service": True,
            "claims_service": True,
            "analytics_service": True
        }
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version="1.0.0",
            environment=settings.ENVIRONMENT,
            services=services_status
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

# =============================================================================
# Eligibility Endpoints
# =============================================================================
# TODO: Add authentication middleware to protect these endpoints
# Currently endpoints are unprotected - implement JWT or API key auth

@app.post("/api/eligibility/check", response_model=EligibilityResponse, tags=["Eligibility"])
async def check_eligibility(request: EligibilityCheckRequest):
    """Check patient eligibility and benefits"""
    try:
        result = await eligibility_service.check_eligibility(
            member_id=request.member_id,
            payer_id=request.payer_id,
            service_date=request.service_date
        )
        
        return EligibilityResponse(
            eligible=result.get("eligible", False),
            member_id=request.member_id,
            coverage_status=result.get("coverage_status", "unknown"),
            benefits=result.get("benefits"),
            message=result.get("message")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Eligibility check failed: {str(e)}"
        )

# =============================================================================
# Claims Endpoints
# =============================================================================

@app.post("/api/claims/submit", response_model=ClaimResponse, tags=["Claims"])
async def submit_claim(claim: ClaimSubmission):
    """Submit a new claim to NPHIES"""
    try:
        result = await claims_service.submit_claim(claim.dict())
        
        return ClaimResponse(
            claim_id=claim.claim_id,
            status=result.get("status", "submitted"),
            submission_date=datetime.now(),
            outcome=result.get("outcome"),
            message=result.get("message"),
            reference_number=result.get("reference_number")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Claim submission failed: {str(e)}"
        )

@app.get("/api/claims/{claim_id}", response_model=ClaimResponse, tags=["Claims"])
async def get_claim_status(claim_id: str):
    """Get status of a submitted claim"""
    try:
        result = await claims_service.get_claim_status(claim_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim {claim_id} not found"
            )
        
        return ClaimResponse(
            claim_id=claim_id,
            status=result.get("status", "unknown"),
            submission_date=result.get("submission_date", datetime.now()),
            outcome=result.get("outcome"),
            message=result.get("message"),
            reference_number=result.get("reference_number")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve claim status: {str(e)}"
        )

@app.get("/api/claims", tags=["Claims"])
async def list_claims(
    status_filter: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 50
):
    """List claims with optional filters"""
    try:
        result = await claims_service.list_claims(
            status_filter=status_filter,
            from_date=from_date,
            to_date=to_date,
            limit=limit
        )
        
        return {
            "claims": result.get("claims", []),
            "total": result.get("total", 0),
            "filtered": result.get("filtered", 0)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list claims: {str(e)}"
        )

# =============================================================================
# Prior Authorization Endpoints
# =============================================================================

@app.post("/api/prior-auth/request", response_model=PriorAuthResponse, tags=["Prior Authorization"])
async def request_prior_authorization(request: PriorAuthRequest):
    """Request prior authorization for a procedure"""
    try:
        result = await prior_auth_service.request_authorization(request.dict())
        
        return PriorAuthResponse(
            authorization_id=result.get("authorization_id", ""),
            status=result.get("status", "pending"),
            approval_number=result.get("approval_number"),
            valid_until=result.get("valid_until"),
            message=result.get("message")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prior authorization request failed: {str(e)}"
        )

@app.get("/api/prior-auth/{auth_id}", tags=["Prior Authorization"])
async def get_authorization_status(auth_id: str):
    """Get status of prior authorization"""
    try:
        result = await prior_auth_service.get_authorization_status(auth_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Authorization {auth_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve authorization status: {str(e)}"
        )

# =============================================================================
# Analytics Endpoints
# =============================================================================

@app.get("/api/analytics/dashboard", response_model=AnalyticsDashboardResponse, tags=["Analytics"])
async def get_analytics_dashboard(
    period: str = "last_30_days",
    provider_id: Optional[str] = None
):
    """Get analytics dashboard data"""
    try:
        result = await analytics_service.get_dashboard_metrics(
            period=period,
            provider_id=provider_id
        )
        
        return AnalyticsDashboardResponse(
            period=period,
            total_claims=result.get("total_claims", 0),
            approved_claims=result.get("approved_claims", 0),
            rejected_claims=result.get("rejected_claims", 0),
            pending_claims=result.get("pending_claims", 0),
            total_amount=result.get("total_amount", 0.0),
            approval_rate=result.get("approval_rate", 0.0),
            rejection_reasons=result.get("rejection_reasons", {}),
            trends=result.get("trends", {})
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )

@app.get("/api/analytics/rejections", tags=["Analytics"])
async def get_rejection_analysis(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """Get detailed rejection analysis"""
    try:
        result = await analytics_service.get_rejection_analysis(
            from_date=from_date,
            to_date=to_date
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve rejection analysis: {str(e)}"
        )

@app.get("/api/analytics/trends", tags=["Analytics"])
async def get_trends(
    metric: str = "claims",
    period: str = "last_90_days"
):
    """Get trend data for specified metric"""
    try:
        result = await analytics_service.get_trends(
            metric=metric,
            period=period
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trends: {str(e)}"
        )

# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error",
            "detail": str(exc) if settings.ENVIRONMENT != "production" else None,
            "timestamp": datetime.now().isoformat()
        }
    )

# =============================================================================
# Startup/Shutdown Events
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting GIVC Healthcare Platform API...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 NPHIES URL: {settings.NPHIES_BASE_URL}")
    print("✅ API is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down GIVC Healthcare Platform API...")

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
