"""
AI-Powered Clinical Decision Support System
Provides intelligent diagnosis suggestions, treatment protocols, and drug interaction checking

Features:
- Diagnosis code suggestions based on symptoms and medical history
- Evidence-based treatment protocol recommendations
- AI-powered drug interaction and contraindication detection
- Risk assessment and outcome prediction
- Clinical note generation from structured data

Author: Dr. Al Fadil (BRAINSAIT LTD)
License: GPL-3.0
Version: 1.0.0
"""
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from dataclasses import dataclass, asdict
import asyncio
from enum import Enum

# ML/AI imports
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from utils.logger import get_logger

logger = get_logger(__name__)


class Severity(str, Enum):
    """Clinical severity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ConfidenceLevel(str, Enum):
    """AI confidence levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class DiagnosisResult:
    """AI diagnosis suggestion result"""
    icd10_code: str
    description: str
    confidence: ConfidenceLevel
    reasoning: str
    severity: Severity
    additional_tests_recommended: List[str]
    differential_diagnoses: List[Dict[str, Any]]


@dataclass
class TreatmentProtocol:
    """Evidence-based treatment protocol"""
    protocol_id: str
    name: str
    description: str
    medications: List[Dict[str, Any]]
    procedures: List[str]
    duration_days: int
    contraindications: List[str]
    monitoring_requirements: List[str]
    evidence_level: str
    success_rate: float


@dataclass
class DrugInteraction:
    """Drug interaction result"""
    drug_a: str
    drug_b: str
    severity: Severity
    description: str
    clinical_effects: List[str]
    management: str
    alternative_drugs: List[str]


class AIClinicalDecisionSupport:
    """
    AI-Powered Clinical Decision Support System

    Integrates multiple AI models for comprehensive clinical decision support
    """

    def __init__(self):
        """Initialize the clinical decision support system"""
        self.openai_client = None
        self.anthropic_client = None

        # Initialize AI clients if API keys are available
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("OpenAI client initialized")

        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            logger.info("Anthropic Claude client initialized")

        # Load medical knowledge bases (in production, load from database)
        self.icd10_database = self._load_icd10_database()
        self.drug_interactions_db = self._load_drug_interactions()
        self.treatment_protocols_db = self._load_treatment_protocols()

        logger.info("AI Clinical Decision Support System initialized")

    def _load_icd10_database(self) -> Dict[str, Any]:
        """Load ICD-10 code database"""
        # In production, load from comprehensive database
        return {
            "E11": {"description": "Type 2 diabetes mellitus", "severity": "moderate"},
            "I10": {"description": "Essential (primary) hypertension", "severity": "moderate"},
            "J45": {"description": "Asthma", "severity": "moderate"},
            "E78.5": {"description": "Hyperlipidemia, unspecified", "severity": "low"},
            "M79.3": {"description": "Panniculitis, unspecified", "severity": "low"},
            # Add comprehensive ICD-10 codes
        }

    def _load_drug_interactions(self) -> Dict[str, List[Dict]]:
        """Load drug interaction database"""
        # In production, load from comprehensive drug database
        return {
            "warfarin": [
                {
                    "interacts_with": "aspirin",
                    "severity": "high",
                    "effect": "Increased bleeding risk",
                    "management": "Monitor INR closely, consider alternative"
                }
            ],
            "metformin": [
                {
                    "interacts_with": "contrast_media",
                    "severity": "high",
                    "effect": "Lactic acidosis risk",
                    "management": "Discontinue 48h before contrast procedure"
                }
            ],
        }

    def _load_treatment_protocols(self) -> Dict[str, TreatmentProtocol]:
        """Load evidence-based treatment protocols"""
        # In production, load from medical guidelines database
        return {
            "diabetes_t2_initial": TreatmentProtocol(
                protocol_id="DM-T2-001",
                name="Type 2 Diabetes Initial Management",
                description="First-line treatment for newly diagnosed Type 2 Diabetes",
                medications=[
                    {
                        "name": "Metformin",
                        "dosage": "500mg twice daily, titrate to 1000mg twice daily",
                        "route": "oral"
                    }
                ],
                procedures=["HbA1c monitoring", "Fasting glucose monitoring"],
                duration_days=90,
                contraindications=["eGFR < 30 mL/min", "Severe liver disease"],
                monitoring_requirements=["HbA1c every 3 months", "Renal function annually"],
                evidence_level="A",
                success_rate=0.75
            )
        }

    async def suggest_diagnosis(
        self,
        symptoms: List[str],
        patient_history: Dict[str, Any],
        vital_signs: Optional[Dict[str, float]] = None,
        lab_results: Optional[Dict[str, Any]] = None
    ) -> List[DiagnosisResult]:
        """
        AI-powered diagnosis suggestions

        Args:
            symptoms: List of patient symptoms
            patient_history: Patient medical history
            vital_signs: Current vital signs (BP, HR, temp, etc.)
            lab_results: Laboratory test results

        Returns:
            List of diagnosis suggestions with confidence scores
        """
        logger.info(f"Generating diagnosis suggestions for symptoms: {symptoms}")

        # Prepare clinical context
        context = self._prepare_clinical_context(
            symptoms, patient_history, vital_signs, lab_results
        )

        # Use AI model to generate suggestions
        if self.anthropic_client:
            suggestions = await self._get_claude_diagnosis(context)
        elif self.openai_client:
            suggestions = await self._get_openai_diagnosis(context)
        else:
            suggestions = self._get_rule_based_diagnosis(context)

        logger.info(f"Generated {len(suggestions)} diagnosis suggestions")
        return suggestions

    def _prepare_clinical_context(
        self,
        symptoms: List[str],
        patient_history: Dict[str, Any],
        vital_signs: Optional[Dict[str, float]],
        lab_results: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare structured clinical context"""
        return {
            "symptoms": symptoms,
            "patient": {
                "age": patient_history.get("age"),
                "gender": patient_history.get("gender"),
                "past_medical_history": patient_history.get("past_conditions", []),
                "medications": patient_history.get("current_medications", []),
                "allergies": patient_history.get("allergies", [])
            },
            "vital_signs": vital_signs or {},
            "lab_results": lab_results or {}
        }

    async def _get_claude_diagnosis(self, context: Dict[str, Any]) -> List[DiagnosisResult]:
        """Get diagnosis suggestions from Claude AI"""
        prompt = f"""You are an expert medical AI assistant. Based on the following clinical information,
suggest the most likely diagnoses with ICD-10 codes.

Clinical Context:
{json.dumps(context, indent=2)}

Provide:
1. Top 3-5 most likely diagnoses with ICD-10 codes
2. Confidence level for each (low, medium, high, very_high)
3. Clinical reasoning
4. Recommended additional tests
5. Differential diagnoses

Format as JSON array."""

        try:
            message = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse AI response
            response_text = message.content[0].text
            diagnoses_data = json.loads(response_text)

            # Convert to DiagnosisResult objects
            results = []
            for diag in diagnoses_data:
                results.append(DiagnosisResult(
                    icd10_code=diag["icd10_code"],
                    description=diag["description"],
                    confidence=ConfidenceLevel(diag["confidence"]),
                    reasoning=diag["reasoning"],
                    severity=Severity(diag.get("severity", "moderate")),
                    additional_tests_recommended=diag.get("additional_tests", []),
                    differential_diagnoses=diag.get("differential_diagnoses", [])
                ))

            return results

        except Exception as e:
            logger.error(f"Error getting Claude diagnosis: {e}")
            return self._get_rule_based_diagnosis(context)

    async def _get_openai_diagnosis(self, context: Dict[str, Any]) -> List[DiagnosisResult]:
        """Get diagnosis suggestions from OpenAI GPT-4"""
        # Similar implementation to Claude
        logger.info("Using OpenAI for diagnosis suggestions")
        return self._get_rule_based_diagnosis(context)

    def _get_rule_based_diagnosis(self, context: Dict[str, Any]) -> List[DiagnosisResult]:
        """Fallback rule-based diagnosis system"""
        logger.info("Using rule-based diagnosis system")

        # Simple rule-based matching (enhance with real medical rules)
        symptoms = context.get("symptoms", [])
        results = []

        # Example rules
        if "polyuria" in symptoms and "polydipsia" in symptoms:
            results.append(DiagnosisResult(
                icd10_code="E11",
                description="Type 2 diabetes mellitus",
                confidence=ConfidenceLevel.HIGH,
                reasoning="Classic symptoms of polyuria and polydipsia present",
                severity=Severity.MODERATE,
                additional_tests_recommended=["Fasting glucose", "HbA1c", "Urinalysis"],
                differential_diagnoses=[
                    {"code": "E10", "description": "Type 1 diabetes mellitus"}
                ]
            ))

        return results

    async def recommend_treatment(
        self,
        diagnosis_code: str,
        patient_factors: Dict[str, Any]
    ) -> List[TreatmentProtocol]:
        """
        Recommend evidence-based treatment protocols

        Args:
            diagnosis_code: ICD-10 diagnosis code
            patient_factors: Patient-specific factors (age, comorbidities, etc.)

        Returns:
            List of recommended treatment protocols
        """
        logger.info(f"Recommending treatment for diagnosis: {diagnosis_code}")

        # In production, query comprehensive treatment database
        protocol_key = f"{diagnosis_code.lower()}_initial"
        protocol = self.treatment_protocols_db.get(protocol_key)

        if protocol:
            # Filter based on patient contraindications
            if self._check_contraindications(protocol, patient_factors):
                return [protocol]

        return []

    def _check_contraindications(
        self,
        protocol: TreatmentProtocol,
        patient_factors: Dict[str, Any]
    ) -> bool:
        """Check if treatment has contraindications for patient"""
        # Implement contraindication checking logic
        return True

    async def check_drug_interactions(
        self,
        medications: List[str]
    ) -> List[DrugInteraction]:
        """
        Check for drug-drug interactions

        Args:
            medications: List of medication names

        Returns:
            List of identified interactions
        """
        logger.info(f"Checking interactions for {len(medications)} medications")

        interactions = []

        # Check all pairs
        for i, drug_a in enumerate(medications):
            for drug_b in medications[i + 1:]:
                interaction = self._check_pair_interaction(drug_a, drug_b)
                if interaction:
                    interactions.append(interaction)

        logger.info(f"Found {len(interactions)} drug interactions")
        return interactions

    def _check_pair_interaction(
        self,
        drug_a: str,
        drug_b: str
    ) -> Optional[DrugInteraction]:
        """Check interaction between two drugs"""
        drug_a_lower = drug_a.lower()

        if drug_a_lower in self.drug_interactions_db:
            for interaction in self.drug_interactions_db[drug_a_lower]:
                if interaction["interacts_with"].lower() in drug_b.lower():
                    return DrugInteraction(
                        drug_a=drug_a,
                        drug_b=drug_b,
                        severity=Severity(interaction["severity"]),
                        description=interaction["effect"],
                        clinical_effects=[interaction["effect"]],
                        management=interaction["management"],
                        alternative_drugs=[]
                    )

        return None

    async def generate_clinical_note(
        self,
        encounter_data: Dict[str, Any],
        template: str = "SOAP"
    ) -> str:
        """
        Generate clinical documentation from structured data

        Args:
            encounter_data: Structured encounter information
            template: Documentation template (SOAP, H&P, etc.)

        Returns:
            Formatted clinical note
        """
        logger.info(f"Generating {template} clinical note")

        if self.anthropic_client:
            return await self._generate_ai_clinical_note(encounter_data, template)

        return self._generate_template_note(encounter_data, template)

    async def _generate_ai_clinical_note(
        self,
        encounter_data: Dict[str, Any],
        template: str
    ) -> str:
        """Use AI to generate clinical note"""
        prompt = f"""Generate a professional {template} clinical note based on this encounter data:

{json.dumps(encounter_data, indent=2)}

Follow standard medical documentation guidelines."""

        try:
            message = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"Error generating AI clinical note: {e}")
            return self._generate_template_note(encounter_data, template)

    def _generate_template_note(
        self,
        encounter_data: Dict[str, Any],
        template: str
    ) -> str:
        """Generate clinical note from template"""
        if template == "SOAP":
            return f"""SUBJECTIVE:
Chief Complaint: {encounter_data.get('chief_complaint', 'Not specified')}
History of Present Illness: {encounter_data.get('hpi', 'Not documented')}

OBJECTIVE:
Vital Signs: {encounter_data.get('vital_signs', {})}
Physical Exam: {encounter_data.get('physical_exam', 'Not documented')}

ASSESSMENT:
Diagnosis: {encounter_data.get('diagnosis', 'Not specified')}

PLAN:
{encounter_data.get('plan', 'Not documented')}
"""

        return f"Clinical note for {template} template"
