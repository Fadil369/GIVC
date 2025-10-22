"""
Certificate Manager for NPHIES SSL/TLS Certificates
"""
import logging
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class CertificateManager:
    """Manages SSL/TLS certificates for NPHIES API"""
    
    def __init__(self, cert_path: Optional[str] = None, key_path: Optional[str] = None):
        """
        Initialize certificate manager
        
        Args:
            cert_path: Path to certificate file
            key_path: Path to private key file
        """
        from config.settings import settings
        
        self.cert_path = Path(cert_path) if cert_path else Path(settings.CERT_FILE_PATH)
        self.key_path = Path(key_path) if key_path else Path(settings.CERT_KEY_PATH)
        self.ca_bundle_path = Path(settings.CA_BUNDLE_PATH) if settings.CA_BUNDLE_PATH else None
    
    def validate_certificate(self) -> Tuple[bool, str]:
        """
        Validate certificate file and check expiration
        
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        try:
            if not self.cert_path.exists():
                return False, f"Certificate file not found: {self.cert_path}"
            
            # Read certificate
            with open(self.cert_path, 'rb') as f:
                cert_data = f.read()
            
            # Parse certificate
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            # Check expiration
            now = datetime.now()
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
            
            if now < not_before:
                return False, f"Certificate not yet valid (valid from {not_before})"
            
            if now > not_after:
                return False, f"Certificate expired on {not_after}"
            
            # Calculate days until expiration
            days_remaining = (not_after - now).days
            
            if days_remaining < 30:
                message = f"⚠️ Certificate expires soon ({days_remaining} days remaining)"
                logger.warning(message)
            else:
                message = f"✓ Certificate valid until {not_after} ({days_remaining} days remaining)"
            
            # Get certificate subject
            subject = cert.subject
            subject_str = ", ".join([f"{attr.oid._name}={attr.value}" for attr in subject])
            
            logger.info(f"Certificate subject: {subject_str}")
            
            return True, message
            
        except Exception as e:
            return False, f"Certificate validation error: {str(e)}"
    
    def validate_private_key(self) -> Tuple[bool, str]:
        """
        Validate private key file
        
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        try:
            if not self.key_path.exists():
                return False, f"Private key file not found: {self.key_path}"
            
            # Try to read the key
            with open(self.key_path, 'rb') as f:
                key_data = f.read()
            
            # Basic validation - check if it's PEM formatted
            if b'BEGIN PRIVATE KEY' not in key_data and b'BEGIN RSA PRIVATE KEY' not in key_data:
                return False, "Invalid private key format (not PEM)"
            
            return True, "✓ Private key file valid"
            
        except Exception as e:
            return False, f"Private key validation error: {str(e)}"
    
    def get_certificate_info(self) -> dict:
        """
        Get detailed certificate information
        
        Returns:
            Dictionary with certificate details
        """
        info = {
            "cert_path": str(self.cert_path),
            "key_path": str(self.key_path),
            "cert_exists": self.cert_path.exists(),
            "key_exists": self.key_path.exists(),
            "is_valid": False,
            "subject": None,
            "issuer": None,
            "not_before": None,
            "not_after": None,
            "days_remaining": None
        }
        
        try:
            if self.cert_path.exists():
                with open(self.cert_path, 'rb') as f:
                    cert_data = f.read()
                
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
                
                # Extract details
                subject = cert.subject
                issuer = cert.issuer
                
                info.update({
                    "is_valid": True,
                    "subject": ", ".join([f"{attr.oid._name}={attr.value}" for attr in subject]),
                    "issuer": ", ".join([f"{attr.oid._name}={attr.value}" for attr in issuer]),
                    "not_before": cert.not_valid_before.isoformat(),
                    "not_after": cert.not_valid_after.isoformat(),
                    "days_remaining": (cert.not_valid_after - datetime.now()).days
                })
        
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def setup_certificates(self) -> Tuple[bool, str]:
        """
        Setup and validate all certificates
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Create certs directory if it doesn't exist
        self.cert_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Validate certificate
        cert_valid, cert_msg = self.validate_certificate()
        if not cert_valid:
            return False, f"Certificate validation failed: {cert_msg}"
        
        # Validate private key
        key_valid, key_msg = self.validate_private_key()
        if not key_valid:
            return False, f"Private key validation failed: {key_msg}"
        
        logger.info("All certificates validated successfully")
        return True, f"Certificates ready - {cert_msg}"


# Helper function to check certificates
def check_certificates() -> dict:
    """
    Check certificate status
    
    Returns:
        Dictionary with certificate status
    """
    manager = CertificateManager()
    
    cert_valid, cert_msg = manager.validate_certificate()
    key_valid, key_msg = manager.validate_private_key()
    
    return {
        "certificate": {
            "valid": cert_valid,
            "message": cert_msg
        },
        "private_key": {
            "valid": key_valid,
            "message": key_msg
        },
        "ready": cert_valid and key_valid,
        "info": manager.get_certificate_info()
    }
