"""
Data validators for NPHIES requests
"""
from typing import Dict, List, Tuple, Any
from datetime import datetime, date
import re


class ValidationError(Exception):
    """Custom validation error"""
    pass


class NPHIESValidator:
    """Validator for NPHIES request data"""
    
    @staticmethod
    def validate_member_id(member_id: str) -> Tuple[bool, str]:
        """
        Validate member/beneficiary ID
        
        Args:
            member_id: Member ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not member_id:
            return False, "Member ID is required"
        
        if not isinstance(member_id, str):
            return False, "Member ID must be a string"
        
        # Remove any spaces
        member_id = member_id.strip()
        
        if len(member_id) < 5:
            return False, "Member ID too short"
        
        if len(member_id) > 50:
            return False, "Member ID too long (max 50 characters)"
        
        return True, ""
    
    @staticmethod
    def validate_payer_id(payer_id: str) -> Tuple[bool, str]:
        """
        Validate payer/insurance license number
        
        Args:
            payer_id: Payer ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not payer_id:
            return False, "Payer ID is required"
        
        if not isinstance(payer_id, str):
            return False, "Payer ID must be a string"
        
        # Saudi license numbers are typically 10 digits
        if not payer_id.isdigit():
            return False, "Payer ID must contain only digits"
        
        if len(payer_id) != 10:
            return False, "Payer ID must be 10 digits"
        
        return True, ""
    
    @staticmethod
    def validate_date(date_value: Any) -> Tuple[bool, str]:
        """
        Validate date value
        
        Args:
            date_value: Date to validate (string or date object)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not date_value:
            return False, "Date is required"
        
        try:
            if isinstance(date_value, str):
                # Try to parse ISO format date
                datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            elif not isinstance(date_value, (date, datetime)):
                return False, "Date must be string or date object"
            
            return True, ""
            
        except ValueError:
            return False, "Invalid date format (use YYYY-MM-DD)"
    
    @staticmethod
    def validate_patient_data(patient: Dict) -> List[str]:
        """
        Validate patient data
        
        Args:
            patient: Patient data dictionary
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Required fields
        if not patient.get("id"):
            errors.append("Patient ID is required")
        
        if not patient.get("identifier"):
            errors.append("Patient identifier is required")
        
        # Validate identifiers
        identifiers = patient.get("identifier", [])
        if not isinstance(identifiers, list) or len(identifiers) == 0:
            errors.append("At least one patient identifier required")
        
        # Name validation
        if not patient.get("name"):
            errors.append("Patient name is required")
        
        # Birth date validation
        if patient.get("birthDate"):
            valid, msg = NPHIESValidator.validate_date(patient["birthDate"])
            if not valid:
                errors.append(f"Invalid birth date: {msg}")
        
        # Gender validation
        if patient.get("gender") and patient["gender"] not in ["male", "female", "other", "unknown"]:
            errors.append("Invalid gender value")
        
        return errors
    
    @staticmethod
    def validate_coverage_data(coverage: Dict) -> List[str]:
        """
        Validate coverage data
        
        Args:
            coverage: Coverage data dictionary
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if not coverage.get("id"):
            errors.append("Coverage ID is required")
        
        if not coverage.get("beneficiary"):
            errors.append("Coverage beneficiary is required")
        
        if not coverage.get("payor"):
            errors.append("Coverage payor is required")
        
        if not coverage.get("class"):
            errors.append("Coverage class information is required")
        
        return errors
    
    @staticmethod
    def validate_claim_data(claim: Dict) -> List[str]:
        """
        Validate claim data
        
        Args:
            claim: Claim data dictionary
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if not claim.get("id"):
            errors.append("Claim ID is required")
        
        if not claim.get("type"):
            errors.append("Claim type is required")
        
        if not claim.get("patient"):
            errors.append("Claim patient reference is required")
        
        if not claim.get("provider"):
            errors.append("Claim provider reference is required")
        
        if not claim.get("insurer"):
            errors.append("Claim insurer reference is required")
        
        # Validate items
        items = claim.get("item", [])
        if not items:
            errors.append("Claim must have at least one item")
        
        for idx, item in enumerate(items):
            if not item.get("sequence"):
                errors.append(f"Item {idx + 1} missing sequence number")
            
            if not item.get("productOrService"):
                errors.append(f"Item {idx + 1} missing product/service code")
        
        return errors
    
    @staticmethod
    def validate_bundle(bundle: Dict) -> List[str]:
        """
        Validate FHIR bundle structure
        
        Args:
            bundle: Bundle data dictionary
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if bundle.get("resourceType") != "Bundle":
            errors.append("Resource type must be 'Bundle'")
        
        if not bundle.get("type"):
            errors.append("Bundle type is required")
        
        if bundle.get("type") not in ["message", "document", "transaction", "batch"]:
            errors.append("Invalid bundle type")
        
        entries = bundle.get("entry", [])
        if not entries:
            errors.append("Bundle must contain at least one entry")
        
        # First entry should be MessageHeader for message bundles
        if bundle.get("type") == "message":
            if entries and entries[0].get("resource", {}).get("resourceType") != "MessageHeader":
                errors.append("First entry in message bundle must be MessageHeader")
        
        return errors


def validate_request(request_type: str, data: Dict) -> None:
    """
    Validate request data and raise ValidationError if invalid
    
    Args:
        request_type: Type of request (eligibility, claim, etc.)
        data: Request data to validate
        
    Raises:
        ValidationError: If validation fails
    """
    validator = NPHIESValidator()
    errors = []
    
    if request_type == "eligibility":
        # Validate eligibility request
        if "patient" in data:
            errors.extend(validator.validate_patient_data(data["patient"]))
        
        if "coverage" in data:
            errors.extend(validator.validate_coverage_data(data["coverage"]))
    
    elif request_type == "claim":
        errors.extend(validator.validate_claim_data(data))
    
    elif request_type == "bundle":
        errors.extend(validator.validate_bundle(data))
    
    if errors:
        raise ValidationError("; ".join(errors))
