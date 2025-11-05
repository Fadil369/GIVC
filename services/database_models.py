"""
Database Models for Ultrathink AI
==================================
SQLAlchemy models for ML training data, audit logs, and metrics.

Author: GIVC Platform Team
License: GPL-3.0
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

Base = declarative_base()

class ValidationAudit(Base):
    """Audit log for all validation operations"""
    __tablename__ = "validation_audits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(String, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String, index=True)
    
    # Input data
    claim_data = Column(JSON)
    context_data = Column(JSON)
    
    # Validation results
    validation_results = Column(JSON)
    total_issues = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    
    # Metadata
    processing_time_ms = Column(Float)
    ai_enabled = Column(Boolean, default=True)
    model_version = Column(String)
    
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<ValidationAudit(claim_id={self.claim_id}, issues={self.total_issues})>"


class SmartCompletionAudit(Base):
    """Audit log for smart completion operations"""
    __tablename__ = "completion_audits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True)
    user_id = Column(String, index=True)
    
    # Input data
    partial_data = Column(JSON)
    context_data = Column(JSON)
    
    # Completion results
    completions = Column(JSON)
    completions_count = Column(Integer, default=0)
    high_confidence_count = Column(Integer, default=0)
    
    # User interaction
    applied_completions = Column(JSON)  # Which completions user accepted
    user_feedback = Column(String)  # User satisfaction rating
    
    # Metadata
    processing_time_ms = Column(Float)
    model_version = Column(String)
    
    created_at = Column(DateTime, default=func.now())


class ErrorPredictionAudit(Base):
    """Audit log for error prediction operations"""
    __tablename__ = "error_prediction_audits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(String, index=True)
    user_id = Column(String, index=True)
    
    # Prediction input
    claim_data = Column(JSON)
    validation_results = Column(JSON)
    
    # Prediction output
    predicted_failure = Column(Boolean)
    failure_probability = Column(Float)
    predicted_errors = Column(JSON)
    recommendations = Column(JSON)
    
    # Actual outcome (filled after submission)
    actual_outcome = Column(String)  # success, failure, pending
    actual_errors = Column(JSON)
    prediction_accuracy = Column(Float)  # How accurate was the prediction
    
    # Metadata
    processing_time_ms = Column(Float)
    model_version = Column(String)
    
    created_at = Column(DateTime, default=func.now())
    outcome_updated_at = Column(DateTime)


class AnomalyDetectionAudit(Base):
    """Audit log for anomaly detection operations"""
    __tablename__ = "anomaly_detection_audits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(String, index=True)
    user_id = Column(String, index=True)
    
    # Detection input
    claim_data = Column(JSON)
    context_data = Column(JSON)
    
    # Detection output
    is_anomaly = Column(Boolean)
    anomaly_score = Column(Float)
    anomaly_type = Column(String)
    risk_level = Column(String)
    details = Column(Text)
    
    # Investigation results (filled by compliance team)
    investigated = Column(Boolean, default=False)
    investigation_result = Column(String)  # confirmed_fraud, false_positive, pending
    investigation_notes = Column(Text)
    investigator_id = Column(String)
    
    # Metadata
    processing_time_ms = Column(Float)
    model_version = Column(String)
    
    created_at = Column(DateTime, default=func.now())
    investigated_at = Column(DateTime)


class MLModelMetrics(Base):
    """Track ML model performance metrics"""
    __tablename__ = "ml_model_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String, index=True)
    model_version = Column(String)
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    
    # Training metadata
    training_samples = Column(Integer)
    test_samples = Column(Integer)
    features_count = Column(Integer)
    training_time_seconds = Column(Float)
    
    # Model configuration
    hyperparameters = Column(JSON)
    feature_importance = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now())


class HistoricalClaimPattern(Base):
    """Store historical claim patterns for ML training"""
    __tablename__ = "historical_claim_patterns"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Claim identifiers
    claim_id = Column(String, index=True)
    provider_id = Column(String, index=True)
    payer_id = Column(String, index=True)
    patient_id = Column(String, index=True)  # Anonymized
    
    # Claim data
    diagnosis_codes = Column(JSON)
    procedure_codes = Column(JSON)
    total_amount = Column(Float)
    service_date = Column(DateTime)
    
    # Outcomes
    submission_result = Column(String)  # success, rejected, pending
    rejection_reasons = Column(JSON)
    processing_time_days = Column(Integer)
    final_amount_paid = Column(Float)
    
    # Features for ML
    extracted_features = Column(JSON)  # Pre-computed features
    
    created_at = Column(DateTime, default=func.now())
    submission_date = Column(DateTime)
    outcome_date = Column(DateTime)


class UserFeedback(Base):
    """Store user feedback on AI predictions"""
    __tablename__ = "user_feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    session_id = Column(String)
    
    # Feedback context
    feature_type = Column(String)  # validation, completion, prediction, anomaly
    claim_id = Column(String)
    
    # Feedback data
    rating = Column(Integer)  # 1-5 scale
    helpful = Column(Boolean)
    accuracy_rating = Column(Integer)  # How accurate was the AI
    
    # Comments
    comment = Column(Text)
    suggestion = Column(Text)
    
    # AI response details
    ai_response = Column(JSON)
    user_action = Column(String)  # accepted, rejected, modified
    
    created_at = Column(DateTime, default=func.now())


class SecurityEvent(Base):
    """Security events and audit trail"""
    __tablename__ = "security_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Event details
    event_type = Column(String, index=True)  # rate_limit, sql_injection, xss_attempt, etc.
    severity = Column(String)  # low, medium, high, critical
    
    # Request details
    ip_address = Column(String, index=True)
    user_agent = Column(Text)
    request_path = Column(String)
    request_method = Column(String)
    request_payload = Column(Text)  # Sanitized
    
    # Response
    blocked = Column(Boolean, default=False)
    response_code = Column(Integer)
    
    # Context
    user_id = Column(String, index=True)
    session_id = Column(String)
    
    created_at = Column(DateTime, default=func.now())


class APIUsageMetrics(Base):
    """Track API usage for analytics"""
    __tablename__ = "api_usage_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Request details
    endpoint = Column(String, index=True)
    method = Column(String)
    user_id = Column(String, index=True)
    ip_address = Column(String)
    
    # Performance
    response_time_ms = Column(Float)
    response_code = Column(Integer)
    request_size_bytes = Column(Integer)
    response_size_bytes = Column(Integer)
    
    # AI features used
    ai_validation_used = Column(Boolean, default=False)
    smart_completion_used = Column(Boolean, default=False)
    error_prediction_used = Column(Boolean, default=False)
    anomaly_detection_used = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    date_hour = Column(String, index=True)  # YYYY-MM-DD-HH for aggregation


# Database initialization and utilities
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ultrathink")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions for common operations
class DatabaseManager:
    """Database operations manager"""
    
    @staticmethod
    async def log_validation(
        claim_id: str,
        user_id: str,
        claim_data: Dict,
        validation_results: List[Dict],
        processing_time_ms: float,
        model_version: str = "1.0"
    ):
        """Log validation operation"""
        db = SessionLocal()
        try:
            # Count issues by severity
            total_issues = len(validation_results)
            critical_count = sum(1 for v in validation_results if v.get('severity') == 'critical' and not v.get('is_valid'))
            error_count = sum(1 for v in validation_results if v.get('severity') == 'error' and not v.get('is_valid'))
            warning_count = sum(1 for v in validation_results if v.get('severity') == 'warning')
            
            audit = ValidationAudit(
                claim_id=claim_id,
                user_id=user_id,
                claim_data=claim_data,
                validation_results=validation_results,
                total_issues=total_issues,
                critical_count=critical_count,
                error_count=error_count,
                warning_count=warning_count,
                processing_time_ms=processing_time_ms,
                model_version=model_version
            )
            
            db.add(audit)
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    async def log_anomaly_detection(
        claim_id: str,
        user_id: str,
        claim_data: Dict,
        detection_result: Dict,
        processing_time_ms: float,
        model_version: str = "1.0"
    ):
        """Log anomaly detection operation"""
        db = SessionLocal()
        try:
            audit = AnomalyDetectionAudit(
                claim_id=claim_id,
                user_id=user_id,
                claim_data=claim_data,
                is_anomaly=detection_result.get('is_anomaly', False),
                anomaly_score=detection_result.get('anomaly_score', 0.0),
                anomaly_type=detection_result.get('anomaly_type', 'none'),
                risk_level=detection_result.get('risk_level', 'low'),
                details=detection_result.get('details', ''),
                processing_time_ms=processing_time_ms,
                model_version=model_version
            )
            
            db.add(audit)
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    async def log_security_event(
        event_type: str,
        severity: str,
        ip_address: str,
        request_path: str,
        blocked: bool = False,
        user_id: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """Log security event"""
        db = SessionLocal()
        try:
            event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                ip_address=ip_address,
                request_path=request_path,
                blocked=blocked,
                user_id=user_id,
                request_payload=str(details) if details else None
            )
            
            db.add(event)
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    async def record_api_usage(
        endpoint: str,
        method: str,
        response_time_ms: float,
        response_code: int,
        user_id: Optional[str] = None,
        ai_features_used: Optional[Dict[str, bool]] = None
    ):
        """Record API usage metrics"""
        db = SessionLocal()
        try:
            usage = APIUsageMetrics(
                endpoint=endpoint,
                method=method,
                user_id=user_id,
                response_time_ms=response_time_ms,
                response_code=response_code,
                ai_validation_used=ai_features_used.get('validation', False) if ai_features_used else False,
                smart_completion_used=ai_features_used.get('completion', False) if ai_features_used else False,
                error_prediction_used=ai_features_used.get('prediction', False) if ai_features_used else False,
                anomaly_detection_used=ai_features_used.get('anomaly', False) if ai_features_used else False,
                date_hour=datetime.now().strftime('%Y-%m-%d-%H')
            )
            
            db.add(usage)
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    async def get_model_performance(model_name: str, days: int = 30) -> Dict:
        """Get model performance metrics"""
        db = SessionLocal()
        try:
            from sqlalchemy import and_
            
            # Get recent metrics
            cutoff_date = datetime.now() - timedelta(days=days)
            
            recent_metrics = db.query(MLModelMetrics).filter(
                and_(
                    MLModelMetrics.model_name == model_name,
                    MLModelMetrics.created_at >= cutoff_date
                )
            ).order_by(MLModelMetrics.created_at.desc()).first()
            
            if recent_metrics:
                return {
                    "accuracy": recent_metrics.accuracy,
                    "precision": recent_metrics.precision,
                    "recall": recent_metrics.recall,
                    "f1_score": recent_metrics.f1_score,
                    "last_updated": recent_metrics.last_updated,
                    "training_samples": recent_metrics.training_samples
                }
            else:
                return {"error": "No recent metrics found"}
                
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()

# Global database manager instance
db_manager = DatabaseManager()