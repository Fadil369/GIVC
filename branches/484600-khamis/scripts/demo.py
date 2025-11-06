"""
Demo script - Extract data from your Bupa documents and showcase the system
"""
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          Bupa Claims Document Extraction Demo                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

try:
    from extractors import PDFExtractor, ExcelExtractor, DocumentParser
    import json
    
    # Find documents in current directory
    current_dir = Path.cwd()
    pdf_files = list(current_dir.glob('CLPROVSTM03_*.pdf'))
    excel_files = list(current_dir.glob('CLPROVSTM03_*.xlsx')) + list(current_dir.glob('CLPROVSTM03_*.xls'))
    
    print("\n📂 Documents found:")
    for f in pdf_files + excel_files:
        print(f"   ✓ {f.name}")
    
    if not pdf_files and not excel_files:
        print("\n⚠ No Bupa documents found in current directory")
        print("Looking for: CLPROVSTM03_*.pdf or CLPROVSTM03_*.xlsx")
        sys.exit(1)
    
    # Process PDF if available
    if pdf_files:
        print(f"\n{'='*65}")
        print("📄 EXTRACTING FROM PDF")
        print(f"{'='*65}\n")
        
        pdf_path = pdf_files[0]
        print(f"Processing: {pdf_path.name}\n")
        
        extractor = PDFExtractor(str(pdf_path))
        pdf_data = extractor.extract_all()
        
        print("✓ Extraction complete!\n")
        
        print("📊 EXTRACTED INFORMATION:")
        print(f"{'-'*65}")
        
        # Metadata
        metadata = pdf_data['metadata']
        print(f"\n🏷️  Document Metadata:")
        print(f"   Statement Number: {metadata.get('statement_number', 'N/A')}")
        print(f"   Statement Date: {metadata.get('statement_date', 'N/A')}")
        print(f"   File Size: {metadata.get('file_size', 0):,} bytes")
        
        # Provider Info
        provider = pdf_data['provider_info']
        print(f"\n🏥 Provider Information:")
        print(f"   Provider ID: {provider.get('provider_id', 'N/A')}")
        print(f"   Provider Name: {provider.get('provider_name', 'N/A')}")
        print(f"   Address: {provider.get('address', 'N/A')}")
        
        # Financial Summary
        financial = pdf_data['financial_summary']
        print(f"\n💰 Financial Summary:")
        print(f"   Period: {financial.get('period_from', 'N/A')} to {financial.get('period_to', 'N/A')}")
        print(f"   Total Claims: {financial.get('total_claims', '0')}")
        print(f"   Total Amount: {financial.get('currency', 'AED')} {financial.get('total_amount', '0.00')}")
        
        # Claims
        claims = pdf_data['claims']
        print(f"\n📋 Claims Extracted: {len(claims)}")
        
        if claims and len(claims) > 0:
            print(f"\n   Sample Claims (first 3):")
            for i, claim in enumerate(claims[:3], 1):
                print(f"\n   Claim {i}:")
                for key, value in list(claim.items())[:5]:  # Show first 5 fields
                    print(f"      {key}: {value}")
        
        # Save to JSON
        json_path = Path(f"{pdf_path.stem}_extracted.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(pdf_data, f, indent=2, default=str)
        print(f"\n💾 Full data saved to: {json_path.name}")
    
    # Process Excel if available
    if excel_files:
        print(f"\n{'='*65}")
        print("📊 EXTRACTING FROM EXCEL")
        print(f"{'='*65}\n")
        
        excel_path = excel_files[0]
        print(f"Processing: {excel_path.name}\n")
        
        extractor = ExcelExtractor(str(excel_path))
        excel_data = extractor.extract_all()
        
        print("✓ Extraction complete!\n")
        
        print("📊 EXTRACTED INFORMATION:")
        print(f"{'-'*65}")
        
        # Metadata
        metadata = excel_data['metadata']
        print(f"\n🏷️  Document Metadata:")
        print(f"   Sheet Count: {metadata.get('sheet_count', 0)}")
        print(f"   Sheet Names: {', '.join(metadata.get('sheet_names', []))}")
        
        # Provider Info
        provider = excel_data['provider_info']
        print(f"\n🏥 Provider Information:")
        print(f"   Provider ID: {provider.get('provider_id', 'N/A')}")
        print(f"   Statement Number: {provider.get('statement_number', 'N/A')}")
        
        # Financial Summary
        financial = excel_data['financial_summary']
        print(f"\n💰 Financial Summary:")
        print(f"   Total Claims: {financial.get('total_claims', 0)}")
        print(f"   Total Amount: {financial.get('currency', 'AED')} {financial.get('total_amount', 0):,.2f}")
        print(f"   Approved: {financial.get('currency', 'AED')} {financial.get('approved_amount', 0):,.2f}")
        
        # Claims
        claims = excel_data['claims']
        print(f"\n📋 Claims Extracted: {len(claims)}")
        
        if claims and len(claims) > 0:
            print(f"\n   Sample Claims (first 3):")
            for i, claim in enumerate(claims[:3], 1):
                print(f"\n   Claim {i}:")
                for key, value in list(claim.items())[:5]:  # Show first 5 fields
                    print(f"      {key}: {value}")
        
        # Save to JSON
        json_path = Path(f"{excel_path.stem}_extracted.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(excel_data, f, indent=2, default=str)
        print(f"\n💾 Full data saved to: {json_path.name}")
    
    print(f"\n{'='*65}")
    print("\n✅ DEMO COMPLETE!")
    print("\n📝 Next Steps:")
    print("   1. Review the extracted JSON files")
    print("   2. Initialize database: python scripts\\init_db.py")
    print("   3. Start API server: python app.py")
    print("   4. Access API at: http://localhost:5000")
    print(f"\n{'='*65}\n")
    
except ImportError as e:
    print(f"\n⚠️  Missing dependencies!")
    print(f"   Error: {e}")
    print("\n📦 Install required packages:")
    print("   1. Activate virtual environment: .\\venv\\Scripts\\activate")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Run demo again: python scripts\\demo.py\n")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error during extraction:")
    print(f"   {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
