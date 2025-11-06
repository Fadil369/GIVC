"""
Initialize database with tables and sample data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from models import db, Customer, Policy, Provider, Claim, ClaimStatus
from datetime import datetime, timedelta
import random


def init_database():
    """Initialize database"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Check if data already exists
        if Customer.query.first():
            print("\n⚠ Database already contains data. Skipping sample data creation.")
            print("Use --force to recreate database with sample data.")
            return
        
        print("\nCreating sample data...")
        create_sample_data()
        
        print("\n✓ Database initialized successfully!")
        print("\nDatabase contains:")
        print(f"  Customers: {Customer.query.count()}")
        print(f"  Policies: {Policy.query.count()}")
        print(f"  Providers: {Provider.query.count()}")
        print(f"  Claims: {Claim.query.count()}")


def create_sample_data():
    """Create sample data for testing"""
    
    # Create sample providers
    providers = [
        Provider(
            provider_id='484600',
            provider_name='Prime Healthcare Center',
            provider_type='Hospital',
            specialty='General Medicine',
            email='contact@primehealthcare.ae',
            phone='+971-4-1234567',
            city='Dubai',
            country='UAE',
            bupa_network=True
        ),
        Provider(
            provider_id='484601',
            provider_name='City Medical Clinic',
            provider_type='Clinic',
            specialty='Family Medicine',
            email='info@citymedical.ae',
            phone='+971-4-7654321',
            city='Abu Dhabi',
            country='UAE',
            bupa_network=True
        ),
        Provider(
            provider_id='484602',
            provider_name='Life Care Pharmacy',
            provider_type='Pharmacy',
            specialty='Pharmacy',
            email='support@lifecare.ae',
            phone='+971-4-9876543',
            city='Dubai',
            country='UAE',
            bupa_network=True
        )
    ]
    
    for provider in providers:
        db.session.add(provider)
    
    db.session.commit()
    print("  ✓ Created 3 sample providers")
    
    # Create sample customers
    customers = []
    for i in range(1, 6):
        customer = Customer(
            customer_number=f'CUST-{datetime.now().strftime("%Y%m%d")}-{i:05d}',
            first_name=f'Customer{i}',
            last_name=f'Test{i}',
            date_of_birth=datetime(1980 + i, i, 15).date(),
            gender='Male' if i % 2 == 0 else 'Female',
            email=f'customer{i}@example.com',
            mobile=f'+971-50-{1000000+i}',
            city='Dubai',
            country='UAE'
        )
        customers.append(customer)
        db.session.add(customer)
    
    db.session.commit()
    print("  ✓ Created 5 sample customers")
    
    # Create sample policies
    policies = []
    for i, customer in enumerate(customers, 1):
        policy = Policy(
            policy_number=f'POL-{datetime.now().strftime("%Y%m%d")}-{i:05d}',
            customer_id=customer.id,
            policy_type='Health Insurance',
            plan_name=f'Premium Plan {i}',
            coverage_amount=100000 + (i * 50000),
            currency='AED',
            start_date=datetime.now().date() - timedelta(days=180),
            end_date=datetime.now().date() + timedelta(days=185),
            premium_amount=5000 + (i * 1000),
            premium_frequency='annual',
            is_active=True,
            status='active'
        )
        policies.append(policy)
        db.session.add(policy)
    
    db.session.commit()
    print("  ✓ Created 5 sample policies")
    
    # Create sample claims
    statuses = [ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW, ClaimStatus.APPROVED, ClaimStatus.REJECTED]
    
    for i in range(1, 11):
        policy = random.choice(policies)
        provider = random.choice(providers)
        status = random.choice(statuses)
        
        claim_amount = random.uniform(500, 5000)
        approved_amount = claim_amount * random.uniform(0.8, 1.0) if status == ClaimStatus.APPROVED else None
        
        claim = Claim(
            claim_number=f'CLM-{datetime.now().strftime("%Y%m%d")}-{i:05d}',
            customer_id=policy.customer_id,
            policy_id=policy.id,
            provider_id=provider.id,
            claim_date=datetime.now().date() - timedelta(days=random.randint(1, 60)),
            service_date=datetime.now().date() - timedelta(days=random.randint(1, 90)),
            description=f'Medical consultation and treatment {i}',
            diagnosis=f'Diagnosis {i}',
            treatment=f'Treatment {i}',
            claim_amount=round(claim_amount, 2),
            approved_amount=round(approved_amount, 2) if approved_amount else None,
            currency='AED',
            status=status,
            reference_number=f'REF-{i:06d}'
        )
        db.session.add(claim)
    
    db.session.commit()
    print("  ✓ Created 10 sample claims")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        print("⚠ Force mode: Dropping existing tables...")
        app = create_app()
        with app.app_context():
            db.drop_all()
    
    init_database()
