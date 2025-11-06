"""
Provider model
"""
from .base import db, TimestampMixin


class Provider(db.Model, TimestampMixin):
    """Healthcare provider model"""
    __tablename__ = 'providers'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Provider information
    provider_name = db.Column(db.String(200), nullable=False)
    provider_type = db.Column(db.String(100), nullable=True)  # Hospital, Clinic, Pharmacy, etc.
    specialty = db.Column(db.String(200), nullable=True)
    
    # Contact information
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    fax = db.Column(db.String(20), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    
    # Address
    address_line1 = db.Column(db.String(200), nullable=True)
    address_line2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    
    # Licensing
    license_number = db.Column(db.String(100), nullable=True)
    license_expiry = db.Column(db.Date, nullable=True)
    
    # Bupa specific
    bupa_network = db.Column(db.Boolean, default=True, nullable=False)
    contract_number = db.Column(db.String(100), nullable=True)
    contract_start = db.Column(db.Date, nullable=True)
    contract_end = db.Column(db.Date, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<Provider {self.provider_id}: {self.provider_name}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'provider_name': self.provider_name,
            'provider_type': self.provider_type,
            'specialty': self.specialty,
            'email': self.email,
            'phone': self.phone,
            'fax': self.fax,
            'website': self.website,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'license_number': self.license_number,
            'license_expiry': self.license_expiry.isoformat() if self.license_expiry else None,
            'bupa_network': self.bupa_network,
            'contract_number': self.contract_number,
            'contract_start': self.contract_start.isoformat() if self.contract_start else None,
            'contract_end': self.contract_end.isoformat() if self.contract_end else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
