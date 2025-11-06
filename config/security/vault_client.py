"""
HashiCorp Vault Client for ClaimLinc-GIVC
Provides secure secret management with AppRole authentication
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hvac
from hvac.exceptions import VaultError, InvalidPath
from functools import lru_cache
import threading

logger = logging.getLogger(__name__)


class VaultClient:
    """
    Secure Vault client with AppRole authentication and automatic token renewal
    
    Compliant with:
    - HIPAA §164.308: Administrative safeguards for access control
    - HIPAA §164.312: Technical safeguards for encryption and access
    """
    
    def __init__(
        self,
        vault_addr: Optional[str] = None,
        role_id: Optional[str] = None,
        secret_id: Optional[str] = None,
        ca_cert_path: Optional[str] = None,
        client_cert_path: Optional[str] = None,
        client_key_path: Optional[str] = None
    ):
        """
        Initialize Vault client with AppRole authentication
        
        Args:
            vault_addr: Vault server address (defaults to VAULT_ADDR env var)
            role_id: AppRole role ID (defaults to VAULT_ROLE_ID env var)
            secret_id: AppRole secret ID (defaults to VAULT_SECRET_ID env var)
            ca_cert_path: Path to CA certificate for TLS verification
            client_cert_path: Path to client certificate for mTLS
            client_key_path: Path to client key for mTLS
        """
        self.vault_addr = vault_addr or os.getenv('VAULT_ADDR', 'https://vault.claimlinc.local:8200')
        self.role_id = role_id or os.getenv('VAULT_ROLE_ID')
        self.secret_id = secret_id or os.getenv('VAULT_SECRET_ID')
        
        if not self.role_id or not self.secret_id:
            raise ValueError("Vault AppRole credentials (role_id, secret_id) must be provided")
        
        # TLS configuration
        self.ca_cert = ca_cert_path or os.getenv('VAULT_CACERT', '/etc/vault.d/tls/ca.pem')
        self.client_cert = client_cert_path or os.getenv('VAULT_CLIENT_CERT')
        self.client_key = client_key_path or os.getenv('VAULT_CLIENT_KEY')
        
        # Initialize client
        self.client: Optional[hvac.Client] = None
        self.token_expiry: Optional[datetime] = None
        self._lock = threading.Lock()
        
        self._authenticate()
        
        logger.info(f"Vault client initialized for {self.vault_addr}")
    
    def _authenticate(self) -> None:
        """Authenticate with Vault using AppRole"""
        try:
            # Configure TLS
            tls_config = {'verify': self.ca_cert}
            if self.client_cert and self.client_key:
                tls_config['cert'] = (self.client_cert, self.client_key)
            
            # Create client
            self.client = hvac.Client(
                url=self.vault_addr,
                **tls_config
            )
            
            # Authenticate with AppRole
            auth_response = self.client.auth.approle.login(
                role_id=self.role_id,
                secret_id=self.secret_id
            )
            
            # Calculate token expiry (with 5-minute buffer)
            ttl = auth_response['auth']['lease_duration']
            self.token_expiry = datetime.now() + timedelta(seconds=ttl - 300)
            
            logger.info(f"Vault authentication successful, token expires at {self.token_expiry}")
            
        except VaultError as e:
            logger.error(f"Vault authentication failed: {e}")
            raise
    
    def _ensure_authenticated(self) -> None:
        """Ensure client is authenticated, re-authenticate if token expired"""
        with self._lock:
            if not self.client or not self.client.is_authenticated():
                logger.warning("Vault client not authenticated, re-authenticating...")
                self._authenticate()
            elif self.token_expiry and datetime.now() >= self.token_expiry:
                logger.info("Vault token expired, re-authenticating...")
                self._authenticate()
    
    def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Retrieve a secret from Vault KV v2 secrets engine
        
        Args:
            path: Secret path (e.g., 'jwt/signing-key')
            key: Optional specific key within the secret
            
        Returns:
            Secret value or entire secret dict if key not specified
            
        Raises:
            VaultError: If secret retrieval fails
        """
        self._ensure_authenticated()
        
        try:
            # KV v2 secrets engine uses 'data' in the path
            full_path = f"secret/data/{path}"
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            
            secret_data = response['data']['data']
            
            if key:
                return secret_data.get(key)
            return secret_data
            
        except InvalidPath:
            logger.error(f"Secret not found at path: {path}")
            raise
        except VaultError as e:
            logger.error(f"Failed to retrieve secret from {path}: {e}")
            raise
    
    def get_database_credentials(self, role: str = "claimlinc-app") -> Dict[str, str]:
        """
        Get dynamic database credentials from Vault
        
        Args:
            role: Database role name
            
        Returns:
            Dict with 'username' and 'password' keys
        """
        self._ensure_authenticated()
        
        try:
            response = self.client.secrets.database.generate_credentials(name=role)
            
            credentials = {
                'username': response['data']['username'],
                'password': response['data']['password'],
                'lease_id': response['lease_id'],
                'lease_duration': response['lease_duration']
            }
            
            logger.info(f"Generated database credentials for role: {role}, lease: {credentials['lease_duration']}s")
            return credentials
            
        except VaultError as e:
            logger.error(f"Failed to generate database credentials for {role}: {e}")
            raise
    
    def get_rabbitmq_credentials(self, role: str = "celery-worker") -> Dict[str, str]:
        """
        Get dynamic RabbitMQ credentials from Vault
        
        Args:
            role: RabbitMQ role name
            
        Returns:
            Dict with 'username' and 'password' keys
        """
        self._ensure_authenticated()
        
        try:
            response = self.client.read(f"rabbitmq/creds/{role}")
            
            credentials = {
                'username': response['data']['username'],
                'password': response['data']['password'],
                'lease_id': response['lease_id'],
                'lease_duration': response['lease_duration']
            }
            
            logger.info(f"Generated RabbitMQ credentials for role: {role}, lease: {credentials['lease_duration']}s")
            return credentials
            
        except VaultError as e:
            logger.error(f"Failed to generate RabbitMQ credentials for {role}: {e}")
            raise
    
    def encrypt_data(self, plaintext: str, key_name: str = "api-data") -> str:
        """
        Encrypt data using Vault Transit engine
        
        Args:
            plaintext: Data to encrypt
            key_name: Transit key name
            
        Returns:
            Encrypted ciphertext (base64 encoded)
        """
        self._ensure_authenticated()
        
        try:
            response = self.client.secrets.transit.encrypt_data(
                name=key_name,
                plaintext=plaintext
            )
            return response['data']['ciphertext']
            
        except VaultError as e:
            logger.error(f"Failed to encrypt data with key {key_name}: {e}")
            raise
    
    def decrypt_data(self, ciphertext: str, key_name: str = "api-data") -> str:
        """
        Decrypt data using Vault Transit engine
        
        Args:
            ciphertext: Encrypted data (base64 encoded)
            key_name: Transit key name
            
        Returns:
            Decrypted plaintext
        """
        self._ensure_authenticated()
        
        try:
            response = self.client.secrets.transit.decrypt_data(
                name=key_name,
                ciphertext=ciphertext
            )
            return response['data']['plaintext']
            
        except VaultError as e:
            logger.error(f"Failed to decrypt data with key {key_name}: {e}")
            raise
    
    def get_nphies_certificate(self) -> Dict[str, str]:
        """
        Issue NPHIES client certificate from Vault PKI engine
        
        Returns:
            Dict with 'certificate', 'private_key', and 'ca_chain' keys
        """
        self._ensure_authenticated()
        
        try:
            response = self.client.secrets.pki.generate_certificate(
                name='nphies-client',
                common_name='claimlinc-nphies.brainsait.io',
                extra_params={
                    'ttl': '8760h',  # 1 year
                    'alt_names': 'nphies.claimlinc.local',
                }
            )
            
            cert_data = {
                'certificate': response['data']['certificate'],
                'private_key': response['data']['private_key'],
                'ca_chain': response['data']['ca_chain'],
                'serial_number': response['data']['serial_number'],
                'expiration': response['data']['expiration']
            }
            
            logger.info(f"Issued NPHIES certificate, serial: {cert_data['serial_number']}")
            return cert_data
            
        except VaultError as e:
            logger.error(f"Failed to issue NPHIES certificate: {e}")
            raise
    
    def revoke_lease(self, lease_id: str) -> None:
        """
        Revoke a Vault lease (e.g., for dynamic credentials)
        
        Args:
            lease_id: Lease ID to revoke
        """
        self._ensure_authenticated()
        
        try:
            self.client.sys.revoke_lease(lease_id)
            logger.info(f"Revoked lease: {lease_id}")
        except VaultError as e:
            logger.error(f"Failed to revoke lease {lease_id}: {e}")
            raise


# Singleton instance
_vault_client: Optional[VaultClient] = None
_client_lock = threading.Lock()


def get_vault_client() -> VaultClient:
    """
    Get singleton Vault client instance
    
    Returns:
        Initialized VaultClient instance
    """
    global _vault_client
    
    with _client_lock:
        if _vault_client is None:
            _vault_client = VaultClient()
    
    return _vault_client


# Convenience functions
@lru_cache(maxsize=128)
def get_secret(path: str, key: Optional[str] = None) -> Any:
    """Cached secret retrieval (use for static secrets only)"""
    client = get_vault_client()
    return client.get_secret(path, key)


def get_db_credentials(role: str = "claimlinc-app") -> Dict[str, str]:
    """Get dynamic database credentials (not cached)"""
    client = get_vault_client()
    return client.get_database_credentials(role)


def get_rabbitmq_credentials(role: str = "celery-worker") -> Dict[str, str]:
    """Get dynamic RabbitMQ credentials (not cached)"""
    client = get_vault_client()
    return client.get_rabbitmq_credentials(role)
