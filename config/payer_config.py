"""
Payer-Specific Configuration
Based on RCM rejection data analysis from InmaRCMRejection network share.
Includes validation rules, claim volumes, and rejection patterns for each payer.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class PayerConfig:
    """Configuration for a specific payer/insurance company."""
    name: str
    code: str
    payer_type: str  # "private", "government"
    api_integration: bool
    claim_volume_monthly: int
    rejection_rate: float
    contact_phone: str
    contact_email: str
    portal_url: str
    nphies_enabled: bool
    nphies_org_id: str
    require_authorization_above: float  # Amount in SAR
    max_submission_days: int
    additional_rules: Dict[str, Any]


# Payer Configurations (Based on RCM Analysis)
PAYER_CONFIGS: Dict[str, PayerConfig] = {
    "BUPA": PayerConfig(
        name="Bupa Arabia for Cooperative Insurance",
        code="7001003602",
        payer_type="private",
        api_integration=True,
        claim_volume_monthly=659,  # Highest volume from analysis
        rejection_rate=0.18,  # 18% rejection rate
        contact_phone="+966-920003456",
        contact_email="claims@bupa.com.sa",
        portal_url="https://provider.bupa.com.sa",
        nphies_enabled=True,
        nphies_org_id="7001003602",
        require_authorization_above=2000.0,
        max_submission_days=90,
        additional_rules={
            "supports_electronic_prescriptions": True,
            "strict_eligibility_check": True,
            "branches": [
                "3-SGH-Aseer",
                "5-SGH-Dammam",
                "Madinah",
                "Jizan",
                "Khamis",
                "Riyadh",
                "Qassim"
            ],
            "common_rejections": [
                "eligibility_verification_failure",
                "authorization_expired",
                "price_exceeds_contracted_rate"
            ]
        }
    ),
    "TAWUNIYA": PayerConfig(
        name="Saudi Arabian Cooperative Insurance Company (TAWUNIYA)",
        code="7000911508",
        payer_type="private",
        api_integration=True,
        claim_volume_monthly=450,  # Estimated
        rejection_rate=0.15,
        contact_phone="+966-11-4601111",
        contact_email="claims@tawuniya.com.sa",
        portal_url="https://portal.tawuniya.com.sa",
        nphies_enabled=True,
        nphies_org_id="7000911508",
        require_authorization_above=5000.0,
        max_submission_days=90,
        additional_rules={
            "supports_electronic_prescriptions": True,
            "initial_rejection_trend": "decreasing_23_to_25",
            "common_rejections": [
                "missing_authorization",
                "incomplete_documentation",
                "coding_errors"
            ]
        }
    ),
    "NCCI": PayerConfig(
        name="National Company for Cooperative Insurance (NCCI)",
        code="INS-809",
        payer_type="private",
        api_integration=True,
        claim_volume_monthly=108,  # From RCM analysis
        rejection_rate=0.12,
        contact_phone="+966-11-2186666",
        contact_email="claims@ncci.com.sa",
        portal_url="https://portal.ncci.com.sa",
        nphies_enabled=True,
        nphies_org_id="INS-809",
        require_authorization_above=3000.0,
        max_submission_days=60,
        additional_rules={
            "enforce_ncci_edits": True,
            "requires_reconciliation": True,
            "common_rejections": [
                "ncci_edit_conflict",
                "duplicate_claim",
                "price_discrepancy"
            ]
        }
    ),
    "MOH": PayerConfig(
        name="Ministry of Health",
        code="MOH-001",
        payer_type="government",
        api_integration=True,
        claim_volume_monthly=89,  # From RCM analysis
        rejection_rate=0.23,  # Highest rejection rate
        contact_phone="+966-11-4011111",
        contact_email="support@moh.gov.sa",
        portal_url="https://portal.moh.gov.sa",
        nphies_enabled=True,
        nphies_org_id="MOH-001",
        require_authorization_above=1000.0,
        max_submission_days=30,
        additional_rules={
            "enforce_per_diem_limits": True,
            "require_discharge_summary": True,
            "strict_price_list_validation": True,
            "per_diem_rates": {
                "general_ward": 1200.0,
                "icu": 3500.0,
                "private_room": 2000.0
            },
            "common_rejections": [
                "per_diem_exceeded",
                "missing_authorization",
                "price_list_exceeded",
                "incomplete_documentation",
                "invalid_patient_id"
            ]
        }
    ),
    "ART": PayerConfig(
        name="Al Rajhi Takaful",
        code="ART-001",
        payer_type="private",
        api_integration=True,
        claim_volume_monthly=26,  # From RCM analysis
        rejection_rate=0.14,
        contact_phone="+966-920000084",
        contact_email="claims@alrajhitakaful.com",
        portal_url="https://portal.alrajhitakaful.com",
        nphies_enabled=True,
        nphies_org_id="ART-001",
        require_authorization_above=3000.0,
        max_submission_days=60,
        additional_rules={
            "takaful_compliant": True,
            "common_rejections": [
                "eligibility_issues",
                "authorization_required"
            ]
        }
    ),
    "MALATH": PayerConfig(
        name="Malath Cooperative Insurance",
        code="MALATH-001",
        payer_type="private",
        api_integration=True,
        claim_volume_monthly=14,  # From RCM analysis
        rejection_rate=0.16,
        contact_phone="+966-11-2183333",
        contact_email="claims@malath.com.sa",
        portal_url="https://portal.malath.com.sa",
        nphies_enabled=True,
        nphies_org_id="MALATH-001",
        require_authorization_above=2500.0,
        max_submission_days=75,
        additional_rules={
            "common_rejections": [
                "documentation_issues",
                "coding_errors"
            ]
        }
    ),
    "SAICO": PayerConfig(
        name="Saudi Arabian Insurance Company (SAICO)",
        code="SAICO-001",
        payer_type="private",
        api_integration=True,
        claim_volume_monthly=2,  # From RCM analysis (lowest volume)
        rejection_rate=0.10,  # Lowest rejection rate
        contact_phone="+966-11-2790000",
        contact_email="claims@saico.com.sa",
        portal_url="https://portal.saico.com.sa",
        nphies_enabled=True,
        nphies_org_id="SAICO-001",
        require_authorization_above=4000.0,
        max_submission_days=90,
        additional_rules={
            "low_volume_payer": True,
            "common_rejections": [
                "eligibility_verification"
            ]
        }
    ),
}


# Financial Impact Data (From RCM Analysis)
FINANCIAL_IMPACT = {
    "total_rejected_amount_sar": 19_197_002.91,
    "average_rejection_amount_sar": 21_425.23,
    "total_rejection_count": 896,
    "monthly_average_rejections": 75,
    "breakdown_by_payer": {
        "BUPA": {
            "rejection_count": 659,
            "estimated_amount_sar": 14_190_000.0,
            "percentage_of_total": 73.5
        },
        "NCCI": {
            "rejection_count": 108,
            "estimated_amount_sar": 2_313_000.0,
            "percentage_of_total": 12.1
        },
        "MOH": {
            "rejection_count": 89,
            "estimated_amount_sar": 1_906_000.0,
            "percentage_of_total": 9.9
        },
        "ART": {
            "rejection_count": 26,
            "estimated_amount_sar": 557_000.0,
            "percentage_of_total": 2.9
        },
        "MALATH": {
            "rejection_count": 14,
            "estimated_amount_sar": 300_000.0,
            "percentage_of_total": 1.6
        },
    }
}


# Payer-Specific Validation Functions

def get_payer_config(payer_code: str) -> PayerConfig:
    """
    Get payer configuration by code.
    
    Args:
        payer_code: Payer code (e.g., "BUPA", "NCCI")
        
    Returns:
        PayerConfig object
        
    Raises:
        ValueError: If payer code not found
    """
    config = PAYER_CONFIGS.get(payer_code)
    if not config:
        raise ValueError(f"Unknown payer code: {payer_code}")
    return config


def requires_authorization(payer_code: str, claim_amount: float) -> bool:
    """
    Check if claim requires prior authorization.
    
    Args:
        payer_code: Payer code
        claim_amount: Claim amount in SAR
        
    Returns:
        True if authorization required
    """
    config = get_payer_config(payer_code)
    return claim_amount >= config.require_authorization_above


def get_submission_deadline_days(payer_code: str) -> int:
    """
    Get maximum submission days for payer.
    
    Args:
        payer_code: Payer code
        
    Returns:
        Maximum days allowed for submission
    """
    config = get_payer_config(payer_code)
    return config.max_submission_days


def get_high_volume_payers() -> List[str]:
    """
    Get list of high-volume payers (>50 claims/month).
    
    Returns:
        List of payer codes
    """
    return [
        code for code, config in PAYER_CONFIGS.items()
        if config.claim_volume_monthly > 50
    ]


def get_high_rejection_rate_payers(threshold: float = 0.15) -> List[str]:
    """
    Get payers with high rejection rates.
    
    Args:
        threshold: Rejection rate threshold (0.0 to 1.0)
        
    Returns:
        List of payer codes
    """
    return [
        code for code, config in PAYER_CONFIGS.items()
        if config.rejection_rate >= threshold
    ]


def get_payer_rejection_patterns(payer_code: str) -> List[str]:
    """
    Get common rejection patterns for payer.
    
    Args:
        payer_code: Payer code
        
    Returns:
        List of common rejection reasons
    """
    config = get_payer_config(payer_code)
    return config.additional_rules.get("common_rejections", [])


# Priority Claims Processing
# Based on RCM analysis: Prioritize high-volume, high-rejection rate payers
PROCESSING_PRIORITY = [
    "BUPA",      # Highest volume (659), high rejection rate (18%)
    "MOH",       # High rejection rate (23%), government payer
    "NCCI",      # Medium volume (108), medium rejection rate (12%)
    "TAWUNIYA",  # Good performance, medium volume
    "ART",       # Low volume (26)
    "MALATH",    # Low volume (14)
    "SAICO",     # Lowest volume (2), best rejection rate (10%)
]
