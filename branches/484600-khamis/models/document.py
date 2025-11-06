"""
Document model
"""
from .base import db, TimestampMixin


class Document(db.Model, TimestampMixin):
    """Document model for storing claim attachments"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relationship
    claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=True)
    
    # Document details
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    
    # Document type
    document_type = db.Column(db.String(50), nullable=True)  # invoice, prescription, medical_report, etc.
    
    # Extracted data
    extracted_data = db.Column(db.JSON, nullable=True)
    extraction_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, processing, completed, failed
    
    # Additional info
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Document {self.filename}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'claim_id': self.claim_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'document_type': self.document_type,
            'extracted_data': self.extracted_data,
            'extraction_status': self.extraction_status,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
