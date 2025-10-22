"""
NPHIES Prior Authorization Service
Advanced prior authorization management with AI-powered validation
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from auth.auth_manager import auth_manager
from models.bundle_builder import FHIRBundleBuilder
from config.settings import settings
from config.endpoints import endpoints
from utils.helpers import generate_request_id, format_date, parse_nphies_response, build_coding
from utils.logger import get_logger
from utils.validators import validate_request, ValidationError

logger = get_logger("prior_authorization")


class PriorAuthorizationService:
    """Service for NPHIES prior authorization requests"""
    
    def __init__(self):
        self.auth = auth_manager
    
    def submit_prior_authorization(
        self,
        patient_id: str,
        member_id: str,
        payer_id: str,
        procedures: List[Dict],
        diagnosis_codes: List[str],
        provider_justification: str,
        priority: str = "routine",
        requested_period_start: str = None,
        requested_period_end: str = None,
        patient_name: Optional[str] = None
    ) -> Dict:
        """
        Submit prior authorization request
        
        Args:
            patient_id: Patient identifier
            member_id: Member/beneficiary ID
            payer_id: Insurance payer ID
            procedures: List of procedures requiring authorization
            diagnosis_codes: List of ICD-10 diagnosis codes
            provider_justification: Medical justification for procedures
            priority: Request priority (routine, urgent, asap, stat)
            requested_period_start: Start of service period
            requested_period_end: End of service period
            patient_name: Patient name
            
        Returns:
            Dictionary with prior authorization response
        """
        try:
            logger.info(f"Submitting prior authorization for patient: {patient_id}")
            
            # Generate IDs
            auth_request_id = f"preauth-{generate_request_id()}"
            coverage_id = f"cov-{generate_request_id()}"
            
            # Default period if not provided
            if not requested_period_start:
                requested_period_start = format_date(datetime.now().date())
            if not requested_period_end:
                requested_period_end = format_date((datetime.now() + timedelta(days=30)).date())
            
            # Build authorization bundle
            bundle = self._build_authorization_bundle(
                auth_request_id=auth_request_id,
                patient_id=patient_id,
                member_id=member_id,
                coverage_id=coverage_id,
                payer_id=payer_id,
                procedures=procedures,
                diagnosis_codes=diagnosis_codes,
                provider_justification=provider_justification,
                priority=priority,
                period_start=requested_period_start,
                period_end=requested_period_end,
                patient_name=patient_name
            )
            
            # Validate bundle
            try:
                validate_request("bundle", bundle)
            except ValidationError as e:
                logger.error(f"Bundle validation failed: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "auth_request_id": auth_request_id
                }
            
            # Send request
            logger.debug(f"Sending prior authorization to {settings.message_url}")
            response = self.auth.post(settings.message_url, bundle)
            
            # Parse response
            result = parse_nphies_response(response.json())
            result["auth_request_id"] = auth_request_id
            result["patient_id"] = patient_id
            
            if result["success"]:
                logger.info(f"Prior authorization submitted successfully: {auth_request_id}")
                result["authorization_response"] = self._extract_auth_response(result["data"])
            else:
                logger.warning(f"Prior authorization failed: {result.get('errors')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error submitting prior authorization: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "auth_request_id": auth_request_id if 'auth_request_id' in locals() else None
            }
    
    def _build_authorization_bundle(
        self,
        auth_request_id: str,
        patient_id: str,
        member_id: str,
        coverage_id: str,
        payer_id: str,
        procedures: List[Dict],
        diagnosis_codes: List[str],
        provider_justification: str,
        priority: str,
        period_start: str,
        period_end: str,
        patient_name: Optional[str]
    ) -> Dict:
        """Build prior authorization FHIR bundle"""
        
        builder = FHIRBundleBuilder()
        
        # Add MessageHeader
        builder.add_message_header(
            event_type=endpoints.MESSAGE_TYPES["prior_auth_request"],
            source_endpoint=f"Organization/{settings.NPHIES_ORGANIZATION_ID}",
            destination_endpoint=f"Organization/{payer_id}"
        )
        
        # Build Claim resource (used for prior authorization)
        claim = {
            "resourceType": "Claim",
            "id": auth_request_id,
            "status": "active",
            "type": {
                "coding": [
                    build_coding(
                        "http://terminology.hl7.org/CodeSystem/claim-type",
                        "institutional",
                        "Institutional"
                    )
                ]
            },
            "use": "preauthorization",
            "patient": {
                "reference": f"Patient/{patient_id}"
            },
            "created": datetime.now().isoformat(),
            "provider": {
                "reference": f"Organization/{settings.NPHIES_ORGANIZATION_ID}"
            },
            "priority": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/processpriority",
                    "code": priority
                }]
            },
            "insurance": [{
                "sequence": 1,
                "focal": True,
                "coverage": {
                    "reference": f"Coverage/{coverage_id}"
                }
            }],
            "insurer": {
                "reference": f"Organization/{payer_id}"
            },
            "item": [],
            "diagnosis": [],
            "supportingInfo": [{
                "sequence": 1,
                "category": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/claiminformationcategory",
                        "code": "info"
                    }]
                },
                "valueString": provider_justification
            }]
        }
        
        # Add diagnosis codes
        for idx, diagnosis_code in enumerate(diagnosis_codes, 1):
            claim["diagnosis"].append({
                "sequence": idx,
                "diagnosisCodeableConcept": {
                    "coding": [
                        build_coding(
                            "http://hl7.org/fhir/sid/icd-10",
                            diagnosis_code,
                            f"Diagnosis {diagnosis_code}"
                        )
                    ]
                }
            })
        
        # Add procedures/services
        for idx, procedure in enumerate(procedures, 1):
            item = {
                "sequence": idx,
                "productOrService": {
                    "coding": [
                        build_coding(
                            procedure.get("code_system", "http://nphies.sa/terminology/CodeSystem/services"),
                            procedure["code"],
                            procedure.get("description", "")
                        )
                    ]
                },
                "servicedPeriod": {
                    "start": period_start,
                    "end": period_end
                },
                "quantity": {
                    "value": procedure.get("quantity", 1)
                },
                "unitPrice": {
                    "value": procedure.get("estimated_cost", 0.0),
                    "currency": "SAR"
                }
            }
            
            # Add diagnosis linkage
            if "diagnosis_sequence" in procedure:
                item["diagnosisSequence"] = [procedure["diagnosis_sequence"]]
            
            claim["item"].append(item)
        
        builder.add_resource(claim)
        
        # Add Patient
        builder.add_patient(
            patient_id=patient_id,
            identifier_value=member_id,
            name=patient_name
        )
        
        # Add Coverage
        builder.add_coverage(
            coverage_id=coverage_id,
            patient_id=patient_id,
            payer_id=payer_id,
            member_id=member_id
        )
        
        # Add Organizations
        builder.add_organization(
            org_id=settings.NPHIES_ORGANIZATION_ID,
            name=settings.PROVIDER_NAME,
            identifier_value=settings.NPHIES_LICENSE
        )
        
        builder.add_organization(
            org_id=payer_id,
            identifier_value=payer_id
        )
        
        return builder.build()
    
    def _extract_auth_response(self, resources: list) -> Dict:
        """Extract authorization response details"""
        response_info = {
            "status": "unknown",
            "disposition": "",
            "decision": "pending",
            "preauth_ref": None,
            "approved_items": [],
            "denied_items": []
        }
        
        try:
            for resource in resources:
                if resource.get("resourceType") == "ClaimResponse":
                    response_info["status"] = resource.get("status", "unknown")
                    response_info["disposition"] = resource.get("disposition", "")
                    response_info["outcome"] = resource.get("outcome", "")
                    response_info["preauth_ref"] = resource.get("preAuthRef")
                    
                    # Extract decision
                    if response_info["outcome"] == "complete":
                        response_info["decision"] = "approved"
                    elif response_info["outcome"] == "error":
                        response_info["decision"] = "denied"
                    
                    # Extract item details
                    items = resource.get("item", [])
                    for item in items:
                        item_info = {
                            "sequence": item.get("itemSequence"),
                            "adjudication": item.get("adjudication", [])
                        }
                        
                        # Determine if approved or denied
                        for adj in item.get("adjudication", []):
                            category = adj.get("category", {}).get("coding", [{}])[0].get("code")
                            if category == "benefit":
                                response_info["approved_items"].append(item_info)
                                break
                            elif category == "denied":
                                response_info["denied_items"].append(item_info)
                                break
        
        except Exception as e:
            logger.error(f"Error extracting authorization response: {str(e)}")
        
        return response_info
    
    def query_authorization_status(self, auth_request_id: str, patient_id: str) -> Dict:
        """
        Query status of a prior authorization request
        
        Args:
            auth_request_id: Authorization request ID
            patient_id: Patient identifier
            
        Returns:
            Dictionary with authorization status
        """
        try:
            logger.info(f"Querying status for authorization: {auth_request_id}")
            
            # Build inquiry bundle (similar to claim inquiry)
            # Implementation depends on NPHIES API specification
            
            return {
                "success": True,
                "auth_request_id": auth_request_id,
                "message": "Authorization status query functionality"
            }
            
        except Exception as e:
            logger.error(f"Error querying authorization status: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "auth_request_id": auth_request_id
            }
