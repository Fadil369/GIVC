"""
Claim model
"""
from enum import Enum
from .base import db, TimestampMixin


class ClaimStatus(str, Enum):
    """Claim status enumeration"""
    SUBMITTED = 'submitted'
    UNDER_REVIEW = 'under_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PENDING_INFO = 'pending_info'
    PAID = 'paid'
    CANCELLED = 'cancelled'


class Claim(db.Model, TimestampMixin):
    """Claim model"""
    __tablename__ = 'claims'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Relationships
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('policies.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=True)
    
    # Claim details
    claim_date = db.Column(db.Date, nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.String(200), nullable=True)
    treatment = db.Column(db.String(200), nullable=True)
    
    # Financial
    claim_amount = db.Column(db.Numeric(10, 2), nullable=False)
    approved_amount = db.Column(db.Numeric(10, 2), nullable=True)
    paid_amount = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(3), default='AED', nullable=False)
    
    # Status
    status = db.Column(db.Enum(ClaimStatus), default=ClaimStatus.SUBMITTED, nullable=False)
    status_reason = db.Column(db.Text, nullable=True)
    
    # Additional info
    reference_number = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    customer = db.relationship('Customer', backref='claims')
    policy = db.relationship('Policy', backref='claims')
    provider = db.relationship('Provider', backref='claims')
    documents = db.relationship('Document', backref='claim', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Claim {self.claim_number}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'claim_number': self.claim_number,
            'customer_id': self.customer_id,
            'policy_id': self.policy_id,
            'provider_id': self.provider_id,
            'claim_date': self.claim_date.isoformat() if self.claim_date else None,
            'service_date': self.service_date.isoformat() if self.service_date else None,
            'description': self.description,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'claim_amount': float(self.claim_amount) if self.claim_amount else 0,
            'approved_amount': float(self.approved_amount) if self.approved_amount else 0,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0,
            'currency': self.currency,
            'status': self.status.value if isinstance(self.status, ClaimStatus) else self.status,
            'status_reason': self.status_reason,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
