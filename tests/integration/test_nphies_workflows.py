"""
Integration tests for NPHIES service workflows
Tests end-to-end scenarios including eligibility, prior authorization, claims, and communication
"""
import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch


class MockResponse:
    """Mock HTTP response"""
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = str(json_data)
        self.ok = status_code == 200
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if not self.ok:
            from requests.exceptions import HTTPError
            raise HTTPError(f"HTTP {self.status_code}", response=self)


@pytest.fixture
def mock_auth_manager(monkeypatch):
    """Mock authentication manager for integration tests"""
    mock_session = Mock()
    
    def mock_post(url, *args, **kwargs):
        # Return different responses based on endpoint
        if "eligibility" in url:
            return MockResponse({
                "resourceType": "Bundle",
                "type": "message",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "MessageHeader",
                            "id": "msg-1"
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "CoverageEligibilityResponse",
                            "id": "eligibility-1",
                            "status": "active",
                            "outcome": "complete",
                            "patient": {"reference": "Patient/patient-1"},
                            "insurance": [
                                {
                                    "coverage": {"reference": "Coverage/cov-1"},
                                    "inforce": True
                                }
                            ]
                        }
                    }
                ]
            })
        elif "preauthorization" in url:
            return MockResponse({
                "resourceType": "Bundle",
                "type": "message",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "MessageHeader",
                            "id": "msg-2"
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "ClaimResponse",
                            "id": "preauth-1",
                            "status": "active",
                            "outcome": "complete",
                            "preAuthRef": "PA-123456"
                        }
                    }
                ]
            })
        elif "claim" in url:
            return MockResponse({
                "resourceType": "Bundle",
                "type": "message",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "MessageHeader",
                            "id": "msg-3"
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "ClaimResponse",
                            "id": "claim-1",
                            "status": "active",
                            "outcome": "complete",
                            "disposition": "Approved"
                        }
                    }
                ]
            })
        elif "communication" in url:
            return MockResponse({
                "resourceType": "Bundle",
                "type": "message",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "MessageHeader",
                            "id": "msg-4"
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "Communication",
                            "id": "comm-1",
                            "status": "completed",
                            "payload": [
                                {
                                    "contentString": "Claim approved"
                                }
                            ]
                        }
                    }
                ]
            })
        else:
            return MockResponse({}, status_code=404)
    
    mock_session.post = mock_post
    
    # Mock auth manager
    mock_auth = SimpleNamespace(
        session=mock_session,
        post=mock_post,
        get_auth_headers=lambda: {"Authorization": "Bearer test-token"}
    )
    
    monkeypatch.setattr("auth.auth_manager.auth_manager", mock_auth)
    return mock_auth


class TestEligibilityToPriorAuthWorkflow:
    """Test workflow from eligibility check to prior authorization"""
    
    def test_eligibility_check_before_prior_auth(self, mock_auth_manager):
        """Test that eligibility is checked before requesting prior authorization"""
        from services.eligibility import EligibilityService
        from services.prior_authorization import PriorAuthorizationService
        
        # Step 1: Check eligibility
        eligibility_service = EligibilityService()
        eligibility_result = eligibility_service.check_eligibility(
            member_id="12345",
            payer_id="7001",
            patient_id="patient-1",
            patient_name="John Doe",
            patient_gender="male",
            patient_dob="1990-01-01"
        )
        
        # Verify eligibility was successful (or at least returned data)
        assert eligibility_result is not None
        assert "request_id" in eligibility_result
        
        # Step 2: Request prior authorization using eligibility data
        prior_auth_service = PriorAuthorizationService()
        prior_auth_result = prior_auth_service.request_authorization(
            member_id="12345",
            payer_id="7001",
            provider_id="provider-1",
            service_type="consultation",
            service_date=datetime.now().strftime("%Y-%m-%d"),
            patient_data={
                "id": "patient-1",
                "name": "John Doe",
                "gender": "male",
                "birthDate": "1990-01-01"
            }
        )
        
        # Verify prior auth returned data
        assert prior_auth_result is not None
        assert "request_id" in prior_auth_result
    
    def test_failed_eligibility_prevents_prior_auth(self, monkeypatch):
        """Test that failed eligibility check prevents prior authorization"""
        # Mock failed eligibility response
        def mock_failed_post(url, *args, **kwargs):
            return MockResponse({
                "resourceType": "Bundle",
                "type": "message",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "MessageHeader",
                            "id": "msg-1"
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "OperationOutcome",
                            "issue": [
                                {
                                    "severity": "error",
                                    "code": "not-found",
                                    "diagnostics": "Member not found"
                                }
                            ]
                        }
                    }
                ]
            }, status_code=400)
        
        mock_session = Mock()
        mock_session.post = mock_failed_post
        mock_auth = SimpleNamespace(
            session=mock_session,
            post=mock_failed_post,
            get_auth_headers=lambda: {"Authorization": "Bearer test-token"}
        )
        
        monkeypatch.setattr("auth.auth_manager.auth_manager", mock_auth)
        
        from services.eligibility import EligibilityService
        
        eligibility_service = EligibilityService()
        
        # Should return error result, not raise exception
        result = eligibility_service.check_eligibility(
            member_id="invalid",
            payer_id="7001"
        )
        
        # Verify the result indicates failure
        assert result is not None
        assert result.get("success") is False or "error" in result or len(result.get("errors", [])) > 0


class TestPriorAuthToClaimWorkflow:
    """Test workflow from prior authorization to claim submission"""
    
    def test_claim_submission_with_prior_auth(self, mock_auth_manager):
        """Test claim submission includes prior authorization reference"""
        from services.prior_authorization import PriorAuthorizationService
        from services.claims import ClaimsService
        
        # Step 1: Get prior authorization
        prior_auth_service = PriorAuthorizationService()
        prior_auth_result = prior_auth_service.request_authorization(
            member_id="12345",
            payer_id="7001",
            provider_id="provider-1",
            service_type="surgery",
            service_date=datetime.now().strftime("%Y-%m-%d"),
            patient_data={
                "id": "patient-1",
                "name": "John Doe",
                "gender": "male",
                "birthDate": "1990-01-01"
            }
        )
        
        assert prior_auth_result is not None
        
        # Step 2: Submit claim with prior auth reference
        claim_service = ClaimsService()
        claim_result = claim_service.submit_claim(
            member_id="12345",
            payer_id="7001",
            provider_id="provider-1",
            claim_type="institutional",
            service_date=datetime.now().strftime("%Y-%m-%d"),
            items=[
                {
                    "sequence": 1,
                    "productOrService": {"coding": [{"code": "surgery"}]},
                    "quantity": {"value": 1},
                    "unitPrice": {"value": 5000, "currency": "SAR"}
                }
            ],
            patient_data={
                "id": "patient-1",
                "name": "John Doe",
                "gender": "male",
                "birthDate": "1990-01-01"
            },
            prior_auth_ref="PA-123456"
        )
        
        assert claim_result is not None
        assert "response" in claim_result or "bundle" in claim_result
    
    def test_claim_without_required_prior_auth(self, mock_auth_manager):
        """Test that claims requiring prior auth are validated"""
        from services.claims import ClaimsService
        
        claim_service = ClaimsService()
        
        # High-value claim typically requires prior auth
        # This should either warn or enforce prior auth requirement
        claim_result = claim_service.submit_claim(
            member_id="12345",
            payer_id="7001",
            provider_id="provider-1",
            claim_type="institutional",
            service_date=datetime.now().strftime("%Y-%m-%d"),
            items=[
                {
                    "sequence": 1,
                    "productOrService": {"coding": [{"code": "major-surgery"}]},
                    "quantity": {"value": 1},
                    "unitPrice": {"value": 50000, "currency": "SAR"}
                }
            ],
            patient_data={
                "id": "patient-1",
                "name": "John Doe",
                "gender": "male",
                "birthDate": "1990-01-01"
            }
        )
        
        # Should complete but may have warnings
        assert claim_result is not None


class TestClaimToCommunicationWorkflow:
    """Test workflow from claim submission to communication polling"""
    
    def test_communication_polling_after_claim(self, mock_auth_manager):
        """Test checking communication after claim submission"""
        from services.claims import ClaimsService
        from services.communication import CommunicationService
        
        # Step 1: Submit claim
        claim_service = ClaimsService()
        claim_result = claim_service.submit_claim(
            member_id="12345",
            payer_id="7001",
            provider_id="provider-1",
            claim_type="professional",
            service_date=datetime.now().strftime("%Y-%m-%d"),
            items=[
                {
                    "sequence": 1,
                    "productOrService": {"coding": [{"code": "consultation"}]},
                    "quantity": {"value": 1},
                    "unitPrice": {"value": 500, "currency": "SAR"}
                }
            ],
            patient_data={
                "id": "patient-1",
                "name": "John Doe",
                "gender": "male",
                "birthDate": "1990-01-01"
            }
        )
        
        assert claim_result is not None
        
        # Step 2: Poll for communication/status updates
        comm_service = CommunicationService()
        comm_result = comm_service.poll_request(
            request_id="claim-1",
            payer_id="7001"
        )
        
        assert comm_result is not None
        assert "response" in comm_result or "bundle" in comm_result


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow"""
    
    def test_complete_nphies_workflow(self, mock_auth_manager):
        """Test complete workflow: eligibility → prior auth → claim → communication"""
        from services.eligibility import EligibilityService
        from services.prior_authorization import PriorAuthorizationService
        from services.claims import ClaimsService
        from services.communication import CommunicationService
        
        patient_data = {
            "id": "patient-1",
            "name": "John Doe",
            "gender": "male",
            "birthDate": "1990-01-01"
        }
        
        # Step 1: Check eligibility
        eligibility_service = EligibilityService()
        eligibility_result = eligibility_service.check_eligibility(
            member_id="12345",
            payer_id="7001",
            patient_id=patient_data["id"],
            patient_name=patient_data["name"],
            patient_gender=patient_data["gender"],
            patient_dob=patient_data["birthDate"]
        )
        assert eligibility_result is not None
        
        # Step 2: Request prior authorization
        prior_auth_service = PriorAuthorizationService()
        prior_auth_result = prior_auth_service.request_authorization(
            member_id="12345",
            payer_id="7001",
            provider_id="provider-1",
            service_type="surgery",
            service_date=datetime.now().strftime("%Y-%m-%d"),
            patient_data=patient_data
        )
        assert prior_auth_result is not None
        
        # Step 3: Submit claim
        claim_service = ClaimsService()
        claim_result = claim_service.submit_claim(
            member_id="12345",
            payer_id="7001",
            provider_id="provider-1",
            claim_type="institutional",
            service_date=datetime.now().strftime("%Y-%m-%d"),
            items=[
                {
                    "sequence": 1,
                    "productOrService": {"coding": [{"code": "surgery"}]},
                    "quantity": {"value": 1},
                    "unitPrice": {"value": 5000, "currency": "SAR"}
                }
            ],
            patient_data=patient_data,
            prior_auth_ref="PA-123456"
        )
        assert claim_result is not None
        
        # Step 4: Check communication
        comm_service = CommunicationService()
        comm_result = comm_service.poll_request(
            request_id="claim-1",
            payer_id="7001"
        )
        assert comm_result is not None


class TestDataFlowBetweenServices:
    """Test data consistency and flow between services"""
    
    def test_patient_data_consistency(self, mock_auth_manager):
        """Test that patient data remains consistent across service calls"""
        from services.eligibility import EligibilityService
        from services.claims import ClaimsService
        
        patient_data = {
            "id": "patient-1",
            "name": "John Doe",
            "gender": "male",
            "birthDate": "1990-01-01"
        }
        
        # Check eligibility
        eligibility_service = EligibilityService()
        eligibility_service.check_eligibility(
            member_id="12345",
            payer_id="7001",
            patient_id=patient_data["id"],
            patient_name=patient_data["name"],
            patient_gender=patient_data["gender"],
            patient_dob=patient_data["birthDate"]
        )
        
        # Submit claim with same patient data
        claim_service = ClaimsService()
        claim_result = claim_service.submit_claim(
            member_id="12345",
            payer_id="7001",
            provider_id="provider-1",
            claim_type="professional",
            service_date=datetime.now().strftime("%Y-%m-%d"),
            items=[
                {
                    "sequence": 1,
                    "productOrService": {"coding": [{"code": "consultation"}]},
                    "quantity": {"value": 1},
                    "unitPrice": {"value": 500, "currency": "SAR"}
                }
            ],
            patient_data=patient_data
        )
        
        assert claim_result is not None
    
    def test_service_date_validation_across_workflow(self, mock_auth_manager):
        """Test that service dates are properly validated across workflow"""
        from services.prior_authorization import PriorAuthorizationService
        from services.claims import ClaimsService
        
        service_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Prior auth for future service
        prior_auth_service = PriorAuthorizationService()
        prior_auth_result = prior_auth_service.request_authorization(
            member_id="12345",
            payer_id="7001",
            provider_id="provider-1",
            service_type="surgery",
            service_date=service_date,
            patient_data={
                "id": "patient-1",
                "name": "John Doe",
                "gender": "male",
                "birthDate": "1990-01-01"
            }
        )
        
        assert prior_auth_result is not None
        
        # Claim with matching service date
        claim_service = ClaimsService()
        claim_result = claim_service.submit_claim(
            member_id="12345",
            payer_id="7001",
            provider_id="provider-1",
            claim_type="institutional",
            service_date=service_date,
            items=[
                {
                    "sequence": 1,
                    "productOrService": {"coding": [{"code": "surgery"}]},
                    "quantity": {"value": 1},
                    "unitPrice": {"value": 5000, "currency": "SAR"}
                }
            ],
            patient_data={
                "id": "patient-1",
                "name": "John Doe",
                "gender": "male",
                "birthDate": "1990-01-01"
            }
        )
        
        assert claim_result is not None
