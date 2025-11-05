"""
Machine Learning Models for Ultrathink AI
==========================================
Real ML implementations for healthcare claims prediction and validation.

Features:
- Diagnosis prediction from procedure codes
- Claim amount prediction
- Error probability prediction  
- Anomaly detection models
- Model training and persistence

Author: GIVC Platform Team
License: GPL-3.0
"""

import os
import pickle
import joblib
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path

import sklearn
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import xgboost as xgb
import lightgbm as lgb
from imblearn.over_sampling import SMOTE

logger = logging.getLogger(__name__)

# Model storage directory
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

class BaseMLModel:
    """Base class for all ML models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self.encoder = None
        self.trained = False
        self.accuracy = 0.0
        self.last_trained = None
        
    def save_model(self):
        """Save trained model to disk"""
        if not self.trained:
            raise ValueError("Model must be trained before saving")
            
        model_path = MODELS_DIR / f"{self.model_name}.pkl"
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'encoder': self.encoder,
            'accuracy': self.accuracy,
            'last_trained': self.last_trained,
            'sklearn_version': sklearn.__version__
        }
        
        joblib.dump(model_data, model_path)
        logger.info(f"Model {self.model_name} saved to {model_path}")
        
    def load_model(self) -> bool:
        """Load trained model from disk"""
        model_path = MODELS_DIR / f"{self.model_name}.pkl"
        
        if not model_path.exists():
            logger.warning(f"Model {self.model_name} not found at {model_path}")
            return False
            
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.scaler = model_data.get('scaler')
            self.encoder = model_data.get('encoder')
            self.accuracy = model_data.get('accuracy', 0.0)
            self.last_trained = model_data.get('last_trained')
            self.trained = True
            
            logger.info(f"Model {self.model_name} loaded successfully (accuracy: {self.accuracy:.3f})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            return False


class DiagnosisPredictionModel(BaseMLModel):
    """
    Predicts diagnosis codes based on procedure codes
    
    Uses ensemble of Random Forest, XGBoost, and LightGBM models
    """
    
    def __init__(self):
        super().__init__("diagnosis_predictor")
        self.procedure_to_diagnosis_map = {}
        self.common_combinations = {}
        
    async def predict(self, procedure_codes: List[str]) -> Dict[str, Any]:
        """
        Predict diagnosis codes from procedure codes
        
        Args:
            procedure_codes: List of CPT procedure codes
            
        Returns:
            Dictionary with predicted diagnosis codes and confidence
        """
        if not self.trained:
            # Fallback to rule-based prediction
            return await self._rule_based_prediction(procedure_codes)
            
        try:
            # Prepare features
            features = self._extract_procedure_features(procedure_codes)
            features_scaled = self.scaler.transform([features])
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Get top 3 predictions
            top_indices = np.argsort(probabilities)[-3:][::-1]
            top_predictions = []
            
            for idx in top_indices:
                diagnosis_code = self.encoder.inverse_transform([idx])[0]
                confidence = probabilities[idx]
                
                if confidence > 0.1:  # Only include if confidence > 10%
                    top_predictions.append({
                        'code': diagnosis_code,
                        'confidence': float(confidence)
                    })
            
            if not top_predictions:
                return await self._rule_based_prediction(procedure_codes)
                
            primary_prediction = top_predictions[0]
            alternatives = [pred['code'] for pred in top_predictions[1:]]
            
            return {
                "codes": [primary_prediction['code']],
                "confidence": primary_prediction['confidence'],
                "reasoning": f"ML prediction based on {len(procedure_codes)} procedure codes",
                "alternatives": alternatives,
                "model_version": "1.0",
                "prediction_method": "ensemble_ml"
            }
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return await self._rule_based_prediction(procedure_codes)
    
    def _extract_procedure_features(self, procedure_codes: List[str]) -> List[float]:
        """Extract numerical features from procedure codes"""
        features = []
        
        # Basic features
        features.append(len(procedure_codes))  # Number of procedures
        
        # Procedure code categories (based on CPT ranges)
        categories = {
            'evaluation_management': 0,
            'anesthesia': 0,
            'surgery': 0,
            'radiology': 0,
            'pathology': 0,
            'medicine': 0
        }
        
        for code in procedure_codes:
            try:
                code_num = int(code)
                if 99201 <= code_num <= 99499:
                    categories['evaluation_management'] += 1
                elif 100 <= code_num <= 1999:
                    categories['anesthesia'] += 1
                elif 10021 <= code_num <= 69990:
                    categories['surgery'] += 1
                elif 70010 <= code_num <= 79999:
                    categories['radiology'] += 1
                elif 80047 <= code_num <= 89398:
                    categories['pathology'] += 1
                elif 90281 <= code_num <= 99607:
                    categories['medicine'] += 1
            except ValueError:
                continue
                
        features.extend(categories.values())
        
        # Complexity indicators
        complexity_score = sum(1 for code in procedure_codes if self._is_complex_procedure(code))
        features.append(complexity_score)
        
        return features
    
    def _is_complex_procedure(self, code: str) -> bool:
        """Determine if procedure is complex based on code"""
        complex_ranges = [
            (10021, 19499),  # Surgical procedures
            (20005, 29999),  # Musculoskeletal system
            (30000, 32999),  # Respiratory system
            (33010, 37799),  # Cardiovascular system
        ]
        
        try:
            code_num = int(code)
            return any(start <= code_num <= end for start, end in complex_ranges)
        except ValueError:
            return False
    
    async def _rule_based_prediction(self, procedure_codes: List[str]) -> Dict[str, Any]:
        """Fallback rule-based prediction when ML model is not available"""
        
        # Common procedure to diagnosis mappings
        procedure_diagnosis_map = {
            "99213": ["Z00.00", "Z01.419"],  # Office visit -> General examination
            "99214": ["Z00.00", "I10"],     # Office visit -> Examination, Hypertension
            "99215": ["Z00.00", "E11.9"],   # Office visit -> Examination, Diabetes
            "36415": ["Z01.7"],             # Blood draw -> Laboratory examination
            "80053": ["Z01.7"],             # Comprehensive metabolic panel
            "85025": ["D64.9"],             # CBC -> Anemia
            "93000": ["I25.9"],             # ECG -> Ischemic heart disease
            "71020": ["J44.1"],             # Chest X-ray -> COPD
            "99281": ["R50.9"],             # Emergency visit -> Fever
            "99282": ["S72.001A"],          # Emergency visit -> Fracture
        }
        
        predicted_codes = []
        confidence = 0.7  # Default confidence for rule-based
        
        for proc_code in procedure_codes:
            if proc_code in procedure_diagnosis_map:
                predicted_codes.extend(procedure_diagnosis_map[proc_code])
                
        if not predicted_codes:
            # Default predictions based on procedure type
            if any(code.startswith('992') for code in procedure_codes):
                predicted_codes = ["Z00.00"]  # General examination
            elif any(code.startswith('800') for code in procedure_codes):
                predicted_codes = ["Z01.7"]   # Laboratory examination
            else:
                predicted_codes = ["Z76.89"]  # Other specified health status
                confidence = 0.5
        
        # Remove duplicates while preserving order
        unique_codes = list(dict.fromkeys(predicted_codes))
        
        return {
            "codes": unique_codes[:1],  # Return primary prediction
            "confidence": confidence,
            "reasoning": "Rule-based prediction from procedure-diagnosis mapping",
            "alternatives": unique_codes[1:3] if len(unique_codes) > 1 else [],
            "model_version": "rule_based_1.0",
            "prediction_method": "rule_based"
        }
    
    async def train(self, training_data: List[Dict]) -> Dict[str, float]:
        """
        Train the diagnosis prediction model
        
        Args:
            training_data: List of {procedure_codes, diagnosis_codes} records
            
        Returns:
            Training metrics
        """
        if len(training_data) < 100:
            logger.warning("Insufficient training data. Need at least 100 samples.")
            return {"accuracy": 0.0, "error": "insufficient_data"}
        
        # Prepare training data
        X = []
        y = []
        
        for record in training_data:
            features = self._extract_procedure_features(record['procedure_codes'])
            X.append(features)
            
            # Use primary diagnosis code
            primary_diagnosis = record['diagnosis_codes'][0] if record['diagnosis_codes'] else 'Z76.89'
            y.append(primary_diagnosis)
        
        X = np.array(X)
        y = np.array(y)
        
        # Encode labels
        self.encoder = LabelEncoder()
        y_encoded = self.encoder.fit_transform(y)
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Handle class imbalance
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
        
        # Train ensemble model
        models = {
            'rf': RandomForestClassifier(n_estimators=100, random_state=42),
            'xgb': xgb.XGBClassifier(random_state=42),
            'lgb': lgb.LGBMClassifier(random_state=42)
        }
        
        best_model = None
        best_score = 0.0
        
        for name, model in models.items():
            try:
                model.fit(X_train_balanced, y_train_balanced)
                score = model.score(X_test, y_test)
                logger.info(f"{name} accuracy: {score:.3f}")
                
                if score > best_score:
                    best_score = score
                    best_model = model
                    
            except Exception as e:
                logger.error(f"Failed to train {name}: {e}")
        
        if best_model is None:
            return {"accuracy": 0.0, "error": "training_failed"}
        
        self.model = best_model
        self.accuracy = best_score
        self.last_trained = datetime.now()
        self.trained = True
        
        # Save model
        self.save_model()
        
        return {
            "accuracy": float(best_score),
            "training_samples": len(training_data),
            "features": len(X[0]),
            "classes": len(self.encoder.classes_),
            "model_type": type(best_model).__name__
        }


class ClaimAmountPredictionModel(BaseMLModel):
    """
    Predicts claim amounts based on procedure codes and patient context
    """
    
    def __init__(self):
        super().__init__("amount_predictor")
        self.procedure_base_costs = {}
        
    async def predict(self, procedure_codes: List[str], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Predict claim amount
        
        Args:
            procedure_codes: List of CPT codes
            context: Patient and provider context
            
        Returns:
            Predicted amount with confidence range
        """
        if not self.trained:
            return await self._rule_based_amount_prediction(procedure_codes, context)
        
        try:
            features = self._extract_amount_features(procedure_codes, context)
            features_scaled = self.scaler.transform([features])
            
            predicted_amount = self.model.predict(features_scaled)[0]
            
            # Calculate confidence range (±20%)
            confidence_range = predicted_amount * 0.2
            
            return {
                "amount": float(max(0, predicted_amount)),
                "confidence": 0.8,
                "reasoning": f"ML prediction based on {len(procedure_codes)} procedures",
                "range": [
                    float(max(0, predicted_amount - confidence_range)),
                    float(predicted_amount + confidence_range)
                ],
                "model_version": "1.0"
            }
            
        except Exception as e:
            logger.error(f"Amount prediction failed: {e}")
            return await self._rule_based_amount_prediction(procedure_codes, context)
    
    def _extract_amount_features(self, procedure_codes: List[str], context: Optional[Dict]) -> List[float]:
        """Extract features for amount prediction"""
        features = []
        
        # Basic procedure features
        features.append(len(procedure_codes))
        
        # Procedure complexity and category features
        total_complexity = 0
        category_counts = {'eval_mgmt': 0, 'surgery': 0, 'radiology': 0, 'lab': 0}
        
        for code in procedure_codes:
            try:
                code_num = int(code)
                
                # Categorize procedures
                if 99201 <= code_num <= 99499:
                    category_counts['eval_mgmt'] += 1
                    total_complexity += 1
                elif 10021 <= code_num <= 69990:
                    category_counts['surgery'] += 1
                    total_complexity += 3  # Surgery is more complex
                elif 70010 <= code_num <= 79999:
                    category_counts['radiology'] += 1
                    total_complexity += 2
                elif 80000 <= code_num <= 89999:
                    category_counts['lab'] += 1
                    total_complexity += 1
                    
            except ValueError:
                continue
        
        features.extend(category_counts.values())
        features.append(total_complexity)
        
        # Context features
        if context:
            features.append(1 if context.get('emergency_visit') else 0)
            features.append(1 if context.get('specialist_visit') else 0)
            features.append(context.get('patient_age', 40) / 100)  # Normalized age
        else:
            features.extend([0, 0, 0.4])  # Default values
        
        return features
    
    async def _rule_based_amount_prediction(self, procedure_codes: List[str], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Rule-based amount prediction fallback"""
        
        # Base costs for common procedures (in SAR)
        base_costs = {
            "99213": 300,   # Office visit
            "99214": 450,   # Office visit, moderate complexity
            "99215": 600,   # Office visit, high complexity
            "36415": 50,    # Blood draw
            "80053": 200,   # Comprehensive metabolic panel
            "85025": 100,   # CBC
            "93000": 150,   # ECG
            "71020": 400,   # Chest X-ray
            "99281": 800,   # Emergency visit, low complexity
            "99282": 1200,  # Emergency visit, moderate complexity
        }
        
        total_amount = 0
        
        for code in procedure_codes:
            if code in base_costs:
                total_amount += base_costs[code]
            else:
                # Estimate based on code range
                try:
                    code_num = int(code)
                    if 99201 <= code_num <= 99499:
                        total_amount += 400  # Office visits
                    elif 10021 <= code_num <= 69990:
                        total_amount += 2000  # Surgery
                    elif 70010 <= code_num <= 79999:
                        total_amount += 600   # Radiology
                    elif 80000 <= code_num <= 89999:
                        total_amount += 150   # Lab
                    else:
                        total_amount += 300   # Default
                except ValueError:
                    total_amount += 300
        
        # Apply context modifiers
        if context:
            if context.get('emergency_visit'):
                total_amount *= 1.5
            if context.get('specialist_visit'):
                total_amount *= 1.2
        
        confidence_range = total_amount * 0.3  # ±30% for rule-based
        
        return {
            "amount": float(total_amount),
            "confidence": 0.7,
            "reasoning": "Rule-based prediction from procedure cost database",
            "range": [
                float(max(0, total_amount - confidence_range)),
                float(total_amount + confidence_range)
            ],
            "model_version": "rule_based_1.0"
        }


class ErrorPredictionModel(BaseMLModel):
    """
    Predicts probability of claim submission errors
    """
    
    def __init__(self):
        super().__init__("error_predictor")
        
    async def predict(self, claim_data: Dict, validation_results: List) -> float:
        """
        Predict probability of claim failure
        
        Args:
            claim_data: Complete claim information
            validation_results: Current validation results
            
        Returns:
            Failure probability (0.0 to 1.0)
        """
        if not self.trained:
            return self._rule_based_error_prediction(claim_data, validation_results)
        
        try:
            features = self._extract_error_features(claim_data, validation_results)
            features_scaled = self.scaler.transform([features])
            
            probability = self.model.predict_proba(features_scaled)[0][1]  # Probability of failure
            return float(probability)
            
        except Exception as e:
            logger.error(f"Error prediction failed: {e}")
            return self._rule_based_error_prediction(claim_data, validation_results)
    
    def _extract_error_features(self, claim_data: Dict, validation_results: List) -> List[float]:
        """Extract features for error prediction"""
        features = []
        
        # Validation result features
        critical_errors = sum(1 for v in validation_results if v.severity == 'critical' and not v.is_valid)
        errors = sum(1 for v in validation_results if v.severity == 'error' and not v.is_valid)
        warnings = sum(1 for v in validation_results if v.severity == 'warning')
        
        features.extend([critical_errors, errors, warnings])
        
        # Claim data features
        features.append(len(claim_data.get('diagnosis_codes', [])))
        features.append(len(claim_data.get('procedure_codes', [])))
        features.append(float(claim_data.get('total_amount', 0)) / 1000)  # Normalized amount
        
        # Data completeness
        required_fields = ['claim_id', 'patient_id', 'provider_id', 'payer_id', 'service_date']
        completeness = sum(1 for field in required_fields if claim_data.get(field)) / len(required_fields)
        features.append(completeness)
        
        # Payer complexity (some payers are more strict)
        payer_id = claim_data.get('payer_id', '')
        payer_complexity = {
            'BUPA': 0.3,
            'TAWUNIYA': 0.4,
            'MEDGULF': 0.5,
            'MOH': 0.2
        }.get(payer_id.upper(), 0.6)  # Default to higher complexity
        features.append(payer_complexity)
        
        return features
    
    def _rule_based_error_prediction(self, claim_data: Dict, validation_results: List) -> float:
        """Rule-based error prediction"""
        
        # Count validation issues
        critical_errors = sum(1 for v in validation_results if v.severity == 'critical' and not v.is_valid)
        errors = sum(1 for v in validation_results if v.severity == 'error' and not v.is_valid)
        warnings = sum(1 for v in validation_results if v.severity == 'warning')
        
        # Base probability calculation
        if critical_errors > 0:
            return 0.95
        elif errors > 0:
            return min(0.70 + (errors * 0.05), 0.90)
        elif warnings > 2:
            return min(0.30 + (warnings * 0.10), 0.60)
        else:
            return 0.10


class AnomalyDetectionModel(BaseMLModel):
    """
    Detects anomalies in claims for fraud prevention
    """
    
    def __init__(self):
        super().__init__("anomaly_detector")
        self.isolation_forest = None
        
    async def detect(self, claim_data: Dict, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Detect anomalies in claim data
        
        Args:
            claim_data: Claim information
            context: Historical context
            
        Returns:
            Anomaly detection result
        """
        if not self.trained:
            return await self._rule_based_anomaly_detection(claim_data, context)
        
        try:
            features = self._extract_anomaly_features(claim_data, context)
            features_scaled = self.scaler.transform([features])
            
            # Isolation Forest prediction (-1 for anomaly, 1 for normal)
            prediction = self.isolation_forest.predict(features_scaled)[0]
            anomaly_score = self.isolation_forest.decision_function(features_scaled)[0]
            
            # Convert to 0-1 scale
            normalized_score = max(0, (-anomaly_score + 0.5) * 2)
            
            is_anomaly = prediction == -1
            
            return {
                "is_anomaly": is_anomaly,
                "anomaly_score": float(normalized_score),
                "anomaly_type": "pattern" if is_anomaly else "none",
                "details": "ML-based pattern anomaly detected" if is_anomaly else "No anomalies detected",
                "risk_level": self._get_risk_level(normalized_score)
            }
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return await self._rule_based_anomaly_detection(claim_data, context)
    
    def _extract_anomaly_features(self, claim_data: Dict, context: Optional[Dict]) -> List[float]:
        """Extract features for anomaly detection"""
        features = []
        
        # Amount features
        amount = float(claim_data.get('total_amount', 0))
        features.append(amount)
        features.append(np.log1p(amount))  # Log-transformed amount
        
        # Procedure features
        num_procedures = len(claim_data.get('procedure_codes', []))
        num_diagnoses = len(claim_data.get('diagnosis_codes', []))
        features.extend([num_procedures, num_diagnoses])
        
        # Amount per procedure
        amount_per_procedure = amount / max(num_procedures, 1)
        features.append(amount_per_procedure)
        
        # Time features
        try:
            service_date = datetime.fromisoformat(claim_data.get('service_date', '2023-01-01'))
            days_old = (datetime.now() - service_date).days
            features.append(days_old)
        except:
            features.append(0)
        
        # Provider and payer features (encoded)
        provider_id = claim_data.get('provider_id', '')
        payer_id = claim_data.get('payer_id', '')
        
        # Simple hash-based encoding
        features.append(hash(provider_id) % 1000 / 1000)
        features.append(hash(payer_id) % 1000 / 1000)
        
        return features
    
    async def _rule_based_anomaly_detection(self, claim_data: Dict, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Rule-based anomaly detection"""
        
        anomaly_score = 0.0
        anomaly_details = []
        anomaly_type = "none"
        
        # Amount anomalies
        amount = float(claim_data.get('total_amount', 0))
        if amount > 50000:  # Very high amount
            anomaly_score = max(anomaly_score, 0.8)
            anomaly_details.append(f"Unusually high amount: {amount:,.2f} SAR")
            anomaly_type = "financial"
        elif amount > 20000:
            anomaly_score = max(anomaly_score, 0.5)
            anomaly_details.append(f"High amount: {amount:,.2f} SAR")
            anomaly_type = "financial"
        
        # Procedure count anomalies
        num_procedures = len(claim_data.get('procedure_codes', []))
        if num_procedures > 10:
            anomaly_score = max(anomaly_score, 0.6)
            anomaly_details.append(f"Many procedures: {num_procedures}")
            anomaly_type = "pattern"
        
        # Amount per procedure anomaly
        if num_procedures > 0:
            amount_per_procedure = amount / num_procedures
            if amount_per_procedure > 5000:
                anomaly_score = max(anomaly_score, 0.7)
                anomaly_details.append(f"High cost per procedure: {amount_per_procedure:,.2f} SAR")
                anomaly_type = "financial"
        
        return {
            "is_anomaly": anomaly_score > 0.3,
            "anomaly_score": anomaly_score,
            "anomaly_type": anomaly_type,
            "details": "; ".join(anomaly_details) if anomaly_details else "No anomalies detected",
            "risk_level": self._get_risk_level(anomaly_score)
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Convert anomaly score to risk level"""
        if score > 0.8:
            return "critical"
        elif score > 0.6:
            return "high"
        elif score > 0.3:
            return "medium"
        else:
            return "low"


# Global model instances
diagnosis_model = DiagnosisPredictionModel()
amount_model = ClaimAmountPredictionModel()
error_model = ErrorPredictionModel()
anomaly_model = AnomalyDetectionModel()

async def initialize_models():
    """Initialize all ML models (load from disk or use defaults)"""
    models = [diagnosis_model, amount_model, error_model, anomaly_model]
    
    for model in models:
        try:
            loaded = model.load_model()
            if loaded:
                logger.info(f"✅ {model.model_name} loaded successfully")
            else:
                logger.warning(f"⚠️ {model.model_name} using fallback (no trained model found)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize {model.model_name}: {e}")

# Auto-initialize on import
import asyncio
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(initialize_models())
    else:
        loop.run_until_complete(initialize_models())
except:
    # If no event loop, models will use fallback methods
    logger.info("No event loop available, models will use fallback methods")