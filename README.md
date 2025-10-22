# NPHIES API Integration Platform

Complete Python integration solution for Saudi Arabia's National Platform for Health Insurance Electronic Services (NPHIES).

## 🌟 Features

- **Authentication & Security**: Certificate-based authentication with encrypted communications
- **Eligibility Verification**: Real-time patient insurance eligibility checks
- **Prior Authorization**: Submit and track prior authorization requests
- **Claims Management**: Submit, query, and track healthcare claims
- **Communication Polling**: Retrieve and process NPHIES communications
- **Data Pipeline**: Automated data extraction and processing workflows
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Logging**: Detailed logging for debugging and monitoring

## 📋 Requirements

- Python 3.8+
- Valid NPHIES credentials (License, NPHIES ID)
- SSL/TLS certificates for production environment

## 🚀 Quick Start

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Update credentials and endpoints

3. **Run Data Extraction**:
```bash
python main.py
```

## 📁 Project Structure

```
nphies-integration/
├── config/              # Configuration files
│   ├── settings.py      # Application settings
│   └── endpoints.py     # API endpoints
├── auth/                # Authentication modules
│   ├── auth_manager.py  # Authentication handler
│   └── cert_manager.py  # Certificate management
├── services/            # API service modules
│   ├── eligibility.py   # Eligibility verification
│   ├── authorization.py # Prior authorization
│   ├── claims.py        # Claims management
│   └── communication.py # Communication polling
├── models/              # Data models
│   ├── request.py       # Request models
│   └── response.py      # Response models
├── pipeline/            # Data pipeline
│   ├── extractor.py     # Data extraction
│   └── processor.py     # Data processing
├── utils/               # Utility functions
│   ├── logger.py        # Logging utilities
│   ├── validators.py    # Data validators
│   └── helpers.py       # Helper functions
├── tests/               # Unit tests
├── main.py             # Main application entry
├── requirements.txt    # Python dependencies
└── .env.example        # Environment template
```

## 🔐 Environment Variables

```
NPHIES_BASE_URL=https://NPHIES.sa/api/fs/fhir
NPHIES_LICENSE=your_license_number
NPHIES_ORGANIZATION_ID=your_organization_id
NPHIES_PROVIDER_ID=your_provider_id
CERT_FILE_PATH=path/to/certificate.pem
CERT_KEY_PATH=path/to/private_key.pem
ENVIRONMENT=production  # or sandbox
LOG_LEVEL=INFO
```

## 📊 Usage Examples

### Eligibility Check
```python
from services.eligibility import EligibilityService

service = EligibilityService()
result = service.check_eligibility(
    member_id="123456789",
    payer_id="7000911508",
    service_date="2025-10-22"
)
```

### Submit Claim
```python
from services.claims import ClaimsService

service = ClaimsService()
claim = service.submit_claim(claim_data)
```

## 🏥 Supported Operations

- ✅ Eligibility Verification
- 📋 Prior Authorization Request
- 💰 Claim Submission
- 🔍 Claim Status Inquiry
- 💬 Communication Polling
- 📝 Authorization Status Check
- 🔄 Batch Processing

## 📖 API Documentation

For detailed NPHIES API documentation, visit:
- Portal: https://portal.nphies.sa
- FHIR Implementation Guide: https://portal.nphies.sa/ig/

## 🛡️ Security

- All communications use TLS 1.2+
- Certificate-based authentication
- Sensitive data encryption
- Audit logging enabled

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Support

For issues and questions:
- NPHIES Support: Via portal
- Project Issues: GitHub Issues
