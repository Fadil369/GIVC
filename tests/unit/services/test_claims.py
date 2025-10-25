"""
Unit tests for services.claims module
Tests claims submission with mocked auth layer
"""
from typing import Dict
from unittest.mock import patch

import pytest  # type: ignore[import-not-found]

from services.claims import ClaimsService


class MockResponse:
    """Mock HTTP response"""

    def __init__(self, json_data: Dict, status_code: int = 200):
        self._json_data = json_data
        self.status_code = status_code
        self.text = str(json_data)

    def json(self) -> Dict:
        return self._json_data


@pytest.fixture
def valid_claim_response():
    """Valid NPHIES claim submission response"""
    return {
        "resourceType": "Bundle",
        "id": "bundle-claim-response-123",
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
                    "id": "claimresp-1",
                    "status": "active",
                    "outcome": "complete",
                    "disposition": "Claim processed successfully",
                    "payment": {
                        "amount": {"value": 500.0, "currency": "SAR"},
                        "date": "2025-10-23",
                    },
                    "item": [
                        {
                            "itemSequence": 1,
                            "adjudication": [
                                {
                                    "category": {
                                        "coding": [{"code": "benefit"}]
                                    },
                                    "amount": {
                                        "value": 500.0,
                                        "currency": "SAR",
                                    },
                                }
                            ],
                        }
                    ],
                }
            },
        ],
    }


@pytest.fixture
def error_claim_response():
    """Error NPHIES claim response"""
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
                            "details": {"text": "Invalid claim data"},
                        }
                    ],
                }
            }
        ],
    }


@pytest.fixture
def sample_services():
    """Sample service items for claim"""
    return [
        {
            "code": "99213",
            "description": "Office visit",
            "quantity": 1,
            "unit_price": 300.0,
            "net_amount": 300.0,
        },
        {
            "code": "80053",
            "description": "Lab work",
            "quantity": 1,
            "unit_price": 200.0,
            "net_amount": 200.0,
        },
    ]


class TestSubmitClaim:
    """Test submit_claim method"""

    @patch("services.claims.auth_manager")
    def test_submit_claim_success(
        self, mock_auth, valid_claim_response, sample_services
    ):
        mock_auth.post.return_value = MockResponse(valid_claim_response)
        service = ClaimsService()

        result = service.submit_claim(
            claim_type="professional",
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            services=sample_services,
            total_amount=500.0,
        )

        assert result["success"] is True
        assert "claim_id" in result
        assert result["patient_id"] == "patient-123"
        assert "claim_response" in result
        assert mock_auth.post.called

    @patch("services.claims.auth_manager")
    def test_submit_claim_with_patient_name(
        self, mock_auth, valid_claim_response, sample_services
    ):
        mock_auth.post.return_value = MockResponse(valid_claim_response)
        service = ClaimsService()

        result = service.submit_claim(
            claim_type="institutional",
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            services=sample_services,
            total_amount=500.0,
            patient_name="Ahmed Al-Saud",
        )

        assert result["success"] is True
        call_args = mock_auth.post.call_args
        bundle = call_args[0][1]
        assert bundle["resourceType"] == "Bundle"

    @patch("services.claims.auth_manager")
    def test_submit_claim_defaults_claim_date(
        self, mock_auth, valid_claim_response, sample_services
    ):
        mock_auth.post.return_value = MockResponse(valid_claim_response)
        service = ClaimsService()

        result = service.submit_claim(
            claim_type="pharmacy",
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            services=sample_services,
            total_amount=500.0,
        )

        assert result["success"] is True
        call_args = mock_auth.post.call_args
        bundle = call_args[0][1]
        assert "entry" in bundle

    @patch("services.claims.auth_manager")
    def test_submit_claim_with_custom_date(
        self, mock_auth, valid_claim_response, sample_services
    ):
        mock_auth.post.return_value = MockResponse(valid_claim_response)
        service = ClaimsService()

        result = service.submit_claim(
            claim_type="professional",
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            services=sample_services,
            total_amount=500.0,
            claim_date="2025-10-15",
        )

        assert result["success"] is True
        assert "claim_id" in result

    @patch("services.claims.auth_manager")
    def test_submit_claim_error_response(
        self, mock_auth, error_claim_response, sample_services
    ):
        mock_auth.post.return_value = MockResponse(error_claim_response)
        service = ClaimsService()

        result = service.submit_claim(
            claim_type="professional",
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            services=sample_services,
            total_amount=500.0,
        )

        assert result["success"] is False
        assert len(result["errors"]) > 0

    @patch("services.claims.auth_manager")
    def test_submit_claim_handles_exception(
        self, mock_auth, sample_services
    ):
        mock_auth.post.side_effect = Exception("Network error")
        service = ClaimsService()

        result = service.submit_claim(
            claim_type="professional",
            patient_id="patient-123",
            member_id="1234567890",
            payer_id="7000911508",
            services=sample_services,
            total_amount=500.0,
        )

        assert result["success"] is False
        assert "error" in result
        assert "Network error" in result["error"]


class TestBuildClaimBundle:
    """Test _build_claim_bundle method"""

    @patch("services.claims.auth_manager")
    def test_build_claim_bundle_structure(
        self, mock_auth, sample_services
    ):
        service = ClaimsService()

        bundle = service._build_claim_bundle(
            claim_id="claim-123",
            claim_type="professional",
            patient_id="patient-123",
            member_id="1234567890",
            coverage_id="cov-123",
            payer_id="7000911508",
            services=sample_services,
            total_amount=500.0,
            claim_date="2025-10-22",
        )

        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "message"
        assert len(bundle["entry"]) > 0

        first_resource = bundle["entry"][0]["resource"]
        assert first_resource["resourceType"] == "MessageHeader"

    @patch("services.claims.auth_manager")
    def test_build_claim_bundle_with_patient_name(
        self, mock_auth, sample_services
    ):
        service = ClaimsService()

        bundle = service._build_claim_bundle(
            claim_id="claim-123",
            claim_type="institutional",
            patient_id="patient-123",
            member_id="1234567890",
            coverage_id="cov-123",
            payer_id="7000911508",
            services=sample_services,
            total_amount=500.0,
            claim_date="2025-10-22",
            patient_name="Test Patient",
        )

        assert bundle["resourceType"] == "Bundle"
        patient_entries = [
            e
            for e in bundle["entry"]
            if e["resource"].get("resourceType") == "Patient"
        ]
        assert len(patient_entries) > 0


class TestExtractClaimResponse:
    """Test _extract_claim_response method"""

    @patch("services.claims.auth_manager")
    def test_extract_claim_response_complete(self, mock_auth):
        service = ClaimsService()

        resources = [
            {
                "resourceType": "ClaimResponse",
                "status": "active",
                "outcome": "complete",
                "disposition": "Approved",
                "payment": {
                    "amount": {"value": 500.0, "currency": "SAR"},
                    "date": "2025-10-23",
                },
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

        response = service._extract_claim_response(resources)

        assert response["status"] == "active"
        assert response["outcome"] == "complete"
        assert abs(response["total_approved"] - 500.0) < 0.01
        assert len(response["items"]) == 1

    @patch("services.claims.auth_manager")
    def test_extract_claim_response_no_payment(self, mock_auth):
        service = ClaimsService()

        resources = [
            {
                "resourceType": "ClaimResponse",
                "status": "active",
                "outcome": "error",
                "disposition": "Denied",
            }
        ]

        response = service._extract_claim_response(resources)

        assert response["status"] == "active"
        assert abs(response["total_approved"]) < 0.01

    @patch("services.claims.auth_manager")
    def test_extract_claim_response_no_claim_response(self, mock_auth):
        service = ClaimsService()

        resources = [{"resourceType": "MessageHeader"}]
        response = service._extract_claim_response(resources)

        assert response["status"] == "unknown"


class TestQueryClaimStatus:
    """Test query_claim_status method"""

    @patch("services.claims.auth_manager")
    def test_query_claim_status(self, mock_auth):
        service = ClaimsService()

        result = service.query_claim_status(
            claim_id="claim-123", patient_id="patient-123"
        )

        assert result["success"] is True
        assert result["claim_id"] == "claim-123"

    @patch("services.claims.auth_manager")
    def test_query_claim_status_returns_stub_response(self, mock_auth):
        """Test that query_claim_status returns stub implementation"""
        service = ClaimsService()

        result = service.query_claim_status(
            claim_id="claim-123", patient_id="patient-123"
        )

        # Current implementation is a stub that returns success
        assert result["success"] is True
        assert result["claim_id"] == "claim-123"
        assert "message" in result
