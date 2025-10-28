"""
Test configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def sample_member_id():
    """Sample member ID for testing"""
    return "1234567890"

@pytest.fixture
def sample_payer_id():
    """Sample payer ID for testing"""
    return "7000911508"

@pytest.fixture
def sample_service_date():
    """Sample service date for testing"""
    return "2025-10-22"

@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing"""
    return {
        "name": "Test Patient",
        "gender": "male",
        "birthDate": "1985-05-15"
    }

@pytest.fixture
def mock_nphies_response_success():
    """Mock successful NPHIES API response"""
    return {
        "resourceType": "Bundle",
        "type": "message",
        "entry": [
            {
                "resource": {
                    "resourceType": "MessageHeader",
                    "eventUri": "http://nphies.sa/eligibility",
                    "response": {
                        "code": "ok"
                    }
                }
            }
        ]
    }

@pytest.fixture
def mock_nphies_response_error():
    """Mock error NPHIES API response"""
    return {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "invalid",
                "diagnostics": "Invalid request"
            }
        ]
    }

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("ENVIRONMENT", "sandbox")
    monkeypatch.setenv("NPHIES_LICENSE", "7000911508")
    monkeypatch.setenv("NPHIES_ORGANIZATION_ID", "10000000000988")
    monkeypatch.setenv("NPHIES_PROVIDER_ID", "7000911508")
