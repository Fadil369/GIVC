"""
Enhanced Main Application with Ultimate Features
Advanced NPHIES Integration with Analytics, RCM, and AI-Powered Processing
"""
import sys
import json
from pathlib import Path
from datetime import datetime
import argparse

from config.settings import settings
from auth.auth_manager import auth_manager
from auth.cert_manager import check_certificates
from pipeline.extractor import NPHIESDataExtractor
from pipeline.data_processor import NPHIESDataProcessor
from services.eligibility import EligibilityService
from services.claims import ClaimsService
from services.prior_authorization import PriorAuthorizationService
from services.communication import CommunicationService
from services.analytics import NPHIESAnalytics
from utils.logger import setup_logger, get_logger

# Setup enhanced logging
logger = setup_logger(
    name="nphies",
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    console=True
)


def print_enhanced_banner():
    """Print enhanced application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🏥  NPHIES RCM Integration Platform - Ultimate Edition           ║
║                                                                      ║
║   Advanced Revenue Cycle Management for Saudi Healthcare            ║
║   AI-Powered Analytics • Real-time Processing • Complete RCM        ║
║                                                                      ║
║   Version: 2.0.0 ULTIMATE                                           ║
║   Environment: {env:<54}║
║   Organization: {org:<54}║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """.format(
        env=settings.ENVIRONMENT.upper(),
        org=settings.PROVIDER_NAME[:54]
    )
    print(banner)


def check_enhanced_system_status():
    """Enhanced system status check with comprehensive diagnostics"""
    logger.info("=== Enhanced System Status Check ===")
    
    status = {
        "environment": settings.ENVIRONMENT,
        "api_url": settings.api_base_url,
        "organization": {
            "name": settings.PROVIDER_NAME,
            "id": settings.NPHIES_ORGANIZATION_ID,
            "license": settings.NPHIES_LICENSE
        },
        "features": {
            "eligibility": True,
            "claims": True,
            "prior_authorization": True,
            "communications": True,
            "analytics": True,
            "batch_processing": True
        },
        "ready": True
    }
    
    # Check certificates
    if settings.ENVIRONMENT == "production":
        logger.info("Checking SSL certificates...")
        cert_status = check_certificates()
        status["certificates"] = cert_status
        
        if not cert_status["ready"]:
            logger.warning("⚠️  Certificates not ready for production")
            status["ready"] = False
        else:
            logger.info("✓ Certificates validated")
    
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
    
    # Check data directories
    logger.info("Checking data directories...")
    for directory in ["logs", "output", "certs", "data"]:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Created directory: {directory}")
        else:
            logger.info(f"✓ Directory exists: {directory}")
    
    return status


def run_enhanced_eligibility_workflow(csv_file: str = None):
    """Enhanced eligibility workflow with CSV processing"""
    logger.info("\n=== Enhanced Eligibility Verification Workflow ===")
    
    processor = NPHIESDataProcessor()
    service = EligibilityService()
    
    # Load data from CSV if provided
    if csv_file:
        logger.info(f"Loading eligibility batch from CSV: {csv_file}")
        batch = processor.process_csv_to_eligibility_batch(csv_file)
        
        # Validate and clean
        valid_batch, invalid_batch = processor.validate_and_clean_batch(batch, "eligibility")
        
        if invalid_batch:
            logger.warning(f"Found {len(invalid_batch)} invalid records")
            # Export invalid records for review
            processor.export_to_csv(
                invalid_batch,
                "output/invalid_eligibility_records.csv"
            )
        
        logger.info(f"Processing {len(valid_batch)} valid eligibility checks")
        results = service.batch_check_eligibility(valid_batch)
        
    else:
        # Example single check
        logger.info("Running example eligibility check")
        results = [service.check_eligibility(
            member_id="1234567890",
            payer_id=settings.NPHIES_PAYER_ID,
            service_date=datetime.now().strftime("%Y-%m-%d")
        )]
    
    # Generate analytics
    analytics = NPHIESAnalytics()
    analysis = analytics.analyze_eligibility_results(results)
    
    logger.info("\n=== Eligibility Analysis ===")
    logger.info(f"Total Checks: {analysis['total_checks']}")
    logger.info(f"Success Rate: {analysis.get('success_rate', 0):.1f}%")
    logger.info(f"Eligibility Rate: {analysis.get('eligibility_rate', 0):.1f}%")
    logger.info(f"Eligible Members: {analysis['eligible_members']}/{analysis['total_checks']}")
    
    return results, analysis


def run_enhanced_claims_workflow(claims_file: str = None):
    """Enhanced claims workflow with advanced processing"""
    logger.info("\n=== Enhanced Claims Processing Workflow ===")
    
    processor = NPHIESDataProcessor()
    service = ClaimsService()
    
    # Load claims
    if claims_file:
        logger.info(f"Loading claims from: {claims_file}")
        if claims_file.endswith('.json'):
            claims = processor.process_claims_from_json(claims_file)
        else:
            logger.error("Only JSON format supported for claims files")
            return [], {}
        
        # Transform to NPHIES format
        claims = [processor.transform_claim_to_nphies_format(claim) for claim in claims]
        
        # Validate
        valid_claims, invalid_claims = processor.validate_and_clean_batch(claims, "claims")
        
        if invalid_claims:
            logger.warning(f"Found {len(invalid_claims)} invalid claims")
            with open("output/invalid_claims.json", 'w') as f:
                json.dump(invalid_claims, f, indent=2)
        
        logger.info(f"Submitting {len(valid_claims)} valid claims")
        results = []
        for claim in valid_claims:
            result = service.submit_claim(**claim)
            results.append(result)
    else:
        # Example claim
        logger.info("Running example claim submission")
        results = [service.submit_claim(
            claim_type="professional",
            patient_id="patient-001",
            member_id="1234567890",
            payer_id=settings.NPHIES_PAYER_ID,
            services=[{
                "code": "99213",
                "description": "Office Visit",
                "quantity": 1,
                "unit_price": 150.00
            }],
            total_amount=150.00
        )]
    
    # Generate analytics
    analytics = NPHIESAnalytics()
    analysis = analytics.analyze_claims_results(results)
    
    logger.info("\n=== Claims Analysis ===")
    logger.info(f"Total Claims: {analysis['total_claims']}")
    logger.info(f"Submission Success Rate: {analysis.get('submission_success_rate', 0):.1f}%")
    logger.info(f"Approval Rate: {analysis.get('approval_rate', 0):.1f}%")
    logger.info(f"Total Claimed: {analysis['total_claimed_amount']:.2f} SAR")
    logger.info(f"Total Approved: {analysis['total_approved_amount']:.2f} SAR")
    logger.info(f"Reimbursement Rate: {analysis.get('reimbursement_rate', 0):.1f}%")
    
    return results, analysis


def run_complete_rcm_pipeline(
    eligibility_csv: str = None,
    claims_json: str = None,
    poll_comms: bool = True
):
    """Run complete Revenue Cycle Management pipeline"""
    logger.info("\n" + "="*70)
    logger.info("  COMPLETE RCM PIPELINE - NPHIES Ultimate Edition")
    logger.info("="*70)
    
    pipeline_results = {
        "started_at": datetime.now().isoformat(),
        "eligibility": None,
        "claims": None,
        "communications": None,
        "analytics_report": None
    }
    
    # Phase 1: Eligibility Verification
    logger.info("\n--- PHASE 1: Eligibility Verification ---")
    elig_results, elig_analysis = run_enhanced_eligibility_workflow(eligibility_csv)
    pipeline_results["eligibility"] = {
        "results": elig_results,
        "analysis": elig_analysis
    }
    
    # Phase 2: Claims Processing
    logger.info("\n--- PHASE 2: Claims Processing ---")
    claims_results, claims_analysis = run_enhanced_claims_workflow(claims_json)
    pipeline_results["claims"] = {
        "results": claims_results,
        "analysis": claims_analysis
    }
    
    # Phase 3: Communications
    if poll_comms:
        logger.info("\n--- PHASE 3: Communication Polling ---")
        comm_service = CommunicationService()
        comm_result = comm_service.poll_communications()
        pipeline_results["communications"] = comm_result
        logger.info(f"Retrieved {len(comm_result.get('communications', []))} communications")
    
    # Phase 4: Comprehensive Analytics
    logger.info("\n--- PHASE 4: Analytics & Reporting ---")
    analytics = NPHIESAnalytics()
    report = analytics.generate_performance_report(
        eligibility_results=elig_results,
        claims_results=claims_results
    )
    pipeline_results["analytics_report"] = report
    
    # Display key metrics
    kpis = analytics.get_key_metrics(report)
    logger.info("\n=== KEY PERFORMANCE INDICATORS ===")
    logger.info(f"Overall Success Rate: {kpis['overall_success_rate']:.1f}%")
    logger.info(f"Total Transactions: {kpis['total_transactions']}")
    logger.info(f"Eligibility Rate: {kpis['eligibility_rate']:.1f}%")
    logger.info(f"Claims Approval Rate: {kpis['claims_approval_rate']:.1f}%")
    logger.info(f"Reimbursement Rate: {kpis['reimbursement_rate']:.1f}%")
    logger.info(f"Total Claimed: {kpis['total_claimed']:.2f} SAR")
    logger.info(f"Total Approved: {kpis['total_approved']:.2f} SAR")
    
    # Display recommendations
    logger.info("\n=== RECOMMENDATIONS ===")
    for rec in report['recommendations']:
        logger.info(rec)
    
    # Save complete results
    output_dir = Path("output/rcm_pipeline")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"complete_rcm_results_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pipeline_results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n✅ Complete RCM pipeline results saved to: {output_file}")
    
    pipeline_results["completed_at"] = datetime.now().isoformat()
    return pipeline_results


def main():
    """Enhanced main application with CLI arguments"""
    parser = argparse.ArgumentParser(
        description="NPHIES RCM Integration Platform - Ultimate Edition"
    )
    parser.add_argument(
        '--mode',
        choices=['eligibility', 'claims', 'full-rcm', 'status'],
        default='status',
        help='Operation mode'
    )
    parser.add_argument(
        '--eligibility-csv',
        help='CSV file with eligibility checks'
    )
    parser.add_argument(
        '--claims-json',
        help='JSON file with claims data'
    )
    parser.add_argument(
        '--no-poll',
        action='store_true',
        help='Skip communication polling'
    )
    
    args = parser.parse_args()
    
    try:
        # Print banner
        print_enhanced_banner()
        
        # Check system status
        status = check_enhanced_system_status()
        
        if not status["ready"]:
            logger.error("\n❌ System not ready. Please fix the issues above.")
            return 1
        
        logger.info("\n✅ System ready for advanced RCM operations!")
        
        # Execute based on mode
        if args.mode == 'status':
            logger.info("\n=== System Status Report ===")
            logger.info(json.dumps(status, indent=2))
        
        elif args.mode == 'eligibility':
            run_enhanced_eligibility_workflow(args.eligibility_csv)
        
        elif args.mode == 'claims':
            run_enhanced_claims_workflow(args.claims_json)
        
        elif args.mode == 'full-rcm':
            run_complete_rcm_pipeline(
                eligibility_csv=args.eligibility_csv,
                claims_json=args.claims_json,
                poll_comms=not args.no_poll
            )
        
        logger.info("\n" + "="*70)
        logger.info("✅ NPHIES RCM Platform - Operation Completed Successfully!")
        logger.info("="*70)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Operation interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\n❌ Application error: {str(e)}", exc_info=True)
        return 1
    finally:
        auth_manager.close()


if __name__ == "__main__":
    sys.exit(main())
