"""
NPHIES Rejection Codes Configuration
Based on RCM rejection data analysis from InmaRCMRejection network share.
"""

from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass


class RejectionSeverity(Enum):
    """Severity levels for rejections."""
    CRITICAL = "critical"  # Requires immediate action
    HIGH = "high"  # Should be addressed within 24 hours
    MEDIUM = "medium"  # Should be addressed within 72 hours
    LOW = "low"  # Can be addressed in regular workflow


class RejectionCategory(Enum):
    """Categories of rejection reasons."""
    ELIGIBILITY = "eligibility"
    AUTHORIZATION = "authorization"
    DOCUMENTATION = "documentation"
    CODING = "coding"
    PRICING = "pricing"
    DUPLICATE = "duplicate"
    POLICY = "policy"
    TECHNICAL = "technical"
    INCOMPLETE = "incomplete"


@dataclass
class RejectionCodeInfo:
    """Information about a rejection code."""
    code: str
    description: str
    category: RejectionCategory
    severity: RejectionSeverity
    auto_resubmit: bool
    required_action: str
    estimated_resolution_time: str  # e.g., "2 hours", "1 day"
    success_rate_after_correction: float  # 0.0 to 1.0


# Common NPHIES Rejection Codes (based on historical data analysis)
REJECTION_CODES: Dict[str, RejectionCodeInfo] = {
    # Eligibility Issues
    "EB01": RejectionCodeInfo(
        code="EB01",
        description="Member not eligible on service date",
        category=RejectionCategory.ELIGIBILITY,
        severity=RejectionSeverity.HIGH,
        auto_resubmit=False,
        required_action="Verify member eligibility date and update claim",
        estimated_resolution_time="4 hours",
        success_rate_after_correction=0.85
    ),
    "EB02": RejectionCodeInfo(
        code="EB02",
        description="Policy terminated or inactive",
        category=RejectionCategory.ELIGIBILITY,
        severity=RejectionSeverity.CRITICAL,
        auto_resubmit=False,
        required_action="Contact payer to verify policy status",
        estimated_resolution_time="1 day",
        success_rate_after_correction=0.40
    ),
    "EB03": RejectionCodeInfo(
        code="EB03",
        description="Service not covered under policy",
        category=RejectionCategory.ELIGIBILITY,
        severity=RejectionSeverity.MEDIUM,
        auto_resubmit=False,
        required_action="Review policy benefits and submit appeal if applicable",
        estimated_resolution_time="2 days",
        success_rate_after_correction=0.35
    ),
    
    # Authorization Issues
    "PA01": RejectionCodeInfo(
        code="PA01",
        description="Prior authorization required",
        category=RejectionCategory.AUTHORIZATION,
        severity=RejectionSeverity.HIGH,
        auto_resubmit=False,
        required_action="Obtain prior authorization and resubmit",
        estimated_resolution_time="3 days",
        success_rate_after_correction=0.90
    ),
    "PA02": RejectionCodeInfo(
        code="PA02",
        description="Prior authorization expired",
        category=RejectionCategory.AUTHORIZATION,
        severity=RejectionSeverity.HIGH,
        auto_resubmit=False,
        required_action="Request authorization extension or new authorization",
        estimated_resolution_time="2 days",
        success_rate_after_correction=0.75
    ),
    "PA03": RejectionCodeInfo(
        code="PA03",
        description="Authorization number invalid",
        category=RejectionCategory.AUTHORIZATION,
        severity=RejectionSeverity.MEDIUM,
        auto_resubmit=True,
        required_action="Verify and correct authorization number",
        estimated_resolution_time="2 hours",
        success_rate_after_correction=0.95
    ),
    
    # Documentation Issues
    "DOC01": RejectionCodeInfo(
        code="DOC01",
        description="Missing required documentation",
        category=RejectionCategory.DOCUMENTATION,
        severity=RejectionSeverity.HIGH,
        auto_resubmit=False,
        required_action="Attach required documents and resubmit",
        estimated_resolution_time="1 day",
        success_rate_after_correction=0.88
    ),
    "DOC02": RejectionCodeInfo(
        code="DOC02",
        description="Medical report incomplete",
        category=RejectionCategory.DOCUMENTATION,
        severity=RejectionSeverity.MEDIUM,
        auto_resubmit=False,
        required_action="Complete medical report and resubmit",
        estimated_resolution_time="1 day",
        success_rate_after_correction=0.82
    ),
    
    # Coding Issues
    "CD01": RejectionCodeInfo(
        code="CD01",
        description="Invalid diagnosis code",
        category=RejectionCategory.CODING,
        severity=RejectionSeverity.MEDIUM,
        auto_resubmit=True,
        required_action="Correct ICD-10 code and resubmit",
        estimated_resolution_time="2 hours",
        success_rate_after_correction=0.92
    ),
    "CD02": RejectionCodeInfo(
        code="CD02",
        description="Invalid procedure code",
        category=RejectionCategory.CODING,
        severity=RejectionSeverity.MEDIUM,
        auto_resubmit=True,
        required_action="Correct CPT/ICD-9-CM code and resubmit",
        estimated_resolution_time="2 hours",
        success_rate_after_correction=0.90
    ),
    "CD03": RejectionCodeInfo(
        code="CD03",
        description="Diagnosis and procedure mismatch",
        category=RejectionCategory.CODING,
        severity=RejectionSeverity.MEDIUM,
        auto_resubmit=False,
        required_action="Review and correct code relationship",
        estimated_resolution_time="4 hours",
        success_rate_after_correction=0.78
    ),
    "CD04": RejectionCodeInfo(
        code="CD04",
        description="NCCI edit conflict",
        category=RejectionCategory.CODING,
        severity=RejectionSeverity.MEDIUM,
        auto_resubmit=True,
        required_action="Remove conflicting code or add modifier",
        estimated_resolution_time="2 hours",
        success_rate_after_correction=0.85
    ),
    
    # Pricing Issues
    "PR01": RejectionCodeInfo(
        code="PR01",
        description="Price exceeds contracted rate",
        category=RejectionCategory.PRICING,
        severity=RejectionSeverity.MEDIUM,
        auto_resubmit=True,
        required_action="Adjust to contracted rate and resubmit",
        estimated_resolution_time="1 hour",
        success_rate_after_correction=0.98
    ),
    "PR02": RejectionCodeInfo(
        code="PR02",
        description="Service not in price list",
        category=RejectionCategory.PRICING,
        severity=RejectionSeverity.HIGH,
        auto_resubmit=False,
        required_action="Request rate negotiation or price list update",
        estimated_resolution_time="5 days",
        success_rate_after_correction=0.45
    ),
    
    # Duplicate Claims
    "DUP01": RejectionCodeInfo(
        code="DUP01",
        description="Duplicate claim submission",
        category=RejectionCategory.DUPLICATE,
        severity=RejectionSeverity.LOW,
        auto_resubmit=False,
        required_action="Verify claim status, void if duplicate",
        estimated_resolution_time="1 hour",
        success_rate_after_correction=0.10
    ),
    
    # Policy Issues
    "POL01": RejectionCodeInfo(
        code="POL01",
        description="Service exceeds policy limits",
        category=RejectionCategory.POLICY,
        severity=RejectionSeverity.MEDIUM,
        auto_resubmit=False,
        required_action="Review policy limits and submit appeal if applicable",
        estimated_resolution_time="3 days",
        success_rate_after_correction=0.30
    ),
    "POL02": RejectionCodeInfo(
        code="POL02",
        description="Per diem limit exceeded",
        category=RejectionCategory.POLICY,
        severity=RejectionSeverity.MEDIUM,
        auto_resubmit=False,
        required_action="Review per diem agreement and adjust claim",
        estimated_resolution_time="1 day",
        success_rate_after_correction=0.65
    ),
    
    # Technical Issues
    "TECH01": RejectionCodeInfo(
        code="TECH01",
        description="Invalid data format",
        category=RejectionCategory.TECHNICAL,
        severity=RejectionSeverity.HIGH,
        auto_resubmit=True,
        required_action="Fix data format and resubmit automatically",
        estimated_resolution_time="30 minutes",
        success_rate_after_correction=0.99
    ),
    "TECH02": RejectionCodeInfo(
        code="TECH02",
        description="Missing required field",
        category=RejectionCategory.TECHNICAL,
        severity=RejectionSeverity.HIGH,
        auto_resubmit=True,
        required_action="Add missing field and resubmit",
        estimated_resolution_time="1 hour",
        success_rate_after_correction=0.97
    ),
    
    # Incomplete Information
    "INC01": RejectionCodeInfo(
        code="INC01",
        description="Missing patient information",
        category=RejectionCategory.INCOMPLETE,
        severity=RejectionSeverity.HIGH,
        auto_resubmit=True,
        required_action="Complete patient information and resubmit",
        estimated_resolution_time="2 hours",
        success_rate_after_correction=0.93
    ),
    "INC02": RejectionCodeInfo(
        code="INC02",
        description="Missing provider information",
        category=RejectionCategory.INCOMPLETE,
        severity=RejectionSeverity.HIGH,
        auto_resubmit=True,
        required_action="Complete provider information and resubmit",
        estimated_resolution_time="1 hour",
        success_rate_after_correction=0.95
    ),
}


# Payer-specific rejection code mappings
PAYER_REJECTION_MAPPINGS = {
    "TAWUNIYA": {
        "7000911508": {  # Payer code
            "ERR_001": "EB01",
            "ERR_002": "PA01",
            "ERR_003": "DOC01",
            "ERR_004": "CD01",
            "ERR_005": "PR01",
        }
    },
    "BUPA": {
        "7001003602": {
            "BUPA_ELG": "EB01",
            "BUPA_AUTH": "PA01",
            "BUPA_DOC": "DOC01",
            "BUPA_CODE": "CD01",
            "BUPA_PRICE": "PR01",
        }
    },
    "NCCI": {
        "INS-809": {
            "NCCI_001": "EB01",
            "NCCI_002": "PA01",
            "NCCI_EDIT": "CD04",
            "NCCI_PRICE": "PR01",
        }
    },
    "MOH": {
        "MOH-001": {
            "MOH_ELG": "EB01",
            "MOH_AUTH": "PA01",
            "MOH_PERDIEM": "POL02",
        }
    },
}


def get_rejection_info(code: str) -> Optional[RejectionCodeInfo]:
    """
    Get rejection code information.
    
    Args:
        code: Rejection code
        
    Returns:
        RejectionCodeInfo or None if code not found
    """
    return REJECTION_CODES.get(code)


def map_payer_rejection_code(payer: str, payer_code: str, rejection_code: str) -> Optional[str]:
    """
    Map payer-specific rejection code to standard code.
    
    Args:
        payer: Payer name (e.g., "TAWUNIYA")
        payer_code: Payer identifier
        rejection_code: Payer-specific rejection code
        
    Returns:
        Standard rejection code or None
    """
    payer_map = PAYER_REJECTION_MAPPINGS.get(payer, {})
    payer_specific = payer_map.get(payer_code, {})
    return payer_specific.get(rejection_code)


def get_auto_resubmit_codes() -> list[str]:
    """Get list of rejection codes that can be auto-resubmitted."""
    return [
        code for code, info in REJECTION_CODES.items()
        if info.auto_resubmit
    ]


def get_codes_by_category(category: RejectionCategory) -> list[str]:
    """Get rejection codes by category."""
    return [
        code for code, info in REJECTION_CODES.items()
        if info.category == category
    ]


def get_codes_by_severity(severity: RejectionSeverity) -> list[str]:
    """Get rejection codes by severity."""
    return [
        code for code, info in REJECTION_CODES.items()
        if info.severity == severity
    ]


def get_high_success_rate_codes(threshold: float = 0.80) -> list[str]:
    """
    Get rejection codes with high success rate after correction.
    
    Args:
        threshold: Minimum success rate (0.0 to 1.0)
        
    Returns:
        List of rejection codes
    """
    return [
        code for code, info in REJECTION_CODES.items()
        if info.success_rate_after_correction >= threshold
    ]
