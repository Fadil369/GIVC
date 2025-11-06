"""
NPHIES API Configuration Settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings from environment variables"""
    
    # Base Configuration
    BASE_DIR = Path(__file__).resolve().parent.parent
    ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")
    
    # NPHIES API Endpoints
    NPHIES_BASE_URL = os.getenv(
        "NPHIES_BASE_URL", 
        "https://NPHIES.sa/api/fs/fhir"
    )
    NPHIES_SANDBOX_URL = os.getenv(
        "NPHIES_SANDBOX_URL", 
        "https://HSB.nphies.sa/api/fs/fhir"
    )
    NPHIES_MESSAGE_ENDPOINT = os.getenv(
        "NPHIES_MESSAGE_ENDPOINT", 
        "$process-message"
    )
    
    @property
    def api_base_url(self) -> str:
        """Get appropriate base URL based on environment"""
        if self.ENVIRONMENT == "production":
            return self.NPHIES_BASE_URL
        return self.NPHIES_SANDBOX_URL
    
    @property
    def message_url(self) -> str:
        """Get full message endpoint URL"""
        return f"{self.api_base_url}/{self.NPHIES_MESSAGE_ENDPOINT}"
    
    # Organization Credentials
    NPHIES_LICENSE = os.getenv("NPHIES_LICENSE", "7000911508")
    NPHIES_ORGANIZATION_ID = os.getenv("NPHIES_ORGANIZATION_ID", "10000000000988")
    NPHIES_PROVIDER_ID = os.getenv("NPHIES_PROVIDER_ID", "1048")
    NPHIES_PAYER_ID = os.getenv("NPHIES_PAYER_ID", "7000911508")
    
    # Provider Details
    PROVIDER_NAME = os.getenv("PROVIDER_NAME", "Al Hayat National Hospital")
    PROVIDER_CHI_ID = os.getenv("PROVIDER_CHI_ID", "1048")
    INSURANCE_GROUP_CODE = os.getenv("INSURANCE_GROUP_CODE", "1096")
    
    # Certificate Configuration
    CERT_FILE_PATH = os.getenv("CERT_FILE_PATH", str(BASE_DIR / "certs" / "client_certificate.pem"))
    CERT_KEY_PATH = os.getenv("CERT_KEY_PATH", str(BASE_DIR / "certs" / "private_key.pem"))
    CA_BUNDLE_PATH = os.getenv("CA_BUNDLE_PATH", str(BASE_DIR / "certs" / "ca_bundle.pem"))
    
    # Worksheet & Portal Data
    FOLLOW_UP_WORKBOOK_PATH = os.getenv(
        "FOLLOW_UP_WORKBOOK_PATH",
        str(BASE_DIR / "daily-follow-ups.xlsx"),
    )
    ACCOUNTS_WORKBOOK_PATH = os.getenv(
        "ACCOUNTS_WORKBOOK_PATH",
        str(BASE_DIR / "Accounts.xlsx"),
    )

    @property
    def use_certificates(self) -> bool:
        """Check if certificates are configured for production"""
        return self.ENVIRONMENT == "production" and os.path.exists(self.CERT_FILE_PATH)
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/nphies_integration.log")
    
    # API Settings
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))
    
    # Data Pipeline Settings
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
    ENABLE_ASYNC = os.getenv("ENABLE_ASYNC", "true").lower() == "true"
    PARALLEL_WORKERS = int(os.getenv("PARALLEL_WORKERS", "5"))
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/nphies_data.db")
    
    # Monitoring
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))
    
    def __repr__(self):
        return f"<Settings environment={self.ENVIRONMENT}>"


# Global settings instance
settings = Settings()
