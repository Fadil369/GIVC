"""
NPHIES Client - FHIR R4 Integration for Saudi Arabian National Platform
Compliant with NPHIES IG v0.4.0
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import jwt
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class NPHIESClient:
    """
    Client for interacting with Saudi Arabia's NPHIES platform
    
    Features:
    - FHIR R4 resource building
    - JWT authentication with RS256
    - mTLS support
    - Idempotent requests
    - Full audit logging
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        provider_license: Optional[str] = None,
        use_sandbox: bool = True
    ):
        """
        Initialize NPHIES client
        
        Args:
            base_url: NPHIES endpoint (defaults to sandbox)
            provider_license: Healthcare provider license number
            use_sandbox: Use sandbox environment (default: True)
        """
        from config.security.vault_client import get_vault_client
        
        self.vault = get_vault_client()
        
        # Get configuration from Vault
        nphies_config = self.vault.get_secret('nphies/config')
        
        self.base_url = base_url or (
            'https://sandbox.nphies.sa/fhir' if use_sandbox
            else 'https://nphies.sa/fhir'
        )
        
        self.provider_license = provider_license or nphies_config.get('provider_license')
        self.organization_id = nphies_config.get('organization_id')
        
        # Get certificates for mTLS
        self.cert_data = self.vault.get_nphies_certificate()
        
        # Save certificates to temp files
        self.cert_path = Path('/tmp/nphies-client-cert.pem')
        self.key_path = Path('/tmp/nphies-client-key.pem')
        self.ca_path = Path('/tmp/nphies-ca.pem')
        
        self.cert_path.write_text(self.cert_data['certificate'])
        self.key_path.write_text(self.cert_data['private_key'])
        self.ca_path.write_text('\n'.join(self.cert_data['ca_chain']))
        
        logger.info(f"NPHIES client initialized for {self.base_url}")
    
    def _generate_jwt(self, scope: str = "eligibility claim payment") -> str:
        """
        Generate JWT for NPHIES authentication
        
        Args:
            scope: OAuth2 scopes required
            
        Returns:
            Signed JWT token
        """
        # Get signing key from Vault
        signing_key = self.vault.get_secret('jwt/nphies-signing-key', 'private_key')
        
        now = datetime.utcnow()
        payload = {
            'iss': f'https://claimlinc.brainsait.io',
            'sub': self.provider_license,
            'aud': 'https://nphies.sa',
            'exp': int((now + timedelta(hours=1)).timestamp()),
            'iat': int(now.timestamp()),
            'jti': str(uuid.uuid4()),
            'scope': scope
        }
        
        token = jwt.encode(
            payload,
            signing_key,
            algorithm='RS256',
            headers={'kid': 'nphies-signing-key-001'}
        )
        
        return token
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to NPHIES
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body
            params: Query parameters
            correlation_id: Request correlation ID
            
        Returns:
            Response data
            
        Raises:
            requests.HTTPError: On API error
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        
        url = f"{self.base_url}/{endpoint}"
        
        # Generate JWT
        token = self._generate_jwt()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json',
            'X-Correlation-ID': correlation_id
        }
        
        # Log request
        logger.info(
            f"NPHIES request: {method} {endpoint} [{correlation_id}]",
            extra={'correlation_id': correlation_id}
        )
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                cert=(str(self.cert_path), str(self.key_path)),
                verify=str(self.ca_path),
                timeout=30
            )
            
            response.raise_for_status()
            
            logger.info(
                f"NPHIES response: {response.status_code} [{correlation_id}]",
                extra={'correlation_id': correlation_id, 'status': response.status_code}
            )
            
            return response.json()
            
        except requests.HTTPError as e:
            logger.error(
                f"NPHIES request failed: {e.response.status_code} - {e.response.text} [{correlation_id}]",
                extra={'correlation_id': correlation_id, 'error': str(e)}
            )
            raise
    
    def build_patient_resource(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build FHIR Patient resource
        
        Args:
            patient_data: Patient demographic information
            
        Returns:
            FHIR Patient resource
        """
        return {
            'resourceType': 'Patient',
            'id': f"patient-{patient_data['member_id']}",
            'identifier': [
                {
                    'type': {
                        'coding': [{
                            'system': 'http://terminology.hl7.org/CodeSystem/v2-0203',
                            'code': 'MR'
                        }]
                    },
                    'system': 'http://claimlinc.brainsait.io/patient',
                    'value': patient_data['member_id']
                },
                {
                    'type': {
                        'coding': [{
                            'system': 'http://terminology.hl7.org/CodeSystem/v2-0203',
                            'code': 'NI'
                        }]
                    },
                    'system': 'http://nphies.sa/identifier/nationalid',
                    'value': patient_data.get('national_id', '')
                }
            ],
            'name': [{
                'use': 'official',
                'family': patient_data.get('family_name', ''),
                'given': [patient_data.get('given_name', '')]
            }],
            'gender': patient_data.get('gender', 'unknown'),
            'birthDate': patient_data.get('birth_date', '')
        }
    
    def build_coverage_resource(
        self,
        patient_id: str,
        payer_code: str,
        member_id: str,
        policy_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build FHIR Coverage resource
        
        Args:
            patient_id: Reference to Patient resource
            payer_code: Insurance payer code
            member_id: Insurance member ID
            policy_number: Policy/card number
            
        Returns:
            FHIR Coverage resource
        """
        return {
            'resourceType': 'Coverage',
            'id': f"coverage-{member_id}",
            'identifier': [{
                'system': 'http://claimlinc.brainsait.io/coverage',
                'value': member_id
            }],
            'status': 'active',
            'type': {
                'coding': [{
                    'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
                    'code': 'HIP',
                    'display': 'health insurance plan policy'
                }]
            },
            'subscriber': {
                'reference': f'Patient/{patient_id}'
            },
            'beneficiary': {
                'reference': f'Patient/{patient_id}'
            },
            'payor': [{
                'identifier': {
                    'system': 'http://nphies.sa/identifier/payer',
                    'value': payer_code
                }
            }],
            'class': [{
                'type': {
                    'coding': [{
                        'system': 'http://terminology.hl7.org/CodeSystem/coverage-class',
                        'code': 'policy'
                    }]
                },
                'value': policy_number or member_id
            }]
        }
    
    def build_eligibility_request(
        self,
        patient_data: Dict[str, Any],
        payer_code: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build FHIR EligibilityRequest bundle
        
        Args:
            patient_data: Patient demographic and insurance info
            payer_code: Insurance payer code
            correlation_id: Request correlation ID
            
        Returns:
            FHIR Bundle with EligibilityRequest
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        
        patient = self.build_patient_resource(patient_data)
        coverage = self.build_coverage_resource(
            patient_id=patient['id'],
            payer_code=payer_code,
            member_id=patient_data['member_id'],
            policy_number=patient_data.get('policy_number')
        )
        
        eligibility_request = {
            'resourceType': 'CoverageEligibilityRequest',
            'id': f"eligibility-{correlation_id}",
            'meta': {
                'profile': ['http://nphies.sa/fhir/ksa/nphies-fs/StructureDefinition/eligibility-request']
            },
            'identifier': [{
                'system': 'http://claimlinc.brainsait.io/eligibility-request',
                'value': f"ELG-{datetime.now().strftime('%Y%m%d')}-{correlation_id[:8]}"
            }],
            'status': 'active',
            'purpose': ['benefits'],
            'patient': {
                'reference': f"Patient/{patient['id']}"
            },
            'servicedDate': datetime.now().strftime('%Y-%m-%d'),
            'created': datetime.utcnow().isoformat() + 'Z',
            'provider': {
                'identifier': {
                    'system': 'http://nphies.sa/identifier/provider',
                    'value': self.provider_license
                }
            },
            'insurer': {
                'identifier': {
                    'system': 'http://nphies.sa/identifier/payer',
                    'value': payer_code
                }
            },
            'insurance': [{
                'focal': True,
                'coverage': {
                    'reference': f"Coverage/{coverage['id']}"
                }
            }]
        }
        
        # Build Bundle
        bundle = {
            'resourceType': 'Bundle',
            'type': 'collection',
            'entry': [
                {'resource': eligibility_request},
                {'resource': patient},
                {'resource': coverage}
            ]
        }
        
        return bundle
    
    def submit_eligibility_request(
        self,
        eligibility_bundle: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit eligibility request to NPHIES
        
        Args:
            eligibility_bundle: FHIR Bundle with EligibilityRequest
            correlation_id: Request correlation ID
            
        Returns:
            EligibilityResponse
        """
        response = self._make_request(
            method='POST',
            endpoint='CoverageEligibilityRequest',
            data=eligibility_bundle,
            correlation_id=correlation_id
        )
        
        return response
    
    def build_claim_bundle(
        self,
        claim_data: Dict[str, Any],
        payer_code: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build FHIR Claim bundle
        
        Args:
            claim_data: Complete claim information
            payer_code: Insurance payer code
            correlation_id: Request correlation ID
            
        Returns:
            FHIR Bundle with Claim and supporting resources
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        
        patient = self.build_patient_resource(claim_data['patient'])
        coverage = self.build_coverage_resource(
            patient_id=patient['id'],
            payer_code=payer_code,
            member_id=claim_data['patient']['member_id']
        )
        
        # Build claim items
        items = []
        for idx, service in enumerate(claim_data['services'], start=1):
            items.append({
                'sequence': idx,
                'productOrService': {
                    'coding': [{
                        'system': 'http://nphies.sa/terminology/CodeSystem/services',
                        'code': service['code'],
                        'display': service.get('description', '')
                    }]
                },
                'servicedDate': service['date'],
                'quantity': {
                    'value': service.get('quantity', 1)
                },
                'unitPrice': {
                    'value': float(service['unit_price']),
                    'currency': 'SAR'
                },
                'net': {
                    'value': float(service['total']),
                    'currency': 'SAR'
                }
            })
        
        claim = {
            'resourceType': 'Claim',
            'id': f"claim-{correlation_id}",
            'meta': {
                'profile': ['http://nphies.sa/fhir/ksa/nphies-fs/StructureDefinition/claim']
            },
            'identifier': [{
                'system': 'http://claimlinc.brainsait.io/claim',
                'value': claim_data.get('claim_id', f"CLM-{datetime.now().strftime('%Y%m%d')}-{correlation_id[:8]}")
            }],
            'status': 'active',
            'type': {
                'coding': [{
                    'system': 'http://terminology.hl7.org/CodeSystem/claim-type',
                    'code': claim_data.get('type', 'professional')
                }]
            },
            'use': 'claim',
            'patient': {
                'reference': f"Patient/{patient['id']}"
            },
            'created': datetime.utcnow().isoformat() + 'Z',
            'provider': {
                'identifier': {
                    'system': 'http://nphies.sa/identifier/provider',
                    'value': self.provider_license
                }
            },
            'priority': {
                'coding': [{
                    'system': 'http://terminology.hl7.org/CodeSystem/processpriority',
                    'code': claim_data.get('priority', 'normal')
                }]
            },
            'insurance': [{
                'sequence': 1,
                'focal': True,
                'coverage': {
                    'reference': f"Coverage/{coverage['id']}"
                }
            }],
            'item': items,
            'total': {
                'value': float(claim_data['total_amount']),
                'currency': 'SAR'
            }
        }
        
        # Build Bundle
        bundle = {
            'resourceType': 'Bundle',
            'type': 'collection',
            'entry': [
                {'resource': claim},
                {'resource': patient},
                {'resource': coverage}
            ]
        }
        
        return bundle
    
    def submit_claim(
        self,
        claim_bundle: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit claim to NPHIES
        
        Args:
            claim_bundle: FHIR Bundle with Claim
            correlation_id: Request correlation ID
            
        Returns:
            Claim acknowledgment or ClaimResponse
        """
        response = self._make_request(
            method='POST',
            endpoint='Claim',
            data=claim_bundle,
            correlation_id=correlation_id
        )
        
        return response
    
    def poll_response(
        self,
        request_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Poll for async claim response
        
        Args:
            request_id: NPHIES request tracking ID
            correlation_id: Original correlation ID
            
        Returns:
            ClaimResponse if available
        """
        response = self._make_request(
            method='GET',
            endpoint='ClaimResponse',
            params={'identifier': request_id},
            correlation_id=correlation_id
        )
        
        return response
