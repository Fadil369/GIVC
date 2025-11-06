"""
Rejection Management Model
"""
from enum import Enum
from .base import db, TimestampMixin
from datetime import datetime, timedelta


class RejectionStatus(str, Enum):
    """Rejection status"""
    NEW = 'new'
    UNDER_REVIEW = 'under_review'
    ASSIGNED = 'assigned'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    RESUBMITTED = 'resubmitted'
    APPEALED = 'appealed'
    CLOSED = 'closed'


class RejectionSeverity(str, Enum):
    """Rejection severity levels"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class Rejection(db.Model, TimestampMixin):
    """Rejection model for tracking denied claims"""
    __tablename__ = 'rejections'
    
    id = db.Column(db.Integer, primary_key=True)
    rejection_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Claim reference
    claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=False)
    
    # Payer information
    payer_id = db.Column(db.String(50), nullable=False)
    payer_name = db.Column(db.String(200), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    
    # Rejection details
    rejection_date = db.Column(db.Date, nullable=False)
    rejection_code = db.Column(db.String(50), nullable=True)
    rejection_reason = db.Column(db.Text, nullable=False)
    rejection_category = db.Column(db.String(100), nullable=True)
    
    # Financial impact
    rejected_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='SAR', nullable=False)
    
    # Status and priority
    status = db.Column(db.Enum(RejectionStatus), default=RejectionStatus.NEW, nullable=False)
    severity = db.Column(db.Enum(RejectionSeverity), default=RejectionSeverity.MEDIUM, nullable=False)
    priority = db.Column(db.Integer, default=5, nullable=False)  # 1-10
    
    # Assignment
    assigned_to = db.Column(db.String(100), nullable=True)
    assigned_date = db.Column(db.DateTime, nullable=True)
    
    # Resolution
    resolution_notes = db.Column(db.Text, nullable=True)
    resolution_date = db.Column(db.DateTime, nullable=True)
    resubmittable = db.Column(db.Boolean, default=True)
    
    # Tracking
    due_date = db.Column(db.Date, nullable=True)
    follow_up_count = db.Column(db.Integer, default=0)
    last_follow_up = db.Column(db.DateTime, nullable=True)
    
    # References
    original_claim_number = db.Column(db.String(100), nullable=True)
    payer_reference = db.Column(db.String(100), nullable=True)
    
    # Metadata
    source_file = db.Column(db.String(500), nullable=True)
    extracted_data = db.Column(db.JSON, nullable=True)
    
    # Relationships
    claim = db.relationship('Claim', backref='rejections')
    resubmissions = db.relationship('Resubmission', backref='rejection', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Rejection {self.rejection_number}>'
    
    def calculate_due_date(self):
        """Calculate due date based on payer configuration"""
        from rcm_config import PayerConfig
        payer_config = PayerConfig.get_payer_by_id(self.payer_id)
        
        if payer_config and 'appeal_deadline' in payer_config:
            days = payer_config['appeal_deadline']
            self.due_date = self.rejection_date + timedelta(days=days)
    
    def is_overdue(self) -> bool:
        """Check if rejection is overdue"""
        if self.due_date:
            return datetime.now().date() > self.due_date
        return False
    
    def days_until_due(self) -> int:
        """Calculate days until due date"""
        if self.due_date:
            delta = self.due_date - datetime.now().date()
            return delta.days
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'rejection_number': self.rejection_number,
            'claim_id': self.claim_id,
            'payer_id': self.payer_id,
            'payer_name': self.payer_name,
            'branch': self.branch,
            'rejection_date': self.rejection_date.isoformat() if self.rejection_date else None,
            'rejection_code': self.rejection_code,
            'rejection_reason': self.rejection_reason,
            'rejection_category': self.rejection_category,
            'rejected_amount': float(self.rejected_amount) if self.rejected_amount else 0,
            'currency': self.currency,
            'status': self.status.value if isinstance(self.status, RejectionStatus) else self.status,
            'severity': self.severity.value if isinstance(self.severity, RejectionSeverity) else self.severity,
            'priority': self.priority,
            'assigned_to': self.assigned_to,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'resolution_notes': self.resolution_notes,
            'resolution_date': self.resolution_date.isoformat() if self.resolution_date else None,
            'resubmittable': self.resubmittable,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_overdue': self.is_overdue(),
            'days_until_due': self.days_until_due(),
            'follow_up_count': self.follow_up_count,
            'last_follow_up': self.last_follow_up.isoformat() if self.last_follow_up else None,
            'original_claim_number': self.original_claim_number,
            'payer_reference': self.payer_reference,
            'source_file': self.source_file,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Resubmission(db.Model, TimestampMixin):
    """Resubmission model for tracking claim resubmissions"""
    __tablename__ = 'resubmissions'
    
    id = db.Column(db.Integer, primary_key=True)
    resubmission_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # References
    rejection_id = db.Column(db.Integer, db.ForeignKey('rejections.id'), nullable=False)
    original_claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=False)
    new_claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=True)
    
    # Resubmission details
    resubmission_date = db.Column(db.Date, nullable=False)
    submission_method = db.Column(db.String(50), nullable=True)  # portal, api, email
    
    # Changes made
    changes_summary = db.Column(db.Text, nullable=True)
    documents_added = db.Column(db.JSON, nullable=True)
    corrections_made = db.Column(db.JSON, nullable=True)
    
    # Status
    status = db.Column(db.String(50), default='submitted', nullable=False)
    outcome = db.Column(db.String(50), nullable=True)  # approved, rejected, pending
    outcome_date = db.Column(db.Date, nullable=True)
    outcome_amount = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Tracking
    follow_up_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    original_claim = db.relationship('Claim', foreign_keys=[original_claim_id], backref='originating_resubmissions')
    new_claim = db.relationship('Claim', foreign_keys=[new_claim_id], backref='resubmission_records')
    
    def __repr__(self):
        return f'<Resubmission {self.resubmission_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'resubmission_number': self.resubmission_number,
            'rejection_id': self.rejection_id,
            'original_claim_id': self.original_claim_id,
            'new_claim_id': self.new_claim_id,
            'resubmission_date': self.resubmission_date.isoformat() if self.resubmission_date else None,
            'submission_method': self.submission_method,
            'changes_summary': self.changes_summary,
            'documents_added': self.documents_added,
            'corrections_made': self.corrections_made,
            'status': self.status,
            'outcome': self.outcome,
            'outcome_date': self.outcome_date.isoformat() if self.outcome_date else None,
            'outcome_amount': float(self.outcome_amount) if self.outcome_amount else 0,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
