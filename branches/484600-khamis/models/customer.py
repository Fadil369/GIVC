"""
Customer model
"""
from .base import db, TimestampMixin


class Customer(db.Model, TimestampMixin):
    """Customer model"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Personal information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    
    # Contact information
    email = db.Column(db.String(120), nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    mobile = db.Column(db.String(20), nullable=True)
    
    # Address
    address_line1 = db.Column(db.String(200), nullable=True)
    address_line2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    
    # Identification
    national_id = db.Column(db.String(50), nullable=True)
    passport_number = db.Column(db.String(50), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<Customer {self.customer_number}: {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'customer_number': self.customer_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'national_id': self.national_id,
            'passport_number': self.passport_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
