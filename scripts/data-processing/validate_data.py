"""
ClaimLinc Data Validation Module
Validates claim data for completeness, accuracy, and compliance
"""

import json
import re
import pandas as pd
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import hashlib


class ClaimDataValidator:
    """Validates claim data for quality, compliance, and business rules"""
    
    def __init__(self):
        self.validation_rules = {
            "required_fields": [
                "claim_id",
                "provider.name",
                "patient.member_id",
                "claim_details.service_date",
                "claim_details.total_amount"
            ],
            "field_constraints": {
                "claim_id": {
                    "min_length": 3,
                    "max_length": 50,
                    "pattern": r"^[A-Za-z0-9\-_]+$"
                },
                "patient.member_id": {
                    "min_length": 5,
                    "max_length": 20,
                    "pattern": r"^[A-Za-z0-9\-_]+$"
                },
                "claim_details.total_amount": {
                    "min_value": 0.01,
                    "max_value": 1000000.0
                }
            },
            "business_rules": {
                "service_date_range": {
                    "days_back": 365,
                    "days_forward": 30
                },
                "branch_codes": ["MainRiyadh", "Unaizah", "Abha", "Madinah", "Khamis"],
                "supported_currencies": ["SAR", "USD", "EUR"],
                "claim_types": ["inpatient", "outpatient", "emergency", "surgery", "consultation"]
            }
        }
        
        self.validation_errors = []
        self.validation_warnings = []
        
    def validate_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation of claim data
        
        Args:
            claim_data: Claim data to validate
            
        Returns:
            Validation result with status, errors, and warnings
        """
        try:
            # Reset validation state
            self.validation_errors = []
            self.validation_warnings = []
            
            # Perform validations
            self._validate_required_fields(claim_data)
            self._validate_field_constraints(claim_data)
            self._validate_business_rules(claim_data)
            self._validate_data_consistency(claim_data)
            self._validate_compliance_rules(claim_data)
            
            # Generate validation report
            validation_result = {
                "claim_id": self._get_claim_id(claim_data),
                "validation_status": "PASS" if not self.validation_errors else "FAIL",
                "validation_timestamp": datetime.now().isoformat(),
                "errors": self.validation_errors.copy(),
                "warnings": self.validation_warnings.copy(),
                "validation_score": self._calculate_validation_score(),
                "data_quality_metrics": self._calculate_quality_metrics(claim_data),
                "compliance_status": self._assess_compliance_status(),
                "recommendations": self._generate_recommendations()
            }
            
            return validation_result
            
        except Exception as e:
            return {
                "claim_id": self._get_claim_id(claim_data),
                "validation_status": "ERROR",
                "validation_timestamp": datetime.now().isoformat(),
                "errors": [f"Validation process failed: {str(e)}"],
                "warnings": [],
                "validation_score": 0,
                "error_details": str(e)
            }
    
    def _validate_required_fields(self, claim_data: Dict[str, Any]) -> None:
        """Validate presence of required fields"""
        for field_path in self.validation_rules["required_fields"]:
            value = self._get_nested_value(claim_data, field_path.split('.'))
            if not value or (isinstance(value, str) and not value.strip()):
                self.validation_errors.append(f"Missing required field: {field_path}")
    
    def _validate_field_constraints(self, claim_data: Dict[str, Any]) -> None:
        """Validate field constraints (length, pattern, range)"""
        for field_path, constraints in self.validation_rules["field_constraints"].items():
            value = self._get_nested_value(claim_data, field_path.split('.'))
            if value is None:
                continue
                
            # String length validation
            if "min_length" in constraints and len(str(value)) < constraints["min_length"]:
                self.validation_errors.append(
                    f"Field {field_path} too short (minimum {constraints['min_length']} characters)"
                )
            
            if "max_length" in constraints and len(str(value)) > constraints["max_length"]:
                self.validation_errors.append(
                    f"Field {field_path} too long (maximum {constraints['max_length']} characters)"
                )
            
            # Pattern validation
            if "pattern" in constraints:
                if not re.match(constraints["pattern"], str(value)):
                    self.validation_errors.append(
                        f"Field {field_path} does not match required pattern"
                    )
            
            # Numeric range validation
            if "min_value" in constraints:
                try:
                    num_value = float(value)
                    if num_value < constraints["min_value"]:
                        self.validation_errors.append(
                            f"Field {field_path} below minimum value {constraints['min_value']}"
                        )
                except (ValueError, TypeError):
                    self.validation_warnings.append(
                        f"Field {field_path} cannot be validated as numeric"
                    )
            
            if "max_value" in constraints:
                try:
                    num_value = float(value)
                    if num_value > constraints["max_value"]:
                        self.validation_errors.append(
                            f"Field {field_path} above maximum value {constraints['max_value']}"
                        )
                except (ValueError, TypeError):
                    pass
    
    def _validate_business_rules(self, claim_data: Dict[str, Any]) -> None:
        """Validate business rule compliance"""
        # Check service date range
        service_date = self._get_nested_value(claim_data, ["claim_details", "service_date"])
        if service_date:
            try:
                if isinstance(service_date, str):
                    parsed_date = datetime.fromisoformat(service_date.replace('Z', '+00:00'))
                else:
                    parsed_date = service_date
                    
                current_date = datetime.now()
                date_diff = (current_date - parsed_date).days
                
                # Check if service date is too far in the past
                max_days_back = self.validation_rules["business_rules"]["service_date_range"]["days_back"]
                if date_diff > max_days_back:
                    self.validation_warnings.append(
                        f"Service date is more than {max_days_back} days old"
                    )
                
                # Check if service date is in the future
                max_days_forward = self.validation_rules["business_rules"]["service_date_range"]["days_forward"]
                if (parsed_date - current_date).days > max_days_forward:
                    self.validation_warnings.append(
                        f"Service date is more than {max_days_forward} days in the future"
                    )
                    
            except (ValueError, TypeError) as e:
                self.validation_warnings.append(f"Service date format validation failed: {str(e)}")
        
        # Check branch code validity
        branch = self._get_nested_value(claim_data, ["provider", "branch"])
        if branch:
            valid_branches = self.validation_rules["business_rules"]["branch_codes"]
            if branch not in valid_branches:
                self.validation_warnings.append(
                    f"Branch '{branch}' not in standard branch list: {valid_branches}"
                )
        
        # Check claim type validity
        claim_type = self._get_nested_value(claim_data, ["claim_details", "type"])
        if claim_type:
            valid_types = self.validation_rules["business_rules"]["claim_types"]
            if claim_type not in valid_types:
                self.validation_warnings.append(
                    f"Claim type '{claim_type}' not in standard types: {valid_types}"
                )
        
        # Check currency
        currency = self._get_nested_value(claim_data, ["claim_details", "currency"])
        if currency:
            valid_currencies = self.validation_rules["business_rules"]["supported_currencies"]
            if currency not in valid_currencies:
                self.validation_warnings.append(
                    f"Currency '{currency}' not in supported currencies: {valid_currencies}"
                )
    
    def _validate_data_consistency(self, claim_data: Dict[str, Any]) -> None:
        """Validate data consistency and logical relationships"""
        # Check admission/discharge date consistency
        admission_date = self._get_nested_value(claim_data, ["claim_details", "admission_date"])
        discharge_date = self._get_nested_value(claim_data, ["claim_details", "discharge_date"])
        claim_type = self._get_nested_value(claim_data, ["claim_details", "type"])
        
        if admission_date and discharge_date:
            try:
                if isinstance(admission_date, str):
                    admission = datetime.fromisoformat(admission_date.replace('Z', '+00:00'))
                else:
                    admission = admission_date
                    
                if isinstance(discharge_date, str):
                    discharge = datetime.fromisoformat(discharge_date.replace('Z', '+00:00'))
                else:
                    discharge = discharge_date
                
                if admission > discharge:
                    self.validation_errors.append("Admission date is after discharge date")
                elif (discharge - admission).days > 30:
                    self.validation_warnings.append("Hospital stay longer than 30 days")
                    
            except (ValueError, TypeError):
                self.validation_warnings.append("Date consistency check failed due to date format issues")
        
        # For inpatient claims, check if admission/discharge dates are provided
        if claim_type == "inpatient" and not (admission_date and discharge_date):
            self.validation_errors.append("Inpatient claims must have both admission and discharge dates")
        
        # For outpatient claims, check that no admission/discharge dates are provided
        if claim_type == "outpatient" and (admission_date or discharge_date):
            self.validation_warnings.append("Outpatient claims typically don't have admission/discharge dates")
        
        # Check diagnosis and procedure code consistency
        diagnosis_codes = self._get_nested_value(claim_data, ["claim_details", "diagnosis_codes"]) or []
        procedure_codes = self._get_nested_value(claim_data, ["claim_details", "procedure_codes"]) or []
        
        if not diagnosis_codes and not procedure_codes:
            self.validation_errors.append("Claims must have at least one diagnosis or procedure code")
        
        # Validate ICD-10 code format
        for code in diagnosis_codes:
            if not re.match(r'^[A-Z]\d{2}(\.\d{1,2})?$', str(code)):
                self.validation_warnings.append(f"Diagnosis code '{code}' doesn't match ICD-10 format")
        
        # Validate CPT code format
        for code in procedure_codes:
            if not re.match(r'^\d{5}$', str(code)):
                self.validation_warnings.append(f"Procedure code '{code}' doesn't match CPT format")
    
    def _validate_compliance_rules(self, claim_data: Dict[str, Any]) -> None:
        """Validate regulatory and compliance requirements"""
        # Check for potential PHI exposure
        patient_name = self._get_nested_value(claim_data, ["patient", "name"])
        national_id = self._get_nested_value(claim_data, ["patient", "national_id"])
        
        # Check if names contain only alphabetic characters and allowed punctuation
        if patient_name and not re.match(r'^[A-Za-z\s\-\'\.]+$', str(patient_name)):
            self.validation_warnings.append("Patient name contains unusual characters")
        
        # Check national ID format (basic Saudi national ID check)
        if national_id:
            if not re.match(r'^\d{10}$', str(national_id)):
                self.validation_warnings.append("National ID doesn't match expected format (10 digits)")
        
        # Check for reasonable amounts (flag suspiciously high amounts)
        total_amount = self._get_nested_value(claim_data, ["claim_details", "total_amount"])
        if total_amount:
            try:
                amount = float(total_amount)
                if amount > 500000:  # Very high amount threshold
                    self.validation_warnings.append(
                        f"Claim amount {amount} is unusually high and may require review"
                    )
                elif amount < 10:  # Very low amount threshold
                    self.validation_warnings.append(
                        f"Claim amount {amount} is unusually low and may be incorrect"
                    )
            except (ValueError, TypeError):
                pass
        
        # Check for completeness of key patient identifiers
        required_patient_fields = ["member_id", "name"]
        missing_patient_fields = []
        for field in required_patient_fields:
            if not self._get_nested_value(claim_data, ["patient", field]):
                missing_patient_fields.append(field)
        
        if missing_patient_fields:
            self.validation_errors.append(f"Missing required patient fields: {missing_patient_fields}")
    
    def _get_claim_id(self, claim_data: Dict[str, Any]) -> str:
        """Extract claim ID from claim data"""
        claim_id = self._get_nested_value(claim_data, ["claim_id"])
        return claim_id or "UNKNOWN"
    
    def _get_nested_value(self, data: Dict[str, Any], keys: List[str]) -> Any:
        """Get value from nested dictionary"""
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def _calculate_validation_score(self) -> float:
        """Calculate validation score based on errors and warnings"""
        base_score = 100.0
        
        # Deduct points for errors
        error_deduction = len(self.validation_errors) * 15
        
        # Deduct points for warnings
        warning_deduction = len(self.validation_warnings) * 5
        
        score = max(0.0, base_score - error_deduction - warning_deduction)
        return round(score, 2)
    
    def _calculate_quality_metrics(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate data quality metrics"""
        total_possible_fields = len(self.validation_rules["required_fields"])
        filled_required_fields = 0
        
        for field_path in self.validation_rules["required_fields"]:
            value = self._get_nested_value(claim_data, field_path.split('.'))
            if value and (not isinstance(value, str) or value.strip()):
                filled_required_fields += 1
        
        completeness_score = (filled_required_fields / total_possible_fields) * 100
        
        # Calculate character encoding health
        encoding_score = 100.0
        text_fields = ["patient.name", "provider.name"]
        for field_path in text_fields:
            value = self._get_nested_value(claim_data, field_path.split('.'))
            if value:
                try:
                    value.encode('utf-8').decode('utf-8')
                except UnicodeError:
                    encoding_score -= 20
        
        return {
            "completeness_score": round(completeness_score, 2),
            "encoding_score": round(max(0, encoding_score), 2),
            "required_fields_filled": f"{filled_required_fields}/{total_possible_fields}",
            "error_count": len(self.validation_errors),
            "warning_count": len(self.validation_warnings)
        }
    
    def _assess_compliance_status(self) -> str:
        """Assess overall compliance status"""
        if self.validation_errors:
            return "NON_COMPLIANT"
        elif len(self.validation_warnings) > 5:
            return "WARNING"
        elif len(self.validation_warnings) > 0:
            return "MINOR_ISSUES"
        else:
            return "COMPLIANT"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Recommendations based on errors
        if self.validation_errors:
            if any("Missing required field" in error for error in self.validation_errors):
                recommendations.append("Ensure all required fields are populated before submission")
            
            if any("date" in error.lower() for error in self.validation_errors):
                recommendations.append("Review and correct date formats to ensure compliance")
            
            if any("admission" in error.lower() or "discharge" in error.lower() for error in self.validation_errors):
                recommendations.append("Verify inpatient claim date consistency")
        
        # Recommendations based on warnings
        if self.validation_warnings:
            if any("unusually" in warning.lower() for warning in self.validation_warnings):
                recommendations.append("Review unusually high or low amounts for accuracy")
            
            if any("branch" in warning.lower() for warning in self.validation_warnings):
                recommendations.append("Verify branch code matches standard hospital branches")
            
            if any("format" in warning.lower() for warning in self.validation_warnings):
                recommendations.append("Ensure medical codes follow standard formatting")
        
        # General recommendations
        if not self.validation_errors and not self.validation_warnings:
            recommendations.append("Claim data meets all validation requirements")
        
        return recommendations
    
    def batch_validate(self, claims_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate multiple claims in batch"""
        results = []
        summary = {
            "total_claims": len(claims_data),
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "error_distribution": {},
            "warning_distribution": {},
            "average_validation_score": 0.0,
            "compliance_summary": {}
        }
        
        total_score = 0
        
        for i, claim_data in enumerate(claims_data):
            try:
                validation_result = self.validate_claim(claim_data)
                validation_result["batch_index"] = i
                results.append(validation_result)
                
                # Update summary statistics
                status = validation_result["validation_status"]
                if status == "PASS":
                    summary["passed"] += 1
                elif status == "FAIL":
                    summary["failed"] += 1
                else:
                    summary["failed"] += 1
                
                if validation_result["warnings"]:
                    summary["warnings"] += 1
                
                # Track error distribution
                for error in validation_result["errors"]:
                    error_type = error.split(":")[0] if ":" in error else "Other"
                    summary["error_distribution"][error_type] = summary["error_distribution"].get(error_type, 0) + 1
                
                # Track warning distribution
                for warning in validation_result["warnings"]:
                    warning_type = warning.split(":")[0] if ":" in warning else "Other"
                    summary["warning_distribution"][warning_type] = summary["warning_distribution"].get(warning_type, 0) + 1
                
                total_score += validation_result["validation_score"]
                
            except Exception as e:
                results.append({
                    "batch_index": i,
                    "validation_status": "ERROR",
                    "errors": [f"Batch validation failed: {str(e)}"],
                    "validation_score": 0
                })
        
        # Calculate averages
        if len(claims_data) > 0:
            summary["average_validation_score"] = round(total_score / len(claims_data), 2)
        
        # Compliance summary
        compliance_statuses = [result.get("compliance_status", "UNKNOWN") for result in results]
        for status in set(compliance_statuses):
            summary["compliance_summary"][status] = compliance_statuses.count(status)
        
        summary["validation_results"] = results
        return summary
    
    def export_validation_report(self, validation_results: Dict[str, Any], output_path: str) -> str:
        """Export validation results to CSV/JSON report"""
        try:
            results = validation_results["validation_results"]
            
            # Create flat data for CSV
            flat_results = []
            for result in results:
                flat_record = {
                    "claim_id": result.get("claim_id"),
                    "batch_index": result.get("batch_index"),
                    "validation_status": result.get("validation_status"),
                    "validation_score": result.get("validation_score"),
                    "compliance_status": result.get("compliance_status"),
                    "error_count": len(result.get("errors", [])),
                    "warning_count": len(result.get("warnings", [])),
                    "errors": "; ".join(result.get("errors", [])),
                    "warnings": "; ".join(result.get("warnings", [])),
                    "recommendations": "; ".join(result.get("recommendations", [])),
                    "validation_timestamp": result.get("validation_timestamp"),
                    "completeness_score": result.get("data_quality_metrics", {}).get("completeness_score", 0),
                    "encoding_score": result.get("data_quality_metrics", {}).get("encoding_score", 0)
                }
                flat_results.append(flat_record)
            
            # Export to CSV
            df = pd.DataFrame(flat_results)
            df.to_csv(output_path, index=False)
            
            return f"Successfully exported {len(flat_results)} validation results to {output_path}"
            
        except Exception as e:
            raise ValueError(f"Validation report export failed: {str(e)}")


# Utility functions
def validate_claim_data(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Utility function to validate a single claim"""
    validator = ClaimDataValidator()
    return validator.validate_claim(claim_data)


def batch_validate_claims(claims_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Utility function to validate multiple claims"""
    validator = ClaimDataValidator()
    return validator.batch_validate(claims_data)


if __name__ == "__main__":
    # Example usage
    sample_claim = {
        "claim_id": "BPA-2025-0001",
        "provider": {
            "name": "Al Hayat Hospital",
            "code": "AH001",
            "branch": "MainRiyadh"
        },
        "patient": {
            "member_id": "BP123456789",
            "name": "Ahmed Al-Rashid",
            "national_id": "1234567890"
        },
        "claim_details": {
            "service_date": "2025-01-15",
            "total_amount": 12500.00,
            "currency": "SAR",
            "diagnosis_codes": ["I10", "E11.9"],
            "procedure_codes": ["99213", "36415"],
            "type": "outpatient"
        }
    }
    
    validator = ClaimDataValidator()
    result = validator.validate_claim(sample_claim)
    print(json.dumps(result, indent=2, default=str))
