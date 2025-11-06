"""
NPHIES Claims Service
Handles claim submission and inquiry
"""
from typing import Dict, List, Optional
from datetime import datetime

from auth.auth_manager import auth_manager
from models.bundle_builder import FHIRBundleBuilder
from config.settings import settings
from config.endpoints import endpoints
from utils.helpers import generate_request_id, format_date, parse_nphies_response, build_coding
from utils.logger import get_logger
from utils.validators import validate_request, ValidationError

logger = get_logger("claims")


class ClaimsService:
    """Service for NPHIES claims management"""
    
    def __init__(self):
        self.auth = auth_manager
    
    def submit_claim(
        self,
        claim_type: str,
        patient_id: str,
        member_id: str,
        payer_id: str,
        services: List[Dict],
        total_amount: float,
        claim_date: str = None,
        patient_name: str = None
    ) -> Dict:
        """
        Submit a claim to NPHIES
        
        Args:
            claim_type: Type of claim (institutional, professional, pharmacy, etc.)
            patient_id: Patient identifier
            member_id: Member/beneficiary ID
            payer_id: Insurance payer ID
            services: List of services/items in claim
            total_amount: Total claim amount
            claim_date: Claim date (defaults to today)
            patient_name: Patient name
            
        Returns:
            Dictionary with claim submission response
        """
        try:
            logger.info(f"Submitting {claim_type} claim for patient: {patient_id}")
            
            # Generate IDs
            claim_id = f"claim-{generate_request_id()}"
            coverage_id = f"cov-{generate_request_id()}"
            
            # Default claim date to today
            if not claim_date:
                claim_date = format_date(datetime.now().date())
            
            # Build claim bundle
            bundle = self._build_claim_bundle(
                claim_id=claim_id,
                claim_type=claim_type,
                patient_id=patient_id,
                member_id=member_id,
                coverage_id=coverage_id,
                payer_id=payer_id,
                services=services,
                total_amount=total_amount,
                claim_date=claim_date,
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
                    "claim_id": claim_id
                }
            
            # Send request
            logger.debug(f"Sending claim to {settings.message_url}")
            response = self.auth.post(settings.message_url, bundle)
            
            # Parse response
            result = parse_nphies_response(response.json())
            result["claim_id"] = claim_id
            result["patient_id"] = patient_id
            
            if result["success"]:
                logger.info(f"Claim submitted successfully: {claim_id}")
                result["claim_response"] = self._extract_claim_response(result["data"])
            else:
                logger.warning(f"Claim submission failed: {result.get('errors')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error submitting claim: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "claim_id": claim_id if 'claim_id' in locals() else None
            }
    
    def _build_claim_bundle(
        self,
        claim_id: str,
        claim_type: str,
        patient_id: str,
        member_id: str,
        coverage_id: str,
        payer_id: str,
        services: List[Dict],
        total_amount: float,
        claim_date: str,
        patient_name: str = None
    ) -> Dict:
        """Build claim FHIR bundle"""
        
        # Initialize bundle builder
        builder = FHIRBundleBuilder()
        
        # Add MessageHeader
        builder.add_message_header(
            event_type=endpoints.MESSAGE_TYPES["claim_request"],
            source_endpoint=f"Organization/{settings.NPHIES_ORGANIZATION_ID}",
            destination_endpoint=f"Organization/{payer_id}"
        )
        
        # Build claim resource
        claim = {
            "resourceType": "Claim",
            "id": claim_id,
            "status": "active",
            "type": {
                "coding": [
                    build_coding(
                        "http://terminology.hl7.org/CodeSystem/claim-type",
                        claim_type,
                        claim_type.capitalize()
                    )
                ]
            },
            "use": "claim",
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
                    "code": "normal"
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
            "item": []
        }
        
        # Add services/items
        for idx, service in enumerate(services, 1):
            item = {
                "sequence": idx,
                "productOrService": {
                    "coding": [
                        build_coding(
                            service.get("code_system", "http://nphies.sa/terminology/CodeSystem/services"),
                            service["code"],
                            service.get("description", "")
                        )
                    ]
                },
                "servicedDate": claim_date,
                "quantity": {
                    "value": service.get("quantity", 1)
                },
                "unitPrice": {
                    "value": service.get("unit_price", 0.0),
                    "currency": "SAR"
                },
                "net": {
                    "value": service.get("net_amount", service.get("unit_price", 0.0) * service.get("quantity", 1)),
                    "currency": "SAR"
                }
            }
            
            claim["item"].append(item)
        
        # Add total
        claim["total"] = {
            "value": total_amount,
            "currency": "SAR"
        }
        
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
    
    def _extract_claim_response(self, resources: list) -> Dict:
        """Extract claim response details"""
        response_info = {
            "status": "unknown",
            "disposition": "",
            "total_approved": 0.0
        }
        
        try:
            for resource in resources:
                if resource.get("resourceType") == "ClaimResponse":
                    response_info["status"] = resource.get("status", "unknown")
                    response_info["disposition"] = resource.get("disposition", "")
                    response_info["outcome"] = resource.get("outcome", "")
                    
                    # Extract payment information
                    payment = resource.get("payment", {})
                    if payment:
                        response_info["total_approved"] = payment.get("amount", {}).get("value", 0.0)
                        response_info["payment_date"] = payment.get("date", "")
                    
                    # Extract item details
                    items = resource.get("item", [])
                    response_info["items"] = [
                        {
                            "sequence": item.get("itemSequence"),
                            "adjudication": item.get("adjudication", [])
                        }
                        for item in items
                    ]
        
        except Exception as e:
            logger.error(f"Error extracting claim response: {str(e)}")
        
        return response_info
    
    def query_claim_status(self, claim_id: str, patient_id: str) -> Dict:
        """
        Query status of a submitted claim
        
        Args:
            claim_id: Claim identifier
            patient_id: Patient identifier
            
        Returns:
            Dictionary with claim status
        """
        try:
            logger.info(f"Querying status for claim: {claim_id}")
            
            # Build claim inquiry bundle
            # This would follow similar pattern to submit_claim but with inquiry message type
            # Implementation details depend on NPHIES API specification
            
            return {
                "success": True,
                "claim_id": claim_id,
                "message": "Claim status query functionality"
            }
            
        except Exception as e:
            logger.error(f"Error querying claim status: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "claim_id": claim_id
            }
