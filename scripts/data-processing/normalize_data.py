"""
ClaimLinc Data Normalization Module
Converts various claim data formats to standardized internal format
"""

import json
import pandas as pd
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import re


class ClaimDataNormalizer:
    """Standardizes claim data from different payer formats to internal format"""
    
    def __init__(self):
        self.standard_format = {
            "claim_id": None,
            "provider": {
                "name": None,
                "code": None,
                "branch": None
            },
            "patient": {
                "member_id": None,
                "name": None,
                "national_id": None,
                "date_of_birth": None,
                "gender": None
            },
            "claim_details": {
                "service_date": None,
                "admission_date": None,
                "discharge_date": None,
                "type": None,
                "total_amount": 0.0,
                "currency": "SAR",
                "diagnosis_codes": [],
                "procedure_codes": []
            },
            "payer": {
                "name": None,
                "insurance_type": None,
                "policy_number": None
            },
            "submission": {
                "method": None,
                "timestamp": None,
                "batch_id": None,
                "status": None
            },
            "metadata": {
                "normalized_at": None,
                "source_format": None,
                "validation_status": None
            }
        }
    
    def normalize_claim(self, claim_data: Dict[str, Any], source_format: str = "unknown") -> Dict[str, Any]:
        """
        Normalize claim data to standard format
        
        Args:
            claim_data: Raw claim data in various formats
            source_format: Source format identifier (bupa, globemed, waseel, etc.)
            
        Returns:
            Normalized claim data
        """
        try:
            # Create a copy of the standard format
            normalized = self.standard_format.copy()
            
            # Set metadata
            normalized["metadata"]["normalized_at"] = datetime.now().isoformat()
            normalized["metadata"]["source_format"] = source_format
            
            # Route to appropriate normalizer based on format
            if source_format.lower() == "bupa":
                normalized = self._normalize_bupa_format(claim_data, normalized)
            elif source_format.lower() == "globemed":
                normalized = self._normalize_globemed_format(claim_data, normalized)
            elif source_format.lower() == "waseel":
                normalized = self._normalize_waseel_format(claim_data, normalized)
            else:
                normalized = self._normalize_generic_format(claim_data, normalized)
            
            # Validate normalized data
            normalized["metadata"]["validation_status"] = self._validate_normalized_data(normalized)
            
            return normalized
            
        except Exception as e:
            return {
                "error": f"Normalization failed: {str(e)}",
                "source_data": claim_data,
                "source_format": source_format
            }
    
    def _normalize_bupa_format(self, data: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Bupa Arabia format"""
        try:
            # Claim ID
            normalized["claim_id"] = data.get("claim_id", f"BPA-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            
            # Provider information
            provider = data.get("provider", {})
            normalized["provider"]["name"] = provider.get("name", "Al Hayat Hospital")
            normalized["provider"]["code"] = provider.get("code", "AH001")
            normalized["provider"]["branch"] = self._normalize_branch_name(provider.get("branch", "MainRiyadh"))
            
            # Patient information
            patient = data.get("patient", {})
            normalized["patient"]["member_id"] = patient.get("member_id")
            normalized["patient"]["name"] = patient.get("name")
            normalized["patient"]["national_id"] = patient.get("national_id")
            normalized["patient"]["date_of_birth"] = patient.get("date_of_birth")
            normalized["patient"]["gender"] = patient.get("gender")
            
            # Claim details
            claim_details = data.get("claim_details", {})
            normalized["claim_details"]["service_date"] = self._normalize_date(claim_details.get("service_date"))
            normalized["claim_details"]["admission_date"] = self._normalize_date(claim_details.get("admission_date"))
            normalized["claim_details"]["discharge_date"] = self._normalize_date(claim_details.get("discharge_date"))
            normalized["claim_details"]["type"] = claim_details.get("type", "outpatient")
            normalized["claim_details"]["total_amount"] = float(claim_details.get("total_amount", 0))
            normalized["claim_details"]["currency"] = claim_details.get("currency", "SAR")
            normalized["claim_details"]["diagnosis_codes"] = claim_details.get("diagnosis_codes", [])
            normalized["claim_details"]["procedure_codes"] = claim_details.get("procedure_codes", [])
            
            # Payer information
            payer = data.get("payer", {})
            normalized["payer"]["name"] = payer.get("name", "Bupa Arabia")
            normalized["payer"]["insurance_type"] = payer.get("insurance_type", "health")
            normalized["payer"]["policy_number"] = payer.get("policy_number")
            
            # Submission details
            submission = data.get("submission", {})
            normalized["submission"]["method"] = submission.get("method", "portal")
            normalized["submission"]["timestamp"] = submission.get("timestamp", datetime.now().isoformat())
            normalized["submission"]["batch_id"] = submission.get("batch_id")
            normalized["submission"]["status"] = submission.get("status", "submitted")
            
            return normalized
            
        except Exception as e:
            raise ValueError(f"Bupa normalization error: {str(e)}")
    
    def _normalize_globemed_format(self, data: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize GlobeMed format"""
        try:
            # Claim ID
            normalized["claim_id"] = data.get("claimId", f"GLB-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            
            # Provider information
            provider_info = data.get("providerInfo", {})
            normalized["provider"]["name"] = provider_info.get("providerName", "Al Hayat Hospital")
            normalized["provider"]["code"] = provider_info.get("providerCode", "AH001")
            normalized["provider"]["branch"] = self._normalize_branch_name(provider_info.get("branch", "MainRiyadh"))
            
            # Patient information
            subscriber_info = data.get("subscriberInfo", {})
            normalized["patient"]["member_id"] = subscriber_info.get("memberId")
            normalized["patient"]["name"] = subscriber_info.get("memberName")
            normalized["patient"]["national_id"] = subscriber_info.get("nationalId")
            normalized["patient"]["date_of_birth"] = subscriber_info.get("dateOfBirth")
            normalized["patient"]["gender"] = subscriber_info.get("gender")
            
            # Claim details
            claim_details = data.get("claimDetails", {})
            normalized["claim_details"]["service_date"] = self._normalize_date(claim_details.get("serviceDate"))
            normalized["claim_details"]["admission_date"] = self._normalize_date(claim_details.get("admissionDate"))
            normalized["claim_details"]["discharge_date"] = self._normalize_date(claim_details.get("dischargeDate"))
            normalized["claim_details"]["type"] = claim_details.get("serviceType", "outpatient")
            normalized["claim_details"]["total_amount"] = float(claim_details.get("totalAmount", 0))
            normalized["claim_details"]["currency"] = claim_details.get("currency", "SAR")
            
            # Extract codes from detailed structures
            diagnosis_info = data.get("diagnosisInformation", [])
            procedure_info = data.get("procedureInformation", [])
            
            normalized["claim_details"]["diagnosis_codes"] = [
                diag.get("diagnosisCode") for diag in diagnosis_info if diag.get("diagnosisCode")
            ]
            normalized["claim_details"]["procedure_codes"] = [
                proc.get("procedureCode") for proc in procedure_info if proc.get("procedureCode")
            ]
            
            # Payer information
            insurance_info = data.get("insuranceInfo", {})
            normalized["payer"]["name"] = insurance_info.get("payerName", "GlobeMed Saudi Arabia")
            normalized["payer"]["insurance_type"] = "health"
            normalized["payer"]["policy_number"] = subscriber_info.get("policyNumber")
            
            # Submission details
            submission_details = data.get("submissionDetails", {})
            normalized["submission"]["method"] = submission_details.get("submissionMethod", "portal")
            normalized["submission"]["timestamp"] = submission_details.get("submissionDate", datetime.now().isoformat())
            normalized["submission"]["batch_id"] = submission_details.get("referenceNumber")
            normalized["submission"]["status"] = submission_details.get("claimStatus", "submitted")
            
            return normalized
            
        except Exception as e:
            raise ValueError(f"GlobeMed normalization error: {str(e)}")
    
    def _normalize_waseel_format(self, data: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Waseel/Tawuniya FHIR format"""
        try:
            # Handle FHIR Bundle format
            if data.get("resourceType") == "Bundle":
                return self._normalize_fhir_bundle(data, normalized)
            else:
                # Handle simplified format
                return self._normalize_generic_format(data, normalized)
                
        except Exception as e:
            raise ValueError(f"Waseel normalization error: {str(e)}")
    
    def _normalize_fhir_bundle(self, bundle: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize FHIR Bundle format"""
        try:
            # Extract Claim resource from Bundle
            claim_entry = None
            for entry in bundle.get("entry", []):
                if entry.get("resource", {}).get("resourceType") == "Claim":
                    claim_entry = entry["resource"]
                    break
            
            if not claim_entry:
                raise ValueError("No Claim resource found in FHIR Bundle")
            
            # Claim ID
            normalized["claim_id"] = claim_entry.get("id", f"WSE-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            
            # Patient information
            patient_ref = claim_entry.get("patient", {})
            normalized["patient"]["name"] = patient_ref.get("display")
            
            # Provider information
            provider_ref = claim_entry.get("provider", {})
            normalized["provider"]["name"] = provider_ref.get("display")
            normalized["provider"]["code"] = "AH001"  # Default for Al Hayat Hospital
            
            # Claim details
            normalized["claim_details"]["total_amount"] = float(claim_entry.get("total", {}).get("value", 0))
            normalized["claim_details"]["currency"] = claim_entry.get("total", {}).get("currency", "SAR")
            normalized["claim_details"]["type"] = "institutional"  # Default for FHIR claims
            
            # Extract dates
            billable_period = claim_entry.get("billablePeriod", {})
            if billable_period.get("start"):
                normalized["claim_details"]["service_date"] = self._normalize_date(billable_period["start"])
            if billable_period.get("end"):
                normalized["claim_details"]["admission_date"] = self._normalize_date(billable_period["start"])
                normalized["claim_details"]["discharge_date"] = self._normalize_date(billable_period["end"])
            
            # Extract diagnosis codes
            diagnoses = claim_entry.get("diagnosis", [])
            normalized["claim_details"]["diagnosis_codes"] = [
                diag.get("diagnosisCodeableConcept", {}).get("coding", [{}])[0].get("code")
                for diag in diagnoses
                if diag.get("diagnosisCodeableConcept", {}).get("coding", [{}])[0].get("code")
            ]
            
            # Extract procedure codes
            procedures = claim_entry.get("procedure", [])
            normalized["claim_details"]["procedure_codes"] = [
                proc.get("procedureCodeableConcept", {}).get("coding", [{}])[0].get("code")
                for proc in procedures
                if proc.get("procedureCodeableConcept", {}).get("coding", [{}])[0].get("code")
            ]
            
            # Payer information
            insurance = claim_entry.get("insurance", [])
            if insurance:
                coverage = insurance[0].get("coverage", {})
                normalized["payer"]["name"] = coverage.get("display", "Tawuniya Insurance Company")
                normalized["payer"]["policy_number"] = coverage.get("reference", "").replace("Coverage/", "")
            
            # Submission details
            normalized["submission"]["method"] = "api"
            normalized["submission"]["timestamp"] = claim_entry.get("created", datetime.now().isoformat())
            normalized["submission"]["status"] = claim_entry.get("status", "active")
            normalized["submission"]["batch_id"] = bundle.get("id")
            
            return normalized
            
        except Exception as e:
            raise ValueError(f"FHIR Bundle normalization error: {str(e)}")
    
    def _normalize_generic_format(self, data: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize generic/unknown format"""
        try:
            # Map common field names to standard format
            field_mappings = {
                "claim_id": ["claimId", "id", "claim_number"],
                "provider_name": ["provider.name", "providerName", "hospital_name"],
                "provider_code": ["provider.code", "providerCode", "hospital_code"],
                "patient_name": ["patient.name", "patientName", "member_name"],
                "patient_id": ["patient.member_id", "patientId", "memberId", "member_id"],
                "service_date": ["serviceDate", "date_of_service", "service_date"],
                "total_amount": ["totalAmount", "amount", "total_amount", "claim_amount"]
            }
            
            # Apply mappings
            for standard_field, possible_keys in field_mappings.items():
                value = self._get_nested_value(data, possible_keys)
                if value:
                    if standard_field == "claim_id":
                        normalized["claim_id"] = value
                    elif standard_field == "provider_name":
                        normalized["provider"]["name"] = value
                    elif standard_field == "provider_code":
                        normalized["provider"]["code"] = value
                    elif standard_field == "patient_name":
                        normalized["patient"]["name"] = value
                    elif standard_field == "patient_id":
                        normalized["patient"]["member_id"] = value
                    elif standard_field == "service_date":
                        normalized["claim_details"]["service_date"] = self._normalize_date(value)
                    elif standard_field == "total_amount":
                        normalized["claim_details"]["total_amount"] = float(value)
            
            # Set defaults
            normalized["claim_id"] = normalized["claim_id"] or f"GEN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            normalized["provider"]["name"] = normalized["provider"]["name"] or "Al Hayat Hospital"
            normalized["provider"]["code"] = normalized["provider"]["code"] or "AH001"
            normalized["claim_details"]["currency"] = "SAR"
            
            return normalized
            
        except Exception as e:
            raise ValueError(f"Generic normalization error: {str(e)}")
    
    def _normalize_branch_name(self, branch_name: str) -> str:
        """Normalize branch names to standard format"""
        if not branch_name:
            return "MainRiyadh"
        
        branch_lower = branch_name.lower().strip()
        
        branch_mapping = {
            "riyadh": "MainRiyadh",
            "main riyadh": "MainRiyadh",
            "unaizah": "Unaizah",
            "unizah": "Unaizah",
            "abha": "Abha",
            "madinah": "Madinah",
            "medina": "Madinah",
            "khamis": "Khamis",
            "khamis mushait": "Khamis",
            "mushait": "Khamis"
        }
        
        return branch_mapping.get(branch_lower, "MainRiyadh")
    
    def _normalize_date(self, date_input: Union[str, date, datetime]) -> Optional[str]:
        """Normalize date to ISO format"""
        if not date_input:
            return None
        
        try:
            if isinstance(date_input, (date, datetime)):
                return date_input.isoformat()
            elif isinstance(date_input, str):
                # Try common date formats
                date_formats = [
                    "%Y-%m-%d",
                    "%d/%m/%Y",
                    "%m/%d/%Y",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S"
                ]
                
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_input, fmt)
                        return parsed_date.isoformat()
                    except ValueError:
                        continue
                
                # If no format matches, return as-is
                return date_input
            
            return str(date_input)
            
        except Exception:
            return None
    
    def _get_nested_value(self, data: Dict[str, Any], keys: List[str]) -> Any:
        """Get value from nested dictionary using multiple possible keys"""
        for key_path in keys:
            if '.' in key_path:
                # Handle nested keys like "provider.name"
                keys_nested = key_path.split('.')
                value = data
                for k in keys_nested:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        value = None
                        break
                if value is not None:
                    return value
            else:
                # Handle simple keys
                if key_path in data:
                    return data[key_path]
        
        return None
    
    def _validate_normalized_data(self, normalized_data: Dict[str, Any]) -> str:
        """Validate normalized data and return status"""
        try:
            required_fields = [
                "claim_id",
                "provider.name",
                "patient.member_id",
                "claim_details.total_amount",
                "claim_details.currency"
            ]
            
            missing_fields = []
            for field in required_fields:
                value = self._get_nested_value(normalized_data, field.split('.'))
                if not value:
                    missing_fields.append(field)
            
            if missing_fields:
                return f"validation_failed: missing {', '.join(missing_fields)}"
            else:
                return "validation_passed"
                
        except Exception as e:
            return f"validation_error: {str(e)}"
    
    def batch_normalize(self, claims_data: List[Dict[str, Any]], source_format: str = "unknown") -> List[Dict[str, Any]]:
        """Normalize multiple claims in batch"""
        results = []
        for i, claim_data in enumerate(claims_data):
            try:
                normalized = self.normalize_claim(claim_data, source_format)
                normalized["batch_index"] = i
                results.append(normalized)
            except Exception as e:
                results.append({
                    "error": f"Batch normalization failed for item {i}: {str(e)}",
                    "source_data": claim_data,
                    "batch_index": i,
                    "source_format": source_format
                })
        
        return results
    
    def export_to_csv(self, normalized_claims: List[Dict[str, Any]], output_path: str) -> str:
        """Export normalized claims to CSV format"""
        try:
            # Flatten the data for CSV export
            csv_data = []
            for claim in normalized_claims:
                if "error" not in claim:
                    flat_record = {
                        "claim_id": claim.get("claim_id"),
                        "provider_name": claim.get("provider", {}).get("name"),
                        "provider_code": claim.get("provider", {}).get("code"),
                        "branch": claim.get("provider", {}).get("branch"),
                        "patient_member_id": claim.get("patient", {}).get("member_id"),
                        "patient_name": claim.get("patient", {}).get("name"),
                        "service_date": claim.get("claim_details", {}).get("service_date"),
                        "total_amount": claim.get("claim_details", {}).get("total_amount"),
                        "currency": claim.get("claim_details", {}).get("currency"),
                        "diagnosis_codes": ";".join(claim.get("claim_details", {}).get("diagnosis_codes", [])),
                        "procedure_codes": ";".join(claim.get("claim_details", {}).get("procedure_codes", [])),
                        "payer_name": claim.get("payer", {}).get("name"),
                        "validation_status": claim.get("metadata", {}).get("validation_status")
                    }
                    csv_data.append(flat_record)
            
            # Create DataFrame and export
            df = pd.DataFrame(csv_data)
            df.to_csv(output_path, index=False)
            
            return f"Successfully exported {len(csv_data)} normalized claims to {output_path}"
            
        except Exception as e:
            raise ValueError(f"CSV export failed: {str(e)}")


# Utility functions
def normalize_claim_data(claim_data: Dict[str, Any], source_format: str = "unknown") -> Dict[str, Any]:
    """Utility function to normalize a single claim"""
    normalizer = ClaimDataNormalizer()
    return normalizer.normalize_claim(claim_data, source_format)


def batch_normalize_claims(claims_data: List[Dict[str, Any]], source_format: str = "unknown") -> List[Dict[str, Any]]:
    """Utility function to normalize multiple claims"""
    normalizer = ClaimDataNormalizer()
    return normalizer.batch_normalize(claims_data, source_format)


if __name__ == "__main__":
    # Example usage
    sample_bupa_claim = {
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
            "procedure_codes": ["99213", "36415"]
        }
    }
    
    normalizer = ClaimDataNormalizer()
    normalized = normalizer.normalize_claim(sample_bupa_claim, "bupa")
    print(json.dumps(normalized, indent=2, default=str))
