"""
Security Module for Teams Integration

Provides HMAC signature verification and generation for securing webhook
communications between ClaimLinc-GIVC and Microsoft Teams.
"""

import hmac
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def generate_hmac_signature(payload: str, secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for a payload.
    
    Args:
        payload: String payload to sign (typically JSON)
        secret: Secret key for signing
        
    Returns:
        Hex-encoded HMAC signature
        
    Example:
        signature = generate_hmac_signature(json.dumps(card), "my-secret-key")
    """
    if not secret:
        raise ValueError("Secret key cannot be empty")
    
    signature = hmac.new(
        key=secret.encode('utf-8'),
        msg=payload.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return signature


def verify_hmac_signature(
    payload: str,
    signature: str,
    secret: str
) -> bool:
    """
    Verify HMAC-SHA256 signature for incoming webhook.
    
    Args:
        payload: String payload to verify (typically JSON)
        signature: Hex-encoded HMAC signature from request header
        secret: Secret key for verification
        
    Returns:
        True if signature is valid, False otherwise
        
    Example:
        if verify_hmac_signature(request.body, request.headers['X-HMAC-Signature'], secret):
            # Process webhook
            pass
    """
    if not secret:
        logger.warning("Secret key is empty, cannot verify signature")
        return False
    
    if not signature:
        logger.warning("Signature is empty")
        return False
    
    try:
        expected_signature = generate_hmac_signature(payload, secret)
        
        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if not is_valid:
            logger.warning(
                "HMAC signature verification failed",
                extra={
                    "provided_signature": signature[:16] + "...",
                    "expected_signature": expected_signature[:16] + "..."
                }
            )
        
        return is_valid
        
    except Exception as exc:
        logger.error(f"Error verifying HMAC signature: {exc}")
        return False


def validate_webhook_request(
    payload: str,
    signature: Optional[str],
    secret: Optional[str],
    require_signature: bool = True
) -> bool:
    """
    Validate incoming webhook request with HMAC signature.
    
    Args:
        payload: Request payload string
        signature: HMAC signature from X-HMAC-Signature header
        secret: Secret key for verification
        require_signature: If True, reject requests without signature
        
    Returns:
        True if request is valid, False otherwise
    """
    # If signatures not required, allow all requests (dev/testing only)
    if not require_signature:
        logger.debug("Signature verification disabled")
        return True
    
    # Check if secret is configured
    if not secret:
        logger.error("HMAC secret not configured")
        return False
    
    # Check if signature is present
    if not signature:
        logger.warning("Request missing HMAC signature")
        return False
    
    # Verify signature
    return verify_hmac_signature(payload, signature, secret)


class WebhookSecurityMiddleware:
    """
    Middleware for validating webhook requests with HMAC signatures.
    
    Can be used with FastAPI, Flask, or other web frameworks.
    """
    
    def __init__(self, secret: str, require_signature: bool = True):
        """
        Initialize middleware.
        
        Args:
            secret: HMAC secret key
            require_signature: If True, reject requests without valid signature
        """
        self.secret = secret
        self.require_signature = require_signature
    
    async def __call__(self, request, call_next):
        """
        Process request with HMAC validation.
        
        Args:
            request: HTTP request object
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Get signature from header
        signature = request.headers.get("X-HMAC-Signature")
        
        # Read request body
        body = await request.body()
        payload = body.decode('utf-8')
        
        # Validate signature
        is_valid = validate_webhook_request(
            payload=payload,
            signature=signature,
            secret=self.secret,
            require_signature=self.require_signature
        )
        
        if not is_valid:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or missing HMAC signature"}
            )
        
        # Continue to next handler
        response = await call_next(request)
        return response
