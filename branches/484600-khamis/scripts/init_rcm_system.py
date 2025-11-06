"""
Complete RCM System Setup Script
Initializes multi-payer RCM system with channels, spaces, and tabs
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from models import db, Channel, Space, Tab
from models.channel import ChannelManager
from rcm_config import PayerConfig
from network_fetcher import NetworkDataFetcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_rcm_system():
    """Initialize complete RCM system"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║           INITIALIZING COMPLETE RCM SYSTEM                               ║
║           Multi-Payer Revenue Cycle Management                           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    app = create_app()
    
    with app.app_context():
        # Step 1: Create all database tables
        print("\n📊 Step 1: Creating database tables...")
        db.create_all()
        print("   ✓ Tables created successfully")
        
        # Step 2: Initialize channels for all payers
        print("\n🏥 Step 2: Initializing payer channels...")
        
        existing_channels = Channel.query.count()
        if existing_channels > 0:
            print(f"   ⚠️  Found {existing_channels} existing channels")
            response = input("   Clear and reinitialize? (yes/no): ")
            if response.lower() == 'yes':
                Channel.query.delete()
                Space.query.delete()
                Tab.query.delete()
                db.session.commit()
                print("   ✓ Cleared existing channels")
        
        ChannelManager.initialize_system_channels()
        print("   ✓ Channels initialized")
        
        # Step 3: Display channel structure
        print("\n📋 Step 3: Channel Structure Created:")
        channels = Channel.query.all()
        
        for channel in channels:
            print(f"\n   {channel.icon} {channel.name}")
            print(f"      Type: {channel.channel_type.value if channel.channel_type else 'N/A'}")
            print(f"      Payer: {channel.payer_id or 'N/A'}")
            print(f"      Spaces: {len(channel.spaces)}")
            
            for space in channel.spaces:
                print(f"         └─ {space.icon} {space.name} ({len(space.tabs)} tabs)")
        
        # Step 4: Network share connectivity test
        print("\n🌐 Step 4: Testing network share connectivity...")
        try:
            fetcher = NetworkDataFetcher()
            print("   ✓ Network share accessible: \\\\128.1.1.86\\InmaRCMRejection")
            
            # Scan all payers
            print("\n📂 Step 5: Scanning payer data...")
            results = fetcher.scan_all_payers()
            
            for payer_id, stats in results.items():
                if stats['total_files'] > 0:
                    print(f"\n   {PayerConfig.get_payer_by_id(payer_id)['icon']} {stats['name']}:")
                    print(f"      Files: {stats['total_files']}")
                    print(f"      Size: {stats['total_size']:,} bytes")
                    print(f"      Types: {dict(list(stats['file_types'].items())[:3])}")
                    if stats['latest_file']:
                        print(f"      Latest: {stats['latest_file']['name']}")
                        print(f"              ({stats['latest_file']['modified'].strftime('%Y-%m-%d %H:%M')})")
        
        except Exception as e:
            print(f"   ⚠️  Network share error: {e}")
            print("   System will work in local mode")
        
        # Step 6: System statistics
        print("\n📊 Step 6: System Statistics:")
        stats = {
            'Channels': Channel.query.count(),
            'Spaces': Space.query.count(),
            'Tabs': Tab.query.count(),
            'Payers Configured': len(PayerConfig.get_all_payers())
        }
        
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n" + "="*76)
        print("\n✅ RCM SYSTEM INITIALIZED SUCCESSFULLY!")
        print("\n📌 Next Steps:")
        print("   1. Start the API server: python app.py")
        print("   2. Access channels at: http://localhost:5000/api/channels")
        print("   3. Fetch network data: python scripts/fetch_network_data.py")
        print("   4. View analytics: http://localhost:5000/api/analytics/rcm-summary")
        print("\n" + "="*76 + "\n")


if __name__ == '__main__':
    if '--force' in sys.argv:
        print("⚠️  Force mode: Dropping all tables...")
        app = create_app()
        with app.app_context():
            db.drop_all()
        print("✓ Tables dropped")
    
    initialize_rcm_system()
