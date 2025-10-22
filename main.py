"""
Main Application Entry Point for NPHIES Integration
"""
import sys
import json
from pathlib import Path
from datetime import datetime

from config.settings import settings
from auth.auth_manager import auth_manager
from auth.cert_manager import check_certificates
from pipeline.extractor import NPHIESDataExtractor
from services.eligibility import EligibilityService
from services.claims import ClaimsService
from services.communication import CommunicationService
from utils.logger import setup_logger, get_logger

# Setup logging
logger = setup_logger(
    name="nphies",
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    console=True
)


def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🏥  NPHIES API Integration Platform                     ║
║                                                              ║
║     Saudi Arabia National Platform for Health Insurance     ║
║     Electronic Services - Data Extraction System            ║
║                                                              ║
║     Version: 1.0.0                                          ║
║     Environment: {env:<45}║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """.format(env=settings.ENVIRONMENT.upper())
    print(banner)


def check_system_status():
    """Check system status and prerequisites"""
    logger.info("=== System Status Check ===")
    
    status = {
        "environment": settings.ENVIRONMENT,
        "api_url": settings.api_base_url,
        "organization_id": settings.NPHIES_ORGANIZATION_ID,
        "ready": True
    }
    
    # Check certificates (for production)
    if settings.ENVIRONMENT == "production":
        cert_status = check_certificates()
        status["certificates"] = cert_status
        
        if not cert_status["ready"]:
            logger.warning("⚠️  Certificates not ready for production")
            status["ready"] = False
    
    # Test API connection
    logger.info("Testing NPHIES API connection...")
    connection_ok, connection_msg = auth_manager.test_connection()
    status["connection"] = {
        "status": "connected" if connection_ok else "failed",
        "message": connection_msg
    }
    
    if connection_ok:
        logger.info(f"✓ {connection_msg}")
    else:
        logger.error(f"✗ {connection_msg}")
        status["ready"] = False
    
    return status


def example_eligibility_check():
    """Example: Check eligibility for a member"""
    logger.info("\n=== Example: Eligibility Check ===")
    
    service = EligibilityService()
    
    # Example member data
    result = service.check_eligibility(
        member_id="1234567890",  # Replace with actual member ID
        payer_id=settings.NPHIES_PAYER_ID,
        service_date="2025-10-22",
        patient_name="Test Patient"
    )
    
    logger.info(f"Eligibility Result: {json.dumps(result, indent=2)}")
    return result


def example_claim_submission():
    """Example: Submit a claim"""
    logger.info("\n=== Example: Claim Submission ===")
    
    service = ClaimsService()
    
    # Example claim data
    services = [
        {
            "code": "99213",
            "description": "Office Visit",
            "quantity": 1,
            "unit_price": 150.00,
            "net_amount": 150.00
        }
    ]
    
    result = service.submit_claim(
        claim_type="professional",
        patient_id="patient-001",
        member_id="1234567890",
        payer_id=settings.NPHIES_PAYER_ID,
        services=services,
        total_amount=150.00,
        patient_name="Test Patient"
    )
    
    logger.info(f"Claim Result: {json.dumps(result, indent=2)}")
    return result


def example_communication_poll():
    """Example: Poll for communications"""
    logger.info("\n=== Example: Communication Poll ===")
    
    service = CommunicationService()
    
    result = service.poll_communications()
    
    logger.info(f"Communications: {json.dumps(result, indent=2)}")
    return result


def run_data_extraction_pipeline():
    """Run complete data extraction pipeline"""
    logger.info("\n=== Running Data Extraction Pipeline ===")
    
    extractor = NPHIESDataExtractor()
    
    # Example data - replace with actual data sources
    eligibility_members = [
        {
            "member_id": "1234567890",
            "payer_id": settings.NPHIES_PAYER_ID,
            "service_date": "2025-10-22"
        },
        # Add more members as needed
    ]
    
    claims_data = [
        {
            "claim_type": "professional",
            "patient_id": "patient-001",
            "member_id": "1234567890",
            "payer_id": settings.NPHIES_PAYER_ID,
            "services": [
                {
                    "code": "99213",
                    "description": "Office Visit",
                    "quantity": 1,
                    "unit_price": 150.00
                }
            ],
            "total_amount": 150.00
        },
        # Add more claims as needed
    ]
    
    # Run extraction
    results = extractor.run_full_extraction(
        eligibility_members=eligibility_members,
        claims_data=claims_data,
        poll_communications=True,
        output_dir="output"
    )
    
    logger.info("\n=== Extraction Summary ===")
    logger.info(json.dumps(results["summary"], indent=2))
    
    return results


def main():
    """Main application entry point"""
    try:
        # Print banner
        print_banner()
        
        # Check system status
        status = check_system_status()
        
        if not status["ready"]:
            logger.error("\n❌ System not ready. Please fix the issues above.")
            return 1
        
        logger.info("\n✅ System ready!")
        
        # Example usage - uncomment what you need
        
        # 1. Single eligibility check
        # example_eligibility_check()
        
        # 2. Single claim submission
        # example_claim_submission()
        
        # 3. Poll communications
        # example_communication_poll()
        
        # 4. Run full data extraction pipeline
        logger.info("\n" + "="*60)
        logger.info("Starting data extraction pipeline...")
        logger.info("="*60)
        
        run_data_extraction_pipeline()
        
        logger.info("\n" + "="*60)
        logger.info("✅ Application completed successfully!")
        logger.info("="*60)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Application interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\n❌ Application error: {str(e)}", exc_info=True)
        return 1
    finally:
        # Cleanup
        auth_manager.close()


if __name__ == "__main__":
    sys.exit(main())
