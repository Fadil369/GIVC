"""
Unit tests for services.prior_authorization module
Tests prior authorization requests with mocked auth layer
"""
from typing import Dict
from unittest.mock import patch

import pytest  # type: ignore[import-not-found]

from services.prior_authorization import PriorAuthorizationService


class MockResponse:
    """Mock HTTP response"""

    def __init__(self, json_data: Dict, status_code: int = 200):
        self._json_data = json_data
        self.status_code = status_code
        self.text = str(json_data)

    def json(self) -> Dict:
        return self._json_data


@pytest.fixture
def valid_auth_response():
    """Valid NPHIES prior authorization response"""
    return {
        "resourceType": "Bundle",
        "id": "bundle-auth-response-123",
        "type": "message",
        "entry": [
            {
                "resource": {
                    "resourceType": "MessageHeader",
                    "id": "msg-header-1",
                }
            },
            {
                "resource": {
                    "resourceType": "ClaimResponse",
                    "id": "authresp-1",
                    "status": "active",
                    "outcome": "complete",
                    "disposition": "Authorization approved",
                    "preAuthRef": "AUTH-12345",
                    "item": [
                        {
                            "itemSequence": 1,
                            "adjudication": [
                                {
                                    "category": {
                                        "coding": [{"code": "benefit"}]
                                    }
                                }
                            ],
                        }
                    ],
                }
            },
        ],
    }


@pytest.fixture
def denied_auth_response():
    """Denied NPHIES prior authorization response"""
    return {
        "resourceType": "Bundle",
        "id": "bundle-auth-denied-123",
        "type": "message",
        "entry": [
            {
                "resource": {
                    "resourceType": "ClaimResponse",
                    "id": "authresp-2",
                    "status": "active",
                    "outcome": "error",
                    "disposition": "Authorization denied",
                    "item": [
                        {
                            "itemSequence": 1,
                            "adjudication": [
                                {
                                    "category": {
                                        "coding": [{"code": "denied"}]
                                    }
                                }
                            ],
                        }
                    ],
                }
            }
        ],
    }


@pytest.fixture
def sample_procedures():
    """Sample procedures for authorization"""
    return [
        {
            "code": "27447",
            "description": "Total knee arthroplasty",
            "quantity": 1,
            "estimated_cost": 15000.0,
            "diagnosis_sequence": 1,
        },
        {
            "code": "73564",
            "description": "Knee X-ray",
            "quantity": 2,
            "estimated_cost": 200.0,
        },
    ]


@pytest.fixture
def sample_diagnosis():
    """Sample diagnosis codes"""
    return ["M17.11", "M25.561"]


class TestSubmitPriorAuthorization:
    """Test submit_prior_authorization method"""

    @patch("services.prior_authorization.auth_manager")
    def test_submit_authorization_success(
        self,
        mock_auth,
        valid_auth_response,
        sample_procedures,
        sample_diagnosis,
    ):
        mock_auth.post.return_value = MockResponse(valid_auth_response)
        service = PriorAuthorizationService()

        result = service.submit_prior_authorization(
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            procedures=sample_procedures,
            diagnosis_codes=sample_diagnosis,
            provider_justification="Patient requires knee surgery",
        )

        assert result["success"] is True
        assert "auth_request_id" in result
        assert result["patient_id"] == "patient-123"
        assert "authorization_response" in result
        assert mock_auth.post.called

    @patch("services.prior_authorization.auth_manager")
    def test_submit_authorization_with_priority(
        self,
        mock_auth,
        valid_auth_response,
        sample_procedures,
        sample_diagnosis,
    ):
        mock_auth.post.return_value = MockResponse(valid_auth_response)
        service = PriorAuthorizationService()

        result = service.submit_prior_authorization(
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            procedures=sample_procedures,
            diagnosis_codes=sample_diagnosis,
            provider_justification="Urgent surgery required",
            priority="urgent",
        )

        assert result["success"] is True
        call_args = mock_auth.post.call_args
        bundle = call_args[0][1]
        assert bundle["resourceType"] == "Bundle"

    @patch("services.prior_authorization.auth_manager")
    def test_submit_authorization_with_custom_period(
        self,
        mock_auth,
        valid_auth_response,
        sample_procedures,
        sample_diagnosis,
    ):
        mock_auth.post.return_value = MockResponse(valid_auth_response)
        service = PriorAuthorizationService()

        result = service.submit_prior_authorization(
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            procedures=sample_procedures,
            diagnosis_codes=sample_diagnosis,
            provider_justification="Scheduled surgery",
            requested_period_start="2025-11-01",
            requested_period_end="2025-11-15",
        )

        assert result["success"] is True
        assert "auth_request_id" in result

    @patch("services.prior_authorization.auth_manager")
    def test_submit_authorization_defaults_period(
        self,
        mock_auth,
        valid_auth_response,
        sample_procedures,
        sample_diagnosis,
    ):
        mock_auth.post.return_value = MockResponse(valid_auth_response)
        service = PriorAuthorizationService()

        result = service.submit_prior_authorization(
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            procedures=sample_procedures,
            diagnosis_codes=sample_diagnosis,
            provider_justification="Surgery required",
        )

        assert result["success"] is True
        call_args = mock_auth.post.call_args
        bundle = call_args[0][1]
        assert "entry" in bundle

    @patch("services.prior_authorization.auth_manager")
    def test_submit_authorization_denied_response(
        self,
        mock_auth,
        denied_auth_response,
        sample_procedures,
        sample_diagnosis,
    ):
        mock_auth.post.return_value = MockResponse(denied_auth_response)
        service = PriorAuthorizationService()

        result = service.submit_prior_authorization(
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            procedures=sample_procedures,
            diagnosis_codes=sample_diagnosis,
            provider_justification="Surgery required",
        )

        assert result["success"] is True
        auth_resp = result["authorization_response"]
        assert auth_resp["decision"] == "denied"

    @patch("services.prior_authorization.auth_manager")
    def test_submit_authorization_handles_exception(
        self, mock_auth, sample_procedures, sample_diagnosis
    ):
        mock_auth.post.side_effect = Exception("Network error")
        service = PriorAuthorizationService()

        result = service.submit_prior_authorization(
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            procedures=sample_procedures,
            diagnosis_codes=sample_diagnosis,
            provider_justification="Surgery required",
        )

        assert result["success"] is False
        assert "error" in result
        assert "Network error" in result["error"]


class TestBuildAuthorizationBundle:
    """Test _build_authorization_bundle method"""

    @patch("services.prior_authorization.auth_manager")
    def test_build_authorization_bundle_structure(
        self, mock_auth, sample_procedures, sample_diagnosis
    ):
        service = PriorAuthorizationService()

        bundle = service._build_authorization_bundle(
            auth_request_id="preauth-123",
            patient_id="patient-123",
            member_id="1234567890",
            coverage_id="cov-123",
            payer_id="7000911508",
            procedures=sample_procedures,
            diagnosis_codes=sample_diagnosis,
            provider_justification="Medical justification",
            priority="routine",
            period_start="2025-11-01",
            period_end="2025-11-15",
            patient_name=None,
        )

        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "message"
        assert len(bundle["entry"]) > 0

        first_resource = bundle["entry"][0]["resource"]
        assert first_resource["resourceType"] == "MessageHeader"

    @patch("services.prior_authorization.auth_manager")
    def test_build_authorization_bundle_with_patient_name(
        self, mock_auth, sample_procedures, sample_diagnosis
    ):
        service = PriorAuthorizationService()

        bundle = service._build_authorization_bundle(
            auth_request_id="preauth-123",
            patient_id="patient-123",
            member_id="1234567890",
            coverage_id="cov-123",
            payer_id="7000911508",
            procedures=sample_procedures,
            diagnosis_codes=sample_diagnosis,
            provider_justification="Medical justification",
            priority="urgent",
            period_start="2025-11-01",
            period_end="2025-11-15",
            patient_name="Ahmed Al-Saud",
        )

        assert bundle["resourceType"] == "Bundle"
        patient_entries = [
            e
            for e in bundle["entry"]
            if e["resource"].get("resourceType") == "Patient"
        ]
        assert len(patient_entries) > 0


class TestExtractAuthResponse:
    """Test _extract_auth_response method"""

    @patch("services.prior_authorization.auth_manager")
    def test_extract_auth_response_approved(self, mock_auth):
        service = PriorAuthorizationService()

        resources = [
            {
                "resourceType": "ClaimResponse",
                "status": "active",
                "outcome": "complete",
                "disposition": "Approved",
                "preAuthRef": "AUTH-12345",
                "item": [
                    {
                        "itemSequence": 1,
                        "adjudication": [
                            {"category": {"coding": [{"code": "benefit"}]}}
                        ],
                    }
                ],
            }
        ]

        response = service._extract_auth_response(resources)

        assert response["status"] == "active"
        assert response["outcome"] == "complete"
        assert response["decision"] == "approved"
        assert response["preauth_ref"] == "AUTH-12345"
        assert len(response["approved_items"]) == 1

    @patch("services.prior_authorization.auth_manager")
    def test_extract_auth_response_denied(self, mock_auth):
        service = PriorAuthorizationService()

        resources = [
            {
                "resourceType": "ClaimResponse",
                "status": "active",
                "outcome": "error",
                "disposition": "Denied",
                "item": [
                    {
                        "itemSequence": 1,
                        "adjudication": [
                            {"category": {"coding": [{"code": "denied"}]}}
                        ],
                    }
                ],
            }
        ]

        response = service._extract_auth_response(resources)

        assert response["decision"] == "denied"
        assert len(response["denied_items"]) == 1

    @patch("services.prior_authorization.auth_manager")
    def test_extract_auth_response_no_claim_response(self, mock_auth):
        service = PriorAuthorizationService()

        resources = [{"resourceType": "MessageHeader"}]
        response = service._extract_auth_response(resources)

        assert response["status"] == "unknown"
        assert response["decision"] == "pending"


class TestQueryAuthorizationStatus:
    """Test query_authorization_status method"""

    @patch("services.prior_authorization.auth_manager")
    def test_query_authorization_status(self, mock_auth):
        service = PriorAuthorizationService()

        result = service.query_authorization_status(
            auth_request_id="preauth-123", patient_id="patient-123"
        )

        assert result["success"] is True
        assert result["auth_request_id"] == "preauth-123"

    @patch("services.prior_authorization.auth_manager")
    def test_query_authorization_status_returns_stub_response(self, mock_auth):
        """Test that query_authorization_status returns stub implementation"""
        service = PriorAuthorizationService()

        result = service.query_authorization_status(
            auth_request_id="preauth-123", patient_id="patient-123"
        )

        # Current implementation is a stub that returns success
        assert result["success"] is True
        assert result["auth_request_id"] == "preauth-123"
        assert "message" in result
