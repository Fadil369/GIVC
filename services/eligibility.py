"""
NPHIES Eligibility Service
Handles eligibility verification requests
"""
from typing import Dict, Optional
from datetime import datetime

from auth.auth_manager import auth_manager
from models.bundle_builder import FHIRBundleBuilder
from config.settings import settings
from config.endpoints import endpoints
from utils.helpers import generate_request_id, format_date, parse_nphies_response
from utils.logger import get_logger
from utils.validators import validate_request, ValidationError

logger = get_logger("eligibility")


class EligibilityService:
    """Service for NPHIES eligibility verification"""
    
    def __init__(self):
        self.auth = auth_manager
    
    def check_eligibility(
        self,
        member_id: str,
        payer_id: str,
        patient_id: str = None,
        service_date: str = None,
        patient_name: str = None,
        patient_gender: str = None,
        patient_dob: str = None
    ) -> Dict:
        """
        Check eligibility for a member
        
        Args:
            member_id: Member/beneficiary identifier
            payer_id: Insurance payer ID
            patient_id: Optional patient ID
            service_date: Service date (defaults to today)
            patient_name: Patient name
            patient_gender: Patient gender
            patient_dob: Patient date of birth
            
        Returns:
            Dictionary with eligibility response
        """
        try:
            logger.info(f"Checking eligibility for member: {member_id}")
            
            # Generate IDs
            request_id = patient_id or generate_request_id()
            coverage_id = f"cov-{generate_request_id()}"
            eligibility_request_id = f"eligreq-{generate_request_id()}"
            
            # Default service date to today
            if not service_date:
                service_date = format_date(datetime.now().date())
            
            # Build the eligibility request bundle
            bundle = self._build_eligibility_bundle(
                eligibility_request_id=eligibility_request_id,
                patient_id=request_id,
                coverage_id=coverage_id,
                member_id=member_id,
                payer_id=payer_id,
                service_date=service_date,
                patient_name=patient_name,
                patient_gender=patient_gender,
                patient_dob=patient_dob
            )
            
            # Validate bundle
            try:
                validate_request("bundle", bundle)
            except ValidationError as e:
                logger.error(f"Bundle validation failed: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "request_id": eligibility_request_id
                }
            
            # Send request
            logger.debug(f"Sending eligibility request to {settings.message_url}")
            response = self.auth.post(settings.message_url, bundle)
            
            # Parse response
            result = parse_nphies_response(response.json())
            result["request_id"] = eligibility_request_id
            result["member_id"] = member_id
            
            if result["success"]:
                logger.info(f"Eligibility check successful for member: {member_id}")
                # Extract coverage details from response
                result["coverage_status"] = self._extract_coverage_status(result["data"])
            else:
                logger.warning(f"Eligibility check failed: {result.get('errors')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking eligibility: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "request_id": eligibility_request_id if 'eligibility_request_id' in locals() else None
            }
    
    def _build_eligibility_bundle(
        self,
        eligibility_request_id: str,
        patient_id: str,
        coverage_id: str,
        member_id: str,
        payer_id: str,
        service_date: str,
        patient_name: str = None,
        patient_gender: str = None,
        patient_dob: str = None
    ) -> Dict:
        """Build eligibility request FHIR bundle"""
        
        # Initialize bundle builder
        builder = FHIRBundleBuilder()
        
        # Add MessageHeader
        builder.add_message_header(
            event_type=endpoints.MESSAGE_TYPES["eligibility_request"],
            source_endpoint=f"Organization/{settings.NPHIES_ORGANIZATION_ID}",
            destination_endpoint=f"Organization/{payer_id}"
        )
        
        # Add CoverageEligibilityRequest
        eligibility_request = {
            "resourceType": "CoverageEligibilityRequest",
            "id": eligibility_request_id,
            "status": "active",
            "purpose": ["validation"],
            "priority": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/processpriority",
                    "code": "normal"
                }]
            },
            "patient": {
                "reference": f"Patient/{patient_id}"
            },
            "servicedDate": service_date,
            "created": datetime.now().isoformat(),
            "provider": {
                "reference": f"Organization/{settings.NPHIES_ORGANIZATION_ID}"
            },
            "insurer": {
                "reference": f"Organization/{payer_id}"
            },
            "insurance": [{
                "coverage": {
                    "reference": f"Coverage/{coverage_id}"
                }
            }]
        }
        
        builder.add_resource(eligibility_request)
        
        # Add Patient
        builder.add_patient(
            patient_id=patient_id,
            identifier_value=member_id,
            identifier_system="http://nphies.sa/identifier/patient-id",
            name=patient_name,
            gender=patient_gender,
            birth_date=patient_dob
        )
        
        # Add Coverage
        builder.add_coverage(
            coverage_id=coverage_id,
            patient_id=patient_id,
            payer_id=payer_id,
            member_id=member_id
        )
        
        # Add Provider Organization
        builder.add_organization(
            org_id=settings.NPHIES_ORGANIZATION_ID,
            name=settings.PROVIDER_NAME,
            identifier_value=settings.NPHIES_LICENSE
        )
        
        # Add Payer Organization
        builder.add_organization(
            org_id=payer_id,
            identifier_value=payer_id
        )
        
        return builder.build()
    
    def _extract_coverage_status(self, resources: list) -> Dict:
        """Extract coverage status from response resources"""
        coverage_info = {
            "eligible": False,
            "coverage_details": []
        }
        
        try:
            for resource in resources:
                if resource.get("resourceType") == "CoverageEligibilityResponse":
                    # Check disposition
                    disposition = resource.get("disposition", "")
                    coverage_info["disposition"] = disposition
                    
                    # Check outcome
                    outcome = resource.get("outcome", "")
                    coverage_info["outcome"] = outcome
                    coverage_info["eligible"] = outcome in ["complete", "queued"]
                    
                    # Extract insurance details
                    insurance = resource.get("insurance", [])
                    for ins in insurance:
                        coverage = ins.get("coverage", {})
                        items = ins.get("item", [])
                        
                        coverage_info["coverage_details"].append({
                            "coverage_reference": coverage.get("reference"),
                            "benefits": [
                                {
                                    "category": item.get("category", {}).get("text"),
                                    "benefit": item.get("benefit", [])
                                }
                                for item in items
                            ]
                        })
        
        except Exception as e:
            logger.error(f"Error extracting coverage status: {str(e)}")
        
        return coverage_info
    
    def batch_check_eligibility(self, members: list) -> list:
        """
        Check eligibility for multiple members
        
        Args:
            members: List of member dictionaries with required fields
            
        Returns:
            List of eligibility results
        """
        logger.info(f"Batch eligibility check for {len(members)} members")
        results = []
        
        for idx, member in enumerate(members, 1):
            logger.info(f"Processing member {idx}/{len(members)}")
            result = self.check_eligibility(**member)
            results.append(result)
        
        return results
