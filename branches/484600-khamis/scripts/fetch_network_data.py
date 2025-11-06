"""
Fetch and process data from network share
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from network_fetcher import NetworkDataFetcher
from extractors import DocumentParser, BatchDocumentParser
from rcm_config import PayerConfig
from datetime import datetime
import argparse
import json


def fetch_payer_data(payer_id: str, days: int = 30, download: bool = False):
    """
    Fetch and process data for a specific payer
    
    Args:
        payer_id: Payer identifier
        days: Number of days to look back
        download: Whether to download files locally
    """
    print(f"\n{'='*70}")
    print(f"FETCHING DATA FOR {payer_id}")
    print(f"{'='*70}\n")
    
    fetcher = NetworkDataFetcher()
    payer_config = PayerConfig.get_payer_by_id(payer_id)
    
    if not payer_config:
        print(f"❌ Invalid payer ID: {payer_id}")
        return
    
    print(f"📊 {payer_config['name']}")
    print(f"   Network Path: {payer_config['network_path']}")
    print(f"   Looking back: {days} days\n")
    
    # Get recent files
    recent_files = fetcher.fetch_recent_files(payer_id, days=days)
    
    print(f"Found {len(recent_files)} files modified in last {days} days:\n")
    
    # Group by extension
    by_ext = {}
    for file in recent_files:
        ext = file['extension']
        by_ext[ext] = by_ext.get(ext, 0) + 1
    
    print("File types:")
    for ext, count in by_ext.items():
        print(f"   {ext}: {count} files")
    
    print("\nRecent files:")
    for i, file in enumerate(recent_files[:20], 1):  # Show first 20
        print(f"   {i}. {file['name']:<50} {file['modified'].strftime('%Y-%m-%d')}")
    
    if len(recent_files) > 20:
        print(f"   ... and {len(recent_files) - 20} more files")
    
    # Download if requested
    if download and recent_files:
        print(f"\n📥 Downloading files...")
        download_dir = Path('downloads') / payer_id / datetime.now().strftime('%Y%m%d')
        download_dir.mkdir(parents=True, exist_ok=True)
        
        downloaded = fetcher.batch_fetch_files(
            payer_id=payer_id,
            local_dir=str(download_dir),
            days=days
        )
        
        print(f"   ✓ Downloaded {len(downloaded)} files to {download_dir}")
        
        # Extract data from Excel files
        excel_files = [f for f in downloaded if f.endswith(('.xlsx', '.xls'))]
        if excel_files:
            print(f"\n📊 Extracting data from {len(excel_files)} Excel files...")
            
            for excel_file in excel_files[:5]:  # Process first 5
                try:
                    parser = DocumentParser(excel_file)
                    data = parser.parse()
                    
                    print(f"\n   File: {Path(excel_file).name}")
                    print(f"      Claims extracted: {len(data.get('claims', []))}")
                    
                    financial = data.get('financial_summary', {})
                    if financial.get('total_amount'):
                        print(f"      Total amount: {financial.get('currency', 'SAR')} {financial.get('total_amount', 0):,.2f}")
                
                except Exception as e:
                    print(f"   ⚠️  Error processing {Path(excel_file).name}: {e}")


def fetch_all_payers(days: int = 7):
    """Fetch data for all primary payers"""
    print(f"\n{'='*70}")
    print(f"SCANNING ALL PRIMARY PAYERS")
    print(f"{'='*70}\n")
    
    fetcher = NetworkDataFetcher()
    results = fetcher.scan_all_payers()
    
    for payer_id, stats in results.items():
        payer_config = PayerConfig.get_payer_by_id(payer_id)
        if payer_config and stats['total_files'] > 0:
            print(f"\n{payer_config['icon']} {stats['name']}")
            print(f"   Total Files: {stats['total_files']}")
            print(f"   Total Size: {stats['total_size']:,} bytes ({stats['total_size']/1024/1024:.2f} MB)")
            print(f"   File Types: {stats['file_types']}")
            
            if stats['latest_file']:
                print(f"   Latest File: {stats['latest_file']['name']}")
                print(f"                {stats['latest_file']['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get recent files
            recent = fetcher.fetch_recent_files(payer_id, days=days)
            if recent:
                print(f"   Recent ({days} days): {len(recent)} files")


def main():
    parser = argparse.ArgumentParser(description='Fetch data from network share')
    parser.add_argument('--payer', type=str, help='Specific payer ID (BUPA, MOH, ALTAWUNIYA, etc.)')
    parser.add_argument('--days', type=int, default=30, help='Number of days to look back (default: 30)')
    parser.add_argument('--download', action='store_true', help='Download files locally')
    parser.add_argument('--all', action='store_true', help='Scan all payers')
    
    args = parser.parse_args()
    
    if args.all:
        fetch_all_payers(days=args.days)
    elif args.payer:
        fetch_payer_data(args.payer, days=args.days, download=args.download)
    else:
        # Default: show primary payers
        print("\n📊 Available payers:")
        for i, payer in enumerate(PayerConfig.get_primary_payers(), 1):
            print(f"   {i}. {payer['icon']} {payer['name']} (ID: {payer['id']})")
        
        print("\nUsage examples:")
        print("   python scripts/fetch_network_data.py --payer BUPA --days 30")
        print("   python scripts/fetch_network_data.py --payer MOH --download")
        print("   python scripts/fetch_network_data.py --all")


if __name__ == '__main__':
    main()
