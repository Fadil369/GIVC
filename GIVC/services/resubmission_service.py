"""
Automated Resubmission Service
Handles intelligent claim resubmission based on rejection patterns.
Based on RCM rejection data analysis showing 19.2M SAR in rejected claims.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio

from config.rejection_codes import (
    get_rejection_info,
    get_auto_resubmit_codes,
    RejectionCodeInfo,
    RejectionSeverity
)
from services.claims import ClaimsService
from services.eligibility import EligibilityService
from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ResubmissionAttempt:
    """Track resubmission attempts."""
    claim_id: str
    original_submission_date: datetime
    rejection_code: str
    rejection_reason: str
    attempt_number: int
    attempted_at: datetime
    status: str  # "pending", "submitted", "accepted", "rejected"
    correction_applied: str
    result: Optional[Dict[str, Any]] = None


@dataclass
class ResubmissionStrategy:
    """Strategy for resubmitting a claim."""
    max_attempts: int = 3
    retry_delay_hours: int = 24
    escalate_after_attempts: int = 2
    auto_correct_enabled: bool = True
    notify_on_failure: bool = True


@dataclass
class ClaimCorrection:
    """Claim correction information."""
    field_name: str
    old_value: Any
    new_value: Any
    correction_reason: str
    confidence_score: float  # 0.0 to 1.0


class ResubmissionService:
    """
    Automated claim resubmission service.
    
    Features:
    - Automatic correction for eligible rejection types
    - Intelligent retry strategies
    - Success rate tracking
    - Financial impact monitoring
    - Escalation for manual review
    """
    
    def __init__(
        self,
        claims_service: ClaimsService,
        eligibility_service: EligibilityService,
        strategy: Optional[ResubmissionStrategy] = None
    ):
        """
        Initialize resubmission service.
        
        Args:
            claims_service: Claims service instance
            eligibility_service: Eligibility service instance
            strategy: Resubmission strategy (uses default if None)
        """
        self.claims_service = claims_service
        self.eligibility_service = eligibility_service
        self.strategy = strategy or ResubmissionStrategy()
        self.logger = logging.getLogger(__name__)
        
        # Track resubmission history
        self.resubmission_history: Dict[str, List[ResubmissionAttempt]] = {}
        
        # Success metrics
        self.metrics = {
            "total_resubmissions": 0,
            "successful_resubmissions": 0,
            "failed_resubmissions": 0,
            "auto_corrected": 0,
            "manual_review_required": 0,
            "total_recovered_amount": 0.0,
        }
    
    def can_auto_resubmit(self, rejection_code: str) -> bool:
        """
        Check if rejection code allows automatic resubmission.
        
        Args:
            rejection_code: Rejection code to check
            
        Returns:
            True if auto-resubmit is allowed
        """
        rejection_info = get_rejection_info(rejection_code)
        if not rejection_info:
            return False
        
        return rejection_info.auto_resubmit
    
    def analyze_rejection(
        self,
        claim_data: Dict[str, Any],
        rejection_code: str,
        rejection_details: Dict[str, Any]
    ) -> List[ClaimCorrection]:
        """
        Analyze rejection and determine corrections.
        
        Args:
            claim_data: Original claim data
            rejection_code: Rejection code
            rejection_details: Detailed rejection information
            
        Returns:
            List of corrections to apply
        """
        corrections = []
        rejection_info = get_rejection_info(rejection_code)
        
        if not rejection_info:
            self.logger.warning(f"Unknown rejection code: {rejection_code}")
            return corrections
        
        # Apply correction strategies based on rejection type
        if rejection_code == "TECH02":  # Missing required field
            corrections.extend(self._correct_missing_fields(claim_data, rejection_details))
        
        elif rejection_code == "CD01":  # Invalid diagnosis code
            corrections.extend(self._correct_diagnosis_codes(claim_data, rejection_details))
        
        elif rejection_code == "CD02":  # Invalid procedure code
            corrections.extend(self._correct_procedure_codes(claim_data, rejection_details))
        
        elif rejection_code == "PR01":  # Price exceeds contracted rate
            corrections.extend(self._correct_pricing(claim_data, rejection_details))
        
        elif rejection_code == "PA03":  # Invalid authorization number
            corrections.extend(self._correct_authorization(claim_data, rejection_details))
        
        elif rejection_code == "INC01":  # Missing patient information
            corrections.extend(self._correct_patient_info(claim_data, rejection_details))
        
        elif rejection_code == "INC02":  # Missing provider information
            corrections.extend(self._correct_provider_info(claim_data, rejection_details))
        
        return corrections
    
    def _correct_missing_fields(
        self,
        claim_data: Dict[str, Any],
        rejection_details: Dict[str, Any]
    ) -> List[ClaimCorrection]:
        """Correct missing required fields."""
        corrections = []
        missing_fields = rejection_details.get("missing_fields", [])
        
        for field in missing_fields:
            # Try to populate from available data sources
            new_value = self._lookup_missing_field_value(claim_data, field)
            if new_value:
                corrections.append(ClaimCorrection(
                    field_name=field,
                    old_value=None,
                    new_value=new_value,
                    correction_reason="Populated missing required field",
                    confidence_score=0.90
                ))
        
        return corrections
    
    def _correct_diagnosis_codes(
        self,
        claim_data: Dict[str, Any],
        rejection_details: Dict[str, Any]
    ) -> List[ClaimCorrection]:
        """Correct invalid diagnosis codes."""
        corrections = []
        invalid_code = rejection_details.get("invalid_diagnosis_code")
        
        if invalid_code:
            # Attempt to map to valid ICD-10 code
            valid_code = self._map_to_valid_icd10(invalid_code)
            if valid_code:
                corrections.append(ClaimCorrection(
                    field_name="diagnosis_code",
                    old_value=invalid_code,
                    new_value=valid_code,
                    correction_reason="Mapped to valid ICD-10 code",
                    confidence_score=0.85
                ))
        
        return corrections
    
    def _correct_procedure_codes(
        self,
        claim_data: Dict[str, Any],
        rejection_details: Dict[str, Any]
    ) -> List[ClaimCorrection]:
        """Correct invalid procedure codes."""
        corrections = []
        invalid_code = rejection_details.get("invalid_procedure_code")
        
        if invalid_code:
            # Attempt to map to valid CPT code
            valid_code = self._map_to_valid_cpt(invalid_code)
            if valid_code:
                corrections.append(ClaimCorrection(
                    field_name="procedure_code",
                    old_value=invalid_code,
                    new_value=valid_code,
                    correction_reason="Mapped to valid CPT code",
                    confidence_score=0.85
                ))
        
        return corrections
    
    def _correct_pricing(
        self,
        claim_data: Dict[str, Any],
        rejection_details: Dict[str, Any]
    ) -> List[ClaimCorrection]:
        """Correct pricing issues."""
        corrections = []
        
        claimed_amount = claim_data.get("total_amount")
        contracted_rate = rejection_details.get("contracted_rate")
        
        if claimed_amount and contracted_rate and claimed_amount > contracted_rate:
            corrections.append(ClaimCorrection(
                field_name="total_amount",
                old_value=claimed_amount,
                new_value=contracted_rate,
                correction_reason="Adjusted to contracted rate",
                confidence_score=0.98
            ))
        
        return corrections
    
    def _correct_authorization(
        self,
        claim_data: Dict[str, Any],
        rejection_details: Dict[str, Any]
    ) -> List[ClaimCorrection]:
        """Correct authorization issues."""
        corrections = []
        
        # Look up correct authorization number
        correct_auth = self._lookup_authorization_number(
            claim_data.get("patient_id"),
            claim_data.get("service_date")
        )
        
        if correct_auth:
            corrections.append(ClaimCorrection(
                field_name="authorization_number",
                old_value=claim_data.get("authorization_number"),
                new_value=correct_auth,
                correction_reason="Corrected authorization number",
                confidence_score=0.95
            ))
        
        return corrections
    
    def _correct_patient_info(
        self,
        claim_data: Dict[str, Any],
        rejection_details: Dict[str, Any]
    ) -> List[ClaimCorrection]:
        """Correct missing patient information."""
        corrections = []
        
        patient_id = claim_data.get("patient_id")
        if patient_id:
            # Look up complete patient information
            patient_info = self._lookup_patient_details(patient_id)
            
            missing_fields = rejection_details.get("missing_patient_fields", [])
            for field in missing_fields:
                if field in patient_info:
                    corrections.append(ClaimCorrection(
                        field_name=f"patient.{field}",
                        old_value=None,
                        new_value=patient_info[field],
                        correction_reason="Populated from patient records",
                        confidence_score=0.93
                    ))
        
        return corrections
    
    def _correct_provider_info(
        self,
        claim_data: Dict[str, Any],
        rejection_details: Dict[str, Any]
    ) -> List[ClaimCorrection]:
        """Correct missing provider information."""
        corrections = []
        
        provider_id = claim_data.get("provider_id")
        if provider_id:
            # Look up complete provider information
            provider_info = self._lookup_provider_details(provider_id)
            
            missing_fields = rejection_details.get("missing_provider_fields", [])
            for field in missing_fields:
                if field in provider_info:
                    corrections.append(ClaimCorrection(
                        field_name=f"provider.{field}",
                        old_value=None,
                        new_value=provider_info[field],
                        correction_reason="Populated from provider records",
                        confidence_score=0.95
                    ))
        
        return corrections
    
    def apply_corrections(
        self,
        claim_data: Dict[str, Any],
        corrections: List[ClaimCorrection]
    ) -> Dict[str, Any]:
        """
        Apply corrections to claim data.
        
        Args:
            claim_data: Original claim data
            corrections: List of corrections to apply
            
        Returns:
            Corrected claim data
        """
        corrected_data = claim_data.copy()
        
        for correction in corrections:
            if correction.confidence_score < 0.70:
                self.logger.warning(
                    f"Low confidence correction ({correction.confidence_score:.2f}) for {correction.field_name}"
                )
                continue
            
            # Apply correction
            field_parts = correction.field_name.split(".")
            current = corrected_data
            
            for part in field_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[field_parts[-1]] = correction.new_value
            
            self.logger.info(
                f"Applied correction: {correction.field_name} = {correction.new_value} "
                f"(reason: {correction.correction_reason})"
            )
        
        return corrected_data
    
    async def resubmit_claim(
        self,
        claim_id: str,
        rejection_code: str,
        rejection_details: Dict[str, Any],
        claim_data: Dict[str, Any],
        claim_amount: float
    ) -> ResubmissionAttempt:
        """
        Resubmit a rejected claim with corrections.
        
        Args:
            claim_id: Original claim ID
            rejection_code: Rejection code
            rejection_details: Rejection details
            claim_data: Original claim data
            claim_amount: Claim amount
            
        Returns:
            Resubmission attempt record
        """
        # Check attempt history
        attempts = self.resubmission_history.get(claim_id, [])
        attempt_number = len(attempts) + 1
        
        if attempt_number > self.strategy.max_attempts:
            self.logger.error(f"Max resubmission attempts ({self.strategy.max_attempts}) reached for claim {claim_id}")
            self.metrics["manual_review_required"] += 1
            
            return ResubmissionAttempt(
                claim_id=claim_id,
                original_submission_date=claim_data.get("submission_date", datetime.now()),
                rejection_code=rejection_code,
                rejection_reason=rejection_details.get("reason", "Unknown"),
                attempt_number=attempt_number,
                attempted_at=datetime.now(),
                status="failed",
                correction_applied="Max attempts reached - manual review required"
            )
        
        # Analyze and generate corrections
        corrections = self.analyze_rejection(claim_data, rejection_code, rejection_details)
        
        if not corrections:
            self.logger.warning(f"No corrections identified for claim {claim_id} with rejection {rejection_code}")
            
            if not self.can_auto_resubmit(rejection_code):
                return ResubmissionAttempt(
                    claim_id=claim_id,
                    original_submission_date=claim_data.get("submission_date", datetime.now()),
                    rejection_code=rejection_code,
                    rejection_reason=rejection_details.get("reason", "Unknown"),
                    attempt_number=attempt_number,
                    attempted_at=datetime.now(),
                    status="pending",
                    correction_applied="Manual review required - cannot auto-correct"
                )
        
        # Apply corrections
        corrected_claim = self.apply_corrections(claim_data, corrections)
        
        # Submit corrected claim
        try:
            result = await self.claims_service.submit_claim(corrected_claim)
            
            is_success = result.get("status") == "accepted"
            
            attempt = ResubmissionAttempt(
                claim_id=claim_id,
                original_submission_date=claim_data.get("submission_date", datetime.now()),
                rejection_code=rejection_code,
                rejection_reason=rejection_details.get("reason", "Unknown"),
                attempt_number=attempt_number,
                attempted_at=datetime.now(),
                status="accepted" if is_success else "rejected",
                correction_applied=", ".join([c.correction_reason for c in corrections]),
                result=result
            )
            
            # Update metrics
            self.metrics["total_resubmissions"] += 1
            if is_success:
                self.metrics["successful_resubmissions"] += 1
                self.metrics["total_recovered_amount"] += claim_amount
                self.metrics["auto_corrected"] += 1
            else:
                self.metrics["failed_resubmissions"] += 1
            
            # Store attempt
            if claim_id not in self.resubmission_history:
                self.resubmission_history[claim_id] = []
            self.resubmission_history[claim_id].append(attempt)
            
            self.logger.info(
                f"Resubmission attempt {attempt_number} for claim {claim_id}: {attempt.status}"
            )
            
            return attempt
            
        except Exception as e:
            self.logger.error(f"Error resubmitting claim {claim_id}: {str(e)}")
            
            return ResubmissionAttempt(
                claim_id=claim_id,
                original_submission_date=claim_data.get("submission_date", datetime.now()),
                rejection_code=rejection_code,
                rejection_reason=rejection_details.get("reason", "Unknown"),
                attempt_number=attempt_number,
                attempted_at=datetime.now(),
                status="failed",
                correction_applied=f"Submission error: {str(e)}"
            )
    
    def get_resubmission_metrics(self) -> Dict[str, Any]:
        """Get resubmission service metrics."""
        success_rate = 0.0
        if self.metrics["total_resubmissions"] > 0:
            success_rate = (self.metrics["successful_resubmissions"] / 
                          self.metrics["total_resubmissions"])
        
        return {
            **self.metrics,
            "success_rate": success_rate,
            "average_recovered_per_claim": (
                self.metrics["total_recovered_amount"] / self.metrics["successful_resubmissions"]
                if self.metrics["successful_resubmissions"] > 0 else 0.0
            )
        }
    
    # Helper methods (stubs - implement based on actual data sources)
    
    def _lookup_missing_field_value(self, claim_data: Dict, field: str) -> Optional[Any]:
        """Lookup value for missing field from data sources."""
        # TODO: Implement actual lookup logic
        return None
    
    def _map_to_valid_icd10(self, code: str) -> Optional[str]:
        """Map to valid ICD-10 code."""
        # TODO: Implement ICD-10 mapping logic
        return None
    
    def _map_to_valid_cpt(self, code: str) -> Optional[str]:
        """Map to valid CPT code."""
        # TODO: Implement CPT mapping logic
        return None
    
    def _lookup_authorization_number(self, patient_id: str, service_date: datetime) -> Optional[str]:
        """Lookup correct authorization number."""
        # TODO: Implement authorization lookup
        return None
    
    def _lookup_patient_details(self, patient_id: str) -> Dict[str, Any]:
        """Lookup patient details."""
        # TODO: Implement patient lookup
        return {}
    
    def _lookup_provider_details(self, provider_id: str) -> Dict[str, Any]:
        """Lookup provider details."""
        # TODO: Implement provider lookup
        return {}
