# NPHIES Integration - Getting Started Guide

> **Need a high-level roadmap?** See the companion [Nphies Integration Recommendations](./nphies_integration_recommendations.md) document for a strategic implementation checklist covering architecture, compliance, testing, and project planning.

## Quick Setup

### 1. Install Dependencies

```powershell
cd C:\nphies-integration
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and update with your credentials:

```powershell
copy .env.example .env
```

Edit `.env` with your actual credentials:
- `NPHIES_LICENSE` - Your healthcare facility license number
- `NPHIES_ORGANIZATION_ID` - Your NPHIES organization ID
- `NPHIES_PROVIDER_ID` - Your provider ID
- `NPHIES_PAYER_ID` - Insurance payer license number
- Certificate paths (for production only)

### 3. Test Connection

```powershell
python main.py
```

## Usage Examples

### Single Eligibility Check

```python
from services.eligibility import EligibilityService

service = EligibilityService()
result = service.check_eligibility(
    member_id="1234567890",
    payer_id="7000911508",
    service_date="2025-10-22"
)

print(result)
```

### Submit a Claim

```python
from services.claims import ClaimsService

service = ClaimsService()
result = service.submit_claim(
    claim_type="professional",
    patient_id="patient-001",
    member_id="1234567890",
    payer_id="7000911508",
    services=[
        {
            "code": "99213",
            "description": "Office Visit",
            "quantity": 1,
            "unit_price": 150.00
        }
    ],
    total_amount=150.00
)
```

### Poll Communications

```python
from services.communication import CommunicationService

service = CommunicationService()
result = service.poll_communications()

for comm in result.get("communications", []):
    print(f"Communication ID: {comm['id']}")
    print(f"Status: {comm['status']}")
    print(f"Content: {comm['payload']}")
```

### Run Complete Data Pipeline

```python
from pipeline.extractor import NPHIESDataExtractor

extractor = NPHIESDataExtractor()

# Prepare data
members = [
    {
        "member_id": "1234567890",
        "payer_id": "7000911508",
        "service_date": "2025-10-22"
    }
]

claims = [
    {
        "claim_type": "professional",
        "patient_id": "patient-001",
        "member_id": "1234567890",
        "payer_id": "7000911508",
        "services": [...],
        "total_amount": 150.00
    }
]

# Run extraction
results = extractor.run_full_extraction(
    eligibility_members=members,
    claims_data=claims,
    poll_communications=True,
    output_dir="output"
)
```

## API Operations

### Supported Operations

1. **Eligibility Verification** - Check patient insurance eligibility
2. **Prior Authorization** - Submit authorization requests
3. **Claim Submission** - Submit healthcare claims
4. **Claim Status Inquiry** - Query claim status
5. **Communication Polling** - Retrieve pending messages

### Response Handling

All service methods return a standardized response:

```python
{
    "success": True/False,
    "message": "Status message",
    "data": [...],  # Response data
    "errors": [],   # List of errors
    "request_id": "unique-id",
    "timestamp": "ISO timestamp"
}
```

## Data Pipeline

The extraction pipeline orchestrates multiple operations:

1. **Eligibility Extraction** - Batch eligibility checks
2. **Claims Extraction** - Batch claim submissions
3. **Communication Polling** - Retrieve all pending communications
4. **Results Storage** - Save results to JSON files

Output files are saved to the `output/` directory:
- `eligibility_results.json`
- `claims_results.json`
- `communications_results.json`
- `complete_extraction_results.json`

## Error Handling

The system includes comprehensive error handling:

- Automatic retry on network failures
- Validation before submission
- Detailed error logging
- Error collection in pipeline results

## Logging

Logs are saved to `logs/nphies_integration.log` with:
- Timestamp
- Log level
- Component name
- Message

Configure log level in `.env`:
```
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Certificates (Production Only)

For production environment:

1. Obtain SSL certificates from NPHIES
2. Place certificates in `certs/` directory:
   - `client_certificate.pem`
   - `private_key.pem`
   - `ca_bundle.pem`
3. Update paths in `.env`
4. Set `ENVIRONMENT=production`

## Troubleshooting

### Connection Issues

1. Verify network connectivity to NPHIES
2. Check credentials in `.env`
3. Review certificate configuration (production)
4. Check logs for detailed error messages

### Validation Errors

1. Verify required fields are provided
2. Check data formats (dates, IDs)
3. Review NPHIES API documentation
4. Enable DEBUG logging

### Authentication Errors

1. Verify license number
2. Confirm organization/provider IDs
3. Check certificate validity (production)
4. Contact NPHIES support

## Support

- NPHIES Portal: https://portal.nphies.sa
- NPHIES Documentation: https://portal.nphies.sa/ig/
- Project Issues: Create issue in repository

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure environment
3. ✅ Test connection
4. 🔄 Customize for your use case
5. 🔄 Integrate with your systems
6. 🔄 Deploy to production
