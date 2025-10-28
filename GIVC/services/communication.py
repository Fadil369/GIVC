"""
NPHIES Communication Service
Handles communication polling and management
"""
from typing import Dict, List, Optional
from datetime import datetime

from auth.auth_manager import auth_manager
from models.bundle_builder import FHIRBundleBuilder
from config.settings import settings
from config.endpoints import endpoints
from utils.helpers import generate_request_id, get_current_timestamp, parse_nphies_response
from utils.logger import get_logger

logger = get_logger("communication")


class CommunicationService:
    """Service for NPHIES communication management"""
    
    def __init__(self):
        self.auth = auth_manager
    
    def poll_communications(self, organization_id: str = None) -> Dict:
        """
        Poll for pending communications from NPHIES
        
        Args:
            organization_id: Organization ID (defaults to configured org)
            
        Returns:
            Dictionary with communication poll response
        """
        try:
            if not organization_id:
                organization_id = settings.NPHIES_ORGANIZATION_ID
            
            logger.info(f"Polling communications for organization: {organization_id}")
            
            # Build poll request bundle
            bundle = self._build_poll_bundle(organization_id)
            
            # Send request
            logger.debug(f"Sending poll request to {settings.message_url}")
            response = self.auth.post(settings.message_url, bundle)
            
            # Parse response
            result = parse_nphies_response(response.json())
            
            if result["success"]:
                logger.info(f"Poll successful, received {len(result.get('data', []))} communications")
                result["communications"] = self._extract_communications(result["data"])
            else:
                logger.warning(f"Poll failed: {result.get('errors')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error polling communications: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_poll_bundle(self, organization_id: str) -> Dict:
        """Build communication poll request bundle"""
        
        builder = FHIRBundleBuilder()
        
        # Add MessageHeader
        builder.add_message_header(
            event_type=endpoints.MESSAGE_TYPES["poll_request"],
            source_endpoint=f"Organization/{organization_id}"
        )
        
        # Add Poll Request (Communication resource)
        poll_request_id = f"poll-{generate_request_id()}"
        
        poll_request = {
            "resourceType": "Communication",
            "id": poll_request_id,
            "status": "completed",
            "category": [{
                "coding": [{
                    "system": "http://nphies.sa/terminology/CodeSystem/communication-category",
                    "code": "poll"
                }]
            }],
            "sender": {
                "reference": f"Organization/{organization_id}"
            },
            "sent": get_current_timestamp()
        }
        
        builder.add_resource(poll_request)
        
        # Add Organization
        builder.add_organization(
            org_id=organization_id,
            name=settings.PROVIDER_NAME,
            identifier_value=settings.NPHIES_LICENSE
        )
        
        return builder.build()
    
    def _extract_communications(self, resources: list) -> List[Dict]:
        """Extract communication details from response"""
        communications = []
        
        try:
            for resource in resources:
                if resource.get("resourceType") == "Communication":
                    comm = {
                        "id": resource.get("id"),
                        "status": resource.get("status"),
                        "category": resource.get("category", [{}])[0].get("coding", [{}])[0].get("code"),
                        "subject": resource.get("subject", {}).get("reference"),
                        "sent": resource.get("sent"),
                        "received": resource.get("received"),
                        "sender": resource.get("sender", {}).get("reference"),
                        "recipient": [r.get("reference") for r in resource.get("recipient", [])],
                        "payload": []
                    }
                    
                    # Extract payload content
                    payloads = resource.get("payload", [])
                    for payload in payloads:
                        content = payload.get("contentString") or payload.get("contentReference", {}).get("reference")
                        comm["payload"].append(content)
                    
                    communications.append(comm)
        
        except Exception as e:
            logger.error(f"Error extracting communications: {str(e)}")
        
        return communications
    
    def send_communication(
        self,
        recipient_id: str,
        subject: str,
        content: str,
        category: str = "info"
    ) -> Dict:
        """
        Send a communication to NPHIES
        
        Args:
            recipient_id: Recipient organization ID
            subject: Communication subject/reference
            content: Communication content
            category: Communication category
            
        Returns:
            Dictionary with send result
        """
        try:
            logger.info(f"Sending communication to: {recipient_id}")
            
            # Build communication bundle
            bundle = self._build_communication_bundle(
                recipient_id, subject, content, category
            )
            
            # Send request
            response = self.auth.post(settings.message_url, bundle)
            
            # Parse response
            result = parse_nphies_response(response.json())
            
            if result["success"]:
                logger.info("Communication sent successfully")
            else:
                logger.warning(f"Communication send failed: {result.get('errors')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending communication: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_communication_bundle(
        self,
        recipient_id: str,
        subject: str,
        content: str,
        category: str
    ) -> Dict:
        """Build communication send request bundle"""
        
        builder = FHIRBundleBuilder()
        
        # Add MessageHeader
        builder.add_message_header(
            event_type=endpoints.MESSAGE_TYPES["communication_request"],
            source_endpoint=f"Organization/{settings.NPHIES_ORGANIZATION_ID}",
            destination_endpoint=f"Organization/{recipient_id}"
        )
        
        # Add Communication
        comm_id = f"comm-{generate_request_id()}"
        
        communication = {
            "resourceType": "Communication",
            "id": comm_id,
            "status": "completed",
            "category": [{
                "coding": [{
                    "system": "http://nphies.sa/terminology/CodeSystem/communication-category",
                    "code": category
                }]
            }],
            "subject": {
                "display": subject
            },
            "sender": {
                "reference": f"Organization/{settings.NPHIES_ORGANIZATION_ID}"
            },
            "recipient": [{
                "reference": f"Organization/{recipient_id}"
            }],
            "payload": [{
                "contentString": content
            }],
            "sent": get_current_timestamp()
        }
        
        builder.add_resource(communication)
        
        # Add Organizations
        builder.add_organization(
            org_id=settings.NPHIES_ORGANIZATION_ID,
            name=settings.PROVIDER_NAME,
            identifier_value=settings.NPHIES_LICENSE
        )
        
        builder.add_organization(
            org_id=recipient_id,
            identifier_value=recipient_id
        )
        
        return builder.build()
