"""
NPHIES Authentication Manager
Handles authentication and session management for NPHIES API
"""
import logging
from typing import Optional, Dict, Tuple
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import settings

logger = logging.getLogger(__name__)


class AuthenticationManager:
    """Manages authentication for NPHIES API requests"""
    
    def __init__(self):
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with proper configuration"""
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=settings.MAX_RETRIES,
            backoff_factor=settings.RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json",
            "User-Agent": "NPHIES-Python-Client/1.0"
        })
        
        # Configure certificates for production
        if settings.use_certificates:
            self._configure_certificates()
        
        logger.info(f"Authentication session initialized for {settings.ENVIRONMENT} environment")
    
    def _configure_certificates(self):
        """Configure SSL certificates for production environment"""
        try:
            cert_file = Path(settings.CERT_FILE_PATH)
            key_file = Path(settings.CERT_KEY_PATH)
            
            if not cert_file.exists():
                logger.warning(f"Certificate file not found: {cert_file}")
                return
            
            if not key_file.exists():
                logger.warning(f"Key file not found: {key_file}")
                return
            
            # Set certificate tuple (cert, key)
            self.session.cert = (str(cert_file), str(key_file))
            
            # Set CA bundle if available
            if settings.CA_BUNDLE_PATH and Path(settings.CA_BUNDLE_PATH).exists():
                self.session.verify = settings.CA_BUNDLE_PATH
            
            logger.info("SSL certificates configured successfully")
            
        except Exception as e:
            logger.error(f"Error configuring certificates: {str(e)}")
            raise
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests
        
        Returns:
            Dictionary of authentication headers
        """
        headers = {
            "X-License-Number": settings.NPHIES_LICENSE,
            "X-Organization-ID": settings.NPHIES_ORGANIZATION_ID,
            "X-Provider-ID": settings.NPHIES_PROVIDER_ID
        }
        
        return headers
    
    def make_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        additional_headers: Optional[Dict] = None
    ) -> requests.Response:
        """
        Make authenticated request to NPHIES API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            data: Request body data
            params: Query parameters
            additional_headers: Additional headers to include
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If request fails
        """
        # Merge headers
        headers = self.get_auth_headers()
        if additional_headers:
            headers.update(additional_headers)
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=settings.REQUEST_TIMEOUT
            )
            
            # Log response status
            logger.debug(f"Response status: {response.status_code}")
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {settings.REQUEST_TIMEOUT} seconds")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {response.status_code}: {response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during request: {str(e)}")
            raise
    
    def post(self, url: str, data: Dict, **kwargs) -> requests.Response:
        """Make POST request"""
        return self.make_request("POST", url, data=data, **kwargs)
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request"""
        return self.make_request("GET", url, **kwargs)
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to NPHIES API
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Try to reach the base URL
            response = self.session.get(
                settings.api_base_url,
                timeout=10,
                verify=True if settings.ENVIRONMENT == "production" else False
            )
            
            if response.status_code < 500:
                return True, f"Connection successful (Status: {response.status_code})"
            else:
                return False, f"Server error (Status: {response.status_code})"
                
        except requests.exceptions.ConnectionError:
            return False, "Connection failed - Cannot reach NPHIES server"
        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()
            logger.info("Authentication session closed")


# Global auth manager instance
auth_manager = AuthenticationManager()
