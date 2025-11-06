"""
PDF Data Extractor for Bupa Claims Documents
"""
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import pdfplumber
from datetime import datetime


class PDFExtractor:
    """Extract data from Bupa PDF documents"""
    
    def __init__(self, pdf_path: str):
        """
        Initialize PDF extractor
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = Path(pdf_path)
        self.data = {}
        self.tables = []
        self.text = ""
        
    def extract_all(self) -> Dict[str, Any]:
        """
        Extract all data from PDF
        
        Returns:
            Dictionary containing all extracted data
        """
        with pdfplumber.open(self.pdf_path) as pdf:
            # Extract text from all pages
            self.text = self._extract_text(pdf)
            
            # Extract tables
            self.tables = self._extract_tables(pdf)
            
            # Extract specific fields
            self.data = self._parse_document_data()
            
        return {
            'metadata': self._extract_metadata(),
            'provider_info': self._extract_provider_info(),
            'claims': self._extract_claims(),
            'financial_summary': self._extract_financial_summary(),
            'tables': self.tables,
            'raw_text': self.text
        }
    
    def _extract_text(self, pdf) -> str:
        """Extract all text from PDF"""
        text_content = []
        for page in pdf.pages:
            text_content.append(page.extract_text())
        return '\n'.join(text_content)
    
    def _extract_tables(self, pdf) -> List[List[List[str]]]:
        """Extract all tables from PDF"""
        tables = []
        for page in pdf.pages:
            page_tables = page.extract_tables()
            if page_tables:
                tables.extend(page_tables)
        return tables
    
    def _parse_document_data(self) -> Dict[str, Any]:
        """Parse document for structured data"""
        data = {}
        
        # Common patterns for Bupa documents
        patterns = {
            'statement_number': r'Statement\s+(?:Number|No|#)[:.]?\s*(\d+)',
            'provider_id': r'Provider\s+(?:ID|Number)[:.]?\s*(\d+)',
            'statement_date': r'Statement\s+Date[:.]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'period_from': r'Period\s+From[:.]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'period_to': r'Period\s+To[:.]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'total_claims': r'Total\s+Claims[:.]?\s*([0-9,]+)',
            'total_amount': r'Total\s+Amount[:.]?\s*\$?\s*([0-9,]+\.?\d{0,2})',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                data[key] = match.group(1)
        
        return data
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract document metadata"""
        return {
            'filename': self.pdf_path.name,
            'file_size': self.pdf_path.stat().st_size,
            'extracted_at': datetime.now().isoformat(),
            'statement_number': self.data.get('statement_number', ''),
            'statement_date': self.data.get('statement_date', ''),
        }
    
    def _extract_provider_info(self) -> Dict[str, Any]:
        """Extract provider information"""
        provider_info = {
            'provider_id': self.data.get('provider_id', '484600'),
            'provider_name': '',
            'address': '',
            'contact': ''
        }
        
        # Try to extract provider name
        name_match = re.search(r'Provider\s+Name[:.]?\s*([^\n]+)', self.text, re.IGNORECASE)
        if name_match:
            provider_info['provider_name'] = name_match.group(1).strip()
        
        # Try to extract address
        address_match = re.search(r'Address[:.]?\s*([^\n]+(?:\n[^\n]+){0,2})', self.text, re.IGNORECASE)
        if address_match:
            provider_info['address'] = address_match.group(1).strip()
        
        return provider_info
    
    def _extract_claims(self) -> List[Dict[str, Any]]:
        """Extract individual claims from tables"""
        claims = []
        
        if not self.tables:
            return claims
        
        # Assume the largest table contains claim details
        main_table = max(self.tables, key=len) if self.tables else []
        
        if not main_table or len(main_table) < 2:
            return claims
        
        # First row is typically headers
        headers = main_table[0]
        
        # Normalize headers
        normalized_headers = [h.lower().strip() if h else f'col_{i}' 
                            for i, h in enumerate(headers)]
        
        # Process data rows
        for row in main_table[1:]:
            if not row or all(cell is None or str(cell).strip() == '' for cell in row):
                continue
                
            claim = {}
            for i, value in enumerate(row):
                if i < len(normalized_headers):
                    claim[normalized_headers[i]] = value
            
            if claim:  # Only add non-empty claims
                claims.append(claim)
        
        return claims
    
    def _extract_financial_summary(self) -> Dict[str, Any]:
        """Extract financial summary"""
        summary = {
            'period_from': self.data.get('period_from', ''),
            'period_to': self.data.get('period_to', ''),
            'total_claims': self.data.get('total_claims', '0'),
            'total_amount': self.data.get('total_amount', '0.00'),
            'currency': 'AED',  # Assuming AED for Bupa
        }
        
        # Try to extract more financial details
        patterns = {
            'approved_amount': r'Approved\s+Amount[:.]?\s*\$?\s*([0-9,]+\.?\d{0,2})',
            'rejected_amount': r'Rejected\s+Amount[:.]?\s*\$?\s*([0-9,]+\.?\d{0,2})',
            'pending_amount': r'Pending\s+Amount[:.]?\s*\$?\s*([0-9,]+\.?\d{0,2})',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                summary[key] = match.group(1)
        
        return summary
    
    def extract_text_only(self) -> str:
        """Extract only text content"""
        with pdfplumber.open(self.pdf_path) as pdf:
            return self._extract_text(pdf)
    
    def extract_tables_only(self) -> List[List[List[str]]]:
        """Extract only tables"""
        with pdfplumber.open(self.pdf_path) as pdf:
            return self._extract_tables(pdf)


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extractor = PDFExtractor(pdf_path)
        data = extractor.extract_all()
        
        print("=== Extracted Data ===")
        print(f"Metadata: {data['metadata']}")
        print(f"Provider Info: {data['provider_info']}")
        print(f"Financial Summary: {data['financial_summary']}")
        print(f"Number of Claims: {len(data['claims'])}")
        print(f"Number of Tables: {len(data['tables'])}")
    else:
        print("Usage: python pdf_extractor.py <path_to_pdf>")
