from datetime import date, datetime

import pytest  # type: ignore[import-not-found]

from utils.validators import NPHIESValidator, ValidationError, validate_request


class TestMemberIDValidation:
    """Test member ID validation"""
    
    def test_validate_member_id_valid(self):
        valid, message = NPHIESValidator.validate_member_id("123456")
        assert valid is True
        assert message == ""
    
    def test_validate_member_id_empty(self):
        invalid, message = NPHIESValidator.validate_member_id("")
        assert invalid is False
        assert "required" in message
    
    def test_validate_member_id_too_short(self):
        invalid, message = NPHIESValidator.validate_member_id("123")
        assert invalid is False
        assert "too short" in message
    
    def test_validate_member_id_too_long(self):
        invalid, message = NPHIESValidator.validate_member_id("a" * 51)
        assert invalid is False
        assert "too long" in message
    
    def test_validate_member_id_non_string(self):
        invalid, message = NPHIESValidator.validate_member_id(12345)
        assert invalid is False
        assert "string" in message
    
    def test_validate_member_id_with_spaces(self):
        valid, message = NPHIESValidator.validate_member_id("  12345  ")
        assert valid is True


class TestPayerIDValidation:
    """Test payer ID validation"""
    
    def test_validate_payer_id_valid(self):
        valid, message = NPHIESValidator.validate_payer_id("1234567890")
        assert valid is True
        assert message == ""
    
    def test_validate_payer_id_non_digits(self):
        invalid, message = NPHIESValidator.validate_payer_id("ABCDEFGHIJ")
        assert invalid is False
        assert "digits" in message
    
    def test_validate_payer_id_wrong_length(self):
        invalid, message = NPHIESValidator.validate_payer_id("12345")
        assert invalid is False
        assert "10 digits" in message
    
    def test_validate_payer_id_empty(self):
        invalid, message = NPHIESValidator.validate_payer_id("")
        assert invalid is False
        assert "required" in message
    
    def test_validate_payer_id_non_string(self):
        """Test line 60 - payer_id must be string"""
        invalid, message = NPHIESValidator.validate_payer_id(1234567890)
        assert invalid is False
        assert "string" in message


class TestDateValidation:
    """Test date validation"""
    
    def test_validate_date_string_valid(self):
        valid, message = NPHIESValidator.validate_date("2025-10-22")
        assert valid is True
        assert message == ""
    
    def test_validate_date_object_valid(self):
        valid, message = NPHIESValidator.validate_date(date(2025, 10, 22))
        assert valid is True
        assert message == ""
    
    def test_validate_date_datetime_valid(self):
        valid, message = NPHIESValidator.validate_date(datetime(2025, 10, 22))
        assert valid is True
        assert message == ""
    
    def test_validate_date_invalid_format(self):
        invalid, message = NPHIESValidator.validate_date("invalid")
        assert invalid is False
        assert "format" in message
    
    def test_validate_date_empty(self):
        invalid, message = NPHIESValidator.validate_date("")
        assert invalid is False
        assert "required" in message
    
    def test_validate_date_non_string_non_date(self):
        """Test line 90 - date must be string or date object"""
        invalid, message = NPHIESValidator.validate_date(12345)
        assert invalid is False
        assert "string or date object" in message


class TestPatientDataValidation:
    """Test patient data validation"""
    
    def test_validate_patient_data_complete(self):
        patient_errors = NPHIESValidator.validate_patient_data(
            {
                "id": "patient-1",
                "identifier": [{"value": "12345"}],
                "name": "John Doe",
                "birthDate": "2025-10-22",
                "gender": "male",
            }
        )
        assert patient_errors == []
    
    def test_validate_patient_data_missing_id(self):
        patient_errors = NPHIESValidator.validate_patient_data({})
        assert "Patient ID is required" in patient_errors
    
    def test_validate_patient_data_missing_identifier(self):
        patient_errors = NPHIESValidator.validate_patient_data({"id": "p1"})
        assert any("identifier" in err for err in patient_errors)
    
    def test_validate_patient_data_invalid_gender(self):
        patient_errors = NPHIESValidator.validate_patient_data({
            "id": "p1",
            "identifier": [{"value": "123"}],
            "name": "Test",
            "gender": "invalid"
        })
        assert "Invalid gender value" in patient_errors
    
    def test_validate_patient_data_invalid_birthdate(self):
        """Test line 130 - invalid birthDate format"""
        patient_errors = NPHIESValidator.validate_patient_data({
            "id": "p1",
            "identifier": [{"value": "123"}],
            "birthDate": "not-a-date"
        })
        assert any("birth date" in err.lower() for err in patient_errors)


class TestCoverageDataValidation:
    """Test coverage data validation"""
    
    def test_validate_coverage_data_complete(self):
        coverage_errors = NPHIESValidator.validate_coverage_data(
            {
                "id": "coverage-1",
                "beneficiary": {"reference": "Patient/patient-1"},
                "payor": [{"reference": "Organization/123"}],
                "class": [
                    {
                        "type": {"coding": [{"code": "plan"}]},
                        "value": "gold",
                    }
                ],
            }
        )
        assert coverage_errors == []
    
    def test_validate_coverage_data_missing_fields(self):
        coverage_errors = NPHIESValidator.validate_coverage_data({})
        assert "Coverage ID is required" in coverage_errors
        assert "Coverage beneficiary is required" in coverage_errors
        assert "Coverage payor is required" in coverage_errors


class TestClaimDataValidation:
    """Test claim data validation"""
    
    def test_validate_claim_data_complete(self):
        claim_errors = NPHIESValidator.validate_claim_data({
            "id": "claim-1",
            "type": {"coding": [{"code": "professional"}]},
            "patient": {"reference": "Patient/p1"},
            "provider": {"reference": "Organization/o1"},
            "insurer": {"reference": "Organization/ins1"},
            "item": [
                {
                    "sequence": 1,
                    "productOrService": {"coding": [{"code": "service1"}]}
                }
            ]
        })
        assert claim_errors == []
    
    def test_validate_claim_data_missing_items(self):
        claim_errors = NPHIESValidator.validate_claim_data({
            "id": "claim-1",
            "type": {"coding": [{"code": "professional"}]},
            "patient": {"reference": "Patient/p1"},
            "provider": {"reference": "Organization/o1"},
            "insurer": {"reference": "Organization/ins1"}
        })
        assert "at least one item" in " ".join(claim_errors)
    
    def test_validate_claim_data_item_missing_sequence(self):
        """Test line 200 - item missing sequence"""
        claim_errors = NPHIESValidator.validate_claim_data({
            "id": "claim-1",
            "type": {"coding": [{"code": "professional"}]},
            "patient": {"reference": "Patient/p1"},
            "provider": {"reference": "Organization/o1"},
            "insurer": {"reference": "Organization/ins1"},
            "item": [{"productOrService": {"coding": [{"code": "s1"}]}}]
        })
        assert any("sequence" in err for err in claim_errors)
    
    def test_validate_claim_data_item_missing_product_or_service(self):
        """Test line 203 - item missing productOrService"""
        claim_errors = NPHIESValidator.validate_claim_data({
            "id": "claim-1",
            "type": {"coding": [{"code": "professional"}]},
            "patient": {"reference": "Patient/p1"},
            "provider": {"reference": "Organization/o1"},
            "insurer": {"reference": "Organization/ins1"},
            "item": [{"sequence": 1}]
        })
        assert any("product/service" in err.lower() for err in claim_errors)


class TestBundleValidation:
    """Test bundle validation"""
    
    def test_validate_bundle_message_type(self):
        bundle_errors = NPHIESValidator.validate_bundle({
            "resourceType": "Bundle",
            "type": "message",
            "entry": [
                {"resource": {"resourceType": "MessageHeader"}}
            ]
        })
        assert bundle_errors == []
    
    def test_validate_bundle_wrong_resource_type(self):
        bundle_errors = NPHIESValidator.validate_bundle({
            "resourceType": "Observation"
        })
        assert "must be 'Bundle'" in " ".join(bundle_errors)
    
    def test_validate_bundle_invalid_type(self):
        bundle_errors = NPHIESValidator.validate_bundle({
            "resourceType": "Bundle",
            "type": "invalid_type",
            "entry": []
        })
        assert "Invalid bundle type" in bundle_errors
    
    def test_validate_bundle_message_type_wrong_first_resource(self):
        """Test line 236 - message bundle first entry must be MessageHeader"""
        bundle_errors = NPHIESValidator.validate_bundle({
            "resourceType": "Bundle",
            "type": "message",
            "entry": [
                {"resource": {"resourceType": "Patient"}}
            ]
        })
        assert "MessageHeader" in " ".join(bundle_errors)


class TestRequestValidation:
    """Test validate_request function"""
    
    def test_validate_request_raises_on_error(self):
        with pytest.raises(ValidationError) as exc:
            validate_request("bundle", {"resourceType": "Observation"})
        assert "Bundle" in str(exc.value)
    
    def test_validate_request_passes_for_valid_bundle(self):
        bundle = {
            "resourceType": "Bundle",
            "type": "message",
            "entry": [
                {"resource": {"resourceType": "MessageHeader"}}
            ],
        }
        validate_request("bundle", bundle)
    
    def test_validate_request_eligibility_type(self):
        with pytest.raises(ValidationError):
            validate_request("eligibility", {"patient": {}, "coverage": {}})
    
    def test_validate_request_claim_type(self):
        with pytest.raises(ValidationError):
            validate_request("claim", {})
