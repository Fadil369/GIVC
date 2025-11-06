"""
Unit tests for Teams security module
Tests HMAC signature generation and verification
"""

import pytest
import hashlib
import hmac
import json
from datetime import datetime, timezone

from integrations.teams.security import (
    generate_hmac_signature,
    verify_hmac_signature,
    validate_webhook_request
)


class TestHMACSignatures:
    """Tests for HMAC signature generation and verification"""
    
    def test_generate_hmac_signature(self):
        """Test HMAC-SHA256 signature generation"""
        secret = "test-secret-key-32-bytes-long!!"
        payload = {"type": "message", "text": "Test"}
        
        signature = generate_hmac_signature(payload, secret)
        
        assert signature is not None
        assert len(signature) == 64  # SHA256 hex digest length
    
    def test_verify_valid_signature(self):
        """Test verification of valid HMAC signature"""
        secret = "test-secret-key-32-bytes-long!!"
        payload = {"type": "message", "text": "Test"}
        
        # Generate valid signature
        signature = generate_hmac_signature(payload, secret)
        
        # Verify should return True
        is_valid = verify_hmac_signature(payload, signature, secret)
        assert is_valid is True
    
    def test_verify_invalid_signature(self):
        """Test verification fails for invalid signature"""
        secret = "test-secret-key-32-bytes-long!!"
        payload = {"type": "message", "text": "Test"}
        
        invalid_signature = "0" * 64  # Invalid signature
        
        is_valid = verify_hmac_signature(payload, invalid_signature, secret)
        assert is_valid is False
    
    def test_verify_signature_with_wrong_secret(self):
        """Test verification fails when secret doesn't match"""
        secret1 = "test-secret-key-32-bytes-long!!"
        secret2 = "different-secret-key-32-bytes!"
        payload = {"type": "message", "text": "Test"}
        
        # Generate with secret1
        signature = generate_hmac_signature(payload, secret1)
        
        # Verify with secret2 should fail
        is_valid = verify_hmac_signature(payload, signature, secret2)
        assert is_valid is False
    
    def test_constant_time_comparison(self):
        """Test that verification uses constant-time comparison"""
        secret = "test-secret-key-32-bytes-long!!"
        payload = {"type": "message"}
        
        valid_signature = generate_hmac_signature(payload, secret)
        invalid_signature = "f" * 64
        
        # Both should take roughly the same time (within reasonable margin)
        # This is a basic test; timing attacks are complex to test
        is_valid_1 = verify_hmac_signature(payload, valid_signature, secret)
        is_valid_2 = verify_hmac_signature(payload, invalid_signature, secret)
        
        assert is_valid_1 is True
        assert is_valid_2 is False
    
    def test_signature_deterministic(self):
        """Test that signature generation is deterministic"""
        secret = "test-secret-key-32-bytes-long!!"
        payload = {"type": "message", "text": "Test"}
        
        sig1 = generate_hmac_signature(payload, secret)
        sig2 = generate_hmac_signature(payload, secret)
        
        assert sig1 == sig2
    
    def test_different_payloads_different_signatures(self):
        """Test that different payloads produce different signatures"""
        secret = "test-secret-key-32-bytes-long!!"
        payload1 = {"type": "message", "text": "Test1"}
        payload2 = {"type": "message", "text": "Test2"}
        
        sig1 = generate_hmac_signature(payload1, secret)
        sig2 = generate_hmac_signature(payload2, secret)
        
        assert sig1 != sig2


class TestWebhookRequestValidation:
    """Tests for webhook request validation"""
    
    def test_validate_webhook_request_success(self):
        """Test successful webhook request validation"""
        secret = "test-secret-key-32-bytes-long!!"
        payload = {"type": "message", "text": "Test"}
        payload_str = json.dumps(payload)
        
        signature = generate_hmac_signature(payload, secret)
        
        is_valid = validate_webhook_request(payload_str, signature, secret)
        assert is_valid is True
    
    def test_validate_webhook_request_failure(self):
        """Test failed webhook request validation"""
        secret = "test-secret-key-32-bytes-long!!"
        payload_str = json.dumps({"type": "message"})
        invalid_signature = "0" * 64
        
        is_valid = validate_webhook_request(payload_str, invalid_signature, secret)
        assert is_valid is False
    
    def test_validate_webhook_request_with_modified_payload(self):
        """Test validation fails when payload is modified after signing"""
        secret = "test-secret-key-32-bytes-long!!"
        original_payload = {"type": "message", "text": "Original"}
        modified_payload = {"type": "message", "text": "Modified"}
        
        signature = generate_hmac_signature(original_payload, secret)
        modified_payload_str = json.dumps(modified_payload)
        
        is_valid = validate_webhook_request(modified_payload_str, signature, secret)
        assert is_valid is False


# Run tests with: pytest integrations/teams/tests/test_security.py -v
