"""
Policy model
"""
from .base import db, TimestampMixin


class Policy(db.Model, TimestampMixin):
    """Insurance policy model"""
    __tablename__ = 'policies'
    
    id = db.Column(db.Integer, primary_key=True)
    policy_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Relationship
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Policy details
    policy_type = db.Column(db.String(100), nullable=False)
    plan_name = db.Column(db.String(200), nullable=True)
    coverage_amount = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(3), default='AED', nullable=False)
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    renewal_date = db.Column(db.Date, nullable=True)
    
    # Premium
    premium_amount = db.Column(db.Numeric(10, 2), nullable=True)
    premium_frequency = db.Column(db.String(20), nullable=True)  # monthly, quarterly, annual
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)
    
    # Additional info
    terms_conditions = db.Column(db.Text, nullable=True)
    exclusions = db.Column(db.Text, nullable=True)
    
    # Relationships
    customer = db.relationship('Customer', backref='policies')
    
    def __repr__(self):
        return f'<Policy {self.policy_number}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'policy_number': self.policy_number,
            'customer_id': self.customer_id,
            'policy_type': self.policy_type,
            'plan_name': self.plan_name,
            'coverage_amount': float(self.coverage_amount) if self.coverage_amount else 0,
            'currency': self.currency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'renewal_date': self.renewal_date.isoformat() if self.renewal_date else None,
            'premium_amount': float(self.premium_amount) if self.premium_amount else 0,
            'premium_frequency': self.premium_frequency,
            'is_active': self.is_active,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
