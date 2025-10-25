"""
Unit tests for services.eligibility module
Tests eligibility service with mocked auth layer
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from services.eligibility import EligibilityService
from utils.validators import ValidationError


class MockResponse:
    """Mock HTTP response"""
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code
        self.text = str(json_data)
    
    def json(self):
        return self._json_data


@pytest.fixture
def valid_eligibility_response():
    """Valid NPHIES eligibility response"""
    return {
        "resourceType": "Bundle",
        "id": "bundle-response-123",
        "type": "message",
        "entry": [
            {
                "resource": {
                    "resourceType": "MessageHeader",
                    "id": "msg-header-1"
                }
            },
            {
                "resource": {
                    "resourceType": "CoverageEligibilityResponse",
                    "id": "eligresp-1",
                    "outcome": "complete",
                    "disposition": "Policy is active",
                    "insurance": [
                        {
                            "coverage": {"reference": "Coverage/cov-1"},
                            "item": [
                                {
                                    "category": {"text": "Medical Care"},
                                    "benefit": [
                                        {"type": {"text": "Coinsurance"}}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }


@pytest.fixture
def error_eligibility_response():
    """Error NPHIES eligibility response"""
    return {
        "resourceType": "Bundle",
        "id": "bundle-error-123",
        "entry": [
            {
                "resource": {
                    "resourceType": "OperationOutcome",
                    "issue": [
                        {
                            "severity": "error",
                            "details": {"text": "Member not found"}
                        }
                    ]
                }
            }
        ]
    }


class TestCheckEligibility:
    """Test check_eligibility method"""
    
    @patch('services.eligibility.auth_manager')
    def test_check_eligibility_success(
        self,
        mock_auth,
        valid_eligibility_response
    ):
        mock_auth.post.return_value = MockResponse(valid_eligibility_response)
        service = EligibilityService()
        
        result = service.check_eligibility(
            member_id="1234567890",
            payer_id="7000911508",
            service_date="2025-10-22"
        )
        
        assert result["success"] is True
        assert result["member_id"] == "1234567890"
        assert "request_id" in result
        assert mock_auth.post.called
    
    @patch('services.eligibility.auth_manager')
    def test_check_eligibility_with_patient_details(
        self,
        mock_auth,
        valid_eligibility_response
    ):
        mock_auth.post.return_value = MockResponse(valid_eligibility_response)
        service = EligibilityService()
        
        result = service.check_eligibility(
            member_id="1234567890",
            payer_id="7000911508",
            patient_name="John Doe",
            patient_gender="male",
            patient_dob="1990-01-01"
        )
        
        assert result["success"] is True
        call_args = mock_auth.post.call_args
        bundle = call_args[0][1]
        assert bundle["resourceType"] == "Bundle"
    
    @patch('services.eligibility.auth_manager')
    def test_check_eligibility_defaults_service_date(
        self,
        mock_auth,
        valid_eligibility_response
    ):
        mock_auth.post.return_value = MockResponse(valid_eligibility_response)
        service = EligibilityService()
        
        result = service.check_eligibility(
            member_id="1234567890",
            payer_id="7000911508"
        )
        
        assert result["success"] is True
        call_args = mock_auth.post.call_args
        bundle = call_args[0][1]
        assert "entry" in bundle
    
    @patch('services.eligibility.auth_manager')
    def test_check_eligibility_error_response(
        self,
        mock_auth,
        error_eligibility_response
    ):
        mock_auth.post.return_value = MockResponse(error_eligibility_response)
        service = EligibilityService()
        
        result = service.check_eligibility(
            member_id="1234567890",
            payer_id="7000911508"
        )
        
        assert result["success"] is False
        assert len(result["errors"]) > 0
    
    @patch('services.eligibility.auth_manager')
    def test_check_eligibility_handles_exception(self, mock_auth):
        mock_auth.post.side_effect = Exception("Network error")
        service = EligibilityService()
        
        result = service.check_eligibility(
            member_id="1234567890",
            payer_id="7000911508"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "Network error" in result["error"]


class TestBuildEligibilityBundle:
    """Test _build_eligibility_bundle method"""
    
    @patch('services.eligibility.auth_manager')
    def test_build_eligibility_bundle_structure(self, mock_auth):
        service = EligibilityService()
        
        bundle = service._build_eligibility_bundle(
            eligibility_request_id="eligreq-123",
            patient_id="patient-123",
            coverage_id="cov-123",
            member_id="1234567890",
            payer_id="7000911508",
            service_date="2025-10-22"
        )
        
        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "message"
        assert len(bundle["entry"]) > 0
        
        first_resource = bundle["entry"][0]["resource"]
        assert first_resource["resourceType"] == "MessageHeader"


class TestExtractCoverageStatus:
    """Test _extract_coverage_status method"""
    
    @patch('services.eligibility.auth_manager')
    def test_extract_coverage_status_complete(self, mock_auth):
        service = EligibilityService()
        
        resources = [
            {
                "resourceType": "CoverageEligibilityResponse",
                "outcome": "complete",
                "disposition": "Policy is active",
                "insurance": [
                    {
                        "coverage": {"reference": "Coverage/cov-1"},
                        "item": [
                            {
                                "category": {"text": "Medical"},
                                "benefit": [{"type": {"text": "Coinsurance"}}]
                            }
                        ]
                    }
                ]
            }
        ]
        
        status = service._extract_coverage_status(resources)
        
        assert status["eligible"] is True
        assert status["outcome"] == "complete"
        assert len(status["coverage_details"]) > 0
    
    @patch('services.eligibility.auth_manager')
    def test_extract_coverage_status_no_eligibility_response(self, mock_auth):
        service = EligibilityService()
        
        resources = [{"resourceType": "MessageHeader"}]
        status = service._extract_coverage_status(resources)
        
        assert status["eligible"] is False
        assert len(status["coverage_details"]) == 0


class TestBatchCheckEligibility:
    """Test batch_check_eligibility method"""
    
    @patch('services.eligibility.auth_manager')
    def test_batch_check_eligibility_single_member(
        self,
        mock_auth,
        valid_eligibility_response
    ):
        mock_auth.post.return_value = MockResponse(valid_eligibility_response)
        service = EligibilityService()
        
        members = [
            {"member_id": "1234567890", "payer_id": "7000911508"}
        ]
        
        results = service.batch_check_eligibility(members)
        
        assert len(results) == 1
        assert results[0]["success"] is True
    
    @patch('services.eligibility.auth_manager')
    def test_batch_check_eligibility_multiple_members(
        self,
        mock_auth,
        valid_eligibility_response
    ):
        mock_auth.post.return_value = MockResponse(valid_eligibility_response)
        service = EligibilityService()
        
        members = [
            {"member_id": "1111111111", "payer_id": "7000911508"},
            {"member_id": "2222222222", "payer_id": "7000911508"}
        ]
        
        results = service.batch_check_eligibility(members)
        
        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert mock_auth.post.call_count == 2

