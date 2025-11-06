"""
BrainSAIT RCM Healthcare Claims Management System
Main FastAPI Application
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import authentication modules
from auth.jwt_handler import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from middleware.auth import get_current_user, get_current_active_user, require_role
from models.user import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    UserRole
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "brainsait")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Prometheus metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Database client
db_client: Optional[AsyncIOMotorClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global db_client
    
    # Startup
    logger.info("Starting BrainSAIT RCM API...")
    try:
        db_client = AsyncIOMotorClient(
            DATABASE_URL,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=50
        )
        # Verify connection
        await db_client.admin.command('ping')
        logger.info("✓ MongoDB connection established")
        
        # Create indexes
        db = db_client[DB_NAME]
        await create_indexes(db)
        logger.info("✓ Database indexes created")
        
    except Exception as e:
        logger.error(f"✗ Failed to connect to MongoDB: {e}")
        db_client = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down BrainSAIT RCM API...")
    if db_client:
        db_client.close()
        logger.info("✓ MongoDB connection closed")


async def create_indexes(db):
    """Create database indexes for performance"""
    # Users
    await db.users.create_index("email", unique=True)
    await db.users.create_index("phone_number")
    await db.users.create_index([("created_at", -1)])
    
    # Rejections
    await db.rejections.create_index("claim_id", unique=True)
    await db.rejections.create_index([("created_at", -1)])
    await db.rejections.create_index("payer")
    await db.rejections.create_index("status")
    
    # Appeals
    await db.appeals.create_index("rejection_id")
    await db.appeals.create_index([("created_at", -1)])
    await db.appeals.create_index("status")
    
    # Audit events
    await db.auth_events.create_index([("timestamp", -1)])
    await db.auth_events.create_index("user_id")
    await db.auth_events.create_index("event_type")
    
    # OTP verifications
    await db.otp_verifications.create_index("expires_at", expireAfterSeconds=0)
    
    # Rate limits
    await db.rate_limits.create_index("expires_at", expireAfterSeconds=0)


# Initialize FastAPI app
app = FastAPI(
    title="BrainSAIT RCM API",
    description="Healthcare Revenue Cycle Management System with NPHIES & OASIS+ Integration",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Dependency to get database
def get_db():
    """Get database instance"""
    if db_client is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return db_client[DB_NAME]


# ============================================================================
# MODELS
# ============================================================================
# User models imported from models.user


class RejectionCreate(BaseModel):
    """Create rejection model"""
    claim_id: str
    patient_id: str
    payer: str
    denial_code: str
    denial_reason: str
    amount: float
    service_date: str
    branch: str


class AppealCreate(BaseModel):
    """Create appeal model"""
    rejection_id: str
    appeal_reason: str
    supporting_documents: list[str] = []
    additional_notes: Optional[str] = None


class NPHIESClaimSubmission(BaseModel):
    """NPHIES claim submission"""
    claim_data: dict
    patient_info: dict
    provider_info: dict


class OASISClaimSubmission(BaseModel):
    """OASIS+ claim submission"""
    patient_id: str
    claim_number: str
    service_date: str
    payer: str
    diagnosis_codes: list[str]
    procedure_codes: list[str]
    total_amount: float


# ============================================================================
# HEALTH & METRICS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "healthy"
    
    if db_client:
        try:
            await db_client.admin.command('ping')
        except Exception as exc:  # noqa: BLE001
            db_status = "error"
            logger.exception("Database health check failed", exc_info=exc)
    else:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "api": "healthy"
        }
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/hour")
async def register(request: Request, user_data: UserCreate, db=Depends(get_db)):
    """
    Register a new user account
    """
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Create user document
        user_doc = {
            "user_id": f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "email": user_data.email,
            "full_name": user_data.full_name,
            "phone_number": user_data.phone_number,
            "role": user_data.role,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "failed_login_attempts": 0
        }

        # Insert user
        result = await db.users.insert_one(user_doc)

        # Log registration event
        await db.auth_events.insert_one({
            "user_id": user_doc["user_id"],
            "event_type": "USER_REGISTERED",
            "ip_address": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.now(timezone.utc)
        })

        return UserResponse(
            user_id=user_doc["user_id"],
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            phone_number=user_doc["phone_number"],
            role=user_doc["role"],
            is_active=user_doc["is_active"],
            is_verified=user_doc["is_verified"],
            created_at=user_doc["created_at"],
            last_login=None
        )

    except Exception as e:
        logger.exception("Error during registration", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )


@app.post("/api/auth/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest, db=Depends(get_db)):
    """
    Authenticate user and return JWT token
    """
    try:
        # Find user by email
        user = await db.users.find_one({"email": credentials.username})

        if not user:
            # Log failed attempt
            await db.auth_events.insert_one({
                "user_id": None,
                "email": credentials.username,
                "event_type": "LOGIN_FAILED",
                "reason": "USER_NOT_FOUND",
                "ip_address": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent"),
                "timestamp": datetime.now(timezone.utc)
            })
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if account is locked
        if user.get("locked_until"):
            if datetime.now(timezone.utc) < user["locked_until"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account is locked until {user['locked_until'].isoformat()}"
                )
            else:
                # Unlock account
                await db.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"locked_until": None, "failed_login_attempts": 0}}
                )

        # Verify password
        if not verify_password(credentials.password, user["hashed_password"]):
            # Increment failed attempts
            failed_attempts = user.get("failed_login_attempts", 0) + 1
            update_data = {
                "failed_login_attempts": failed_attempts,
                "updated_at": datetime.now(timezone.utc)
            }

            # Lock account after 5 failed attempts
            if failed_attempts >= 5:
                update_data["locked_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)

            await db.users.update_one({"_id": user["_id"]}, {"$set": update_data})

            # Log failed attempt
            await db.auth_events.insert_one({
                "user_id": user["user_id"],
                "event_type": "LOGIN_FAILED",
                "reason": "INVALID_PASSWORD",
                "failed_attempts": failed_attempts,
                "ip_address": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent"),
                "timestamp": datetime.now(timezone.utc)
            })

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # Reset failed login attempts and update last login
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "failed_login_attempts": 0,
                    "last_login": datetime.now(timezone.utc),
                    "locked_until": None,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        # Create JWT tokens
        token_data = {
            "sub": user["user_id"],
            "email": user["email"],
            "role": user["role"],
            "full_name": user["full_name"]
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Log successful login
        await db.auth_events.insert_one({
            "user_id": user["user_id"],
            "event_type": "LOGIN_SUCCESS",
            "ip_address": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.now(timezone.utc)
        })

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                user_id=user["user_id"],
                email=user["email"],
                full_name=user["full_name"],
                phone_number=user.get("phone_number"),
                role=user["role"],
                is_active=user.get("is_active", True),
                is_verified=user.get("is_verified", False),
                created_at=user["created_at"],
                last_login=user.get("last_login")
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error during login", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Get current authenticated user information"""
    try:
        # Fetch full user data from database
        user = await db.users.find_one({"user_id": current_user["user_id"]})

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            full_name=user["full_name"],
            phone_number=user.get("phone_number"),
            role=user["role"],
            is_active=user.get("is_active", True),
            is_verified=user.get("is_verified", False),
            created_at=user["created_at"],
            last_login=user.get("last_login")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching user info", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user information"
        )


@app.post("/api/auth/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Logout user and log the event"""
    try:
        # Log logout event
        await db.auth_events.insert_one({
            "user_id": current_user["user_id"],
            "event_type": "LOGOUT",
            "ip_address": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.now(timezone.utc)
        })

        # Note: JWT tokens are stateless, so true invalidation requires:
        # - Token blacklist in Redis (implement if needed)
        # - Client-side token removal
        # - Short token expiration times

        return {
            "success": True,
            "message": "Logged out successfully"
        }

    except Exception as e:
        logger.exception("Error during logout", exc_info=e)
        return {
            "success": True,
            "message": "Logged out successfully"
        }


# ============================================================================
# REJECTIONS MANAGEMENT
# ============================================================================

@app.get("/api/rejections/current-month")
async def get_current_month_rejections(db=Depends(get_db)):
    """Get all rejections for the current month"""
    try:
        # Get first day of current month
        now = datetime.now(timezone.utc)
        first_day = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        
        rejections = await db.rejections.find({
            "created_at": {"$gte": first_day}
        }).to_list(length=1000)
        
        # Convert ObjectId to string
        for rejection in rejections:
            rejection["_id"] = str(rejection["_id"])
        
        return rejections
    except Exception as e:
        logger.exception("Error fetching rejections", exc_info=e)
        return []


@app.post("/api/rejections")
async def create_rejection(rejection: RejectionCreate, db=Depends(get_db)):
    """Create a new rejection record"""
    rejection_doc = {
        **rejection.model_dump(),
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    result = await db.rejections.insert_one(rejection_doc)
    
    return {
        "id": str(result.inserted_id),
        "status": "created"
    }


# ============================================================================
# APPEALS MANAGEMENT
# ============================================================================

@app.post("/api/appeals")
async def create_appeal(appeal: AppealCreate, db=Depends(get_db)):
    """Create a new appeal for a rejected claim"""
    appeal_doc = {
        **appeal.model_dump(),
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    result = await db.appeals.insert_one(appeal_doc)
    
    return {
        "id": str(result.inserted_id),
        "status": "created"
    }


@app.get("/api/appeals")
async def get_appeals(status: Optional[str] = None, db=Depends(get_db)):
    """Get all appeals with optional status filter"""
    query = {}
    if status:
        query["status"] = status
    
    appeals = await db.appeals.find(query).to_list(length=1000)
    
    for appeal in appeals:
        appeal["_id"] = str(appeal["_id"])
    
    return appeals


# ============================================================================
# ANALYTICS
# ============================================================================

@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics(db=Depends(get_db)):
    """Get comprehensive dashboard analytics"""
    now = datetime.now(timezone.utc)
    first_day = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    
    # Count rejections
    total_rejections = await db.rejections.count_documents({
        "created_at": {"$gte": first_day}
    })
    
    # Count appeals
    total_appeals = await db.appeals.count_documents({
        "created_at": {"$gte": first_day}
    })
    
    # Calculate recovery rate
    approved_appeals = await db.appeals.count_documents({
        "created_at": {"$gte": first_day},
        "status": "APPROVED"
    })
    
    recovery_rate = (approved_appeals / total_appeals * 100) if total_appeals > 0 else 0
    
    return {
        "period": "current_month",
        "total_rejections": total_rejections,
        "total_appeals": total_appeals,
        "recovery_rate": round(recovery_rate, 1),
        "pending_appeals": await db.appeals.count_documents({"status": "PENDING"}),
        "avg_appeal_cycle_time": 7.2,  # TODO: Calculate from actual data
        "fraud_alerts_count": 0  # TODO: Implement fraud detection
    }


@app.get("/api/analytics/trends")
async def get_trends(days: int = 30, db=Depends(get_db)):
    """Get rejection and recovery trends"""
    # TODO: Implement actual trend calculation
    return {
        "start_date": datetime.now(timezone.utc).isoformat(),
        "end_date": datetime.now(timezone.utc).isoformat(),
        "rejection_trend": {"data": [], "change_percent": 0},
        "recovery_trend": {"data": [], "change_percent": 0}
    }


# ============================================================================
# COMPLIANCE LETTERS
# ============================================================================

@app.get("/api/compliance/letters/pending")
async def get_pending_compliance_letters(db=Depends(get_db)):
    """Get all pending compliance letters"""
    letters = await db.compliance_letters.find({
        "status": "PENDING"
    }).to_list(length=100)
    
    for letter in letters:
        letter["_id"] = str(letter["_id"])
    
    return letters


@app.post("/api/compliance/letters")
async def create_compliance_letter(letter_data: dict, db=Depends(get_db)):
    """Create a new compliance letter"""
    letter_doc = {
        **letter_data,
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc)
    }
    
    result = await db.compliance_letters.insert_one(letter_doc)
    
    return {
        "id": str(result.inserted_id),
        "status": "created"
    }


# ============================================================================
# AI/ML ENDPOINTS
# ============================================================================

@app.post("/api/ai/fraud-detection")
async def run_fraud_detection(data: dict, db=Depends(get_db)):
    """Run AI-powered fraud detection analysis"""
    # TODO: Implement actual fraud detection model
    return {
        "alerts": [],
        "risk_score": 0.0,
        "analyzed_claims": len(data.get("claims", [])),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/ai/predictive-analytics")
async def run_predictive_analytics(data: dict, db=Depends(get_db)):
    """Generate predictive analytics forecasts"""
    # TODO: Implement actual predictive model
    return {
        "rejection_forecast": {
            "next_30_days": 0,
            "confidence": 0.0
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/ai/physician-risk/{physician_id}")
async def get_physician_risk(physician_id: str, db=Depends(get_db)):
    """Get fraud risk assessment for a specific physician"""
    # TODO: Implement actual risk assessment
    return {
        "physician_id": physician_id,
        "risk_score": 0.0,
        "risk_level": "LOW",
        "analyzed_claims": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ============================================================================
# FHIR VALIDATION
# ============================================================================

@app.post("/api/fhir/validate")
async def validate_fhir(resource: dict):
    """Validate FHIR R4 resources"""
    # TODO: Implement FHIR validation
    return {
        "valid": True,
        "errors": [],
        "warnings": [],
        "resource_type": resource.get("resource_type", "Unknown")
    }


# ============================================================================
# NPHIES INTEGRATION
# ============================================================================

@app.post("/api/nphies/submit-claim")
async def submit_claim_to_nphies(submission: NPHIESClaimSubmission, db=Depends(get_db)):
    """Submit claim to NPHIES platform"""
    # TODO: Implement actual NPHIES API integration
    
    # Log submission
    await db.nphies_submissions.insert_one({
        "claim_data": submission.claim_data,
        "status": "SUBMITTED",
        "submitted_at": datetime.now(timezone.utc)
    })
    
    return {
        "success": True,
        "nphies_reference": f"NPHIES-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "SUBMITTED",
        "created": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/nphies/submit-appeal")
async def submit_appeal_to_nphies(appeal_data: dict, db=Depends(get_db)):
    """Submit appeal to NPHIES"""
    # TODO: Implement actual NPHIES appeal submission
    return {
        "success": True,
        "nphies_reference": f"APPEAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "SUBMITTED"
    }


@app.get("/api/nphies/claim-response/{nphies_reference}")
async def get_nphies_claim_response(nphies_reference: str, db=Depends(get_db)):
    """Get claim response from NPHIES"""
    # TODO: Implement actual NPHIES response retrieval
    return {
        "nphies_reference": nphies_reference,
        "status": "PROCESSING",
        "response_data": {}
    }


# ============================================================================
# OASIS+ INTEGRATION
# ============================================================================

@app.post("/api/oasis/submit")
async def submit_to_oasis(submission: OASISClaimSubmission, db=Depends(get_db)):
    """Submit claim to OASIS+ legacy system"""
    # TODO: Implement OASIS+ automation
    
    # Log submission attempt
    await db.oasis_submissions.insert_one({
        "claim_data": submission.model_dump(),
        "status": "PENDING",
        "submitted_at": datetime.now(timezone.utc)
    })
    
    return {
        "success": True,
        "oasis_reference": f"OASIS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "SUBMITTED",
        "message": "Claim submitted to OASIS+ for processing"
    }


# ============================================================================
# NOTIFICATIONS
# ============================================================================

@app.post("/api/notifications/whatsapp")
async def send_whatsapp_notification(data: dict, db=Depends(get_db)):
    """Send WhatsApp notification"""
    # TODO: Implement Twilio WhatsApp integration
    return {
        "success": True,
        "message_id": f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "SENT"
    }


# ============================================================================
# AUDIT LOGS
# ============================================================================

@app.get("/api/audit/user/{user_id}")
async def get_user_audit_trail(user_id: str, db=Depends(get_db)):
    """Get audit trail for a specific user"""
    events = await db.auth_events.find({
        "user_id": user_id
    }).sort("timestamp", -1).limit(100).to_list(length=100)
    
    for event in events:
        event["_id"] = str(event["_id"])
    
    return events


@app.get("/api/audit/suspicious-activity")
async def get_suspicious_activity(db=Depends(get_db)):
    """Get suspicious activity alerts"""
    # TODO: Implement suspicious activity detection
    return []


# ============================================================================
# ROOT
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "BrainSAIT RCM API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
