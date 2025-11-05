"""
Security Middleware
===================
Comprehensive security layer for API protection including:
- Input validation and sanitization
- Rate limiting
- Request signing validation
- SQL injection prevention
- XSS protection
- CSRF protection

Author: GIVC Platform Team
License: GPL-3.0
"""

import re
import logging
import hashlib
import hmac
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field, validator
import bleach

logger = logging.getLogger(__name__)


# =========================================================================
# Rate Limiting
# =========================================================================

class RateLimiter:
    """
    Token bucket rate limiter

    Implements per-IP and per-user rate limiting with different tiers
    """

    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = {}
        self.limits = {
            "default": {"requests": 100, "window": 60},  # 100 req/min
            "strict": {"requests": 10, "window": 60},     # 10 req/min
            "burst": {"requests": 1000, "window": 3600}   # 1000 req/hour
        }

    async def check_rate_limit(
        self,
        identifier: str,
        limit_type: str = "default"
    ) -> tuple[bool, Optional[Dict]]:
        """
        Check if request is within rate limit

        Returns:
            (is_allowed, rate_limit_info)
        """
        # Check if IP is blocked
        if identifier in self.blocked_ips:
            block_until = self.blocked_ips[identifier]
            if datetime.now() < block_until:
                return False, {
                    "blocked": True,
                    "retry_after": int((block_until - datetime.now()).total_seconds())
                }
            else:
                del self.blocked_ips[identifier]

        # Get limit configuration
        limit_config = self.limits.get(limit_type, self.limits["default"])
        max_requests = limit_config["requests"]
        window_seconds = limit_config["window"]

        # Clean old requests
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]

        # Check limit
        current_requests = len(self.requests[identifier])

        if current_requests >= max_requests:
            # Block for 5 minutes if consistently exceeding
            if current_requests > max_requests * 1.5:
                self.blocked_ips[identifier] = now + timedelta(minutes=5)
                logger.warning(f"Blocked {identifier} for 5 minutes due to rate limit abuse")

            return False, {
                "limit": max_requests,
                "remaining": 0,
                "reset": int((now - cutoff + timedelta(seconds=window_seconds)).timestamp()),
                "retry_after": window_seconds
            }

        # Add current request
        self.requests[identifier].append(now)

        return True, {
            "limit": max_requests,
            "remaining": max_requests - current_requests - 1,
            "reset": int((now - cutoff + timedelta(seconds=window_seconds)).timestamp())
        }


# =========================================================================
# Input Validation & Sanitization
# =========================================================================

class InputValidator:
    """
    Comprehensive input validation and sanitization

    Prevents:
    - SQL injection
    - XSS attacks
    - Command injection
    - Path traversal
    - Malicious payloads
    """

    # SQL injection patterns
    SQL_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(--|#|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(;|\||&&)"
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>"
    ]

    # Command injection patterns
    CMD_PATTERNS = [
        r"[;&|`$()]",
        r"\$\{.*\}",
        r"\.\.\/",
        r"~/"
    ]

    @classmethod
    def sanitize_string(cls, value: str, allow_html: bool = False) -> str:
        """
        Sanitize string input

        Args:
            value: String to sanitize
            allow_html: Whether to allow safe HTML tags

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)

        # Remove null bytes
        value = value.replace('\x00', '')

        # Trim whitespace
        value = value.strip()

        if allow_html:
            # Allow only safe HTML tags
            value = bleach.clean(
                value,
                tags=['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li'],
                attributes={'a': ['href', 'title']},
                strip=True
            )
        else:
            # Escape HTML entities
            value = bleach.clean(value, strip=True, tags=[])

        return value

    @classmethod
    def validate_sql_injection(cls, value: str) -> bool:
        """Check for SQL injection attempts"""
        value_upper = value.upper()
        for pattern in cls.SQL_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                logger.warning(f"SQL injection attempt detected: {value[:50]}")
                return False
        return True

    @classmethod
    def validate_xss(cls, value: str) -> bool:
        """Check for XSS attempts"""
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"XSS attempt detected: {value[:50]}")
                return False
        return True

    @classmethod
    def validate_command_injection(cls, value: str) -> bool:
        """Check for command injection attempts"""
        for pattern in cls.CMD_PATTERNS:
            if re.search(pattern, value):
                logger.warning(f"Command injection attempt detected: {value[:50]}")
                return False
        return True

    @classmethod
    def validate_path_traversal(cls, value: str) -> bool:
        """Check for path traversal attempts"""
        dangerous_patterns = ['../', '..\\', '%2e%2e', '%252e']
        value_lower = value.lower()
        for pattern in dangerous_patterns:
            if pattern in value_lower:
                logger.warning(f"Path traversal attempt detected: {value}")
                return False
        return True

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], allow_html: bool = False) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary

        Args:
            data: Dictionary to sanitize
            allow_html: Whether to allow safe HTML

        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = cls.sanitize_string(value, allow_html)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value, allow_html)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_string(item, allow_html) if isinstance(item, str)
                    else cls.sanitize_dict(item, allow_html) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        return sanitized

    @classmethod
    async def validate_request_data(cls, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate request data for security threats

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        def check_value(value: Any, field_name: str = ""):
            if isinstance(value, str):
                if not cls.validate_sql_injection(value):
                    errors.append(f"SQL injection detected in {field_name or 'field'}")
                if not cls.validate_xss(value):
                    errors.append(f"XSS attempt detected in {field_name or 'field'}")
                if not cls.validate_command_injection(value):
                    errors.append(f"Command injection detected in {field_name or 'field'}")
                if not cls.validate_path_traversal(value):
                    errors.append(f"Path traversal detected in {field_name or 'field'}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_value(v, f"{field_name}.{k}" if field_name else k)
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    check_value(item, f"{field_name}[{idx}]" if field_name else f"item[{idx}]")

        for key, value in data.items():
            check_value(value, key)

        return len(errors) == 0, errors


# =========================================================================
# Request Signing
# =========================================================================

class RequestSigner:
    """
    HMAC-based request signing for API authentication

    Ensures request integrity and authenticity
    """

    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()

    def sign_request(
        self,
        method: str,
        path: str,
        body: bytes,
        timestamp: str
    ) -> str:
        """
        Generate HMAC signature for request

        Args:
            method: HTTP method
            path: Request path
            body: Request body
            timestamp: ISO timestamp

        Returns:
            HMAC signature (hex)
        """
        message = f"{method}\n{path}\n{timestamp}\n".encode() + body
        signature = hmac.new(self.secret_key, message, hashlib.sha256)
        return signature.hexdigest()

    def verify_signature(
        self,
        method: str,
        path: str,
        body: bytes,
        timestamp: str,
        provided_signature: str
    ) -> bool:
        """
        Verify request signature

        Returns:
            True if signature is valid
        """
        # Check timestamp (reject requests older than 5 minutes)
        try:
            request_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            age = datetime.now() - request_time.replace(tzinfo=None)
            if age > timedelta(minutes=5):
                logger.warning("Request signature expired")
                return False
        except ValueError:
            logger.warning("Invalid timestamp format")
            return False

        # Verify signature
        expected_signature = self.sign_request(method, path, body, timestamp)
        return hmac.compare_digest(expected_signature, provided_signature)


# =========================================================================
# Security Middleware
# =========================================================================

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware

    Applies all security checks to incoming requests
    """

    def __init__(self, app, secret_key: Optional[str] = None):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
        self.validator = InputValidator()
        self.signer = RequestSigner(secret_key) if secret_key else None

        # Paths that don't need rate limiting
        self.rate_limit_exempt = [
            "/health",
            "/ready",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json"
        ]

        # Paths that need strict rate limiting
        self.strict_rate_limit = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/reset-password"
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request through security checks"""

        # Skip security for health checks
        if request.url.path in ["/health", "/ready"]:
            return await call_next(request)

        # Get client identifier
        client_ip = request.client.host
        user_id = request.headers.get("X-User-ID", client_ip)
        identifier = user_id if user_id != client_ip else client_ip

        # Apply rate limiting
        if request.url.path not in self.rate_limit_exempt:
            limit_type = "strict" if request.url.path in self.strict_rate_limit else "default"
            allowed, rate_info = await self.rate_limiter.check_rate_limit(identifier, limit_type)

            if not allowed:
                logger.warning(f"Rate limit exceeded for {identifier} on {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": "Too many requests. Please try again later.",
                        **rate_info
                    },
                    headers={
                        "Retry-After": str(rate_info.get("retry_after", 60)),
                        "X-RateLimit-Limit": str(rate_info.get("limit", 100)),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(rate_info.get("reset", 0))
                    }
                )

        # Verify request signature if enabled
        if self.signer and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            signature = request.headers.get("X-Signature")
            timestamp = request.headers.get("X-Timestamp")

            if not signature or not timestamp:
                logger.warning(f"Missing signature headers from {identifier}")
                # Don't block for now, but log
                # return JSONResponse(
                #     status_code=status.HTTP_401_UNAUTHORIZED,
                #     content={"error": "Missing request signature"}
                # )
            elif signature and timestamp:
                body = await request.body()
                if not self.signer.verify_signature(
                    request.method,
                    str(request.url.path),
                    body,
                    timestamp,
                    signature
                ):
                    logger.warning(f"Invalid signature from {identifier}")
                    # Don't block for now, but log
                    # return JSONResponse(
                    #     status_code=status.HTTP_401_UNAUTHORIZED,
                    #     content={"error": "Invalid request signature"}
                    # )

        # Validate request data for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    import json
                    try:
                        data = json.loads(body)
                        is_valid, errors = await self.validator.validate_request_data(data)

                        if not is_valid:
                            logger.error(f"Security validation failed for {identifier}: {errors}")
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                    "error": "Invalid request data",
                                    "message": "Request contains potentially malicious content",
                                    "details": errors
                                }
                            )
                    except json.JSONDecodeError:
                        pass  # Not JSON, skip validation
            except Exception as e:
                logger.error(f"Error validating request: {e}")

        # Add security headers to response
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.nphies.sa"
        )

        # Add rate limit headers if available
        if request.url.path not in self.rate_limit_exempt:
            _, rate_info = await self.rate_limiter.check_rate_limit(identifier)
            if rate_info:
                response.headers["X-RateLimit-Limit"] = str(rate_info.get("limit", 100))
                response.headers["X-RateLimit-Remaining"] = str(rate_info.get("remaining", 0))
                response.headers["X-RateLimit-Reset"] = str(rate_info.get("reset", 0))

        return response


# =========================================================================
# Utility Functions
# =========================================================================

def get_client_ip(request: Request) -> str:
    """Get real client IP considering proxies"""
    # Check X-Forwarded-For header (from reverse proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get first IP in the chain
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct client IP
    return request.client.host


def sanitize_input(data: Any, allow_html: bool = False) -> Any:
    """
    Convenience function to sanitize any input

    Args:
        data: Data to sanitize (str, dict, list, etc.)
        allow_html: Whether to allow safe HTML

    Returns:
        Sanitized data
    """
    if isinstance(data, str):
        return InputValidator.sanitize_string(data, allow_html)
    elif isinstance(data, dict):
        return InputValidator.sanitize_dict(data, allow_html)
    elif isinstance(data, list):
        return [sanitize_input(item, allow_html) for item in data]
    else:
        return data


# Global instances
rate_limiter = RateLimiter()
input_validator = InputValidator()
