# NPHIES Integration Platform - Complete Setup & Deployment Guide

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [API Integration](#api-integration)
5. [Data Extraction](#data-extraction)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

## 🔧 System Requirements

- Python 3.8 or higher
- Windows 10/11 or Windows Server 2016+
- Network access to NPHIES portal (https://nphies.sa)
- Valid NPHIES credentials (License, Organization ID)
- SSL certificates (for production environment)

## 📦 Installation

### Step 1: Clone or Download the Project

```powershell
cd C:\
# Project is already at C:\nphies-integration
```

### Step 2: Create Virtual Environment (Recommended)

```powershell
cd C:\nphies-integration
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Create Required Directories

```powershell
New-Item -ItemType Directory -Force -Path logs, output, certs
```

## ⚙️ Configuration

### Step 1: Create Environment File

```powershell
copy .env.example .env
```

### Step 2: Update Credentials

Edit `.env` file with your actual credentials:

```ini
# NPHIES API Configuration
NPHIES_BASE_URL=https://NPHIES.sa/api/fs/fhir
NPHIES_SANDBOX_URL=https://HSB.nphies.sa/api/fs/fhir

# Your Organization Credentials
NPHIES_LICENSE=7000911508          # Your license number
NPHIES_ORGANIZATION_ID=10000000000988  # Your org ID
NPHIES_PROVIDER_ID=1048            # Your provider ID
NPHIES_PAYER_ID=7000911508         # Insurance payer ID

# Provider Details
PROVIDER_NAME=Al Hayat National Hospital
PROVIDER_CHI_ID=1048
INSURANCE_GROUP_CODE=1096

# Environment (sandbox for testing, production for live)
ENVIRONMENT=sandbox

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/nphies_integration.log
```

### Step 3: Configure Certificates (Production Only)

For production environment:

1. Obtain certificates from NPHIES
2. Place in `certs/` directory:
   - `client_certificate.pem`
   - `private_key.pem`
   - `ca_bundle.pem`
3. Update paths in `.env`

## 🔌 API Integration

### Understanding NPHIES API

NPHIES uses **FHIR (Fast Healthcare Interoperability Resources)** standard:

- **Base Endpoint**: `https://NPHIES.sa/api/fs/fhir`
- **Message Format**: FHIR Bundle (JSON)
- **Authentication**: Certificate-based (production) or License-based (sandbox)
- **Message Types**:
  - Eligibility Verification
  - Prior Authorization
  - Claim Submission
  - Claim Inquiry
  - Communication Polling

### API Request Flow

```
1. Build FHIR Bundle
   ├── MessageHeader (routing info)
   ├── Request Resource (Eligibility/Claim/etc)
   ├── Patient Resource
   ├── Coverage Resource
   └── Organization Resources

2. Authenticate Request
   ├── Add License/Org headers
   └── Attach certificates (production)

3. Send to NPHIES
   POST https://NPHIES.sa/api/fs/fhir/$process-message

4. Parse Response
   ├── Extract resources from Bundle
   ├── Check for errors
   └── Process results
```

### Available Services

#### 1. Eligibility Service

```python
from services.eligibility import EligibilityService

service = EligibilityService()
result = service.check_eligibility(
    member_id="1234567890",
    payer_id="7000911508",
    service_date="2025-10-22"
)
```

#### 2. Claims Service

```python
from services.claims import ClaimsService

service = ClaimsService()
result = service.submit_claim(
    claim_type="professional",
    patient_id="patient-001",
    member_id="1234567890",
    payer_id="7000911508",
    services=[...],
    total_amount=150.00
)
```

#### 3. Communication Service

```python
from services.communication import CommunicationService

service = CommunicationService()
result = service.poll_communications()
```

## 📊 Data Extraction

### Using the Data Pipeline

The extraction pipeline provides automated data collection:

```python
from pipeline.extractor import NPHIESDataExtractor

extractor = NPHIESDataExtractor()

# Define data sources
members_to_check = [
    {"member_id": "1234567890", "payer_id": "7000911508"},
    {"member_id": "0987654321", "payer_id": "7000911508"}
]

claims_to_submit = [
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
    eligibility_members=members_to_check,
    claims_data=claims_to_submit,
    poll_communications=True,
    output_dir="output"
)
```

### Output Files

Results are saved to JSON files:

```
output/
├── eligibility_results.json          # Eligibility check results
├── claims_results.json                # Claim submission results
├── communications_results.json        # Polled communications
└── complete_extraction_results.json   # Complete pipeline summary
```

### Integrating with Your Platform

#### Option 1: Direct Integration

```python
# Import services into your application
from services.eligibility import EligibilityService

# Use in your code
eligibility = EligibilityService()
result = eligibility.check_eligibility(...)
```

#### Option 2: API Wrapper

Create REST API wrapper using Flask/FastAPI:

```python
from fastapi import FastAPI
from services.eligibility import EligibilityService

app = FastAPI()
eligibility = EligibilityService()

@app.post("/api/check-eligibility")
def check_eligibility(data: dict):
    return eligibility.check_eligibility(**data)
```

#### Option 3: Scheduled Jobs

Use Windows Task Scheduler or cron:

```powershell
# Run daily at 2 AM
schtasks /create /tn "NPHIES Data Extraction" /tr "C:\nphies-integration\venv\Scripts\python.exe C:\nphies-integration\main.py" /sc daily /st 02:00
```

## 🚀 Production Deployment

### Pre-Deployment Checklist

- [ ] Obtain production NPHIES credentials
- [ ] Install and configure SSL certificates
- [ ] Update `.env` with production values
- [ ] Set `ENVIRONMENT=production`
- [ ] Test connection to production endpoint
- [ ] Setup logging and monitoring
- [ ] Configure backup and recovery
- [ ] Document runbooks and procedures

### Production Configuration

```ini
# .env for production
ENVIRONMENT=production
NPHIES_BASE_URL=https://NPHIES.sa/api/fs/fhir

# Production credentials
NPHIES_LICENSE=YOUR_PRODUCTION_LICENSE
NPHIES_ORGANIZATION_ID=YOUR_PROD_ORG_ID

# Certificates
CERT_FILE_PATH=C:/nphies-integration/certs/prod_certificate.pem
CERT_KEY_PATH=C:/nphies-integration/certs/prod_key.pem
CA_BUNDLE_PATH=C:/nphies-integration/certs/ca_bundle.pem

# Production logging
LOG_LEVEL=INFO
LOG_FILE=C:/logs/nphies_production.log
```

### Running in Production

```powershell
# Activate virtual environment
cd C:\nphies-integration
.\venv\Scripts\Activate.ps1

# Run application
python main.py

# Or run as Windows service (requires additional setup)
```

### Monitoring & Logging

Monitor these log files:
- `logs/nphies_integration.log` - Application logs
- `output/` - Extraction results

Key metrics to monitor:
- Success/failure rates
- Response times
- Error patterns
- API quotas/limits

## 🔍 Troubleshooting

### Common Issues

#### 1. Connection Failed

**Problem**: Cannot connect to NPHIES API

**Solutions**:
```powershell
# Check network connectivity
Test-NetConnection NPHIES.sa -Port 443

# Verify DNS resolution
nslookup NPHIES.sa

# Check firewall rules
# Review proxy settings if behind corporate firewall
```

#### 2. Certificate Errors (Production)

**Problem**: SSL certificate validation fails

**Solutions**:
- Verify certificate files exist and are readable
- Check certificate expiration date
- Ensure private key matches certificate
- Verify CA bundle contains correct root certificates

```python
# Test certificates
from auth.cert_manager import check_certificates
status = check_certificates()
print(status)
```

#### 3. Authentication Errors

**Problem**: 401 Unauthorized or 403 Forbidden

**Solutions**:
- Verify license number is correct
- Confirm organization/provider IDs
- Check if credentials are active in NPHIES portal
- Review authentication headers

#### 4. Validation Errors

**Problem**: Request rejected due to invalid data

**Solutions**:
- Enable DEBUG logging: `LOG_LEVEL=DEBUG`
- Review validation error messages
- Check required fields are present
- Verify data formats (dates, codes, etc.)
- Consult NPHIES FHIR documentation

#### 5. Timeout Errors

**Problem**: Requests timing out

**Solutions**:
```ini
# Increase timeout in .env
REQUEST_TIMEOUT=60
MAX_RETRIES=5
RETRY_DELAY=3
```

### Enable Debug Mode

```ini
# In .env
LOG_LEVEL=DEBUG
```

### Get Support

1. **NPHIES Portal**: https://portal.nphies.sa
2. **NPHIES Documentation**: https://portal.nphies.sa/ig/
3. **Technical Support**: Contact through NPHIES portal
4. **Project Issues**: Review code and logs

## 📈 Performance Optimization

### Batch Processing

Process multiple records efficiently:

```python
# Instead of individual calls
for member in members:
    service.check_eligibility(**member)

# Use batch method
service.batch_check_eligibility(members)
```

### Async Processing (Future Enhancement)

Enable async processing in config:

```ini
ENABLE_ASYNC=true
PARALLEL_WORKERS=5
```

### Caching

Implement caching for repeated queries:
- Cache eligibility results (TTL: 24 hours)
- Cache organization lookups
- Use Redis or in-memory cache

## 🔐 Security Best Practices

1. **Credentials**: Never commit `.env` or certificates to version control
2. **Certificates**: Restrict file permissions (read-only for app user)
3. **Logs**: Mask sensitive data (member IDs, etc.)
4. **Network**: Use VPN/secure network for production
5. **Backups**: Encrypt backup files
6. **Access**: Limit who can run production jobs

## 📝 Maintenance

### Regular Tasks

- **Daily**: Review logs for errors
- **Weekly**: Check certificate expiration
- **Monthly**: Review and rotate logs
- **Quarterly**: Update dependencies
- **Annually**: Renew certificates

### Updating Dependencies

```powershell
pip list --outdated
pip install --upgrade package_name
pip freeze > requirements.txt
```

## 🎯 Next Steps

1. **Test in Sandbox**: Thoroughly test all operations
2. **Validate Data**: Ensure data quality and accuracy
3. **Monitor Performance**: Track metrics and optimize
4. **Scale**: Add more parallel workers as needed
5. **Integrate**: Connect with your healthcare systems
6. **Automate**: Schedule regular data extraction
7. **Document**: Keep documentation up-to-date

## 📚 Additional Resources

- **FHIR Specification**: https://hl7.org/fhir/
- **NPHIES Implementation Guide**: Available on portal
- **Saudi eHealth Guidelines**: https://ehealth.sa

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Contact**: Support via NPHIES Portal
