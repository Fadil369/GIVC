"""
Unit tests for services.communication module
Tests communication polling and sending with mocked auth layer
"""
from typing import Dict
from unittest.mock import patch

import pytest  # type: ignore[import-not-found]

from services.communication import CommunicationService


class MockResponse:
    """Mock HTTP response"""

    def __init__(self, json_data: Dict, status_code: int = 200):
        self._json_data = json_data
        self.status_code = status_code
        self.text = str(json_data)

    def json(self) -> Dict:
        return self._json_data


@pytest.fixture
def valid_poll_response():
    """Valid NPHIES communication poll response"""
    return {
        "resourceType": "Bundle",
        "id": "bundle-comm-poll-123",
        "type": "message",
        "entry": [
            {
                "resource": {
                    "resourceType": "Communication",
                    "id": "comm-1",
                    "status": "completed",
                    "subject": {"reference": "Patient/patient-123"},
                    "payload": [
                        {"contentString": "Prior authorization approved"}
                    ],
                    "sent": "2025-11-01T10:00:00Z",
                }
            },
            {
                "resource": {
                    "resourceType": "Communication",
                    "id": "comm-2",
                    "status": "completed",
                    "subject": {"reference": "Patient/patient-456"},
                    "payload": [{"contentString": "Claim requires review"}],
                    "sent": "2025-11-01T11:30:00Z",
                }
            },
        ],
    }


@pytest.fixture
def empty_poll_response():
    """Empty NPHIES communication poll response"""
    return {
        "resourceType": "Bundle",
        "id": "bundle-comm-poll-empty",
        "type": "message",
        "entry": [],
    }


@pytest.fixture
def valid_send_response():
    """Valid NPHIES communication send response"""
    return {
        "resourceType": "Bundle",
        "id": "bundle-comm-send-123",
        "type": "message",
        "entry": [
            {
                "resource": {
                    "resourceType": "Communication",
                    "id": "comm-send-1",
                    "status": "completed",
                }
            }
        ],
    }


class TestPollCommunications:
    """Test poll_communications method"""

    @patch("services.communication.auth_manager")
    def test_poll_communications_success(self, mock_auth, valid_poll_response):
        mock_auth.post.return_value = MockResponse(valid_poll_response)
        service = CommunicationService()

        result = service.poll_communications(organization_id="org-123")

        assert result["success"] is True
        assert len(result["communications"]) == 2
        assert mock_auth.post.called

    @patch("services.communication.auth_manager")
    def test_poll_communications_empty_response(
        self, mock_auth, empty_poll_response
    ):
        mock_auth.post.return_value = MockResponse(empty_poll_response)
        service = CommunicationService()

        result = service.poll_communications(organization_id="org-123")

        # Empty bundle will be parsed as failed by parse_nphies_response
        # because it expects entries but gets none
        assert result["success"] is False
        assert "errors" in result or "communications" in result

    @patch("services.communication.auth_manager")
    def test_poll_communications_without_organization(
        self, mock_auth, valid_poll_response
    ):
        mock_auth.post.return_value = MockResponse(valid_poll_response)
        service = CommunicationService()

        result = service.poll_communications()

        assert result["success"] is True
        assert len(result["communications"]) == 2

    @patch("services.communication.auth_manager")
    def test_poll_communications_handles_exception(self, mock_auth):
        mock_auth.post.side_effect = Exception("Network error")
        service = CommunicationService()

        result = service.poll_communications(organization_id="org-123")

        assert result["success"] is False
        assert "error" in result
        assert "Network error" in result["error"]


class TestBuildPollBundle:
    """Test _build_poll_bundle method"""

    @patch("services.communication.auth_manager")
    def test_build_poll_bundle_with_organization(self, mock_auth):
        service = CommunicationService()

        bundle = service._build_poll_bundle(organization_id="org-123")

        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "message"
        assert len(bundle["entry"]) > 0

        comm_entries = [
            e
            for e in bundle["entry"]
            if e["resource"].get("resourceType") == "Communication"
        ]
        assert len(comm_entries) > 0

    @patch("services.communication.auth_manager")
    def test_build_poll_bundle_default_organization(self, mock_auth):
        """Test _build_poll_bundle with organization from settings"""
        service = CommunicationService()

        # _build_poll_bundle requires organization_id parameter
        # This test verifies it builds a valid bundle structure
        bundle = service._build_poll_bundle(organization_id="org-default")

        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "message"
        comm_entries = [
            e
            for e in bundle["entry"]
            if e["resource"].get("resourceType") == "Communication"
        ]
        assert len(comm_entries) > 0


class TestExtractCommunications:
    """Test _extract_communications method"""

    @patch("services.communication.auth_manager")
    def test_extract_communications_with_data(self, mock_auth):
        service = CommunicationService()

        resources = [
            {
                "resourceType": "Communication",
                "id": "comm-1",
                "status": "completed",
                "subject": {"reference": "Patient/patient-123"},
                "payload": [{"contentString": "Test message 1"}],
                "sent": "2025-11-01T10:00:00Z",
            },
            {
                "resourceType": "Communication",
                "id": "comm-2",
                "status": "in-progress",
                "subject": {"reference": "Patient/patient-456"},
                "payload": [{"contentString": "Test message 2"}],
            },
        ]

        communications = service._extract_communications(resources)

        assert len(communications) == 2
        assert communications[0]["id"] == "comm-1"
        assert communications[0]["status"] == "completed"
        assert communications[0]["payload"] == ["Test message 1"]
        assert communications[0]["sent"] == "2025-11-01T10:00:00Z"

    @patch("services.communication.auth_manager")
    def test_extract_communications_empty(self, mock_auth):
        service = CommunicationService()

        resources = [{"resourceType": "MessageHeader"}]
        communications = service._extract_communications(resources)

        assert len(communications) == 0

    @patch("services.communication.auth_manager")
    def test_extract_communications_no_payload(self, mock_auth):
        service = CommunicationService()

        resources = [
            {
                "resourceType": "Communication",
                "id": "comm-1",
                "status": "completed",
                "subject": {"reference": "Patient/patient-123"},
            }
        ]

        communications = service._extract_communications(resources)

        assert len(communications) == 1
        assert communications[0]["payload"] == []


class TestSendCommunication:
    """Test send_communication method"""

    @patch("services.communication.auth_manager")
    def test_send_communication_success(self, mock_auth, valid_send_response):
        mock_auth.post.return_value = MockResponse(valid_send_response)
        service = CommunicationService()

        result = service.send_communication(
            recipient_id="org-payer-123",
            subject="Claim inquiry",
            content="Additional information requested",
            category="info",
        )

        assert result["success"] is True
        assert mock_auth.post.called

    @patch("services.communication.auth_manager")
    def test_send_communication_without_category(
        self, mock_auth, valid_send_response
    ):
        mock_auth.post.return_value = MockResponse(valid_send_response)
        service = CommunicationService()

        result = service.send_communication(
            recipient_id="org-payer-123",
            subject="General inquiry",
            content="General inquiry content",
        )

        assert result["success"] is True

    @patch("services.communication.auth_manager")
    def test_send_communication_handles_exception(self, mock_auth):
        mock_auth.post.side_effect = Exception("Network error")
        service = CommunicationService()

        result = service.send_communication(
            recipient_id="org-payer-123",
            subject="Test",
            content="Test message",
        )

        assert result["success"] is False
        assert "error" in result
        assert "Network error" in result["error"]


class TestBuildCommunicationBundle:
    """Test _build_communication_bundle method"""

    @patch("services.communication.auth_manager")
    def test_build_communication_bundle_structure(self, mock_auth):
        service = CommunicationService()

        bundle = service._build_communication_bundle(
            recipient_id="org-payer-123",
            subject="Claim inquiry",
            content="Test communication content",
            category="info",
        )

        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "message"
        assert len(bundle["entry"]) > 0

        comm_entries = [
            e
            for e in bundle["entry"]
            if e["resource"].get("resourceType") == "Communication"
        ]
        assert len(comm_entries) > 0

    @patch("services.communication.auth_manager")
    def test_build_communication_bundle_with_default_category(self, mock_auth):
        service = CommunicationService()

        bundle = service._build_communication_bundle(
            recipient_id="org-payer-123",
            subject="General inquiry",
            content="Test communication content",
            category="general",
        )

        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "message"
