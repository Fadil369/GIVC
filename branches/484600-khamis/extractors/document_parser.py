"""
Document Parser - Unified interface for parsing various document types
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .pdf_extractor import PDFExtractor
from .excel_extractor import ExcelExtractor


class DocumentParser:
    """Unified document parser for Bupa claims documents"""
    
    SUPPORTED_FORMATS = {
        '.pdf': PDFExtractor,
        '.xlsx': ExcelExtractor,
        '.xls': ExcelExtractor,
    }
    
    def __init__(self, document_path: str):
        """
        Initialize document parser
        
        Args:
            document_path: Path to the document
        """
        self.document_path = Path(document_path)
        self.extractor = None
        self.data = None
        
        if not self.document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        # Determine appropriate extractor
        ext = self.document_path.suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {ext}. Supported: {list(self.SUPPORTED_FORMATS.keys())}")
        
        self.extractor = self.SUPPORTED_FORMATS[ext](str(self.document_path))
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse the document and extract all data
        
        Returns:
            Dictionary containing extracted data
        """
        if not self.extractor:
            raise RuntimeError("No extractor initialized")
        
        self.data = self.extractor.extract_all()
        self.data['document_type'] = self.document_path.suffix.lower()
        self.data['parsed_at'] = datetime.now().isoformat()
        
        return self.data
    
    def get_claims(self) -> List[Dict[str, Any]]:
        """Get extracted claims"""
        if not self.data:
            self.parse()
        return self.data.get('claims', [])
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        if not self.data:
            self.parse()
        return self.data.get('provider_info', {})
    
    def get_financial_summary(self) -> Dict[str, Any]:
        """Get financial summary"""
        if not self.data:
            self.parse()
        return self.data.get('financial_summary', {})
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get document metadata"""
        if not self.data:
            self.parse()
        return self.data.get('metadata', {})
    
    def save_to_json(self, output_path: Optional[str] = None) -> str:
        """
        Save extracted data to JSON file
        
        Args:
            output_path: Optional output path. If not provided, saves next to source file
            
        Returns:
            Path to saved JSON file
        """
        if not self.data:
            self.parse()
        
        if not output_path:
            output_path = self.document_path.with_suffix('.json')
        
        output_path = Path(output_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, default=str)
        
        return str(output_path)
    
    def generate_summary(self) -> str:
        """
        Generate a human-readable summary of the document
        
        Returns:
            Summary string
        """
        if not self.data:
            self.parse()
        
        provider = self.get_provider_info()
        financial = self.get_financial_summary()
        claims = self.get_claims()
        
        summary = f"""
=== Bupa Claims Document Summary ===

Document: {self.document_path.name}
Parsed: {self.data.get('parsed_at', 'N/A')}

--- Provider Information ---
Provider ID: {provider.get('provider_id', 'N/A')}
Provider Name: {provider.get('provider_name', 'N/A')}
Statement Number: {provider.get('statement_number', 'N/A')}
Statement Date: {provider.get('statement_date', 'N/A')}

--- Financial Summary ---
Period: {financial.get('period_from', 'N/A')} to {financial.get('period_to', 'N/A')}
Total Claims: {financial.get('total_claims', 0)}
Total Amount: {financial.get('currency', 'AED')} {financial.get('total_amount', '0.00')}
Approved: {financial.get('currency', 'AED')} {financial.get('approved_amount', '0.00')}
Rejected: {financial.get('currency', 'AED')} {financial.get('rejected_amount', '0.00')}
Pending: {financial.get('currency', 'AED')} {financial.get('pending_amount', '0.00')}

--- Claims Details ---
Number of Claims Extracted: {len(claims)}

"""
        if claims and len(claims) > 0:
            summary += "\n--- Sample Claims (first 3) ---\n"
            for i, claim in enumerate(claims[:3], 1):
                summary += f"\nClaim {i}:\n"
                for key, value in claim.items():
                    summary += f"  {key}: {value}\n"
        
        return summary


class BatchDocumentParser:
    """Parse multiple documents at once"""
    
    def __init__(self, document_paths: List[str]):
        """
        Initialize batch parser
        
        Args:
            document_paths: List of document paths
        """
        self.document_paths = [Path(p) for p in document_paths]
        self.parsers = []
        self.results = []
    
    def parse_all(self) -> List[Dict[str, Any]]:
        """
        Parse all documents
        
        Returns:
            List of extracted data from all documents
        """
        self.results = []
        
        for doc_path in self.document_paths:
            try:
                parser = DocumentParser(str(doc_path))
                data = parser.parse()
                self.results.append({
                    'success': True,
                    'document': str(doc_path),
                    'data': data
                })
            except Exception as e:
                self.results.append({
                    'success': False,
                    'document': str(doc_path),
                    'error': str(e)
                })
        
        return self.results
    
    def get_all_claims(self) -> List[Dict[str, Any]]:
        """Get all claims from all documents"""
        all_claims = []
        
        for result in self.results:
            if result['success']:
                claims = result['data'].get('claims', [])
                # Add source document to each claim
                for claim in claims:
                    claim['source_document'] = result['document']
                all_claims.extend(claims)
        
        return all_claims
    
    def save_combined_results(self, output_path: str) -> str:
        """
        Save combined results to JSON file
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to saved file
        """
        combined_data = {
            'parsed_at': datetime.now().isoformat(),
            'total_documents': len(self.document_paths),
            'successful': sum(1 for r in self.results if r['success']),
            'failed': sum(1 for r in self.results if not r['success']),
            'results': self.results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, default=str)
        
        return output_path


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        doc_path = sys.argv[1]
        parser = DocumentParser(doc_path)
        print(parser.generate_summary())
        
        # Save to JSON
        json_path = parser.save_to_json()
        print(f"\nData saved to: {json_path}")
    else:
        print("Usage: python document_parser.py <path_to_document>")
