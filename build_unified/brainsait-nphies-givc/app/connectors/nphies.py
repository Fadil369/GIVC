"""
NPHIES (National Platform for Health Insurance Exchange Services) Connector
Implements certificate-based authentication and FHIR-compliant healthcare transactions
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import ssl
import httpx
from pathlib import Path
import jwt
from app.connectors.base import BaseConnector
from app.core import log


class NPHIESConnector(BaseConnector):
    """
    NPHIES Platform connector with certificate authentication
    Supports: Eligibility, Prior Authorization, Claims, Communication
    """
    
    def __init__(self, environment: str = "production", config: Dict[str, Any] = None):
        super().__init__("nphies", environment, config or {})
        self.environment = environment
        self.base_url = self._get_base_url()
        self.auth_url = config.get('auth_url', 'https://sso.nphies.sa')
        self.realm = config.get('realm', 'sehaticoreprod')
        self.client_id = config.get('client_id', 'community')
        
        # Hospital Configuration
        self.hospital_id = config.get('hospital_id', '10000000000988')
        self.chi_id = config.get('chi_id', '1048')
        self.license = config.get('license', '7000911508')
        
        # Certificate paths
        self.cert_path = config.get('cert_path', './certificates/nphies_production.pem')
        self.key_path = config.get('key_path', './certificates/nphies_production_key.pem')
        self.cert_password = config.get('cert_password')
        
        # Access token
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    def _get_base_url(self) -> str:
        """Get base URL based on environment"""
        urls = {
            'production': 'https://HSB.nphies.sa',
            'sandbox': 'https://sandbox.nphies.sa',
            'conformance': 'https://conformance.nphies.sa'
        }
        return urls.get(self.environment, urls['production'])
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get HTTP client with SSL certificate authentication"""
        if self._client is None or self._client.is_closed:
            # Check if certificates exist
            cert_exists = Path(self.cert_path).exists() if self.cert_path else False
            key_exists = Path(self.key_path).exists() if self.key_path else False
            
            if cert_exists and key_exists:
                # Create SSL context with certificate
                ssl_context = ssl.create_default_context()
                ssl_context.load_cert_chain(
                    certfile=self.cert_path,
                    keyfile=self.key_path,
                    password=self.cert_password
                )
                
                self._client = httpx.AsyncClient(
                    timeout=httpx.Timeout(self.timeout),
                    verify=ssl_context,
                    cert=(self.cert_path, self.key_path),
                    follow_redirects=True,
                    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
                )
                log.info(f"NPHIES client initialized with certificate authentication")
            else:
                log.warning(f"NPHIES certificates not found, using basic client")
                self._client = httpx.AsyncClient(
                    timeout=httpx.Timeout(self.timeout),
                    follow_redirects=True,
                    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
                )
        
        return self._client
    
    async def login(self, username: Optional[str] = None, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate with NPHIES using OpenID Connect
        Returns access token for API calls
        """
        log.info(f"Authenticating with NPHIES {self.environment}...")
        
        try:
            # Build token endpoint
            token_url = f"{self.auth_url}/auth/realms/{self.realm}/protocol/openid-connect/token"
            
            # Prepare token request
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id
            }
            
            if username and password:
                data['grant_type'] = 'password'
                data['username'] = username
                data['password'] = password
            
            client = await self.get_client()
            response = await client.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                
                # Create session
                session_data = {
                    'access_token': self.access_token,
                    'token_type': token_data.get('token_type', 'Bearer'),
                    'expires_at': self.token_expires_at.isoformat(),
                    'environment': self.environment,
                    'hospital_id': self.hospital_id
                }
                
                session_id = self.session_manager.create_session(
                    portal="nphies",
                    branch=self.environment,
                    session_data=session_data,
                    timeout=expires_in
                )
                
                log.info(f"Successfully authenticated to NPHIES {self.environment}")
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'access_token': self.access_token,
                    'expires_at': self.token_expires_at.isoformat(),
                    'environment': self.environment
                }
            else:
                raise Exception(f"Authentication failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            log.error(f"NPHIES authentication failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'environment': self.environment
            }
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or (self.token_expires_at and datetime.utcnow() >= self.token_expires_at):
            result = await self.login()
            if not result.get('success'):
                raise Exception("Failed to authenticate with NPHIES")
    
    async def _make_nphies_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make authenticated request to NPHIES API"""
        await self._ensure_authenticated()
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json'
        }
        
        if data:
            kwargs['json'] = data
        
        response = await self.make_request(method, url, headers=headers, **kwargs)
        return response.json()
    
    async def check_eligibility(
        self,
        patient_id: str,
        insurance_id: str,
        service_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check patient eligibility with insurance
        FHIR CoverageEligibilityRequest
        """
        log.info(f"Checking eligibility for patient {patient_id}...")
        
        try:
            # Build FHIR CoverageEligibilityRequest
            request_data = {
                'resourceType': 'CoverageEligibilityRequest',
                'status': 'active',
                'purpose': ['validation'],
                'patient': {
                    'reference': f'Patient/{patient_id}'
                },
                'servicedDate': service_date or datetime.utcnow().strftime('%Y-%m-%d'),
                'insurance': [{
                    'coverage': {
                        'reference': f'Coverage/{insurance_id}'
                    }
                }],
                'provider': {
                    'reference': f'Organization/{self.hospital_id}'
                }
            }
            
            result = await self._make_nphies_request(
                'POST',
                '/eligibility/v1/check',
                data=request_data
            )
            
            return {
                'success': True,
                'eligible': result.get('outcome') == 'complete',
                'data': result
            }
            
        except Exception as e:
            log.error(f"Eligibility check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_prior_authorization(
        self,
        patient_id: str,
        insurance_id: str,
        services: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create prior authorization request
        FHIR Claim resource with type=preauthorization
        """
        log.info(f"Creating prior authorization for patient {patient_id}...")
        
        try:
            # Build FHIR Claim for prior authorization
            claim_data = {
                'resourceType': 'Claim',
                'status': 'active',
                'type': {
                    'coding': [{
                        'system': 'http://terminology.hl7.org/CodeSystem/claim-type',
                        'code': 'institutional'
                    }]
                },
                'use': 'preauthorization',
                'patient': {
                    'reference': f'Patient/{patient_id}'
                },
                'created': datetime.utcnow().isoformat(),
                'provider': {
                    'reference': f'Organization/{self.hospital_id}'
                },
                'priority': {
                    'coding': [{
                        'code': 'normal'
                    }]
                },
                'insurance': [{
                    'sequence': 1,
                    'focal': True,
                    'coverage': {
                        'reference': f'Coverage/{insurance_id}'
                    }
                }],
                'item': []
            }
            
            # Add service items
            for idx, service in enumerate(services, 1):
                claim_data['item'].append({
                    'sequence': idx,
                    'productOrService': {
                        'coding': [{
                            'code': service.get('code')
                        }]
                    },
                    'servicedDate': service.get('date'),
                    'quantity': {
                        'value': service.get('quantity', 1)
                    },
                    'unitPrice': {
                        'value': service.get('unit_price'),
                        'currency': 'SAR'
                    }
                })
            
            result = await self._make_nphies_request(
                'POST',
                '/priorauth/v1/create',
                data=claim_data
            )
            
            return {
                'success': True,
                'authorization_id': result.get('id'),
                'status': result.get('status'),
                'data': result
            }
            
        except Exception as e:
            log.error(f"Prior authorization creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def submit_claim(self, claim_data: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit institutional/professional claim to NPHIES
        FHIR Claim resource
        """
        log.info(f"Submitting claim to NPHIES...")
        
        try:
            # Build FHIR Claim resource
            fhir_claim = self._build_fhir_claim(claim_data)
            
            result = await self._make_nphies_request(
                'POST',
                '/claim/v1/submit',
                data=fhir_claim
            )
            
            return {
                'success': True,
                'claim_id': result.get('id'),
                'status': result.get('status'),
                'submitted_at': datetime.utcnow().isoformat(),
                'data': result
            }
            
        except Exception as e:
            log.error(f"NPHIES claim submission failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_fhir_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build FHIR-compliant Claim resource"""
        return {
            'resourceType': 'Claim',
            'status': 'active',
            'type': {
                'coding': [{
                    'system': 'http://terminology.hl7.org/CodeSystem/claim-type',
                    'code': claim_data.get('claim_type', 'institutional')
                }]
            },
            'use': 'claim',
            'patient': {
                'reference': f"Patient/{claim_data.get('patient_id')}"
            },
            'created': datetime.utcnow().isoformat(),
            'provider': {
                'reference': f'Organization/{self.hospital_id}'
            },
            'priority': {
                'coding': [{
                    'code': 'normal'
                }]
            },
            'insurance': [{
                'sequence': 1,
                'focal': True,
                'coverage': {
                    'reference': f"Coverage/{claim_data.get('insurance_id')}"
                }
            }],
            'item': self._build_claim_items(claim_data.get('items', []))
        }
    
    def _build_claim_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build FHIR claim items"""
        fhir_items = []
        for idx, item in enumerate(items, 1):
            fhir_items.append({
                'sequence': idx,
                'productOrService': {
                    'coding': [{
                        'code': item.get('code'),
                        'display': item.get('description')
                    }]
                },
                'servicedDate': item.get('service_date'),
                'quantity': {
                    'value': item.get('quantity', 1)
                },
                'unitPrice': {
                    'value': item.get('unit_price'),
                    'currency': 'SAR'
                },
                'net': {
                    'value': item.get('quantity', 1) * item.get('unit_price'),
                    'currency': 'SAR'
                }
            })
        return fhir_items
    
    async def get_claim_status(self, claim_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get claim status from NPHIES"""
        log.info(f"Getting claim status for {claim_id}...")
        
        try:
            result = await self._make_nphies_request(
                'GET',
                f'/claim/v1/status?claim={claim_id}'
            )
            
            return {
                'success': True,
                'claim_id': claim_id,
                'status': result.get('status'),
                'outcome': result.get('outcome'),
                'data': result
            }
            
        except Exception as e:
            log.error(f"Get claim status failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def poll_status(self, bundle_id: str) -> Dict[str, Any]:
        """Poll for transaction bundle status"""
        try:
            result = await self._make_nphies_request(
                'GET',
                f'/poll/v1/status?bundle={bundle_id}'
            )
            
            return {
                'success': True,
                'bundle_id': bundle_id,
                'status': result.get('status'),
                'data': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def send_communication(
        self,
        claim_id: str,
        message: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send communication related to a claim"""
        try:
            comm_data = {
                'resourceType': 'Communication',
                'status': 'completed',
                'category': [{
                    'coding': [{
                        'code': 'claim-attachment'
                    }]
                }],
                'about': [{
                    'reference': f'Claim/{claim_id}'
                }],
                'payload': [{
                    'contentString': message
                }]
            }
            
            if attachments:
                for attachment in attachments:
                    comm_data['payload'].append({
                        'contentAttachment': attachment
                    })
            
            result = await self._make_nphies_request(
                'POST',
                '/communication/v1/send',
                data=comm_data
            )
            
            return {
                'success': True,
                'communication_id': result.get('id'),
                'data': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def logout(self, session_id: str) -> bool:
        """Logout from NPHIES (invalidate token)"""
        try:
            self.access_token = None
            self.token_expires_at = None
            self.session_manager.delete_session(session_id)
            return True
        except Exception as e:
            log.error(f"NPHIES logout failed: {str(e)}")
            return False
