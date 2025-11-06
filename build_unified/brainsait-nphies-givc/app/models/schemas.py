"""
Pydantic Models and Schemas
Request/Response validation models
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class BranchEnum(str, Enum):
    """Al Hayat Hospital Branches"""
    RIYADH = "riyadh"
    MADINAH = "madinah"
    UNAIZAH = "unaizah"
    KHAMIS = "khamis"
    JIZAN = "jizan"
    ABHA = "abha"


class PortalEnum(str, Enum):
    """Available Portals"""
    NPHIES = "nphies"
    OASES = "oases"
    MOH = "moh"
    JISR = "jisr"
    BUPA = "bupa"


class SubmissionStrategyEnum(str, Enum):
    """Claim submission strategies"""
    NPHIES_ONLY = "nphies_only"
    LEGACY_ONLY = "legacy_only"
    NPHIES_FIRST = "nphies_first"
    ALL_PORTALS = "all_portals"
    SMART_ROUTE = "smart_route"


# Authentication Models
class LoginRequest(BaseModel):
    """Login request"""
    portal: PortalEnum
    branch: Optional[BranchEnum] = None
    username: Optional[str] = None
    password: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response"""
    success: bool
    session_id: Optional[str] = None
    message: Optional[str] = None
    expires_at: Optional[str] = None


# Claim Models
class ServiceItem(BaseModel):
    """Service/Item in a claim"""
    code: str = Field(..., description="Service or procedure code")
    description: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(..., gt=0)
    service_date: Optional[str] = None
    diagnosis: Optional[str] = None


class ClaimRequest(BaseModel):
    """Claim submission request"""
    patient_id: str = Field(..., description="Patient national ID or Iqama")
    patient_name: Optional[str] = None
    insurance_id: str = Field(..., description="Insurance policy number")
    insurance_company: Optional[str] = None
    service_date: str = Field(..., description="Service date (YYYY-MM-DD)")
    claim_type: Optional[str] = Field(default="institutional", description="institutional or professional")
    items: List[ServiceItem] = Field(..., min_items=1)
    diagnosis_codes: Optional[List[str]] = None
    notes: Optional[str] = None


class ClaimSubmissionRequest(BaseModel):
    """Claim submission with strategy"""
    claim: ClaimRequest
    strategy: Optional[SubmissionStrategyEnum] = SubmissionStrategyEnum.NPHIES_FIRST
    portals: Optional[List[PortalEnum]] = None


class ClaimResponse(BaseModel):
    """Claim submission response"""
    success: bool
    claim_id: Optional[str] = None
    status: Optional[str] = None
    portals: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None
    optimization: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    submitted_at: Optional[str] = None


class BatchClaimRequest(BaseModel):
    """Batch claim submission"""
    claims: List[ClaimRequest] = Field(..., min_items=1)
    strategy: Optional[SubmissionStrategyEnum] = SubmissionStrategyEnum.NPHIES_FIRST


class BatchClaimResponse(BaseModel):
    """Batch claim submission response"""
    success: bool
    total_claims: int
    successful: int
    failed: int
    results: List[ClaimResponse]


# NPHIES-Specific Models
class EligibilityRequest(BaseModel):
    """Eligibility check request"""
    patient_id: str
    insurance_id: str
    service_date: Optional[str] = None


class EligibilityResponse(BaseModel):
    """Eligibility check response"""
    success: bool
    eligible: Optional[bool] = None
    patient_id: str
    insurance_id: str
    coverage_status: Optional[str] = None
    coverage_period: Optional[Dict[str, str]] = None
    message: Optional[str] = None


class PriorAuthRequest(BaseModel):
    """Prior authorization request"""
    patient_id: str
    insurance_id: str
    services: List[ServiceItem]
    diagnosis_codes: Optional[List[str]] = None
    clinical_notes: Optional[str] = None


class PriorAuthResponse(BaseModel):
    """Prior authorization response"""
    success: bool
    authorization_id: Optional[str] = None
    status: Optional[str] = None
    approved_services: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


# GIVC AI Models
class AIValidationRequest(BaseModel):
    """AI validation request"""
    claim: ClaimRequest


class AIValidationResponse(BaseModel):
    """AI validation response"""
    is_valid: bool
    confidence: float
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    ai_insights: Optional[Dict[str, Any]] = None


class SmartFormRequest(BaseModel):
    """Smart form completion request"""
    partial_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class SmartFormResponse(BaseModel):
    """Smart form completion response"""
    success: bool
    completed_data: Dict[str, Any]
    suggestions: List[Dict[str, Any]]
    fields_completed: int


# Health Check Models
class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    portal: Optional[str] = None
    branch: Optional[str] = None
    response_time_ms: Optional[float] = None
    checked_at: str
    error: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """System-wide health check"""
    overall_status: str
    portals: Dict[str, HealthCheckResponse]
    checked_at: str


# Status Models
class ClaimStatusRequest(BaseModel):
    """Claim status check request"""
    claim_id: str
    portal: PortalEnum = PortalEnum.NPHIES
    branch: Optional[BranchEnum] = None


class ClaimStatusResponse(BaseModel):
    """Claim status response"""
    success: bool
    claim_id: str
    status: Optional[str] = None
    outcome: Optional[str] = None
    last_updated: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
