"""
ClaimLinc Security Manager
Handles credential management, encryption, and security operations
"""

import os
import json
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyring
import bcrypt


class SecurityManager:
    """Manages security operations including credential encryption and validation"""
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize security manager
        
        Args:
            master_key: Master encryption key (should be from environment)
        """
        self.config_dir = Path("./config/security")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption key
        self.master_key = master_key or os.getenv("CLAIMLINC_MASTER_KEY")
        if not self.master_key:
            self.master_key = self._generate_master_key()
            self._save_master_key(self.master_key)
        
        self.fernet = self._get_fernet_encryption()
        self._load_security_config()
    
    def _generate_master_key(self) -> str:
        """Generate a new master encryption key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _save_master_key(self, key: str):
        """Save master key to secure location"""
        key_path = self.config_dir / "master.key"
        with open(key_path, "w") as f:
            f.write(key)
        # Set restrictive permissions
        os.chmod(key_path, 0o600)
    
    def _get_fernet_encryption(self) -> Fernet:
        """Get Fernet encryption instance"""
        if not self.master_key:
            raise ValueError("Master key not available")
        
        # Derive key from master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'claimlinc_salt',  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def _load_security_config(self):
        """Load security configuration"""
        config_file = self.config_dir / "security_config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                self.security_config = json.load(f)
        else:
            self.security_config = self._create_default_config()
            self._save_security_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default security configuration"""
        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "encryption_algorithms": ["Fernet", "PBKDF2"],
            "credential_expiry_days": 90,
            "max_login_attempts": 3,
            "session_timeout_minutes": 60,
            "password_policy": {
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special_chars": True,
                "prevent_common_passwords": True
            },
            "api_security": {
                "require_api_key": True,
                "rate_limiting": {
                    "requests_per_minute": 100,
                    "burst_limit": 10
                },
                "cors_origins": ["localhost", "127.0.0.1"],
                "secure_headers": True
            },
            "audit_logging": {
                "enabled": True,
                "log_level": "INFO",
                "include_sensitive_data": False
            }
        }
    
    def _save_security_config(self):
        """Save security configuration"""
        config_file = self.config_dir / "security_config.json"
        with open(config_file, "w") as f:
            json.dump(self.security_config, f, indent=2)
    
    def encrypt_credential(self, credential: str, credential_type: str = "password") -> str:
        """
        Encrypt a credential value
        
        Args:
            credential: Plain text credential
            credential_type: Type of credential (password, api_key, token)
            
        Returns:
            Encrypted credential string
        """
        try:
            # Add metadata
            payload = {
                "credential": credential,
                "type": credential_type,
                "timestamp": datetime.now().isoformat(),
                "version": self.security_config["version"]
            }
            
            # Encrypt the payload
            encrypted_data = self.fernet.encrypt(json.dumps(payload).encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt_credential(self, encrypted_credential: str) -> Dict[str, Any]:
        """
        Decrypt a credential value
        
        Args:
            encrypted_credential: Base64 encoded encrypted credential
            
        Returns:
            Dictionary with decrypted credential and metadata
        """
        try:
            # Decode from base64
            encrypted_data = base64.urlsafe_b64decode(encrypted_credential.encode())
            
            # Decrypt
            decrypted_data = self.fernet.decrypt(encrypted_data)
            payload = json.loads(decrypted_data.decode())
            
            return payload
            
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def store_credential(self, service_name: str, credential_name: str, 
                       credential_value: str, credential_type: str = "password") -> bool:
        """
        Store credential using system keyring
        
        Args:
            service_name: Name of the service (bupa, globemed, waseel)
            credential_name: Name of the credential (username, password, api_key)
            credential_value: Value of the credential
            credential_type: Type of credential
            
        Returns:
            Success status
        """
        try:
            # Encrypt the credential
            encrypted_value = self.encrypt_credential(credential_value, credential_type)
            
            # Store in system keyring
            keyring.set_password(
                service_name=f"claimlinc_{service_name}",
                username=credential_name,
                password=encrypted_value
            )
            
            self._audit_log("credential_stored", {
                "service": service_name,
                "credential_type": credential_type,
                "credential_name": credential_name
            })
            
            return True
            
        except Exception as e:
            self._audit_log("credential_storage_failed", {
                "service": service_name,
                "error": str(e)
            })
            return False
    
    def get_credential(self, service_name: str, credential_name: str) -> Optional[str]:
        """
        Retrieve credential from keyring
        
        Args:
            service_name: Name of the service
            credential_name: Name of the credential
            
        Returns:
            Decrypted credential value or None if not found
        """
        try:
            # Get encrypted credential from keyring
            encrypted_value = keyring.get_password(
                service_name=f"claimlinc_{service_name}",
                username=credential_name
            )
            
            if not encrypted_value:
                return None
            
            # Decrypt the credential
            payload = self.decrypt_credential(encrypted_value)
            
            # Check if credential is expired
            created_time = datetime.fromisoformat(payload["timestamp"])
            expiry_days = self.security_config["credential_expiry_days"]
            if datetime.now() - created_time > timedelta(days=expiry_days):
                self._audit_log("expired_credential_accessed", {
                    "service": service_name,
                    "credential_name": credential_name
                })
                return None
            
            self._audit_log("credential_retrieved", {
                "service": service_name,
                "credential_name": credential_name
            })
            
            return payload["credential"]
            
        except Exception as e:
            self._audit_log("credential_retrieval_failed", {
                "service": service_name,
                "credential_name": credential_name,
                "error": str(e)
            })
            return None
    
    def delete_credential(self, service_name: str, credential_name: str) -> bool:
        """
        Delete credential from keyring
        
        Args:
            service_name: Name of the service
            credential_name: Name of the credential
            
        Returns:
            Success status
        """
        try:
            keyring.delete_password(
                service_name=f"claimlinc_{service_name}",
                username=credential_name
            )
            
            self._audit_log("credential_deleted", {
                "service": service_name,
                "credential_name": credential_name
            })
            
            return True
            
        except Exception as e:
            self._audit_log("credential_deletion_failed", {
                "service": service_name,
                "credential_name": credential_name,
                "error": str(e)
            })
            return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    def validate_password_policy(self, password: str) -> Dict[str, Any]:
        """Validate password against security policy"""
        policy = self.security_config["password_policy"]
        errors = []
        warnings = []
        
        # Check minimum length
        if len(password) < policy["min_length"]:
            errors.append(f"Password must be at least {policy['min_length']} characters long")
        
        # Check character requirements
        if policy["require_uppercase"] and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if policy["require_lowercase"] and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if policy["require_numbers"] and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if policy["require_special_chars"] and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        # Check for common passwords
        if policy["prevent_common_passwords"]:
            common_passwords = [
                "password", "password123", "admin", "admin123",
                "123456", "123456789", "qwerty", "abc123",
                "password1", "12345678"
            ]
            if password.lower() in common_passwords:
                errors.append("Password cannot be a common password")
        
        # Calculate password strength score
        score = 100
        if len(password) < 8:
            score -= 20
        if not any(c.isupper() for c in password):
            score -= 10
        if not any(c.islower() for c in password):
            score -= 10
        if not any(c.isdigit() for c in password):
            score -= 10
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score -= 10
        
        return {
            "valid": len(errors) == 0,
            "score": max(0, score),
            "errors": errors,
            "warnings": warnings,
            "strength": "Very Weak" if score < 30 else "Weak" if score < 50 else "Fair" if score < 70 else "Good" if score < 85 else "Strong"
        }
    
    def create_api_key(self, service_name: str, permissions: List[str] = None) -> Dict[str, Any]:
        """Create a new API key with specified permissions"""
        if permissions is None:
            permissions = ["read", "write"]
        
        # Generate API key components
        key_id = f"{service_name}_{secrets.token_hex(8)}"
        secret_key = self.generate_secure_token(32)
        
        # Create full API key
        api_key = f"ck_{key_id}.{secret_key}"
        
        # Store API key securely
        self.store_credential(service_name, f"api_key_{key_id}", secret_key, "api_key")
        
        # Create API key metadata
        key_metadata = {
            "key_id": key_id,
            "service_name": service_name,
            "permissions": permissions,
            "created": datetime.now().isoformat(),
            "last_used": None,
            "active": True,
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat()  # 1 year expiry
        }
        
        # Save metadata
        metadata_file = self.config_dir / f"api_key_{key_id}.json"
        with open(metadata_file, "w") as f:
            json.dump(key_metadata, f, indent=2)
        
        self._audit_log("api_key_created", {
            "service": service_name,
            "key_id": key_id,
            "permissions": permissions
        })
        
        return {
            "api_key": api_key,
            "key_id": key_id,
            "service_name": service_name,
            "permissions": permissions,
            "created": key_metadata["created"],
            "expires_at": key_metadata["expires_at"]
        }
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return metadata"""
        try:
            # Parse API key
            if not api_key.startswith("ck_"):
                return None
            
            parts = api_key.split(".", 1)
            if len(parts) != 2:
                return None
            
            key_id, secret_key = parts
            
            # Get service name from key_id
            service_name = key_id.split("_")[1] if "_" in key_id else "unknown"
            
            # Retrieve stored secret
            stored_secret = self.get_credential(service_name, f"api_key_{key_id.split('_', 1)[1]}")
            if not stored_secret:
                return None
            
            # Verify secret key
            if stored_secret != secret_key:
                return None
            
            # Load metadata
            metadata_file = self.config_dir / f"api_key_{key_id.split('_', 1)[1]}.json"
            if not metadata_file.exists():
                return None
            
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            
            # Check if key is active and not expired
            if not metadata.get("active", False):
                return None
            
            expiry_date = datetime.fromisoformat(metadata["expires_at"])
            if datetime.now() > expiry_date:
                return None
            
            # Update last used
            metadata["last_used"] = datetime.now().isoformat()
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            
            self._audit_log("api_key_validated", {
                "service": service_name,
                "key_id": key_id
            })
            
            return metadata
            
        except Exception as e:
            self._audit_log("api_key_validation_failed", {
                "error": str(e)
            })
            return None
    
    def _audit_log(self, event_type: str, details: Dict[str, Any]):
        """Log security events"""
        if not self.security_config["audit_logging"]["enabled"]:
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "severity": self._get_event_severity(event_type)
        }
        
        # In production, this would write to a secure audit log
        # For now, store in local log file
        log_file = self.config_dir / "audit.log"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _get_event_severity(self, event_type: str) -> str:
        """Get severity level for security event"""
        high_risk_events = [
            "credential_storage_failed",
            "credential_retrieval_failed",
            "api_key_validation_failed",
            "expired_credential_accessed"
        ]
        
        if event_type in high_risk_events:
            return "HIGH"
        elif "failed" in event_type:
            return "MEDIUM"
        else:
            return "INFO"
    
    def rotate_master_key(self) -> bool:
        """Rotate the master encryption key"""
        try:
            # Generate new master key
            new_master_key = self._generate_master_key()
            
            # Re-encrypt all stored credentials
            # This is a simplified implementation - in production,
            # you would need to decrypt and re-encrypt all stored data
            
            # Update master key
            self.master_key = new_master_key
            self.fernet = self._get_fernet_encryption()
            self._save_master_key(new_master_key)
            
            self._audit_log("master_key_rotated", {})
            return True
            
        except Exception as e:
            self._audit_log("master_key_rotation_failed", {"error": str(e)})
            return False
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security status report"""
        try:
            # Count stored credentials
            credential_count = 0
            api_key_count = 0
            
            for credential_file in self.config_dir.glob("api_key_*.json"):
                api_key_count += 1
            
            # Check for expired API keys
            expired_keys = []
            for key_file in self.config_dir.glob("api_key_*.json"):
                with open(key_file, "r") as f:
                    metadata = json.load(f)
                    expiry_date = datetime.fromisoformat(metadata["expires_at"])
                    if datetime.now() > expiry_date and metadata.get("active", False):
                        expired_keys.append(metadata["key_id"])
            
            return {
                "security_status": "SECURE",
                "master_key_status": "ACTIVE",
                "total_credentials": credential_count,
                "total_api_keys": api_key_count,
                "expired_api_keys": len(expired_keys),
                "configuration": self.security_config,
                "audit_log_size": len(list(self.config_dir.glob("audit.log"))) if (self.config_dir / "audit.log").exists() else 0,
                "last_audit_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "security_status": "ERROR",
                "error": str(e),
                "last_audit_check": datetime.now().isoformat()
            }


# Utility functions
def get_security_manager() -> SecurityManager:
    """Get global security manager instance"""
    if not hasattr(get_security_manager, "_instance"):
        master_key = os.getenv("CLAIMLINC_MASTER_KEY")
        get_security_manager._instance = SecurityManager(master_key)
    return get_security_manager._instance


def store_payer_credentials(payer: str, username: str, password: str) -> bool:
    """Store payer credentials securely"""
    security_manager = get_security_manager()
    
    # Store username
    username_success = security_manager.store_credential(payer, "username", username, "username")
    
    # Store password (encrypted)
    password_success = security_manager.store_credential(payer, "password", password, "password")
    
    return username_success and password_success


def get_payer_credentials(payer: str) -> Dict[str, Optional[str]]:
    """Get payer credentials securely"""
    security_manager = get_security_manager()
    
    return {
        "username": security_manager.get_credential(payer, "username"),
        "password": security_manager.get_credential(payer, "password")
    }


if __name__ == "__main__":
    # Example usage
    security_manager = SecurityManager()
    
    # Store sample credentials
    success = store_payer_credentials("bupa", "test_user", "test_password")
    print(f"Credential storage successful: {success}")
    
    # Retrieve credentials
    credentials = get_payer_credentials("bupa")
    print(f"Retrieved credentials: {credentials}")
    
    # Generate API key
    api_key_info = security_manager.create_api_key("bupa", ["read", "write", "admin"])
    print(f"API Key created: {api_key_info}")
    
    # Validate API key
    validation = security_manager.validate_api_key(api_key_info["api_key"])
    print(f"API Key validation: {validation}")
    
    # Generate security report
    report = security_manager.get_security_report()
    print(f"Security report: {json.dumps(report, indent=2)}")
