import uuid
from datetime import date, datetime
from typing import cast

import pytest  # type: ignore[import-not-found]

from utils import helpers


def test_generate_message_id(monkeypatch):
    fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
    monkeypatch.setattr("utils.helpers.uuid.uuid4", lambda: fixed_uuid)

    message_id = helpers.generate_message_id()

    assert message_id == str(fixed_uuid)
    assert uuid.UUID(message_id)


def test_generate_bundle_and_request_ids(monkeypatch):
    fixed_uuid = uuid.UUID("87654321-4321-6789-4321-678987654321")
    monkeypatch.setattr("utils.helpers.uuid.uuid4", lambda: fixed_uuid)

    bundle_id = helpers.generate_bundle_id()
    request_id = helpers.generate_request_id()

    assert bundle_id == f"bundle-{fixed_uuid}"
    assert request_id == f"req-{fixed_uuid}"


def test_format_date_accepts_string_and_date():
    today = date(2025, 10, 22)

    assert helpers.format_date(today) == "2025-10-22"
    formatted = helpers.format_date(cast(date, "2025-10-22"))
    assert formatted == "2025-10-22"


def test_format_datetime_accepts_string_and_datetime():
    timestamp = datetime(2025, 10, 22, 12, 30, 15)

    assert helpers.format_datetime(timestamp) == "2025-10-22T12:30:15"
    formatted = helpers.format_datetime(cast(datetime, "2025-10-22T12:30:15"))
    assert formatted == "2025-10-22T12:30:15"


def test_parse_nphies_date_handles_invalid_values():
    parsed = helpers.parse_nphies_date("2025-10-22T12:30:15Z")
    assert parsed == date(2025, 10, 22)

    assert helpers.parse_nphies_date("not-a-date") is None
    assert helpers.parse_nphies_date(cast(str, None)) is None


def test_safe_get_returns_nested_value_and_default():
    data = {"level1": {"level2": {"value": 42}}}

    assert helpers.safe_get(data, "level1", "level2", "value") == 42
    assert helpers.safe_get(data, "missing", default="fallback") == "fallback"


def test_mask_sensitive_data_handles_short_and_long_values():
    assert helpers.mask_sensitive_data("1234") == "***"
    masked = helpers.mask_sensitive_data("123456789", visible_chars=3)
    assert masked == "******789"


def test_validation_helpers_for_identifiers():
    assert helpers.validate_saudi_id("1234567890") is True
    assert helpers.validate_saudi_id("abc") is False

    assert helpers.validate_iqama("1234567890") is True
    assert helpers.validate_iqama("2234567890") is True
    assert helpers.validate_iqama("323456789") is False


def test_calculate_hash_produces_expected_digest():
    digest = helpers.calculate_hash("test-data")
    # Verify it produces a valid SHA256 hash (64 hex chars)
    assert len(digest) == 64
    assert all(c in '0123456789abcdef' for c in digest)
    # Verify it's deterministic
    assert digest == helpers.calculate_hash("test-data")


def test_parse_nphies_response_successful_bundle():
    bundle = {
        "resourceType": "Bundle",
        "id": "bundle-123",
        "entry": [
            {
                "resource": {
                    "resourceType": "CoverageEligibilityResponse",
                    "outcome": "complete",
                    "insurance": [
                        {
                            "coverage": {"reference": "Coverage/cov-1"},
                            "item": [
                                {
                                    "category": {"text": "General"},
                                    "benefit": [
                                        {"type": {"text": "Coinsurance"}}
                                    ],
                                }
                            ],
                        }
                    ],
                }
            }
        ],
    }

    result = helpers.parse_nphies_response(bundle)

    assert result["success"] is True
    assert result["data"][0]["resourceType"] == "CoverageEligibilityResponse"
    assert result["bundle_id"] == "bundle-123"
    assert "timestamp" in result


def test_parse_nphies_response_with_operation_outcome():
    bundle = {
        "resourceType": "Bundle",
        "entry": [
            {
                "resource": {
                    "resourceType": "OperationOutcome",
                    "issue": [
                        {
                            "severity": "error",
                            "details": {"text": "Invalid request"},
                        }
                    ],
                }
            }
        ],
    }

    result = helpers.parse_nphies_response(bundle)

    assert result["success"] is False
    assert "Invalid request" in result["errors"][0]


@pytest.mark.parametrize(
    "value,expected",
    [
        ("1234567890", True),  # Valid 10-digit number
        ("", False),
        (None, False),
    ],
)
def test_validate_saudi_id_parametrized(value, expected):
    assert helpers.validate_saudi_id(value) is expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("1234567890", True),
        ("abcdefghij", False),
        ("0234567890", False),
    ],
)
def test_validate_iqama_parametrized(value, expected):
    assert helpers.validate_iqama(value) is expected


def test_get_current_timestamp_returns_iso_format():
    """Test get_current_timestamp returns valid ISO format"""
    timestamp = helpers.get_current_timestamp()
    
    # Should be parseable as datetime
    parsed = datetime.fromisoformat(timestamp)
    assert isinstance(parsed, datetime)


def test_pretty_json_formats_dict():
    """Test pretty_json formats dictionary correctly"""
    data = {"key": "value", "nested": {"item": 123}}
    
    formatted = helpers.pretty_json(data)
    
    assert '"key"' in formatted
    assert '"value"' in formatted
    assert "\n" in formatted  # Contains newlines
    
    # With custom indent
    formatted_4 = helpers.pretty_json(data, indent=4)
    assert "    " in formatted_4


def test_build_identifier_creates_fhir_identifier():
    """Test build_identifier creates valid FHIR identifier"""
    identifier = helpers.build_identifier(
        "http://nphies.sa/identifier/national-id",
        "1234567890"
    )
    
    assert identifier["system"] == "http://nphies.sa/identifier/national-id"
    assert identifier["value"] == "1234567890"


def test_build_reference_creates_fhir_reference():
    """Test build_reference creates valid FHIR reference"""
    reference = helpers.build_reference("Patient", "patient-123")
    
    assert reference["reference"] == "Patient/patient-123"


def test_build_coding_creates_fhir_coding():
    """Test build_coding creates valid FHIR coding"""
    # Without display
    coding = helpers.build_coding(
        "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "AMB"
    )
    
    assert coding["system"] == "http://terminology.hl7.org/CodeSystem/v3-ActCode"
    assert coding["code"] == "AMB"
    assert "display" not in coding
    
    # With display
    coding_with_display = helpers.build_coding(
        "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "AMB",
        "Ambulatory"
    )
    
    assert coding_with_display["display"] == "Ambulatory"


def test_parse_nphies_response_invalid_bundle_type():
    """Test parse_nphies_response handles non-Bundle resources"""
    response = {
        "resourceType": "Patient",
        "id": "patient-1"
    }
    
    result = helpers.parse_nphies_response(response)
    
    assert result["success"] is False
    assert "not a FHIR Bundle" in result["errors"][0]


def test_parse_nphies_response_handles_exceptions():
    """Test parse_nphies_response handles parsing exceptions"""
    # Invalid structure that might cause exceptions
    response = {"resourceType": "Bundle", "entry": "not-a-list"}
    
    result = helpers.parse_nphies_response(response)
    
    assert result["success"] is False
    assert len(result["errors"]) > 0


def test_parse_nphies_response_mixed_resources():
    """Test parse_nphies_response with both data and errors"""
    bundle = {
        "resourceType": "Bundle",
        "id": "bundle-mixed",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-1"
                }
            },
            {
                "resource": {
                    "resourceType": "OperationOutcome",
                    "issue": [
                        {
                            "severity": "warning",
                            "details": {"text": "Potential issue detected"}
                        }
                    ]
                }
            }
        ]
    }
    
    result = helpers.parse_nphies_response(bundle)
    
    assert result["success"] is False  # Has errors/warnings
    assert len(result["data"]) == 2
    assert "warning" in result["errors"][0].lower()
