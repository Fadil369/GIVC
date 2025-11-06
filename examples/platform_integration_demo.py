"""
GIVC Platform Integration Demo
Demonstrates enhanced integration with BrainSAIT platform features
"""

import sys
import logging
from datetime import datetime
from typing import Dict

# Add parent directory to path
sys.path.insert(0, '.')

from auth.auth_manager import AuthenticationManager
from services.platform_integration import PlatformIntegrationService
from config.platform_config import (
    GIVCPlatformConfig,
    get_tawuniya_license,
    get_al_hayat_nphies_id
)
from utils.logger import setup_logger

# Setup logging
logger = setup_logger()


def demo_platform_info():
    """Demonstrate platform information retrieval"""
    logger.info("\n" + "="*60)
    logger.info("🧠 GIVC BRAINSAIT PLATFORM INFORMATION")
    logger.info("="*60)
    
    info = GIVCPlatformConfig.get_platform_info()
    
    logger.info(f"\n📋 Platform: {info['platform_name']}")
    logger.info(f"🔢 Version: {info['version']}")
    logger.info(f"🌐 URL: {info['url']}")
    
    logger.info(f"\n✨ Features:")
    for feature, enabled in info['features'].items():
        status = "✅" if enabled else "❌"
        logger.info(f"  {status} {feature.replace('_', ' ').title()}")
    
    logger.info(f"\n📊 Live Statistics:")
    for key, value in info['statistics'].items():
        logger.info(f"  • {key.replace('_', ' ').title()}: {value}")
    
    logger.info(f"\n🏥 Integrated Providers:")
    for provider_key, provider_data in info['providers'].items():
        logger.info(f"  • {provider_data['name']}")
        logger.info(f"    License: {provider_data['license']}")
        logger.info(f"    NPHIES ID: {provider_data['nphies_id']}")


def demo_tawuniya_integration():
    """Demonstrate TAWUNIYA insurance integration"""
    logger.info("\n" + "="*60)
    logger.info("🏢 TAWUNIYA MEDICAL INSURANCE INTEGRATION")
    logger.info("="*60)
    
    tawuniya = GIVCPlatformConfig.get_tawuniya_config()
    
    logger.info(f"\n✅ Provider: {tawuniya.name}")
    logger.info(f"📝 License: {tawuniya.license}")
    logger.info(f"👥 Group Code: {tawuniya.group_code}")
    logger.info(f"📋 Policies: {len(tawuniya.policies)} BALSAM GOLD")
    logger.info(f"👤 Contact: {tawuniya.contact_person}")
    
    # Simulate eligibility check
    logger.info(f"\n🔍 Simulating TAWUNIYA eligibility check...")
    
    auth_manager = AuthenticationManager()
    platform_service = PlatformIntegrationService(auth_manager)
    
    sample_member_id = "1234567890"
    service_date = datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"  Member ID: {sample_member_id}")
    logger.info(f"  Service Date: {service_date}")
    logger.info(f"  Policy Type: BALSAM GOLD")
    
    # Validate credentials
    validation = platform_service.validate_provider_credentials(
        tawuniya.license,
        tawuniya.nphies_id
    )
    
    if validation['valid']:
        logger.info(f"\n✅ Credentials validated")
        logger.info(f"  Provider: {validation['provider_name']}")
        logger.info(f"  Group Code: {validation['group_code']}")
    else:
        logger.error(f"❌ Validation failed: {validation['message']}")


def demo_al_hayat_integration():
    """Demonstrate Al Hayat Hospital integration"""
    logger.info("\n" + "="*60)
    logger.info("🏥 AL HAYAT NATIONAL HOSPITAL INTEGRATION")
    logger.info("="*60)
    
    al_hayat = GIVCPlatformConfig.get_al_hayat_config()
    
    logger.info(f"\n✅ Provider: {al_hayat.name}")
    logger.info(f"📝 License: {al_hayat.license}")
    logger.info(f"🆔 NPHIES ID: {al_hayat.nphies_id}")
    logger.info(f"🏥 CHI ID: {al_hayat.chi_id}")
    logger.info(f"📡 Real-time Monitoring: Enabled")
    
    # Validate credentials
    auth_manager = AuthenticationManager()
    platform_service = PlatformIntegrationService(auth_manager)
    
    validation = platform_service.validate_provider_credentials(
        al_hayat.license,
        al_hayat.nphies_id
    )
    
    if validation['valid']:
        logger.info(f"\n✅ Credentials validated")
        logger.info(f"  Provider: {validation['provider_name']}")
        logger.info(f"  CHI ID: {validation['chi_id']}")


def demo_ai_validation():
    """Demonstrate AI-powered claim validation"""
    logger.info("\n" + "="*60)
    logger.info("🤖 AI-POWERED CLAIM VALIDATION")
    logger.info("="*60)
    
    auth_manager = AuthenticationManager()
    platform_service = PlatformIntegrationService(auth_manager)
    
    # Sample claim data
    sample_claim = {
        "member_id": "1234567890",
        "payer_id": get_tawuniya_license(),
        "provider_id": get_al_hayat_nphies_id(),
        "service_date": datetime.now().strftime("%Y-%m-%d"),
        "total_amount": 15000.00,
        "diagnosis_code": "J18.9"
    }
    
    logger.info(f"\n📋 Sample Claim:")
    for key, value in sample_claim.items():
        logger.info(f"  {key}: {value}")
    
    # Run AI validation
    logger.info(f"\n🔍 Running AI validation...")
    validation_result = platform_service.ai_powered_claim_validation(sample_claim)
    
    logger.info(f"\n{'✅' if validation_result['valid'] else '❌'} Validation: {'PASSED' if validation_result['valid'] else 'FAILED'}")
    
    if validation_result['errors']:
        logger.info(f"\n❌ Errors:")
        for error in validation_result['errors']:
            logger.error(f"  • {error}")
    
    if validation_result['warnings']:
        logger.info(f"\n⚠️ Warnings:")
        for warning in validation_result['warnings']:
            logger.warning(f"  • {warning}")
    
    if validation_result['recommendations']:
        logger.info(f"\n💡 AI Recommendations:")
        for rec in validation_result['recommendations']:
            logger.info(f"  • {rec}")


def demo_platform_status():
    """Demonstrate platform status monitoring"""
    logger.info("\n" + "="*60)
    logger.info("📊 PLATFORM STATUS MONITORING")
    logger.info("="*60)
    
    auth_manager = AuthenticationManager()
    platform_service = PlatformIntegrationService(auth_manager)
    
    status = platform_service.get_platform_status()
    
    logger.info(f"\n🕐 Timestamp: {status['timestamp']}")
    logger.info(f"🌐 Connection: {status['connection_status']}")
    logger.info(f"📈 System Uptime: {status['statistics']['system_uptime']}")
    logger.info(f"👥 Beneficiaries Served: {status['statistics']['beneficiaries_served']}")
    logger.info(f"🏢 Insurance Providers: {status['statistics']['insurance_providers']}")
    logger.info(f"🏥 Healthcare Facilities: {status['statistics']['healthcare_facilities']}")


def demo_comprehensive_report():
    """Generate comprehensive platform integration report"""
    logger.info("\n" + "="*60)
    logger.info("📑 COMPREHENSIVE PLATFORM REPORT")
    logger.info("="*60)
    
    auth_manager = AuthenticationManager()
    platform_service = PlatformIntegrationService(auth_manager)
    
    report = platform_service.generate_platform_report()
    
    logger.info(f"\n📅 Report Date: {report['report_date']}")
    logger.info(f"🔗 Connection: {report['connection_status']}")
    
    logger.info(f"\n🏢 Configured Providers:")
    for provider_key, provider_data in report['providers'].items():
        logger.info(f"  • {provider_data['name']}")
        logger.info(f"    License: {provider_data.get('license', 'N/A')}")
        logger.info(f"    NPHIES ID: {provider_data.get('nphies_id', 'N/A')}")
    
    logger.info(f"\n✨ Enabled Features:")
    for feature, enabled in report['features_enabled'].items():
        if enabled:
            logger.info(f"  ✅ {feature.replace('_', ' ').title()}")


def demo_endpoints():
    """Demonstrate endpoint configuration"""
    logger.info("\n" + "="*60)
    logger.info("🌐 NPHIES ENDPOINT CONFIGURATION")
    logger.info("="*60)
    
    logger.info(f"\n🔴 Production Endpoint:")
    logger.info(f"  {GIVCPlatformConfig.get_endpoint_url('production')}")
    
    logger.info(f"\n🟡 Sandbox Endpoint:")
    logger.info(f"  {GIVCPlatformConfig.get_endpoint_url('sandbox')}")
    
    logger.info(f"\n🟢 Conformance Endpoint:")
    logger.info(f"  {GIVCPlatformConfig.get_endpoint_url('conformance')}")
    
    logger.info(f"\n📡 FTP Server:")
    logger.info(f"  Host: {GIVCPlatformConfig.FTP_CONFIG['host']}")
    logger.info(f"  Port: {GIVCPlatformConfig.FTP_CONFIG['port']}")
    logger.info(f"  TLS: {GIVCPlatformConfig.FTP_CONFIG['use_tls']}")


def main():
    """Run all platform integration demos"""
    logger.info("\n\n" + "🚀"*30)
    logger.info("GIVC BRAINSAIT PLATFORM INTEGRATION DEMO")
    logger.info("🚀"*30 + "\n")
    
    try:
        # Run all demos
        demo_platform_info()
        demo_endpoints()
        demo_tawuniya_integration()
        demo_al_hayat_integration()
        demo_ai_validation()
        demo_platform_status()
        demo_comprehensive_report()
        
        logger.info("\n\n" + "✅"*30)
        logger.info("DEMO COMPLETED SUCCESSFULLY!")
        logger.info("✅"*30 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
