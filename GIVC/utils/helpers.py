"""
Helper utility functions for NPHIES integration
"""
import uuid
import json
from typing import Dict, Any, Optional
from datetime import datetime, date
import hashlib


def generate_message_id() -> str:
    """
    Generate unique message ID for NPHIES requests
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def generate_bundle_id() -> str:
    """Generate unique bundle ID"""
    return f"bundle-{uuid.uuid4()}"


def generate_request_id() -> str:
    """Generate unique request ID"""
    return f"req-{uuid.uuid4()}"


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        ISO formatted timestamp
    """
    return datetime.now().isoformat()


def format_date(date_obj: date) -> str:
    """
    Format date for FHIR resources
    
    Args:
        date_obj: Date object
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d")


def format_datetime(dt: datetime) -> str:
    """
    Format datetime for FHIR resources
    
    Args:
        dt: Datetime object
        
    Returns:
        ISO formatted datetime string
    """
    if isinstance(dt, str):
        return dt
    return dt.isoformat()


def parse_nphies_date(date_str: str) -> Optional[date]:
    """
    Parse date string from NPHIES response
    
    Args:
        date_str: Date string
        
    Returns:
        Date object or None
    """
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
    except (ValueError, AttributeError):
        return None


def safe_get(data: Dict, *keys, default=None) -> Any:
    """
    Safely get nested dictionary value
    
    Args:
        data: Dictionary to search
        *keys: Sequence of keys to traverse
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data


def pretty_json(data: Dict, indent: int = 2) -> str:
    """
    Format dictionary as pretty JSON string
    
    Args:
        data: Dictionary to format
        indent: Indentation spaces
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def calculate_hash(data: str) -> str:
    """
    Calculate SHA256 hash of data
    
    Args:
        data: String data to hash
        
    Returns:
        Hex digest of hash
    """
    return hashlib.sha256(data.encode()).hexdigest()


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging
    
    Args:
        data: Sensitive string to mask
        visible_chars: Number of visible characters at end
        
    Returns:
        Masked string
    """
    if not data or len(data) <= visible_chars:
        return "***"
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


def validate_saudi_id(national_id: str) -> bool:
    """
    Validate Saudi National ID format
    
    Args:
        national_id: National ID to validate
        
    Returns:
        True if valid format
    """
    # Basic validation - 10 digits
    if not national_id or len(national_id) != 10:
        return False
    
    return national_id.isdigit()


def validate_iqama(iqama: str) -> bool:
    """
    Validate Iqama number format
    
    Args:
        iqama: Iqama number to validate
        
    Returns:
        True if valid format
    """
    # Basic validation - 10 digits, starts with 1 or 2
    if not iqama or len(iqama) != 10:
        return False
    
    if not iqama.isdigit():
        return False
    
    return iqama[0] in ['1', '2']


def parse_nphies_response(response_data: Dict) -> Dict[str, Any]:
    """
    Parse NPHIES FHIR response bundle
    
    Args:
        response_data: Response dictionary
        
    Returns:
        Parsed response with extracted data
    """
    result = {
        "success": False,
        "message": "",
        "data": None,
        "errors": [],
        "bundle_id": safe_get(response_data, "id"),
        "timestamp": get_current_timestamp()
    }
    
    try:
        # Check if it's a Bundle
        if response_data.get("resourceType") != "Bundle":
            result["errors"].append("Response is not a FHIR Bundle")
            return result
        
        # Extract entries
        entries = response_data.get("entry", [])
        
        if not entries:
            result["errors"].append("No entries in response bundle")
            return result
        
        # Process each entry
        resources = []
        for entry in entries:
            resource = entry.get("resource", {})
            resources.append(resource)
            
            # Check for OperationOutcome (errors)
            if resource.get("resourceType") == "OperationOutcome":
                issues = resource.get("issue", [])
                for issue in issues:
                    severity = issue.get("severity", "error")
                    details = issue.get("details", {}).get("text", "Unknown error")
                    result["errors"].append(f"[{severity}] {details}")
        
        result["data"] = resources
        result["success"] = len(result["errors"]) == 0
        result["message"] = "Success" if result["success"] else "Response contains errors"
        
    except Exception as e:
        result["errors"].append(f"Error parsing response: {str(e)}")
    
    return result


def build_identifier(system: str, value: str) -> Dict:
    """
    Build FHIR identifier object
    
    Args:
        system: Identifier system URL
        value: Identifier value
        
    Returns:
        FHIR identifier dictionary
    """
    return {
        "system": system,
        "value": value
    }


def build_reference(resource_type: str, resource_id: str) -> Dict:
    """
    Build FHIR reference object
    
    Args:
        resource_type: Type of resource (Patient, Organization, etc.)
        resource_id: Resource ID
        
    Returns:
        FHIR reference dictionary
    """
    return {
        "reference": f"{resource_type}/{resource_id}"
    }


def build_coding(system: str, code: str, display: str = None) -> Dict:
    """
    Build FHIR coding object
    
    Args:
        system: Code system URL
        code: Code value
        display: Display text
        
    Returns:
        FHIR coding dictionary
    """
    coding = {
        "system": system,
        "code": code
    }
    
    if display:
        coding["display"] = display
    
    return coding
