"""
MOH (Ministry of Health) Specific Rules and Configuration
Based on RCM rejection data analysis showing MOH-specific patterns.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta


@dataclass
class MOHPriceListItem:
    """MOH price list item."""
    code: str
    description: str
    unit_price: float
    effective_date: str
    expiry_date: Optional[str] = None


@dataclass
class MOHPerDiemRule:
    """MOH per diem rules."""
    facility_type: str
    per_diem_rate: float
    max_days: int
    requires_authorization_after: int
    excluded_services: List[str]


@dataclass
class MOHValidationRule:
    """MOH validation rule."""
    rule_id: str
    description: str
    condition: str
    severity: str  # "error", "warning"
    message: str


# MOH Per Diem Rates (Based on RCM analysis)
MOH_PER_DIEM_RATES = {
    "general_ward": MOHPerDiemRule(
        facility_type="general_ward",
        per_diem_rate=1200.0,  # SAR
        max_days=30,
        requires_authorization_after=7,
        excluded_services=["surgical_procedures", "icu_admission"]
    ),
    "icu": MOHPerDiemRule(
        facility_type="icu",
        per_diem_rate=3500.0,  # SAR
        max_days=14,
        requires_authorization_after=3,
        excluded_services=[]
    ),
    "private_room": MOHPerDiemRule(
        facility_type="private_room",
        per_diem_rate=2000.0,  # SAR
        max_days=21,
        requires_authorization_after=5,
        excluded_services=["elective_procedures"]
    ),
}


# MOH Validation Rules
MOH_VALIDATION_RULES = [
    MOHValidationRule(
        rule_id="MOH_001",
        description="Patient must have valid MOH number",
        condition="patient.identifier.system == 'MOH'",
        severity="error",
        message="Missing or invalid MOH patient identifier"
    ),
    MOHValidationRule(
        rule_id="MOH_002",
        description="Service date must be within policy period",
        condition="service_date >= policy_start AND service_date <= policy_end",
        severity="error",
        message="Service date outside policy coverage period"
    ),
    MOHValidationRule(
        rule_id="MOH_003",
        description="Per diem limit check",
        condition="days_count <= max_per_diem_days",
        severity="error",
        message="Per diem days exceed policy maximum"
    ),
    MOHValidationRule(
        rule_id="MOH_004",
        description="Prior authorization required for stays > 7 days",
        condition="days_count > 7 AND authorization_present",
        severity="error",
        message="Prior authorization required for extended stay"
    ),
    MOHValidationRule(
        rule_id="MOH_005",
        description="Price must not exceed MOH price list",
        condition="claim_amount <= moh_price_list_amount",
        severity="error",
        message="Claimed amount exceeds MOH contracted rate"
    ),
    MOHValidationRule(
        rule_id="MOH_006",
        description="ICD-10 code must be valid",
        condition="diagnosis_code IN moh_accepted_icd10_codes",
        severity="error",
        message="Invalid or unsupported ICD-10 diagnosis code"
    ),
    MOHValidationRule(
        rule_id="MOH_007",
        description="Service must be in MOH covered services list",
        condition="procedure_code IN moh_covered_services",
        severity="error",
        message="Service not covered under MOH policy"
    ),
    MOHValidationRule(
        rule_id="MOH_008",
        description="Discharge summary required for inpatient",
        condition="encounter_type == 'inpatient' AND discharge_summary_attached",
        severity="error",
        message="Missing discharge summary for inpatient claim"
    ),
]


# MOH Common Rejection Patterns (from RCM analysis)
MOH_COMMON_REJECTIONS = {
    "per_diem_exceeded": {
        "frequency": "high",  # 23% of MOH rejections
        "prevention": "Implement per diem day counter with alerts at 5, 7, 10 days",
        "resolution_time": "1 day",
        "success_rate": 0.65
    },
    "missing_authorization": {
        "frequency": "high",  # 19% of MOH rejections
        "prevention": "Auto-check authorization requirement before submission",
        "resolution_time": "3 days",
        "success_rate": 0.90
    },
    "price_list_exceeded": {
        "frequency": "medium",  # 15% of MOH rejections
        "prevention": "Pre-submission price validation against MOH price list",
        "resolution_time": "2 hours",
        "success_rate": 0.95
    },
    "incomplete_documentation": {
        "frequency": "medium",  # 12% of MOH rejections
        "prevention": "Document checklist validation before submission",
        "resolution_time": "1 day",
        "success_rate": 0.88
    },
    "invalid_patient_id": {
        "frequency": "low",  # 8% of MOH rejections
        "prevention": "Real-time patient ID verification",
        "resolution_time": "2 hours",
        "success_rate": 0.92
    },
}


# MOH Submission Requirements
MOH_SUBMISSION_REQUIREMENTS = {
    "inpatient": {
        "required_documents": [
            "admission_report",
            "discharge_summary",
            "medical_report",
            "lab_results",
            "imaging_reports"
        ],
        "required_fields": [
            "admission_date",
            "discharge_date",
            "principal_diagnosis",
            "procedures_performed",
            "attending_physician"
        ],
        "max_submission_days_after_discharge": 30
    },
    "outpatient": {
        "required_documents": [
            "medical_report",
            "prescription"
        ],
        "required_fields": [
            "service_date",
            "diagnosis",
            "service_description",
            "treating_physician"
        ],
        "max_submission_days_after_service": 90
    },
    "emergency": {
        "required_documents": [
            "emergency_report",
            "triage_assessment"
        ],
        "required_fields": [
            "arrival_time",
            "emergency_diagnosis",
            "treatment_provided",
            "disposition"
        ],
        "max_submission_days_after_service": 15
    },
}


def validate_moh_per_diem(
    facility_type: str,
    days_count: int,
    has_authorization: bool
) -> tuple[bool, Optional[str]]:
    """
    Validate MOH per diem requirements.
    
    Args:
        facility_type: Type of facility (general_ward, icu, private_room)
        days_count: Number of days
        has_authorization: Whether prior authorization exists
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    rule = MOH_PER_DIEM_RATES.get(facility_type)
    if not rule:
        return False, f"Invalid facility type: {facility_type}"
    
    if days_count > rule.max_days:
        return False, f"Days ({days_count}) exceed maximum ({rule.max_days}) for {facility_type}"
    
    if days_count > rule.requires_authorization_after and not has_authorization:
        return False, f"Authorization required for stays exceeding {rule.requires_authorization_after} days"
    
    return True, None


def calculate_moh_per_diem_amount(facility_type: str, days_count: int) -> Optional[float]:
    """
    Calculate MOH per diem amount.
    
    Args:
        facility_type: Type of facility
        days_count: Number of days
        
    Returns:
        Total per diem amount or None if invalid
    """
    rule = MOH_PER_DIEM_RATES.get(facility_type)
    if not rule:
        return None
    
    if days_count > rule.max_days:
        return None
    
    return rule.per_diem_rate * days_count


def get_moh_required_documents(encounter_type: str) -> List[str]:
    """
    Get required documents for MOH submission.
    
    Args:
        encounter_type: Type of encounter (inpatient, outpatient, emergency)
        
    Returns:
        List of required documents
    """
    requirements = MOH_SUBMISSION_REQUIREMENTS.get(encounter_type, {})
    return requirements.get("required_documents", [])


def validate_moh_submission_timing(
    encounter_type: str,
    service_date: datetime,
    submission_date: datetime
) -> tuple[bool, Optional[str]]:
    """
    Validate MOH submission timing requirements.
    
    Args:
        encounter_type: Type of encounter
        service_date: Date of service/discharge
        submission_date: Date of submission
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    requirements = MOH_SUBMISSION_REQUIREMENTS.get(encounter_type)
    if not requirements:
        return False, f"Invalid encounter type: {encounter_type}"
    
    max_days_key = "max_submission_days_after_discharge" if encounter_type == "inpatient" else "max_submission_days_after_service"
    max_days = requirements.get(max_days_key, 30)
    
    days_difference = (submission_date - service_date).days
    
    if days_difference > max_days:
        return False, f"Submission ({days_difference} days) exceeds maximum allowed ({max_days} days) after service"
    
    return True, None


def get_moh_rejection_prevention_tip(rejection_type: str) -> Optional[Dict]:
    """
    Get prevention tips for common MOH rejections.
    
    Args:
        rejection_type: Type of rejection
        
    Returns:
        Dictionary with prevention information
    """
    return MOH_COMMON_REJECTIONS.get(rejection_type)


# MOH-specific endpoint configuration
MOH_NPHIES_CONFIG = {
    "base_url": "https://HSB.nphies.sa",
    "eligibility_endpoint": "/eligibility/v1/check",
    "claim_endpoint": "/claim/v1/submit",
    "communication_endpoint": "/communication/v1",
    "payer_code": "MOH-001",
    "provider_license": "10000000000988",  # Al Hayat Hospital
    "requires_certificate": True,
    "timeout_seconds": 30,
    "retry_attempts": 3,
}


# MOH Price List (sample - should be loaded from database or file)
MOH_PRICE_LIST: Dict[str, MOHPriceListItem] = {
    "99213": MOHPriceListItem(
        code="99213",
        description="Office visit - established patient",
        unit_price=150.0,
        effective_date="2024-01-01"
    ),
    "99214": MOHPriceListItem(
        code="99214",
        description="Office visit - established patient, moderate complexity",
        unit_price=200.0,
        effective_date="2024-01-01"
    ),
    "71020": MOHPriceListItem(
        code="71020",
        description="Chest X-ray, 2 views",
        unit_price=100.0,
        effective_date="2024-01-01"
    ),
}


def get_moh_price_list_rate(procedure_code: str) -> Optional[float]:
    """
    Get MOH contracted rate for procedure code.
    
    Args:
        procedure_code: Procedure code
        
    Returns:
        Unit price or None if not found
    """
    item = MOH_PRICE_LIST.get(procedure_code)
    return item.unit_price if item else None
