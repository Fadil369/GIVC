"""
GIVC Platform Configuration
Enhanced configuration with real provider credentials and platform details
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ProviderConfig:
    """Provider configuration details"""
    name: str
    license: str
    nphies_id: str
    chi_id: str = None
    group_code: str = None
    policies: List[str] = None
    contact_person: str = None
    account_id: str = None

@dataclass
class PlatformEndpoints:
    """NPHIES Platform endpoints"""
    production_base: str = "https://HSB.nphies.sa"
    sandbox_base: str = "https://HSB.nphies.sa/sandbox"
    conformance_base: str = "https://HSB.nphies.sa/conformance"
    fhir_endpoint: str = "/api/fs/fhir/$process-message"
    ftp_host: str = "172.25.11.15"
    ftp_port: int = 21


class GIVCPlatformConfig:
    """
    GIVC (BrainSAIT) Platform Configuration
    Real production credentials and provider details
    """
    
    # Platform Information
    PLATFORM_NAME = "BrainSAIT Ultrathink Healthcare Platform"
    PLATFORM_VERSION = "2.0"
    PLATFORM_URL = "https://4d31266d.givc-platform-static.pages.dev/"
    
    # Integrated Healthcare Providers
    PROVIDERS = {
        "tawuniya": ProviderConfig(
            name="TAWUNIYA Medical Insurance",
            license="7000911508",
            nphies_id="7000911508",
            group_code="1096",
            policies=["BALSAM GOLD"] * 8,  # 8 BALSAM GOLD Policies
            contact_person="MOHAMMED SALEH"
        ),
        "al_hayat": ProviderConfig(
            name="Al Hayat National Hospital",
            license="7000911508",
            nphies_id="10000000000988",
            chi_id="1048"
        ),
        "ncci": ProviderConfig(
            name="NCCI Referral System",
            license="7000911508",
            nphies_id="7000911508",
            account_id="INS-809"
        )
    }
    
    # NPHIES Endpoints
    ENDPOINTS = PlatformEndpoints()
    
    # Platform Features
    FEATURES = {
        "ai_powered_processing": True,
        "real_time_integration": True,
        "enterprise_security": True,
        "mobile_first_design": True,
        "automated_validation": True,
        "smart_form_completion": True,
        "claim_validation": True,
        "error_detection": True
    }
    
    # Platform Statistics (Live)
    STATISTICS = {
        "insurance_providers": 28,
        "healthcare_facilities": 6600,
        "active_transactions": "Real-time",
        "system_uptime": "99.9%",
        "beneficiaries_served": "13+ Million",
        "provider_facilities_onboarded": "5,320+",
        "insurers_onboarded": 25,
        "software_vendors_onboarded": "60+",
        "market_share_claims": "98%",
        "authorization_adjudication_30min": "96%"
    }
    
    # Integration Modes
    INTEGRATION_MODES = {
        "production": {
            "base_url": "https://HSB.nphies.sa",
            "requires_certificate": True,
            "environment": "production"
        },
        "sandbox": {
            "base_url": "https://HSB.nphies.sa/sandbox",
            "requires_certificate": False,
            "environment": "sandbox"
        },
        "conformance": {
            "base_url": "https://HSB.nphies.sa/conformance",
            "requires_certificate": False,
            "environment": "testing"
        }
    }
    
    # Message Types (FHIR R4)
    MESSAGE_TYPES = {
        "eligibility": {
            "event": "http://nphies.sa/eligibility",
            "focus": "EligibilityRequest",
            "code": "EligibilityRequest"
        },
        "claim": {
            "event": "http://nphies.sa/claim",
            "focus": "Claim",
            "code": "claim-request"
        },
        "prior_authorization": {
            "event": "http://nphies.sa/priorauthorization",
            "focus": "Claim",
            "code": "preauth-request"
        },
        "claim_inquiry": {
            "event": "http://nphies.sa/claim-inquiry",
            "focus": "ClaimResponse",
            "code": "claim-inquiry"
        },
        "communication": {
            "event": "http://nphies.sa/communication",
            "focus": "Communication",
            "code": "communication-request"
        },
        "poll": {
            "event": "http://nphies.sa/poll",
            "focus": "Communication",
            "code": "poll-request"
        }
    }
    
    # Default Headers
    DEFAULT_HEADERS = {
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json",
        "User-Agent": "GIVC-BrainSAIT/2.0"
    }
    
    # Security Standards
    SECURITY_STANDARDS = {
        "certificate_based_auth": True,
        "encrypted_communications": True,
        "saudi_healthcare_compliance": True,
        "hipaa_compliant": True,
        "tls_version": "1.2+",
        "encryption_algorithm": "AES-256"
    }
    
    # Validation Rules
    VALIDATION_RULES = {
        "member_id_length": 10,
        "payer_license_length": 10,
        "provider_license_length": 10,
        "nphies_id_min_length": 14,
        "required_fields": [
            "member_id",
            "payer_id",
            "provider_id",
            "service_date"
        ]
    }
    
    # Timeouts and Retry Configuration
    NETWORK_CONFIG = {
        "connection_timeout": 30,
        "read_timeout": 60,
        "max_retries": 3,
        "retry_backoff_factor": 2,
        "retry_statuses": [500, 502, 503, 504]
    }
    
    # FTP Configuration for File Exchange
    FTP_CONFIG = {
        "host": "172.25.11.15",
        "port": 21,
        "use_tls": True,
        "passive_mode": True
    }
    
    @classmethod
    def get_provider_config(cls, provider_key: str) -> ProviderConfig:
        """Get provider configuration by key"""
        return cls.PROVIDERS.get(provider_key)
    
    @classmethod
    def get_endpoint_url(cls, mode: str = "production") -> str:
        """Get full endpoint URL for specified mode"""
        config = cls.INTEGRATION_MODES.get(mode, cls.INTEGRATION_MODES["production"])
        return f"{config['base_url']}{cls.ENDPOINTS.fhir_endpoint}"
    
    @classmethod
    def get_message_event(cls, message_type: str) -> str:
        """Get FHIR event URL for message type"""
        msg_config = cls.MESSAGE_TYPES.get(message_type, {})
        return msg_config.get("event", "")
    
    @classmethod
    def validate_credentials(cls, license: str, nphies_id: str) -> bool:
        """Validate if credentials match known providers"""
        for provider in cls.PROVIDERS.values():
            if provider.license == license and provider.nphies_id == nphies_id:
                return True
        return False
    
    @classmethod
    def get_platform_info(cls) -> Dict:
        """Get complete platform information"""
        return {
            "platform_name": cls.PLATFORM_NAME,
            "version": cls.PLATFORM_VERSION,
            "url": cls.PLATFORM_URL,
            "features": cls.FEATURES,
            "statistics": cls.STATISTICS,
            "providers": {k: {
                "name": v.name,
                "license": v.license,
                "nphies_id": v.nphies_id
            } for k, v in cls.PROVIDERS.items()}
        }
    
    @classmethod
    def get_tawuniya_config(cls) -> ProviderConfig:
        """Quick access to TAWUNIYA configuration"""
        return cls.PROVIDERS["tawuniya"]
    
    @classmethod
    def get_al_hayat_config(cls) -> ProviderConfig:
        """Quick access to Al Hayat Hospital configuration"""
        return cls.PROVIDERS["al_hayat"]
    
    @classmethod
    def build_request_headers(cls, license: str = None) -> Dict:
        """Build request headers with optional license"""
        headers = cls.DEFAULT_HEADERS.copy()
        if license:
            headers["License"] = license
        return headers


# Convenience functions for common operations
def get_tawuniya_license() -> str:
    """Get TAWUNIYA license number"""
    return GIVCPlatformConfig.PROVIDERS["tawuniya"].license


def get_al_hayat_nphies_id() -> str:
    """Get Al Hayat Hospital NPHIES ID"""
    return GIVCPlatformConfig.PROVIDERS["al_hayat"].nphies_id


def get_production_endpoint() -> str:
    """Get production NPHIES endpoint"""
    return GIVCPlatformConfig.get_endpoint_url("production")


def get_sandbox_endpoint() -> str:
    """Get sandbox NPHIES endpoint"""
    return GIVCPlatformConfig.get_endpoint_url("sandbox")


# Platform-specific constants
BALSAM_GOLD_POLICY_COUNT = 8
GROUP_CODE_1096 = "1096"
DEFAULT_PROVIDER_LICENSE = "7000911508"
AL_HAYAT_CHI_ID = "1048"
NCCI_ACCOUNT_ID = "INS-809"
