"""
NPHIES API Endpoints Configuration
"""

class NPHIESEndpoints:
    """NPHIES API Endpoint definitions"""
    
    # Main Message Processing Endpoint
    PROCESS_MESSAGE = "$process-message"
    
    # Operation Types (used in FHIR Bundle)
    OPERATIONS = {
        "eligibility": "eligibility-request",
        "prior_auth": "priorauth-request",
        "claim": "claim-request",
        "claim_status": "claim-inquiry",
        "auth_status": "priorauth-inquiry",
        "communication": "communication-request",
        "poll": "poll-request"
    }
    
    # Message Types
    MESSAGE_TYPES = {
        "eligibility_request": "http://nphies.sa/eligibility-request",
        "eligibility_response": "http://nphies.sa/eligibility-response",
        "prior_auth_request": "http://nphies.sa/prior-auth-request",
        "prior_auth_response": "http://nphies.sa/prior-auth-response",
        "claim_request": "http://nphies.sa/claim-request",
        "claim_response": "http://nphies.sa/claim-response",
        "communication_request": "http://nphies.sa/communication-request",
        "poll_request": "http://nphies.sa/poll-request",
        "poll_response": "http://nphies.sa/poll-response"
    }
    
    # FHIR Resource Types
    RESOURCES = {
        "bundle": "Bundle",
        "message_header": "MessageHeader",
        "coverage_eligibility_request": "CoverageEligibilityRequest",
        "coverage_eligibility_response": "CoverageEligibilityResponse",
        "claim": "Claim",
        "claim_response": "ClaimResponse",
        "prior_authorization": "Claim",  # Prior auth uses Claim resource
        "communication": "Communication",
        "patient": "Patient",
        "organization": "Organization",
        "practitioner": "Practitioner",
        "coverage": "Coverage"
    }
    
    # Request Priorities
    PRIORITIES = {
        "routine": "routine",
        "urgent": "urgent",
        "asap": "asap",
        "stat": "stat"
    }
    
    # Claim Types
    CLAIM_TYPES = {
        "institutional": "institutional",
        "oral": "oral",
        "pharmacy": "pharmacy",
        "professional": "professional",
        "vision": "vision"
    }
    
    # Use Types
    USE_TYPES = {
        "claim": "claim",
        "preauthorization": "preauthorization",
        "predetermination": "predetermination"
    }
    
    @staticmethod
    def get_message_type(operation: str, is_request: bool = True) -> str:
        """
        Get message type URL for operation
        
        Args:
            operation: Operation name (eligibility, prior_auth, claim, etc.)
            is_request: True for request, False for response
            
        Returns:
            Message type URL
        """
        suffix = "_request" if is_request else "_response"
        key = f"{operation}{suffix}"
        return NPHIESEndpoints.MESSAGE_TYPES.get(key, "")
    
    @staticmethod
    def get_operation_code(operation: str) -> str:
        """Get operation code for the given operation type"""
        return NPHIESEndpoints.OPERATIONS.get(operation, "")


# Global endpoints instance
endpoints = NPHIESEndpoints()
