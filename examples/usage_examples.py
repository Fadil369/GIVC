"""
Example usage scripts for NPHIES Integration
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.eligibility import EligibilityService
from services.claims import ClaimsService
from services.communication import CommunicationService
from pipeline.extractor import NPHIESDataExtractor
from config.settings import settings
import json


def example_1_simple_eligibility():
    """Example 1: Simple eligibility check"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Eligibility Check")
    print("="*60)
    
    service = EligibilityService()
    
    result = service.check_eligibility(
        member_id="1234567890",
        payer_id=settings.NPHIES_PAYER_ID,
        service_date="2025-10-22",
        patient_name="Ahmed Mohammed",
        patient_gender="male",
        patient_dob="1985-05-15"
    )
    
    print(json.dumps(result, indent=2))


def example_2_batch_eligibility():
    """Example 2: Batch eligibility checks"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Batch Eligibility Checks")
    print("="*60)
    
    # Sample data - replace with actual member data
    members = [
        {
            "member_id": "1234567890",
            "payer_id": settings.NPHIES_PAYER_ID,
            "service_date": "2025-10-22",
            "patient_name": "Ahmed Mohammed"
        },
        {
            "member_id": "0987654321",
            "payer_id": settings.NPHIES_PAYER_ID,
            "service_date": "2025-10-22",
            "patient_name": "Fatima Ali"
        }
    ]
    
    service = EligibilityService()
    results = service.batch_check_eligibility(members)
    
    print(f"\nProcessed {len(results)} members")
    for idx, result in enumerate(results, 1):
        print(f"\nMember {idx}: {'✓ Eligible' if result['success'] else '✗ Not Eligible'}")


def example_3_submit_claim():
    """Example 3: Submit a professional claim"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Submit Professional Claim")
    print("="*60)
    
    service = ClaimsService()
    
    # Define services provided
    services = [
        {
            "code": "99213",
            "description": "Office/Outpatient Visit, Established Patient",
            "quantity": 1,
            "unit_price": 150.00,
            "net_amount": 150.00
        },
        {
            "code": "80053",
            "description": "Comprehensive Metabolic Panel",
            "quantity": 1,
            "unit_price": 75.00,
            "net_amount": 75.00
        }
    ]
    
    result = service.submit_claim(
        claim_type="professional",
        patient_id="patient-12345",
        member_id="1234567890",
        payer_id=settings.NPHIES_PAYER_ID,
        services=services,
        total_amount=225.00,
        claim_date="2025-10-22",
        patient_name="Ahmed Mohammed"
    )
    
    print(json.dumps(result, indent=2))


def example_4_poll_communications():
    """Example 4: Poll for communications"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Poll Communications")
    print("="*60)
    
    service = CommunicationService()
    
    result = service.poll_communications()
    
    if result.get("success"):
        communications = result.get("communications", [])
        print(f"\nReceived {len(communications)} communications")
        
        for comm in communications:
            print(f"\n- ID: {comm['id']}")
            print(f"  Category: {comm['category']}")
            print(f"  Status: {comm['status']}")
            print(f"  Sent: {comm['sent']}")
    else:
        print(f"Error: {result.get('errors')}")


def example_5_complete_pipeline():
    """Example 5: Complete data extraction pipeline"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Complete Data Extraction Pipeline")
    print("="*60)
    
    extractor = NPHIESDataExtractor()
    
    # Eligibility members
    eligibility_members = [
        {
            "member_id": "1234567890",
            "payer_id": settings.NPHIES_PAYER_ID,
            "service_date": "2025-10-22"
        }
    ]
    
    # Claims to submit
    claims_data = [
        {
            "claim_type": "professional",
            "patient_id": "patient-12345",
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
        }
    ]
    
    # Run full extraction
    results = extractor.run_full_extraction(
        eligibility_members=eligibility_members,
        claims_data=claims_data,
        poll_communications=True,
        output_dir="examples/output"
    )
    
    print("\n=== Pipeline Summary ===")
    print(json.dumps(results["summary"], indent=2))
    print("\nResults saved to: examples/output/")


def main():
    """Run examples"""
    print("\n" + "="*60)
    print("NPHIES Integration - Usage Examples")
    print("="*60)
    
    print("\nAvailable Examples:")
    print("1. Simple eligibility check")
    print("2. Batch eligibility checks")
    print("3. Submit professional claim")
    print("4. Poll communications")
    print("5. Complete data extraction pipeline")
    print("0. Run all examples")
    
    try:
        choice = input("\nSelect example (0-5): ")
        
        if choice == "1":
            example_1_simple_eligibility()
        elif choice == "2":
            example_2_batch_eligibility()
        elif choice == "3":
            example_3_submit_claim()
        elif choice == "4":
            example_4_poll_communications()
        elif choice == "5":
            example_5_complete_pipeline()
        elif choice == "0":
            example_1_simple_eligibility()
            example_2_batch_eligibility()
            example_3_submit_claim()
            example_4_poll_communications()
            example_5_complete_pipeline()
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nExamples interrupted")
    except Exception as e:
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
