# BrainSAIT-NPHIES-GIVC Integration Platform

AI-Powered Healthcare Claims Integration Platform for Al Hayat National Hospital, combining NPHIES (National Platform for Health Insurance Exchange Services) with legacy portal integrations and GIVC Ultrathink AI capabilities.

## 🚀 Features

### NPHIES Integration
- ✅ **Certificate-Based Authentication** - OpenID Connect with HSB.nphies.sa
- ✅ **FHIR-Compliant Transactions** - Full support for FHIR resources
- ✅ **Eligibility Checking** - Real-time coverage verification
- ✅ **Prior Authorization** - Pre-approval for planned services
- ✅ **Claims Submission** - Institutional and professional claims
- ✅ **Communication** - Claim-related messaging and attachments
- ✅ **Status Polling** - Transaction bundle status tracking

### GIVC Ultrathink AI
- 🤖 **Intelligent Validation** - AI-powered claim validation with confidence scoring
- 🎯 **Smart Form Completion** - Auto-fill based on historical patterns
- 🔍 **Automated Error Detection** - Identify issues before submission
- 📈 **Claim Optimization** - Suggestions for better reimbursement
- 📊 **Analytics & Insights** - Performance metrics and trends

### Legacy Portal Support
- 🏥 **OASES** - 6 hospital branches (Riyadh, Madinah, Unaizah, Khamis, Jizan, Abha)
- 🏛️ **MOH** - Ministry of Health approval and claims portals
- 💼 **Jisr** - HR platform integration
- 🏢 **Bupa Arabia** - Direct insurance portal

### Smart Routing
- **NPHIES-First** - Try NPHIES, fallback to legacy
- **Legacy-Only** - Direct submission to legacy portals
- **All Portals** - Parallel submission to all configured portals
- **Smart Route** - AI-based routing decision

## 📋 Prerequisites

- Python 3.9 or higher
- NPHIES Production Certificate (`.pem` files)
- Access credentials for all portals
- PostgreSQL database (optional)
- Redis server (optional)

## 🔧 Installation

### 1. Clone or Navigate to Project

```powershell
cd C:\Users\rcmrejection3\nphies-rcm\brainsait-nphies-givc
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update with your credentials:

```powershell
copy .env.example .env
notepad .env
```

### 5. Place NPHIES Certificates

Place your NPHIES certificates in the `certificates/` directory:

```
certificates/
├── nphies_production.pem
└── nphies_production_key.pem
```

### 6. Configure YAML

Update `config/config.yaml` with your hospital-specific settings.

## 🚀 Running the Application

### Development Mode

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```powershell
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Quick Start Examples

### 1. Check Patient Eligibility

```bash
curl -X POST "http://localhost:8000/api/v1/nphies/eligibility" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "1234567890",
    "insurance_id": "TAWUNIYA-12345",
    "service_date": "2024-01-15"
  }'
```

### 2. Submit Claim with AI Validation

```bash
curl -X POST "http://localhost:8000/api/v1/claims/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": {
      "patient_id": "1234567890",
      "patient_name": "Ahmed Ali",
      "insurance_id": "TAWUNIYA-12345",
      "service_date": "2024-01-15",
      "items": [
        {
          "code": "99213",
          "description": "Office Visit",
          "quantity": 1,
          "unit_price": 150.00
        }
      ]
    },
    "strategy": "nphies_first"
  }'
```

### 3. AI Validation Only

```bash
curl -X POST "http://localhost:8000/api/v1/givc/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": {
      "patient_id": "1234567890",
      "insurance_id": "TAWUNIYA-12345",
      "service_date": "2024-01-15",
      "items": [...]
    }
  }'
```

### 4. Health Check

```bash
curl http://localhost:8000/api/v1/health/
```

## 🏗️ Project Structure

```
brainsait-nphies-givc/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── claims.py        # Claims submission
│   │       ├── nphies.py        # NPHIES-specific operations
│   │       ├── givc.py          # GIVC AI features
│   │       └── health.py        # Health monitoring
│   ├── connectors/
│   │   ├── base.py              # Base connector class
│   │   ├── nphies.py            # NPHIES connector
│   │   ├── oases.py             # OASES connector
│   │   ├── moh.py               # MOH connector
│   │   ├── jisr.py              # Jisr connector
│   │   └── bupa.py              # Bupa connector
│   ├── services/
│   │   ├── integration.py       # Integration orchestration
│   │   └── givc.py              # GIVC AI service
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   └── logging.py           # Logging setup
│   └── models/
│       └── schemas.py           # Pydantic models
├── config/
│   └── config.yaml              # Portal configurations
├── certificates/
│   └── (NPHIES certificates)
├── logs/
│   └── app.log
├── tests/
│   └── (test files)
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── main.py                      # FastAPI application
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔐 Hospital Configuration

**Al Hayat National Hospital**
- NPHIES ID: `10000000000988`
- CHI ID: `1048`
- License: `7000911508`
- FTP Host: `172.25.11.15`

**Branches:**
- Riyadh: 10.67.4.180
- Madinah: 192.168.192.5
- Unaizah: 192.168.80.5
- Khamis: 192.168.70.5
- Jizan: 192.168.60.5
- Abha: 192.168.50.5

## 📊 Insurance Configuration

**TAWUNIYA** (Primary)
- Group Code: `1096`
- 8 BALSAM GOLD policies
- Contact: MOHAMMED SALEH

**NCCI Referral**
- Account: `INS-809`

## 🧪 Testing

Run tests with pytest:

```powershell
pytest tests/ -v --cov=app
```

## 📝 Environment Variables

Key environment variables (see `.env.example` for complete list):

```ini
# NPHIES
NPHIES_HOSPITAL_ID=10000000000988
NPHIES_CERT_PATH=./certificates/nphies_production.pem
NPHIES_KEY_PATH=./certificates/nphies_production_key.pem

# GIVC
GIVC_API_KEY=your_api_key_here
GIVC_ULTRATHINK_ENABLED=true

# Portal Credentials
OASES_RIYADH_USERNAME=ITSupport
OASES_RIYADH_PASSWORD=your_password

MOH_APPROVAL_USERNAME=admin
MOH_APPROVAL_PASSWORD=Hcd@230F836
```

## 🤝 Integration Workflow

1. **Eligibility Check** → Verify patient coverage via NPHIES
2. **AI Validation** → GIVC Ultrathink validates claim data
3. **Prior Authorization** → Submit pre-approval if required
4. **Claim Submission** → Smart routing to NPHIES/legacy portals
5. **Status Tracking** → Monitor claim processing
6. **Communication** → Exchange messages/attachments

## 🔄 Submission Strategies

### NPHIES-First (Recommended)
```python
{
  "strategy": "nphies_first"
}
```
- Attempts NPHIES submission
- Falls back to legacy portals if NPHIES fails
- Best for TAWUNIYA and supported insurers

### Smart Route (AI-Powered)
```python
{
  "strategy": "smart_route"
}
```
- AI determines optimal routing
- Based on insurance type and historical success rates

### All Portals
```python
{
  "strategy": "all_portals"
}
```
- Submits to all configured portals in parallel
- Maximum coverage, useful for complex cases

## 🛡️ Security Features

- ✅ Certificate-based NPHIES authentication
- ✅ Session management with expiry
- ✅ API key authentication for GIVC
- ✅ HTTPS/TLS encryption
- ✅ Input validation with Pydantic
- ✅ Circuit breaker pattern
- ✅ Rate limiting (configurable)

## 📈 Monitoring & Logging

- Structured JSON logging
- Health check endpoints
- Performance metrics
- AI validation insights
- Claim submission analytics

## 🐛 Troubleshooting

### NPHIES Authentication Failed
- Verify certificates are valid and not expired
- Check certificate paths in `.env`
- Ensure correct realm configuration

### Legacy Portal Connection Failed
- Verify credentials in `.env`
- Check network connectivity to portal IPs
- Review session timeout settings

### AI Validation Low Confidence
- Review validation errors and warnings
- Ensure all required fields are populated
- Check data formats (dates, IDs, amounts)

## 📞 Support

For issues or questions:
- Check logs in `logs/app.log`
- Review API documentation at `/docs`
- Contact system administrator

## 📄 License

Copyright © 2024 Al Hayat National Hospital - BrainSAIT Division

---

**Version**: 2.0.0  
**Last Updated**: January 2024  
**Platform**: NPHIES Production (HSB.nphies.sa)
