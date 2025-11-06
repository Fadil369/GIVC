"""
ClaimLinc Test Data Generator and Reports Module
Generates synthetic test data for different payer formats and creates various reports
"""

import json
import random
import csv
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd
from faker import Faker
import uuid


class TestDataGenerator:
    """Generates synthetic test data for various claim formats"""
    
    def __init__(self, locale='en_SA'):  # Saudi Arabia locale
        self.fake = Faker(locale)
        self.payers = {
            "bupa": "Bupa Arabia",
            "globemed": "GlobeMed Saudi Arabia", 
            "waseel": "Tawuniya Insurance Company"
        }
        
        self.branches = [
            "MainRiyadh", "Unaizah", "Abha", "Madinah", "Khamis"
        ]
        
        # Medical codes for realistic test data
        self.diagnosis_codes = [
            "I10", "E11.9", "J44.0", "M79.3", "N18.6", "K21.9",
            "I25.10", "Z51.11", "S72.00", "G47.00", "F32.9", "J06.9"
        ]
        
        self.procedure_codes = [
            "99213", "99214", "99215", "36415", "80048", "93000",
            "99401", "99402", "90471", "90472", "76700", "73060"
        ]
        
        self.member_id_prefixes = {
            "bupa": "BP",
            "globemed": "GM", 
            "waseel": "TW"
        }
    
    def generate_single_claim(self, payer_format: str = "bupa", **overrides) -> Dict[str, Any]:
        """Generate a single synthetic claim"""
        if payer_format.lower() == "bupa":
            return self._generate_bupa_claim(**overrides)
        elif payer_format.lower() == "globemed":
            return self._generate_globemed_claim(**overrides)
        elif payer_format.lower() == "waseel":
            return self._generate_waseel_claim(**overrides)
        else:
            raise ValueError(f"Unsupported payer format: {payer_format}")
    
    def _generate_bupa_claim(self, **overrides) -> Dict[str, Any]:
        """Generate a Bupa format claim"""
        claim_id = overrides.get("claim_id", f"BPA-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}")
        
        return {
            "claim_id": claim_id,
            "provider": {
                "name": overrides.get("provider_name", "Al Hayat Hospital"),
                "code": overrides.get("provider_code", "AH001"),
                "branch": overrides.get("branch", random.choice(self.branches))
            },
            "patient": {
                "member_id": overrides.get("member_id", f"{self.member_id_prefixes['bupa']}{random.randint(100000000, 999999999)}"),
                "name": overrides.get("patient_name", self.fake.name()),
                "national_id": overrides.get("national_id", f"{random.randint(1000000000, 9999999999)}"),
                "date_of_birth": overrides.get("date_of_birth", self.fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat()),
                "gender": overrides.get("gender", random.choice(["M", "F"]))
            },
            "claim_details": {
                "service_date": overrides.get("service_date", self.fake.date_between(start_date='-30d', end_date='today').isoformat()),
                "admission_date": overrides.get("admission_date"),
                "discharge_date": overrides.get("discharge_date"),
                "type": overrides.get("claim_type", random.choice(["inpatient", "outpatient", "emergency", "surgery", "consultation"])),
                "total_amount": overrides.get("total_amount", round(random.uniform(100, 50000), 2)),
                "currency": overrides.get("currency", "SAR"),
                "diagnosis_codes": overrides.get("diagnosis_codes", random.sample(self.diagnosis_codes, random.randint(1, 3))),
                "procedure_codes": overrides.get("procedure_codes", random.sample(self.procedure_codes, random.randint(1, 4)))
            },
            "payer": {
                "name": overrides.get("payer_name", self.payers["bupa"]),
                "insurance_type": overrides.get("insurance_type", "health"),
                "policy_number": overrides.get("policy_number", f"BPH-{random.randint(100000, 999999)}")
            },
            "submission": {
                "method": overrides.get("submission_method", "portal"),
                "timestamp": overrides.get("timestamp", datetime.now().isoformat()),
                "batch_id": overrides.get("batch_id", f"BPA-BATCH-{datetime.now().strftime('%Y%m%d')}"),
                "status": overrides.get("status", "submitted")
            },
            "metadata": {
                "created_by": overrides.get("created_by", "TestGenerator"),
                "version": overrides.get("version", "1.0"),
                "source_system": overrides.get("source_system", "EMR-Test")
            }
        }
    
    def _generate_globemed_claim(self, **overrides) -> Dict[str, Any]:
        """Generate a GlobeMed format claim"""
        claim_id = overrides.get("claim_id", f"GLB-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}")
        diagnosis_count = random.randint(1, 4)
        procedure_count = random.randint(1, 5)
        
        return {
            "claimId": claim_id,
            "batchNumber": overrides.get("batch_number", f"GLB-BATCH-{datetime.now().strftime('%Y%m%d')}"),
            "providerInfo": {
                "providerCode": overrides.get("provider_code", "AH001"),
                "providerName": overrides.get("provider_name", "Al Hayat Hospital"),
                "branch": overrides.get("branch", random.choice(self.branches)),
                "contactPerson": overrides.get("contact_person", self.fake.name()),
                "phone": overrides.get("phone", self.fake.phone_number()),
                "email": overrides.get("email", f"billing@{overrides.get('branch', 'main').lower()}.alhayat.example")
            },
            "subscriberInfo": {
                "memberId": overrides.get("member_id", f"{self.member_id_prefixes['globemed']}{random.randint(100000000, 999999999)}"),
                "memberName": overrides.get("member_name", self.fake.name()),
                "nationalId": overrides.get("national_id", f"{random.randint(1000000000, 9999999999)}"),
                "gender": overrides.get("gender", random.choice(["M", "F"])),
                "dateOfBirth": overrides.get("date_of_birth", self.fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat()),
                "relationship": overrides.get("relationship", "self"),
                "policyNumber": overrides.get("policy_number", f"GMH-{random.randint(100000, 999999)}"),
                "effectiveDate": overrides.get("effective_date", "2025-01-01"),
                "expirationDate": overrides.get("expiration_date", "2025-12-31")
            },
            "claimDetails": {
                "serviceType": overrides.get("service_type", random.choice(["outpatient", "inpatient", "emergency"])),
                "serviceDate": overrides.get("service_date", self.fake.date_between(start_date='-30d', end_date='today').isoformat()),
                "admissionDate": overrides.get("admission_date"),
                "dischargeDate": overrides.get("discharge_date"),
                "totalAmount": overrides.get("total_amount", round(random.uniform(200, 75000), 2)),
                "currency": overrides.get("currency", "SAR"),
                "providerFees": overrides.get("provider_fees"),
                "patientResponsibility": overrides.get("patient_responsibility", round(random.uniform(50, 15000), 2)),
                "insurancePayment": overrides.get("insurance_payment")
            },
            "diagnosisInformation": [
                {
                    "sequence": i + 1,
                    "diagnosisCode": code,
                    "diagnosisDescription": self._get_diagnosis_description(code),
                    "diagnosisType": "primary" if i == 0 else "secondary"
                }
                for i, code in enumerate(overrides.get("diagnosis_codes", random.sample(self.diagnosis_codes, diagnosis_count)))
            ],
            "procedureInformation": [
                {
                    "sequence": i + 1,
                    "procedureCode": code,
                    "procedureDescription": self._get_procedure_description(code),
                    "procedureDate": overrides.get("service_date", self.fake.date_between(start_date='-30d', end_date='today').isoformat()),
                    "quantity": 1,
                    "unitPrice": round(random.uniform(50, 2000), 2),
                    "totalAmount": round(random.uniform(50, 2000), 2)
                }
                for i, code in enumerate(overrides.get("procedure_codes", random.sample(self.procedure_codes, procedure_count)))
            ],
            "medicationDetails": overrides.get("medication_details", [
                {
                    "medicationName": self.fake.word().capitalize(),
                    "medicationCode": f"J{random.randint(1000, 9999)}",
                    "quantity": random.randint(1, 30),
                    "unit": "units",
                    "unitPrice": round(random.uniform(0.5, 50), 3),
                    "totalAmount": round(random.uniform(10, 500), 2)
                }
            ]),
            "insuranceInfo": {
                "payerName": overrides.get("payer_name", self.payers["globemed"]),
                "payerCode": "GM001",
                "planName": overrides.get("plan_name", "GlobeMed Health Plan Plus"),
                "copayPercentage": overrides.get("copay_percentage", 20),
                "deductibleAmount": overrides.get("deductible_amount", 500.00),
                "outOfPocketMax": overrides.get("out_of_pocket_max", 3000.00)
            },
            "authorizationInfo": {
                "preAuthorizationRequired": overrides.get("pre_auth_required", random.choice([True, False])),
                "authorizationNumber": overrides.get("authorization_number", f"AUTH-GM-{random.randint(100000, 999999)}") if random.choice([True, False]) else None,
                "authorizationDate": overrides.get("authorization_date", self.fake.date_between(start_date='-60d', end_date='-1d').isoformat()) if random.choice([True, False]) else None,
                "validFrom": overrides.get("valid_from", self.fake.date_between(start_date='-60d', end_date='-1d').isoformat()) if random.choice([True, False]) else None,
                "validTo": overrides.get("valid_to", self.fake.date_between(start_date='+1d', end_date='+60d').isoformat()) if random.choice([True, False]) else None,
                "authorizedUnits": overrides.get("authorized_units", random.randint(1, 10)) if random.choice([True, False]) else None
            },
            "submissionDetails": {
                "submissionMethod": overrides.get("submission_method", "portal"),
                "submissionDate": overrides.get("submission_date", datetime.now().isoformat()),
                "submissionType": overrides.get("submission_type", "electronic"),
                "claimStatus": overrides.get("claim_status", "submitted"),
                "referenceNumber": overrides.get("reference_number", f"GLB-REF-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}")
            },
            "documents": overrides.get("documents", [
                {
                    "documentType": "medical_record",
                    "documentName": f"{self.fake.word()}_notes.pdf",
                    "documentSize": random.randint(500000, 2000000),
                    "uploadedDate": datetime.now().isoformat()
                }
            ]),
            "additionalInfo": {
                "attendingPhysician": overrides.get("attending_physician", self.fake.name()),
                "referringPhysician": overrides.get("referring_physician", self.fake.name()) if random.choice([True, False]) else None,
                "clinicalNotes": overrides.get("clinical_notes", self.fake.text(max_nb_chars=500)),
                "admissionReason": overrides.get("admission_reason", self.fake.sentence(nb_words=6)),
                "dischargeDisposition": overrides.get("discharge_disposition", "Home")
            }
        }
    
    def _generate_waseel_claim(self, **overrides) -> Dict[str, Any]:
        """Generate a Waseel/Tawuniya FHIR format claim"""
        claim_id = overrides.get("claim_id", f"WSE-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}")
        patient_id = overrides.get("patient_id", f"P{random.randint(1000, 9999)}")
        organization_id = overrides.get("organization_id", "AH001")
        
        return {
            "resourceType": "Bundle",
            "id": f"WSE-CLAIM-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "type": "transaction",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Claim",
                        "id": claim_id,
                        "identifier": [
                            {
                                "system": "http://hospital.example.com/claim-ids",
                                "value": claim_id
                            }
                        ],
                        "status": "active",
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                                    "code": random.choice(["institutional", "professional", "oral"]),
                                    "display": random.choice(["Institutional", "Professional", "Oral"])
                                }
                            ]
                        },
                        "patient": {
                            "reference": f"Patient/{patient_id}",
                            "display": overrides.get("patient_name", self.fake.name())
                        },
                        "provider": {
                            "reference": f"Organization/{organization_id}",
                            "display": overrides.get("provider_name", "Al Hayat Hospital")
                        },
                        "insurance": [
                            {
                                "sequence": 1,
                                "focal": True,
                                "coverage": {
                                    "reference": f"Coverage/{overrides.get('policy_number', f'C{random.randint(1000, 9999)}')}",
                                    "display": "Tawuniya Insurance Company"
                                }
                            }
                        ],
                        "billablePeriod": {
                            "start": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                            "end": datetime.now().isoformat()
                        },
                        "created": overrides.get("created_date", datetime.now().isoformat()),
                        "insurer": {
                            "reference": "Organization/T001",
                            "display": "Tawuniya Insurance Company"
                        },
                        "total": {
                            "value": overrides.get("total_amount", round(random.uniform(500, 100000), 2)),
                            "currency": overrides.get("currency", "SAR")
                        },
                        "diagnosis": [
                            {
                                "sequence": i + 1,
                                "diagnosisCodeableConcept": {
                                    "coding": [
                                        {
                                            "system": "http://hl7.org/fhir/sid/icd-10",
                                            "code": code,
                                            "display": self._get_diagnosis_description(code)
                                        }
                                    ]
                                }
                            }
                            for i, code in enumerate(overrides.get("diagnosis_codes", random.sample(self.diagnosis_codes, random.randint(1, 3))))
                        ],
                        "procedure": [
                            {
                                "sequence": i + 1,
                                "procedureCodeableConcept": {
                                    "coding": [
                                        {
                                            "system": "http://www.ama-assn.org/go/cpt",
                                            "code": code,
                                            "display": self._get_procedure_description(code)
                                        }
                                    ]
                                }
                            }
                            for i, code in enumerate(overrides.get("procedure_codes", random.sample(self.procedure_codes, random.randint(1, 4))))
                        ],
                        "item": [
                            {
                                "sequence": i + 1,
                                "productOrService": {
                                    "coding": [
                                        {
                                            "system": "http://www.ama-assn.org/go/cpt",
                                            "code": code,
                                            "display": self._get_procedure_description(code)
                                        }
                                    ]
                                },
                                "net": {
                                    "value": round(random.uniform(100, 5000), 2),
                                    "currency": "SAR"
                                }
                            }
                            for i, code in enumerate(overrides.get("procedure_codes", random.sample(self.procedure_codes, random.randint(1, 4))))
                        ]
                    }
                },
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": patient_id,
                        "identifier": [
                            {
                                "system": "http://waseel.com/member-id",
                                "value": f"{self.member_id_prefixes['waseel']}{random.randint(100000000, 999999999)}"
                            }
                        ],
                        "name": [
                            {
                                "family": overrides.get("patient_name", self.fake.name()).split()[-1],
                                "given": overrides.get("patient_name", self.fake.name()).split()[:-1]
                            }
                        ],
                        "gender": overrides.get("gender", random.choice(["male", "female"])),
                        "birthDate": overrides.get("date_of_birth", self.fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat()),
                        "address": [
                            {
                                "line": [self.fake.street_address()],
                                "city": self.fake.city(),
                                "state": self.fake.state(),
                                "postalCode": self.fake.postcode(),
                                "country": "SA"
                            }
                        ]
                    }
                },
                {
                    "resource": {
                        "resourceType": "Organization",
                        "id": organization_id,
                        "name": overrides.get("provider_name", "Al Hayat Hospital"),
                        "type": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                                        "code": "prov",
                                        "display": "Healthcare Provider"
                                    }
                                ]
                            }
                        ],
                        "contact": [
                            {
                                "purpose": "billing",
                                "name": "Billing Department",
                                "telecom": [
                                    {
                                        "system": "phone",
                                        "value": self.fake.phone_number()
                                    }
                                ]
                            }
                        ]
                    }
                }
            ],
            "meta": {
                "lastUpdated": datetime.now().isoformat(),
                "source": "EMR-System-v2.1",
                "profile": ["http://nphies.org/fhir/StructureDefinition/ClaimBundle"]
            },
            "extension": [
                {
                    "url": "http://nphies.org/fhir/StructureDefinition/provider-branch",
                    "valueCode": overrides.get("branch", random.choice(self.branches))
                }
            ]
        }
    
    def _get_diagnosis_description(self, code: str) -> str:
        """Get diagnosis description for ICD-10 code"""
        descriptions = {
            "I10": "Essential hypertension",
            "E11.9": "Type 2 diabetes mellitus without complications",
            "J44.0": "Chronic obstructive pulmonary disease with acute lower respiratory infection",
            "M79.3": "Panniculitis, unspecified",
            "N18.6": "End stage renal disease",
            "K21.9": "Gastro-esophageal reflux disease without esophagitis",
            "I25.10": "Atherosclerotic heart disease of native coronary artery without angina pectoris",
            "Z51.11": "Encounter for antineoplastic chemotherapy",
            "S72.00": "Fracture of unspecified part of femur",
            "G47.00": "Disorder of sleep cycle, unspecified",
            "F32.9": "Major depressive disorder, single episode, unspecified",
            "J06.9": "Acute upper respiratory infection, unspecified"
        }
        return descriptions.get(code, "Diagnosis description not available")
    
    def _get_procedure_description(self, code: str) -> str:
        """Get procedure description for CPT code"""
        descriptions = {
            "99213": "Office or other outpatient visit for E/M",
            "99214": "Office or other outpatient visit for E/M",
            "99215": "Office or other outpatient visit for E/M",
            "36415": "Collection of venous blood by venipuncture",
            "80048": "Basic metabolic panel",
            "93000": "Electrocardiogram, routine ECG with at least 12 leads",
            "99401": "Preventive medicine counseling",
            "99402": "Preventive medicine counseling",
            "90471": "Immunization administration",
            "90472": "Each additional vaccine",
            "76700": "Ultrasound, abdominal, real time with image documentation",
            "73060": "Radiological examination, humerus, minimum 2 views"
        }
        return descriptions.get(code, "Procedure description not available")
    
    def generate_batch_claims(self, count: int, payer_format: str = "bupa", **overrides) -> List[Dict[str, Any]]:
        """Generate multiple claims in batch"""
        claims = []
        for i in range(count):
            claim_overrides = overrides.copy()
            if "batch_size" in claim_overrides:
                del claim_overrides["batch_size"]
            
            # Add some variation to make claims more realistic
            if i % 5 == 0:  # Every 5th claim is inpatient
                claim_overrides["claim_type"] = "inpatient"
                claim_overrides["admission_date"] = (datetime.now() - timedelta(days=random.randint(1, 7))).isoformat()
                claim_overrides["discharge_date"] = datetime.now().isoformat()
            
            claim = self.generate_single_claim(payer_format, **claim_overrides)
            claims.append(claim)
        
        return claims
    
    def generate_rejection_scenarios(self, payer_format: str = "bupa") -> List[Dict[str, Any]]:
        """Generate claims with various rejection scenarios for testing"""
        rejection_scenarios = []
        
        # Missing required fields
        incomplete_claim = self.generate_single_claim(payer_format)
        if "patient" in incomplete_claim:
            del incomplete_claim["patient"]["member_id"]
        incomplete_claim["metadata"]["scenario"] = "missing_required_fields"
        rejection_scenarios.append(incomplete_claim)
        
        # Invalid dates
        invalid_date_claim = self.generate_single_claim(payer_format)
        if "claim_details" in invalid_date_claim:
            invalid_date_claim["claim_details"]["service_date"] = "2020-01-01"  # Too old
        invalid_date_claim["metadata"]["scenario"] = "invalid_service_date"
        rejection_scenarios.append(invalid_date_claim)
        
        # High amount requiring review
        high_amount_claim = self.generate_single_claim(payer_format, total_amount=500000)
        high_amount_claim["metadata"]["scenario"] = "high_amount_review"
        rejection_scenarios.append(high_amount_claim)
        
        # Missing diagnosis/procedure codes
        no_codes_claim = self.generate_single_claim(payer_format)
        if "claim_details" in no_codes_claim:
            no_codes_claim["claim_details"]["diagnosis_codes"] = []
            no_codes_claim["claim_details"]["procedure_codes"] = []
        no_codes_claim["metadata"]["scenario"] = "missing_medical_codes"
        rejection_scenarios.append(no_codes_claim)
        
        return rejection_scenarios


class ReportGenerator:
    """Generates various reports from claim data"""
    
    def __init__(self):
        self.output_dir = Path("./reports")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_summary_report(self, claims_data: List[Dict[str, Any]], output_filename: str = None) -> str:
        """Generate a comprehensive summary report"""
        if not output_filename:
            output_filename = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Analyze claims
        total_claims = len(claims_data)
        total_amount = 0
        payer_distribution = {}
        branch_distribution = {}
        claim_type_distribution = {}
        date_range = {"earliest": None, "latest": None}
        
        for claim in claims_data:
            # Total amount
            amount = self._get_nested_value(claim, ["claim_details", "total_amount"])
            if amount:
                total_amount += float(amount)
            
            # Payer distribution
            payer = self._get_nested_value(claim, ["payer", "name"])
            if payer:
                payer_distribution[payer] = payer_distribution.get(payer, 0) + 1
            
            # Branch distribution
            branch = self._get_nested_value(claim, ["provider", "branch"])
            if branch:
                branch_distribution[branch] = branch_distribution.get(branch, 0) + 1
            
            # Claim type distribution
            claim_type = self._get_nested_value(claim, ["claim_details", "type"])
            if claim_type:
                claim_type_distribution[claim_type] = claim_type_distribution.get(claim_type, 0) + 1
            
            # Date range
            service_date = self._get_nested_value(claim, ["claim_details", "service_date"])
            if service_date:
                if not date_range["earliest"] or service_date < date_range["earliest"]:
                    date_range["earliest"] = service_date
                if not date_range["latest"] or service_date > date_range["latest"]:
                    date_range["latest"] = service_date
        
        # Generate report
        report = {
            "report_metadata": {
                "report_type": "Summary Report",
                "generated_at": datetime.now().isoformat(),
                "total_claims": total_claims,
                "report_period": f"{date_range['earliest']} to {date_range['latest']}" if date_range["earliest"] else "N/A"
            },
            "financial_summary": {
                "total_amount": round(total_amount, 2),
                "average_amount": round(total_amount / total_claims, 2) if total_claims > 0 else 0,
                "currency": "SAR"
            },
            "distribution_analysis": {
                "payer_distribution": payer_distribution,
                "branch_distribution": branch_distribution,
                "claim_type_distribution": claim_type_distribution
            },
            "data_quality": {
                "claims_with_amounts": sum(1 for claim in claims_data if self._get_nested_value(claim, ["claim_details", "total_amount"])),
                "claims_with_diagnosis_codes": sum(1 for claim in claims_data if self._get_nested_value(claim, ["claim_details", "diagnosis_codes"])),
                "claims_with_procedure_codes": sum(1 for claim in claims_data if self._get_nested_value(claim, ["claim_details", "procedure_codes"]))
            }
        }
        
        # Save to JSON
        output_path = self.output_dir / f"{output_filename}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Generate CSV summary
        csv_path = self.output_dir / f"{output_filename}.csv"
        self._generate_csv_summary(claims_data, csv_path)
        
        return f"Summary report generated: {output_path} and {csv_path}"
    
    def generate_rejection_analysis_report(self, claims_data: List[Dict[str, Any]], output_filename: str = None) -> str:
        """Generate rejection analysis report based on validation results"""
        if not output_filename:
            output_filename = f"rejection_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # This would typically integrate with validation results
        # For now, generate a placeholder analysis
        
        rejection_patterns = {
            "common_rejection_reasons": {
                "Missing required field": 0.15,
                "Invalid service date": 0.12,
                "Missing diagnosis codes": 0.08,
                "Amount exceeds limits": 0.05,
                "Invalid patient ID": 0.03
            },
            "payer_specific_patterns": {
                "Bupa Arabia": {"data_quality_issues": 0.18, "missing_fields": 0.12},
                "GlobeMed Saudi Arabia": {"procedure_validation": 0.20, "authorization_missing": 0.10},
                "Tawuniya Insurance Company": {"fhir_compliance": 0.08, "member_validation": 0.07}
            }
        }
        
        report = {
            "report_metadata": {
                "report_type": "Rejection Analysis Report",
                "generated_at": datetime.now().isoformat(),
                "analysis_period": "Last 30 days",
                "total_claims_analyzed": len(claims_data)
            },
            "rejection_patterns": rejection_patterns,
            "recommendations": [
                "Implement mandatory field validation before submission",
                "Establish real-time member ID verification",
                "Create payer-specific validation rules",
                "Implement automated coding validation",
                "Set up rejection monitoring dashboard"
            ]
        }
        
        output_path = self.output_dir / f"{output_filename}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return f"Rejection analysis report generated: {output_path}"
    
    def _get_nested_value(self, data: Dict[str, Any], keys: List[str]) -> Any:
        """Get value from nested dictionary"""
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def _generate_csv_summary(self, claims_data: List[Dict[str, Any]], output_path: Path):
        """Generate CSV summary of claims"""
        csv_data = []
        for claim in claims_data:
            flat_record = {
                "claim_id": self._get_nested_value(claim, ["claim_id"]),
                "payer": self._get_nested_value(claim, ["payer", "name"]),
                "provider": self._get_nested_value(claim, ["provider", "name"]),
                "branch": self._get_nested_value(claim, ["provider", "branch"]),
                "patient_member_id": self._get_nested_value(claim, ["patient", "member_id"]),
                "patient_name": self._get_nested_value(claim, ["patient", "name"]),
                "service_date": self._get_nested_value(claim, ["claim_details", "service_date"]),
                "claim_type": self._get_nested_value(claim, ["claim_details", "type"]),
                "total_amount": self._get_nested_value(claim, ["claim_details", "total_amount"]),
                "currency": self._get_nested_value(claim, ["claim_details", "currency"]),
                "diagnosis_count": len(self._get_nested_value(claim, ["claim_details", "diagnosis_codes"]) or []),
                "procedure_count": len(self._get_nested_value(claim, ["claim_details", "procedure_codes"]) or [])
            }
            csv_data.append(flat_record)
        
        df = pd.DataFrame(csv_data)
        df.to_csv(output_path, index=False)


# Utility functions
def generate_test_claims(count: int = 10, payer_format: str = "bupa") -> List[Dict[str, Any]]:
    """Utility function to generate test claims"""
    generator = TestDataGenerator()
    return generator.generate_batch_claims(count, payer_format)


def generate_rejection_test_cases(payer_format: str = "bupa") -> List[Dict[str, Any]]:
    """Utility function to generate rejection test cases"""
    generator = TestDataGenerator()
    return generator.generate_rejection_scenarios(payer_format)


def create_summary_report(claims_data: List[Dict[str, Any]], output_filename: str = None) -> str:
    """Utility function to create summary report"""
    generator = ReportGenerator()
    return generator.generate_summary_report(claims_data, output_filename)


if __name__ == "__main__":
    # Example usage
    generator = TestDataGenerator()
    
    # Generate test claims for different payers
    bupa_claims = generator.generate_batch_claims(5, "bupa")
    globemed_claims = generator.generate_batch_claims(3, "globemed")
    waseel_claims = generator.generate_batch_claims(2, "waseel")
    
    # Generate rejection test cases
    rejection_cases = generator.generate_rejection_scenarios("bupa")
    
    # Generate summary report
    all_claims = bupa_claims + globemed_claims + waseel_claims
    report_generator = ReportGenerator()
    report_path = report_generator.generate_summary_report(all_claims, "test_data_summary")
    
    print(f"Generated {len(all_claims)} test claims")
    print(f"Generated {len(rejection_cases)} rejection test cases")
    print(f"Report saved to: {report_path}")
    
    # Save sample data files
    with open("./test_sample_bupa_claims.json", "w") as f:
        json.dump(bupa_claims, f, indent=2)
    
    with open("./test_sample_rejection_cases.json", "w") as f:
        json.dump(rejection_cases, f, indent=2)
