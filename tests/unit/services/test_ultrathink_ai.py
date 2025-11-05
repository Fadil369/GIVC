"""
Unit Tests for Ultrathink AI Service
=====================================
Comprehensive test suite for AI validation, prediction, and detection features.

Author: GIVC Platform Team
License: GPL-3.0
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import numpy as np

# Import the service we're testing
from services.ultrathink_ai import (
    UltrathinkAIService,
    ValidationResult,
    ValidationSeverity,
    SmartCompletionResult,
    ErrorPrediction,
    AnomalyDetection,
    ultrathink_ai
)

class TestUltrathinkAIValidation:
    """Test suite for claim validation functionality"""

    @pytest.fixture
    def sample_claim_data(self):
        """Sample claim data for testing"""
        return {
            "claim_id": "CLM-1234567890",
            "patient_id": "PAT-001",
            "provider_id": "PRV-001",
            "payer_id": "BUPA",
            "service_date": "2024-11-05",
            "diagnosis_codes": ["J06.9"],
            "procedure_codes": ["99213"],
            "total_amount": 500.00
        }

    @pytest.fixture
    def incomplete_claim_data(self):
        """Incomplete claim data for testing validation"""
        return {
            "patient_id": "PAT-001",
            "service_date": "2024-11-05",
            "total_amount": 500.00
            # Missing required fields
        }

    @pytest.mark.asyncio
    async def test_validate_claim_complete_data(self, sample_claim_data):
        """Test validation with complete, valid claim data"""
        results = await ultrathink_ai.validate_claim(sample_claim_data)
        
        # Should have some validation results (even if all pass)
        assert isinstance(results, list)
        
        # Check that we get reasonable validation results
        critical_errors = [r for r in results if r.severity == ValidationSeverity.CRITICAL and not r.is_valid]
        assert len(critical_errors) == 0, "Valid claim should not have critical errors"

    @pytest.mark.asyncio
    async def test_validate_claim_missing_required_fields(self, incomplete_claim_data):
        """Test validation with missing required fields"""
        results = await ultrathink_ai.validate_claim(incomplete_claim_data)
        
        # Should detect missing required fields
        missing_fields = [r for r in results if not r.is_valid and "missing" in r.message.lower()]
        assert len(missing_fields) > 0, "Should detect missing required fields"
        
        # Check specific missing fields
        missing_claim_id = any(r.field == "claim_id" for r in missing_fields)
        missing_provider_id = any(r.field == "provider_id" for r in missing_fields)
        assert missing_claim_id and missing_provider_id

    @pytest.mark.asyncio
    async def test_validate_claim_invalid_amount(self):
        """Test validation with invalid amounts"""
        claim_data = {
            "claim_id": "CLM-1234567890",
            "patient_id": "PAT-001",
            "provider_id": "PRV-001",
            "payer_id": "BUPA",
            "service_date": "2024-11-05",
            "diagnosis_codes": ["J06.9"],
            "procedure_codes": ["99213"],
            "total_amount": -100.00  # Invalid negative amount
        }
        
        results = await ultrathink_ai.validate_claim(claim_data)
        
        # Should detect invalid amount
        amount_errors = [r for r in results if r.field == "total_amount" and not r.is_valid]
        assert len(amount_errors) > 0, "Should detect negative amount"

    @pytest.mark.asyncio
    async def test_validate_claim_future_service_date(self):
        """Test validation with future service date"""
        future_date = (datetime.now() + timedelta(days=30)).date().isoformat()
        claim_data = {
            "claim_id": "CLM-1234567890",
            "patient_id": "PAT-001",
            "provider_id": "PRV-001",
            "payer_id": "BUPA",
            "service_date": future_date,  # Future date
            "diagnosis_codes": ["J06.9"],
            "procedure_codes": ["99213"],
            "total_amount": 500.00
        }
        
        results = await ultrathink_ai.validate_claim(claim_data)
        
        # Should detect future service date
        date_errors = [r for r in results if r.field == "service_date" and not r.is_valid]
        assert len(date_errors) > 0, "Should detect future service date"

    @pytest.mark.asyncio
    async def test_validate_claim_with_context(self, sample_claim_data):
        """Test validation with additional context"""
        context = {
            "patient_history": {"previous_claims": 5},
            "provider_data": {"license_status": "active"}
        }
        
        results = await ultrathink_ai.validate_claim(sample_claim_data, context)
        
        assert isinstance(results, list)
        # Context should not cause errors for valid data
        critical_errors = [r for r in results if r.severity == ValidationSeverity.CRITICAL]
        assert len(critical_errors) == 0

    @pytest.mark.asyncio
    async def test_validate_claim_confidence_scores(self, sample_claim_data):
        """Test that validation results include confidence scores"""
        results = await ultrathink_ai.validate_claim(sample_claim_data)
        
        for result in results:
            assert isinstance(result.confidence, float)
            assert 0.0 <= result.confidence <= 1.0, f"Confidence {result.confidence} out of range"


class TestUltrathinkAISmartCompletion:
    """Test suite for smart completion functionality"""

    @pytest.fixture
    def partial_claim_data(self):
        """Partial claim data for completion testing"""
        return {
            "provider_id": "PRV-001",
            "procedure_codes": ["99213"],
            "service_date": "2024-11-05"
            # Missing: diagnosis_codes, total_amount, etc.
        }

    @pytest.mark.asyncio
    async def test_smart_complete_provider_info(self):
        """Test completion of provider information"""
        partial_data = {"provider_id": "PRV-001"}
        
        completions = await ultrathink_ai.smart_complete(partial_data)
        
        # Should suggest provider name completion
        provider_completions = [c for c in completions if c.field == "provider_name"]
        if provider_completions:  # May not always have completions
            completion = provider_completions[0]
            assert isinstance(completion.confidence, float)
            assert 0.0 <= completion.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_smart_complete_diagnosis_from_procedure(self):
        """Test diagnosis prediction from procedure codes"""
        partial_data = {"procedure_codes": ["99213", "36415"]}
        
        completions = await ultrathink_ai.smart_complete(partial_data)
        
        # Should suggest diagnosis codes
        diagnosis_completions = [c for c in completions if c.field == "diagnosis_codes"]
        if diagnosis_completions:
            completion = diagnosis_completions[0]
            assert isinstance(completion.predicted_value, list)
            assert len(completion.predicted_value) > 0

    @pytest.mark.asyncio
    async def test_smart_complete_amount_prediction(self):
        """Test amount prediction from procedures"""
        partial_data = {"procedure_codes": ["99213", "99214"]}
        
        completions = await ultrathink_ai.smart_complete(partial_data)
        
        # Should suggest total amount
        amount_completions = [c for c in completions if c.field == "total_amount"]
        if amount_completions:
            completion = amount_completions[0]
            assert isinstance(completion.predicted_value, (int, float))
            assert completion.predicted_value > 0

    @pytest.mark.asyncio
    async def test_smart_complete_with_context(self, partial_claim_data):
        """Test smart completion with patient context"""
        context = {
            "patient_insurance": {
                "payer_id": "BUPA",
                "secondary_payers": ["TAWUNIYA"]
            }
        }
        
        completions = await ultrathink_ai.smart_complete(partial_claim_data, context)
        
        # Should suggest payer from context
        payer_completions = [c for c in completions if c.field == "payer_id"]
        if payer_completions:
            completion = payer_completions[0]
            assert completion.predicted_value == "BUPA"


class TestUltrathinkAIErrorPrediction:
    """Test suite for error prediction functionality"""

    @pytest.fixture
    def valid_claim_data(self):
        """Valid claim data that should have low error probability"""
        return {
            "claim_id": "CLM-1234567890",
            "patient_id": "PAT-001",
            "provider_id": "PRV-001",
            "payer_id": "BUPA",
            "service_date": "2024-11-05",
            "diagnosis_codes": ["J06.9"],
            "procedure_codes": ["99213"],
            "total_amount": 500.00
        }

    @pytest.fixture
    def problematic_claim_data(self):
        """Claim data with issues that should have high error probability"""
        return {
            "claim_id": "INVALID-FORMAT",
            "patient_id": "PAT-001",
            "provider_id": "",  # Empty provider
            "payer_id": "UNKNOWN_PAYER",
            "service_date": "2030-01-01",  # Future date
            "diagnosis_codes": [],  # No diagnoses
            "procedure_codes": ["99213"],
            "total_amount": -100.00  # Negative amount
        }

    @pytest.mark.asyncio
    async def test_predict_errors_valid_claim(self, valid_claim_data):
        """Test error prediction for valid claim"""
        prediction = await ultrathink_ai.predict_errors(valid_claim_data)
        
        assert isinstance(prediction, ErrorPrediction)
        assert isinstance(prediction.probability, float)
        assert 0.0 <= prediction.probability <= 1.0
        
        # Valid claim should have low failure probability
        assert prediction.probability < 0.5, f"Valid claim has high failure probability: {prediction.probability}"

    @pytest.mark.asyncio
    async def test_predict_errors_problematic_claim(self, problematic_claim_data):
        """Test error prediction for problematic claim"""
        prediction = await ultrathink_ai.predict_errors(problematic_claim_data)
        
        assert isinstance(prediction, ErrorPrediction)
        assert prediction.will_fail == True, "Problematic claim should be predicted to fail"
        assert prediction.probability > 0.7, f"Problematic claim has low failure probability: {prediction.probability}"
        
        # Should have predicted errors
        assert len(prediction.predicted_errors) > 0, "Should predict specific errors"
        
        # Should have recommendations
        assert len(prediction.recommendations) > 0, "Should provide recommendations"

    @pytest.mark.asyncio
    async def test_predict_errors_with_context(self, valid_claim_data):
        """Test error prediction with historical context"""
        context = {
            "submission_history": {
                "success_rate": 0.95,
                "common_rejections": ["missing_auth"]
            }
        }
        
        prediction = await ultrathink_ai.predict_errors(valid_claim_data, context)
        
        assert isinstance(prediction, ErrorPrediction)
        # Context should influence recommendations
        assert len(prediction.recommendations) > 0


class TestUltrathinkAIAnomalyDetection:
    """Test suite for anomaly detection functionality"""

    @pytest.fixture
    def normal_claim_data(self):
        """Normal claim data that should not trigger anomalies"""
        return {
            "claim_id": "CLM-1234567890",
            "patient_id": "PAT-001",
            "provider_id": "PRV-001",
            "payer_id": "BUPA",
            "service_date": "2024-11-05",
            "diagnosis_codes": ["J06.9"],
            "procedure_codes": ["99213"],
            "total_amount": 500.00
        }

    @pytest.fixture
    def suspicious_claim_data(self):
        """Suspicious claim data that should trigger anomalies"""
        return {
            "claim_id": "CLM-1234567890",
            "patient_id": "PAT-001",
            "provider_id": "PRV-001",
            "payer_id": "BUPA",
            "service_date": "2024-11-05",
            "diagnosis_codes": ["J06.9"],
            "procedure_codes": ["99213"] * 20,  # Too many procedures
            "total_amount": 100000.00  # Extremely high amount
        }

    @pytest.mark.asyncio
    async def test_detect_anomalies_normal_claim(self, normal_claim_data):
        """Test anomaly detection for normal claim"""
        detection = await ultrathink_ai.detect_anomalies(normal_claim_data)
        
        assert isinstance(detection, AnomalyDetection)
        assert isinstance(detection.anomaly_score, float)
        assert 0.0 <= detection.anomaly_score <= 1.0
        
        # Normal claim should have low anomaly score
        assert detection.anomaly_score < 0.5, f"Normal claim has high anomaly score: {detection.anomaly_score}"
        assert detection.is_anomaly == False or detection.risk_level in ["low", "medium"]

    @pytest.mark.asyncio
    async def test_detect_anomalies_suspicious_claim(self, suspicious_claim_data):
        """Test anomaly detection for suspicious claim"""
        detection = await ultrathink_ai.detect_anomalies(suspicious_claim_data)
        
        assert isinstance(detection, AnomalyDetection)
        
        # Suspicious claim should trigger anomaly detection
        assert detection.anomaly_score > 0.3, f"Suspicious claim has low anomaly score: {detection.anomaly_score}"
        assert detection.is_anomaly == True, "Suspicious claim should be flagged as anomaly"
        assert detection.risk_level in ["medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_detect_anomalies_high_amount(self):
        """Test anomaly detection for high amount claims"""
        claim_data = {
            "claim_id": "CLM-1234567890",
            "patient_id": "PAT-001",
            "provider_id": "PRV-001",
            "payer_id": "BUPA",
            "service_date": "2024-11-05",
            "diagnosis_codes": ["J06.9"],
            "procedure_codes": ["99213"],
            "total_amount": 75000.00  # Very high amount
        }
        
        detection = await ultrathink_ai.detect_anomalies(claim_data)
        
        assert detection.is_anomaly == True
        assert "financial" in detection.anomaly_type.lower() or "amount" in detection.details.lower()

    @pytest.mark.asyncio
    async def test_detect_anomalies_with_context(self, normal_claim_data):
        """Test anomaly detection with historical context"""
        context = {
            "historical_claims": [
                {"amount": 400, "procedures": 1},
                {"amount": 600, "procedures": 1},
                {"amount": 500, "procedures": 1}
            ],
            "provider_patterns": {
                "average_claim_amount": 500,
                "typical_procedures_per_claim": 1
            }
        }
        
        detection = await ultrathink_ai.detect_anomalies(normal_claim_data, context)
        
        assert isinstance(detection, AnomalyDetection)
        # With normal context, normal claim should not be anomalous
        assert detection.anomaly_score < 0.4


class TestUltrathinkAIIntegration:
    """Integration tests for combined AI functionality"""

    @pytest.fixture
    def complete_workflow_data(self):
        """Complete claim data for workflow testing"""
        return {
            "claim_id": "CLM-1234567890",
            "patient_id": "PAT-001",
            "provider_id": "PRV-001",
            "payer_id": "BUPA",
            "service_date": "2024-11-05",
            "diagnosis_codes": ["J06.9"],
            "procedure_codes": ["99213"],
            "total_amount": 500.00
        }

    @pytest.mark.asyncio
    async def test_complete_ai_workflow(self, complete_workflow_data):
        """Test complete AI workflow: validation -> prediction -> anomaly detection"""
        
        # Step 1: Validate claim
        validation_results = await ultrathink_ai.validate_claim(complete_workflow_data)
        assert isinstance(validation_results, list)
        
        # Step 2: Predict errors
        error_prediction = await ultrathink_ai.predict_errors(complete_workflow_data)
        assert isinstance(error_prediction, ErrorPrediction)
        
        # Step 3: Detect anomalies
        anomaly_detection = await ultrathink_ai.detect_anomalies(complete_workflow_data)
        assert isinstance(anomaly_detection, AnomalyDetection)
        
        # All should complete without errors
        assert True  # If we get here, workflow completed successfully

    @pytest.mark.asyncio
    async def test_smart_completion_workflow(self):
        """Test smart completion workflow"""
        
        # Start with minimal data
        partial_data = {"provider_id": "PRV-001"}
        
        # Get completions
        completions = await ultrathink_ai.smart_complete(partial_data)
        assert isinstance(completions, list)
        
        # Apply completions (simulate)
        completed_data = partial_data.copy()
        for completion in completions:
            if completion.confidence > 0.8:  # Only apply high-confidence completions
                completed_data[completion.field] = completion.predicted_value
        
        # Validate completed data
        if len(completed_data) > 1:  # If we have more than just provider_id
            validation_results = await ultrathink_ai.validate_claim(completed_data)
            assert isinstance(validation_results, list)

    @pytest.mark.asyncio
    async def test_performance_timing(self, complete_workflow_data):
        """Test that AI operations complete within reasonable time"""
        import time
        
        start_time = time.time()
        
        # Run all AI operations
        validation_task = ultrathink_ai.validate_claim(complete_workflow_data)
        completion_task = ultrathink_ai.smart_complete(complete_workflow_data)
        prediction_task = ultrathink_ai.predict_errors(complete_workflow_data)
        anomaly_task = ultrathink_ai.detect_anomalies(complete_workflow_data)
        
        # Wait for completion
        await validation_task
        await completion_task
        await prediction_task
        await anomaly_task
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert total_time < 5.0, f"AI operations took too long: {total_time:.2f} seconds"


# Error handling tests
class TestUltrathinkAIErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_validation_with_none_data(self):
        """Test validation with None data"""
        try:
            results = await ultrathink_ai.validate_claim(None)
            # Should either handle gracefully or raise appropriate error
            assert isinstance(results, list) or results is None
        except (TypeError, ValueError):
            # Acceptable to raise these errors for None input
            pass

    @pytest.mark.asyncio
    async def test_validation_with_empty_data(self):
        """Test validation with empty data"""
        results = await ultrathink_ai.validate_claim({})
        
        # Should detect missing required fields
        assert isinstance(results, list)
        assert len(results) > 0  # Should have validation errors

    @pytest.mark.asyncio
    async def test_smart_complete_with_invalid_data(self):
        """Test smart completion with invalid data types"""
        try:
            completions = await ultrathink_ai.smart_complete("invalid_data")
            # Should handle gracefully or raise appropriate error
            assert isinstance(completions, list)
        except (TypeError, ValueError):
            # Acceptable to raise these errors for invalid input
            pass

    @pytest.mark.asyncio
    async def test_anomaly_detection_with_missing_amount(self):
        """Test anomaly detection with missing total_amount field"""
        claim_data = {
            "claim_id": "CLM-1234567890",
            "patient_id": "PAT-001",
            # Missing total_amount
        }
        
        detection = await ultrathink_ai.detect_anomalies(claim_data)
        
        # Should handle missing data gracefully
        assert isinstance(detection, AnomalyDetection)
        assert detection.anomaly_score >= 0.0


# Fixtures for all tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/unit/services/test_ultrathink_ai.py -v
    pytest.main([__file__, "-v"])