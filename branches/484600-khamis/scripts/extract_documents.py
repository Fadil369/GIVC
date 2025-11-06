"""
Script to extract data from Bupa documents
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors import DocumentParser, BatchDocumentParser
import argparse
import json


def extract_single_document(file_path, output_json=True, verbose=True):
    """Extract data from a single document"""
    print(f"\n{'='*60}")
    print(f"Processing: {file_path}")
    print(f"{'='*60}\n")
    
    try:
        parser = DocumentParser(file_path)
        data = parser.parse()
        
        if verbose:
            print(parser.generate_summary())
        
        if output_json:
            json_path = parser.save_to_json()
            print(f"\nExtracted data saved to: {json_path}")
        
        return data
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None


def extract_multiple_documents(file_paths, output_json=True):
    """Extract data from multiple documents"""
    print(f"\n{'='*60}")
    print(f"Batch Processing {len(file_paths)} documents")
    print(f"{'='*60}\n")
    
    batch_parser = BatchDocumentParser(file_paths)
    results = batch_parser.parse_all()
    
    # Print summary
    successful = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'])
    
    print(f"\nProcessing complete:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    
    # Print failed files
    if failed > 0:
        print("\nFailed files:")
        for result in results:
            if not result['success']:
                print(f"  - {result['document']}: {result['error']}")
    
    # Get all claims
    all_claims = batch_parser.get_all_claims()
    print(f"\nTotal claims extracted: {len(all_claims)}")
    
    if output_json:
        output_path = Path('extracted_data_batch.json')
        batch_parser.save_combined_results(output_path)
        print(f"\nCombined data saved to: {output_path}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Extract data from Bupa claims documents')
    parser.add_argument('files', nargs='+', help='Document files to process')
    parser.add_argument('--no-json', action='store_true', help='Do not save JSON output')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    # Process files
    if len(args.files) == 1:
        extract_single_document(
            args.files[0],
            output_json=not args.no_json,
            verbose=not args.quiet
        )
    else:
        extract_multiple_documents(
            args.files,
            output_json=not args.no_json
        )


if __name__ == '__main__':
    # If no arguments provided, look for documents in current directory
    if len(sys.argv) == 1:
        current_dir = Path.cwd()
        
        # Find PDF and Excel files
        pdf_files = list(current_dir.glob('*.pdf'))
        excel_files = list(current_dir.glob('*.xlsx')) + list(current_dir.glob('*.xls'))
        
        all_files = pdf_files + excel_files
        
        if all_files:
            print(f"Found {len(all_files)} documents in current directory:")
            for f in all_files:
                print(f"  - {f.name}")
            
            print("\nProcessing all documents...")
            
            if len(all_files) == 1:
                extract_single_document(str(all_files[0]))
            else:
                extract_multiple_documents([str(f) for f in all_files])
        else:
            print("No PDF or Excel files found in current directory.")
            print("\nUsage: python extract_documents.py <file1> <file2> ...")
    else:
        main()
