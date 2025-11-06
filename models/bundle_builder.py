"""
FHIR Bundle Builder for NPHIES Requests
"""
from typing import Dict, List, Optional
from datetime import datetime

from utils.helpers import (
    generate_bundle_id, generate_message_id, 
    get_current_timestamp, build_reference, build_identifier
)
from config.endpoints import endpoints
from config.settings import settings


class FHIRBundleBuilder:
    """Build FHIR Bundle messages for NPHIES"""
    
    def __init__(self):
        self.bundle = {
            "resourceType": "Bundle",
            "id": generate_bundle_id(),
            "type": "message",
            "timestamp": get_current_timestamp(),
            "entry": []
        }
    
    def add_message_header(
        self, 
        event_type: str, 
        source_endpoint: str,
        destination_endpoint: str = None
    ) -> "FHIRBundleBuilder":
        """
        Add MessageHeader to bundle
        
        Args:
            event_type: Message event type URL
            source_endpoint: Source endpoint URL
            destination_endpoint: Destination endpoint URL
        """
        message_header = {
            "fullUrl": f"urn:uuid:{generate_message_id()}",
            "resource": {
                "resourceType": "MessageHeader",
                "id": generate_message_id(),
                "eventUri": event_type,
                "source": {
                    "endpoint": source_endpoint
                },
                "sender": {
                    "reference": f"Organization/{settings.NPHIES_ORGANIZATION_ID}"
                },
                "timestamp": get_current_timestamp()
            }
        }
        
        if destination_endpoint:
            message_header["resource"]["destination"] = [{
                "endpoint": destination_endpoint,
                "receiver": {
                    "reference": f"Organization/{settings.NPHIES_PAYER_ID}"
                }
            }]
        
        self.bundle["entry"].append(message_header)
        return self
    
    def add_resource(self, resource: Dict, full_url: str = None) -> "FHIRBundleBuilder":
        """
        Add resource to bundle
        
        Args:
            resource: FHIR resource dictionary
            full_url: Full URL for the resource (optional)
        """
        entry = {
            "resource": resource
        }
        
        if full_url:
            entry["fullUrl"] = full_url
        elif resource.get("id"):
            resource_type = resource.get("resourceType", "Resource")
            entry["fullUrl"] = f"urn:uuid:{resource['id']}"
        
        self.bundle["entry"].append(entry)
        return self
    
    def add_patient(
        self, 
        patient_id: str,
        identifier_value: str,
        identifier_system: str = "http://nphies.sa/identifier/patient",
        name: str = None,
        gender: str = None,
        birth_date: str = None
    ) -> "FHIRBundleBuilder":
        """
        Add Patient resource to bundle
        
        Args:
            patient_id: Patient ID
            identifier_value: Patient identifier (National ID/Iqama)
            identifier_system: Identifier system URL
            name: Patient name
            gender: Patient gender
            birth_date: Patient birth date
        """
        patient = {
            "resourceType": "Patient",
            "id": patient_id,
            "identifier": [
                build_identifier(identifier_system, identifier_value)
            ]
        }
        
        if name:
            patient["name"] = [{
                "text": name,
                "use": "official"
            }]
        
        if gender:
            patient["gender"] = gender
        
        if birth_date:
            patient["birthDate"] = birth_date
        
        self.add_resource(patient)
        return self
    
    def add_coverage(
        self,
        coverage_id: str,
        patient_id: str,
        payer_id: str,
        member_id: str,
        group_id: str = None
    ) -> "FHIRBundleBuilder":
        """
        Add Coverage resource to bundle
        
        Args:
            coverage_id: Coverage ID
            patient_id: Patient ID reference
            payer_id: Payer organization ID
            member_id: Member identifier
            group_id: Group/policy identifier
        """
        coverage = {
            "resourceType": "Coverage",
            "id": coverage_id,
            "status": "active",
            "beneficiary": build_reference("Patient", patient_id),
            "payor": [build_reference("Organization", payer_id)],
            "class": [
                {
                    "type": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                            "code": "group"
                        }]
                    },
                    "value": group_id or settings.INSURANCE_GROUP_CODE
                }
            ]
        }
        
        # Add subscriber ID
        coverage["subscriberId"] = member_id
        
        self.add_resource(coverage)
        return self
    
    def add_organization(
        self,
        org_id: str,
        name: str = None,
        identifier_value: str = None,
        identifier_system: str = "http://nphies.sa/identifier/organization"
    ) -> "FHIRBundleBuilder":
        """
        Add Organization resource to bundle
        
        Args:
            org_id: Organization ID
            name: Organization name
            identifier_value: Organization identifier
            identifier_system: Identifier system URL
        """
        organization = {
            "resourceType": "Organization",
            "id": org_id,
            "active": True
        }
        
        if name:
            organization["name"] = name
        
        if identifier_value:
            organization["identifier"] = [
                build_identifier(identifier_system, identifier_value)
            ]
        
        self.add_resource(organization)
        return self
    
    def build(self) -> Dict:
        """
        Build and return the complete bundle
        
        Returns:
            Complete FHIR Bundle dictionary
        """
        return self.bundle
