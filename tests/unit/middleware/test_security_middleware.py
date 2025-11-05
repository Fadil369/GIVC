"""
Unit Tests for Security Middleware
===================================
Comprehensive test suite for security features including rate limiting,
input validation, and request signing.

Author: GIVC Platform Team
License: GPL-3.0
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# Import security middleware components
from middleware.security_middleware import (
    SecurityMiddleware,
    RateLimiter,
    InputValidator,
    RequestSigner,
    sanitize_input
)

class TestRateLimiter:
    """Test suite for rate limiting functionality"""

    @pytest.fixture
    def rate_limiter(self):
        """Create a fresh rate limiter for each test"""
        return RateLimiter()

    @pytest.mark.asyncio
    async def test_rate_limit_within_limit(self, rate_limiter):
        """Test requests within rate limit"""
        identifier = "test_user_1"
        
        # Make requests within limit
        for i in range(10):
            allowed, info = await rate_limiter.check_rate_limit(identifier)
            assert allowed == True, f"Request {i} should be allowed"
            assert "remaining" in info
            assert info["remaining"] >= 0

    @pytest.mark.asyncio
    async def test_rate_limit_exceeds_limit(self, rate_limiter):
        """Test requests that exceed rate limit"""
        identifier = "test_user_2"
        
        # Exceed the default limit (100 requests)
        for i in range(105):
            allowed, info = await rate_limiter.check_rate_limit(identifier)
            
            if i < 100:
                assert allowed == True, f"Request {i} should be allowed"
            else:
                assert allowed == False, f"Request {i} should be blocked"
                assert "retry_after" in info

    @pytest.mark.asyncio
    async def test_rate_limit_different_users(self, rate_limiter):
        """Test that rate limits are per-user"""
        user1 = "test_user_1"
        user2 = "test_user_2"
        
        # User 1 makes many requests
        for i in range(50):
            allowed, _ = await rate_limiter.check_rate_limit(user1)
            assert allowed == True
        
        # User 2 should still be allowed
        allowed, info = await rate_limiter.check_rate_limit(user2)
        assert allowed == True
        assert info["remaining"] > 90  # Should have almost full quota

    @pytest.mark.asyncio
    async def test_rate_limit_strict_mode(self, rate_limiter):
        """Test strict rate limiting for sensitive endpoints"""
        identifier = "test_user_strict"
        
        # Strict mode allows only 10 requests
        for i in range(15):
            allowed, info = await rate_limiter.check_rate_limit(identifier, "strict")
            
            if i < 10:
                assert allowed == True, f"Strict request {i} should be allowed"
            else:
                assert allowed == False, f"Strict request {i} should be blocked"

    @pytest.mark.asyncio
    async def test_rate_limit_ip_blocking(self, rate_limiter):
        """Test automatic IP blocking for abuse"""
        identifier = "abusive_user"
        
        # Exceed limit significantly to trigger blocking
        for i in range(160):  # 1.5x the default limit
            allowed, info = await rate_limiter.check_rate_limit(identifier)
        
        # Should be blocked
        assert allowed == False
        assert "blocked" in info or "retry_after" in info


class TestInputValidator:
    """Test suite for input validation and sanitization"""

    def test_sanitize_string_basic(self):
        """Test basic string sanitization"""
        clean_text = "Hello World"
        result = InputValidator.sanitize_string(clean_text)
        assert result == clean_text

    def test_sanitize_string_html_removal(self):
        """Test HTML tag removal"""
        malicious_text = "<script>alert('xss')</script>Hello"
        result = InputValidator.sanitize_string(malicious_text)
        assert "<script>" not in result
        assert "Hello" in result

    def test_sanitize_string_sql_patterns(self):
        """Test detection of SQL injection patterns"""
        sql_injection = "'; DROP TABLE users; --"
        is_valid = InputValidator.validate_sql_injection(sql_injection)
        assert is_valid == False

    def test_sanitize_string_xss_patterns(self):
        """Test detection of XSS patterns"""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src='javascript:alert(1)'></iframe>"
        ]
        
        for xss in xss_attempts:
            is_valid = InputValidator.validate_xss(xss)
            assert is_valid == False, f"Should detect XSS in: {xss}"

    def test_sanitize_string_command_injection(self):
        """Test detection of command injection"""
        command_injections = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& rm important_file",
            "$(whoami)",
            "`id`"
        ]
        
        for cmd in command_injections:
            is_valid = InputValidator.validate_command_injection(cmd)
            assert is_valid == False, f"Should detect command injection in: {cmd}"

    def test_sanitize_string_path_traversal(self):
        """Test detection of path traversal"""
        path_traversals = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "%2e%2e%2f",
            "%252e%252e%252f"
        ]
        
        for path in path_traversals:
            is_valid = InputValidator.validate_path_traversal(path)
            assert is_valid == False, f"Should detect path traversal in: {path}"

    def test_sanitize_dict_recursive(self):
        """Test recursive dictionary sanitization"""
        dirty_dict = {
            "name": "John <script>alert('xss')</script>",
            "nested": {
                "value": "'; DROP TABLE users; --",
                "safe": "normal text"
            },
            "list": ["safe", "<img src=x onerror=alert(1)>"]
        }
        
        clean_dict = InputValidator.sanitize_dict(dirty_dict)
        
        # Check that malicious content is removed
        assert "<script>" not in clean_dict["name"]
        assert "John" in clean_dict["name"]
        assert "safe" in clean_dict["nested"]["safe"]
        assert "<img" not in clean_dict["list"][1]

    @pytest.mark.asyncio
    async def test_validate_request_data_clean(self):
        """Test validation of clean request data"""
        clean_data = {
            "username": "john_doe",
            "email": "john@example.com",
            "age": 25
        }
        
        is_valid, errors = await InputValidator.validate_request_data(clean_data)
        assert is_valid == True
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_validate_request_data_malicious(self):
        """Test validation of malicious request data"""
        malicious_data = {
            "username": "'; DROP TABLE users; --",
            "comment": "<script>alert('xss')</script>",
            "file_path": "../../../etc/passwd"
        }
        
        is_valid, errors = await InputValidator.validate_request_data(malicious_data)
        assert is_valid == False
        assert len(errors) > 0
        
        # Check that specific threats are detected
        error_text = " ".join(errors)
        assert "SQL injection" in error_text or "XSS" in error_text or "Path traversal" in error_text


class TestRequestSigner:
    """Test suite for request signing functionality"""

    @pytest.fixture
    def request_signer(self):
        """Create request signer with test secret"""
        return RequestSigner("test_secret_key_123")

    def test_sign_request_basic(self, request_signer):
        """Test basic request signing"""
        method = "POST"
        path = "/api/test"
        body = b'{"test": "data"}'
        timestamp = datetime.now().isoformat()
        
        signature = request_signer.sign_request(method, path, body, timestamp)
        
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA-256 hex length

    def test_verify_signature_valid(self, request_signer):
        """Test verification of valid signature"""
        method = "POST"
        path = "/api/test"
        body = b'{"test": "data"}'
        timestamp = datetime.now().isoformat()
        
        # Generate signature
        signature = request_signer.sign_request(method, path, body, timestamp)
        
        # Verify signature
        is_valid = request_signer.verify_signature(method, path, body, timestamp, signature)
        assert is_valid == True

    def test_verify_signature_invalid(self, request_signer):
        """Test verification of invalid signature"""
        method = "POST"
        path = "/api/test"
        body = b'{"test": "data"}'
        timestamp = datetime.now().isoformat()
        
        # Use wrong signature
        wrong_signature = "invalid_signature_123"
        
        is_valid = request_signer.verify_signature(method, path, body, timestamp, wrong_signature)
        assert is_valid == False

    def test_verify_signature_expired(self, request_signer):
        """Test verification of expired signature"""
        method = "POST"
        path = "/api/test"
        body = b'{"test": "data"}'
        
        # Use old timestamp (more than 5 minutes ago)
        old_timestamp = (datetime.now() - timedelta(minutes=10)).isoformat()
        
        signature = request_signer.sign_request(method, path, body, old_timestamp)
        
        is_valid = request_signer.verify_signature(method, path, body, old_timestamp, signature)
        assert is_valid == False

    def test_signature_consistency(self, request_signer):
        """Test that same inputs produce same signature"""
        method = "POST"
        path = "/api/test"
        body = b'{"test": "data"}'
        timestamp = datetime.now().isoformat()
        
        signature1 = request_signer.sign_request(method, path, body, timestamp)
        signature2 = request_signer.sign_request(method, path, body, timestamp)
        
        assert signature1 == signature2


class TestSecurityMiddleware:
    """Test suite for complete security middleware"""

    @pytest.fixture
    def mock_app(self):
        """Mock FastAPI app for testing"""
        async def app(request):
            return Response("OK", status_code=200)
        return app

    @pytest.fixture
    def security_middleware(self, mock_app):
        """Create security middleware instance"""
        return SecurityMiddleware(mock_app, secret_key="test_secret")

    @pytest.fixture
    def mock_request(self):
        """Create mock request for testing"""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"
        request.client.host = "127.0.0.1"
        request.headers = {}
        return request

    @pytest.mark.asyncio
    async def test_middleware_allows_health_checks(self, security_middleware, mock_request):
        """Test that health check endpoints bypass security"""
        mock_request.url.path = "/health"
        
        async def call_next(request):
            return Response("OK")
        
        response = await security_middleware.dispatch(mock_request, call_next)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_middleware_adds_security_headers(self, security_middleware, mock_request):
        """Test that security headers are added to responses"""
        async def call_next(request):
            return Response("OK")
        
        response = await security_middleware.dispatch(mock_request, call_next)
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"

    @pytest.mark.asyncio
    async def test_middleware_rate_limiting(self, security_middleware):
        """Test rate limiting functionality"""
        # Create many requests from same IP
        for i in range(105):  # Exceed default limit
            mock_request = Mock(spec=Request)
            mock_request.url.path = "/api/test"
            mock_request.method = "GET"
            mock_request.client.host = "192.168.1.100"
            mock_request.headers = {}
            
            async def call_next(request):
                return Response("OK")
            
            response = await security_middleware.dispatch(mock_request, call_next)
            
            if i >= 100:  # Should be rate limited
                assert response.status_code == 429
                break

    @pytest.mark.asyncio
    async def test_middleware_input_validation_post(self, security_middleware):
        """Test input validation for POST requests"""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "POST"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}
        
        # Mock malicious request body
        malicious_body = json.dumps({
            "username": "'; DROP TABLE users; --",
            "comment": "<script>alert('xss')</script>"
        }).encode()
        
        async def mock_body():
            return malicious_body
        
        mock_request.body = mock_body
        
        async def call_next(request):
            return Response("OK")
        
        response = await security_middleware.dispatch(mock_request, call_next)
        
        # Should block malicious request
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_middleware_strict_rate_limiting(self, security_middleware):
        """Test strict rate limiting for auth endpoints"""
        # Test auth endpoint with strict limits
        for i in range(15):  # Exceed strict limit of 10
            mock_request = Mock(spec=Request)
            mock_request.url.path = "/api/v1/auth/login"
            mock_request.method = "POST"
            mock_request.client.host = "192.168.1.101"
            mock_request.headers = {}
            
            async def call_next(request):
                return Response("OK")
            
            response = await security_middleware.dispatch(mock_request, call_next)
            
            if i >= 10:  # Should be rate limited with strict limits
                assert response.status_code == 429
                break


class TestSecurityUtilities:
    """Test suite for security utility functions"""

    def test_sanitize_input_string(self):
        """Test utility sanitize_input function with string"""
        malicious_string = "<script>alert('xss')</script>Hello"
        result = sanitize_input(malicious_string)
        assert "<script>" not in result
        assert "Hello" in result

    def test_sanitize_input_dict(self):
        """Test utility sanitize_input function with dict"""
        malicious_dict = {
            "safe": "normal text",
            "dangerous": "<script>alert('xss')</script>"
        }
        result = sanitize_input(malicious_dict)
        assert isinstance(result, dict)
        assert result["safe"] == "normal text"
        assert "<script>" not in result["dangerous"]

    def test_sanitize_input_list(self):
        """Test utility sanitize_input function with list"""
        malicious_list = [
            "safe text",
            "<script>alert('xss')</script>",
            {"nested": "'; DROP TABLE users; --"}
        ]
        result = sanitize_input(malicious_list)
        assert isinstance(result, list)
        assert result[0] == "safe text"
        assert "<script>" not in result[1]
        assert isinstance(result[2], dict)

    def test_sanitize_input_none_and_numbers(self):
        """Test sanitize_input with None and numeric values"""
        assert sanitize_input(None) is None
        assert sanitize_input(42) == 42
        assert sanitize_input(3.14) == 3.14
        assert sanitize_input(True) is True


# Performance and edge case tests
class TestSecurityPerformance:
    """Test performance characteristics of security middleware"""

    @pytest.mark.asyncio
    async def test_validation_performance(self):
        """Test that validation doesn't significantly slow down requests"""
        import time
        
        validator = InputValidator()
        large_data = {f"field_{i}": f"value_{i}" for i in range(1000)}
        
        start_time = time.time()
        is_valid, errors = await validator.validate_request_data(large_data)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 1.0, f"Validation took too long: {processing_time:.3f}s"

    @pytest.mark.asyncio
    async def test_rate_limiter_performance(self):
        """Test rate limiter performance with many users"""
        import time
        
        rate_limiter = RateLimiter()
        
        start_time = time.time()
        
        # Simulate 100 different users making requests
        for user_id in range(100):
            for request in range(10):
                await rate_limiter.check_rate_limit(f"user_{user_id}")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert processing_time < 2.0, f"Rate limiting took too long: {processing_time:.3f}s"


# Edge cases and error handling
class TestSecurityEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_string_validation(self):
        """Test validation of empty strings"""
        result = InputValidator.sanitize_string("")
        assert result == ""
        
        is_valid = InputValidator.validate_sql_injection("")
        assert is_valid == True

    def test_very_long_string_validation(self):
        """Test validation of very long strings"""
        long_string = "a" * 10000
        result = InputValidator.sanitize_string(long_string)
        assert len(result) <= len(long_string)

    def test_unicode_string_validation(self):
        """Test validation of unicode strings"""
        unicode_string = "Hello 世界 🌍"
        result = InputValidator.sanitize_string(unicode_string)
        assert "Hello" in result
        assert "世界" in result

    def test_null_byte_handling(self):
        """Test handling of null bytes in input"""
        malicious_string = "hello\x00world"
        result = InputValidator.sanitize_string(malicious_string)
        assert "\x00" not in result
        assert "hello" in result
        assert "world" in result


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/unit/middleware/test_security_middleware.py -v
    pytest.main([__file__, "-v", "--tb=short"])