"""
NPHIES Integration Tests
Validates FHIR conformance and integration workflows
"""

import pytest
import json
from pathlib import Path
from nphies_sim.client import NPHIESClient
from datetime import datetime


@pytest.fixture
def nphies_client():
    """Initialize NPHIES client for sandbox"""
    return NPHIESClient(use_sandbox=True)


@pytest.fixture
def sample_patient():
    """Sample patient data"""
    return {
        'member_id': 'TEST-MB-001',
        'national_id': '1234567890',
        'given_name': 'Ahmed',
        'family_name': 'Al-Rashid',
        'gender': 'male',
        'birth_date': '1990-01-15',
        'policy_number': 'POL-2025-001'
    }


@pytest.fixture
def sample_claim():
    """Sample claim data"""
    return {
        'claim_id': 'CLM-TEST-001',
        'type': 'professional',
        'priority': 'normal',
        'patient': {
            'member_id': 'TEST-MB-001',
            'national_id': '1234567890',
            'given_name': 'Ahmed',
            'family_name': 'Al-Rashid',
            'gender': 'male',
            'birth_date': '1990-01-15'
        },
        'services': [
            {
                'code': 'CONS-001',
                'description': 'General consultation',
                'date': '2025-11-06',
                'quantity': 1,
                'unit_price': 200.00,
                'total': 200.00
            },
            {
                'code': 'LAB-CBC',
                'description': 'Complete blood count',
                'date': '2025-11-06',
                'quantity': 1,
                'unit_price': 150.00,
                'total': 150.00
            }
        ],
        'total_amount': 350.00
    }


class TestFHIRResourceBuilding:
    """Test FHIR resource creation"""
    
    def test_build_patient_resource(self, nphies_client, sample_patient):
        """Test Patient resource building"""
        patient = nphies_client.build_patient_resource(sample_patient)
        
        assert patient['resourceType'] == 'Patient'
        assert patient['id'] == f"patient-{sample_patient['member_id']}"
        assert len(patient['identifier']) == 2
        assert patient['gender'] == 'male'
        assert patient['birthDate'] == '1990-01-15'
    
    def test_build_coverage_resource(self, nphies_client):
        """Test Coverage resource building"""
        coverage = nphies_client.build_coverage_resource(
            patient_id='patient-TEST-MB-001',
            payer_code='7001071327',  # Bupa
            member_id='TEST-MB-001',
            policy_number='POL-2025-001'
        )
        
        assert coverage['resourceType'] == 'Coverage'
        assert coverage['status'] == 'active'
        assert coverage['beneficiary']['reference'] == 'Patient/patient-TEST-MB-001'
    
    def test_build_eligibility_request(self, nphies_client, sample_patient):
        """Test EligibilityRequest bundle building"""
        bundle = nphies_client.build_eligibility_request(
            patient_data=sample_patient,
            payer_code='7001071327',
            correlation_id='test-correlation-001'
        )
        
        assert bundle['resourceType'] == 'Bundle'
        assert bundle['type'] == 'collection'
        assert len(bundle['entry']) == 3
        
        # Verify EligibilityRequest
        eligibility_req = bundle['entry'][0]['resource']
        assert eligibility_req['resourceType'] == 'CoverageEligibilityRequest'
        assert eligibility_req['status'] == 'active'
        assert 'benefits' in eligibility_req['purpose']
    
    def test_build_claim_bundle(self, nphies_client, sample_claim):
        """Test Claim bundle building"""
        bundle = nphies_client.build_claim_bundle(
            claim_data=sample_claim,
            payer_code='7001071327',
            correlation_id='test-correlation-002'
        )
        
        assert bundle['resourceType'] == 'Bundle'
        assert bundle['type'] == 'collection'
        assert len(bundle['entry']) == 3
        
        # Verify Claim
        claim = bundle['entry'][0]['resource']
        assert claim['resourceType'] == 'Claim'
        assert claim['status'] == 'active'
        assert len(claim['item']) == 2
        assert claim['total']['value'] == 350.00
        assert claim['total']['currency'] == 'SAR'


class TestFHIRValidation:
    """Test FHIR profile conformance"""
    
    def test_eligibility_request_profile(self, nphies_client, sample_patient):
        """Validate EligibilityRequest against NPHIES profile"""
        bundle = nphies_client.build_eligibility_request(
            patient_data=sample_patient,
            payer_code='7001071327'
        )
        
        eligibility_req = bundle['entry'][0]['resource']
        profile_url = 'http://nphies.sa/fhir/ksa/nphies-fs/StructureDefinition/eligibility-request'
        
        assert profile_url in eligibility_req['meta']['profile']
    
    def test_claim_profile(self, nphies_client, sample_claim):
        """Validate Claim against NPHIES profile"""
        bundle = nphies_client.build_claim_bundle(
            claim_data=sample_claim,
            payer_code='7001071327'
        )
        
        claim = bundle['entry'][0]['resource']
        profile_url = 'http://nphies.sa/fhir/ksa/nphies-fs/StructureDefinition/claim'
        
        assert profile_url in claim['meta']['profile']
    
    def test_required_fields_eligibility(self, nphies_client, sample_patient):
        """Ensure all required fields present in EligibilityRequest"""
        bundle = nphies_client.build_eligibility_request(
            patient_data=sample_patient,
            payer_code='7001071327'
        )
        
        eligibility_req = bundle['entry'][0]['resource']
        
        required_fields = [
            'identifier', 'status', 'purpose', 'patient',
            'created', 'provider', 'insurer', 'insurance'
        ]
        
        for field in required_fields:
            assert field in eligibility_req, f"Missing required field: {field}"
    
    def test_required_fields_claim(self, nphies_client, sample_claim):
        """Ensure all required fields present in Claim"""
        bundle = nphies_client.build_claim_bundle(
            claim_data=sample_claim,
            payer_code='7001071327'
        )
        
        claim = bundle['entry'][0]['resource']
        
        required_fields = [
            'identifier', 'status', 'type', 'use', 'patient',
            'created', 'provider', 'priority', 'insurance', 'item', 'total'
        ]
        
        for field in required_fields:
            assert field in claim, f"Missing required field: {field}"


class TestSecurityIntegration:
    """Test security components"""
    
    def test_jwt_generation(self, nphies_client):
        """Test JWT token generation"""
        token = nphies_client._generate_jwt()
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # header.payload.signature
    
    def test_mtls_certificate_loading(self, nphies_client):
        """Test mTLS certificate loading"""
        assert nphies_client.cert_path.exists()
        assert nphies_client.key_path.exists()
        assert nphies_client.ca_path.exists()


class TestIdempotency:
    """Test idempotent request handling"""
    
    def test_same_request_generates_same_identifier(self, nphies_client, sample_patient):
        """Ensure same data produces same identifier"""
        correlation_id = 'test-idem-001'
        
        bundle1 = nphies_client.build_eligibility_request(
            patient_data=sample_patient,
            payer_code='7001071327',
            correlation_id=correlation_id
        )
        
        bundle2 = nphies_client.build_eligibility_request(
            patient_data=sample_patient,
            payer_code='7001071327',
            correlation_id=correlation_id
        )
        
        id1 = bundle1['entry'][0]['resource']['identifier'][0]['value']
        id2 = bundle2['entry'][0]['resource']['identifier'][0]['value']
        
        assert id1 == id2


class TestErrorHandling:
    """Test error scenarios"""
    
    def test_missing_required_patient_data(self, nphies_client):
        """Test handling of incomplete patient data"""
        incomplete_patient = {
            'member_id': 'TEST-MB-001'
            # Missing other required fields
        }
        
        # Should still build resource with empty strings
        patient = nphies_client.build_patient_resource(incomplete_patient)
        assert patient['resourceType'] == 'Patient'
    
    def test_invalid_payer_code_format(self, nphies_client, sample_patient):
        """Test handling of invalid payer code"""
        # Should still build request (validation happens on NPHIES side)
        bundle = nphies_client.build_eligibility_request(
            patient_data=sample_patient,
            payer_code='INVALID'
        )
        
        assert bundle['resourceType'] == 'Bundle'


@pytest.mark.integration
class TestNPHIESSandbox:
    """Integration tests against NPHIES sandbox (requires credentials)"""
    
    @pytest.mark.skip(reason="Requires NPHIES sandbox credentials")
    def test_submit_eligibility_request_sandbox(self, nphies_client, sample_patient):
        """Test actual eligibility submission to sandbox"""
        bundle = nphies_client.build_eligibility_request(
            patient_data=sample_patient,
            payer_code='7001071327'
        )
        
        response = nphies_client.submit_eligibility_request(bundle)
        
        assert response is not None
        assert 'resourceType' in response
    
    @pytest.mark.skip(reason="Requires NPHIES sandbox credentials")
    def test_submit_claim_sandbox(self, nphies_client, sample_claim):
        """Test actual claim submission to sandbox"""
        bundle = nphies_client.build_claim_bundle(
            claim_data=sample_claim,
            payer_code='7001071327'
        )
        
        response = nphies_client.submit_claim(bundle)
        
        assert response is not None
        assert 'resourceType' in response


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
