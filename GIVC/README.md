#  BrainSAIT-NPHIES-GIVC Ultimate Integration Platform

**Version 3.0.0**  **October 26, 2025**  **Unified Monorepo**

A comprehensive, AI-powered healthcare integration platform combining NPHIES compliance, GIVC Ultrathink AI, OASIS automation, and multi-portal connectivity for Al Hayat Hospital branches.

---

##  Table of Contents

- [ Overview](#-overview)
- [ Key Features](#-key-features)
- [ Architecture](#-architecture)
- [ Quick Start](#-quick-start)
- [ Documentation](#-documentation)
- [ Configuration](#-configuration)
- [ Testing](#-testing)
- [ Deployment](#-deployment-1)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Support](#-support)
- [ Roadmap](#-roadmap)

---

##  Overview

The **BrainSAIT-NPHIES-GIVC Ultimate Integration Platform** unifies:

- **NPHIES Compliance**  Full FHIR R4 implementation with certificate-based authentication
- **GIVC Ultrathink AI**  Intelligent claim validation, smart form completion, and error detection
- **OASIS Automation**  Automated portal interactions for all Al Hayat hospital branches
- **Multi-Portal Connectivity**  Seamless integration with MOH, Jisr, Bupa, TAWUNIYA, and NCCI systems
- **Enterprise Architecture**  Monorepo structure with microservices, infrastructure as code, and CI/CD

###  Hospital Coverage

- **Al Hayat Hospital**  NPHIES ID `10000000000988`, CHI ID `1048`, License `7000911508`
- **Branches**  Riyadh, Madinah, Unaizah, Khamis, Jizan, Abha
- **Credentials**  Unified U2415/U2415 across all OASES portals

###  Portal Integrations

- **NPHIES**  Production `https://HSB.nphies.sa` with certificate authentication
- **GIVC**  AI services at `https://4d31266d.givc-platform-static.pages.dev/`
- **TAWUNIYA**  8 BALSAM GOLD policies (Group Code 1096)
- **NCCI**  Account INS-809
- **OASES**  6 branch portals with standardized credentials

---

##  Key Features

###  NPHIES Integration v2.0

-  Certificate-based OpenID Connect authentication
-  FHIR R4 message bundles with MessageHeader-first structure
-  Five authorization types: institutional, professional, pharmacy, dental, vision
-  Automated claim submission with FHIR Claim/ClaimResponse
-  Real-time status polling and communication workflows
-  Comprehensive error handling with BV code awareness

###  GIVC Ultrathink AI

-  AI-powered claim validation with confidence scoring
-  Smart form completion for provider details, dates, and CPT codes
-  Automated detection of data gaps and pricing anomalies
-  Claim optimization, bundling recommendations, and prior-auth hints
-  Analytics dashboards with service-level metrics

###  OASIS Automation

-  Unified credentials (U2415/U2415) across all branches
-  Automated login, submission, and status retrieval workflows
-  Session manager with expiry and renewal
-  Retry logic plus circuit breaker resilience
-  Structured logging for audit readiness

###  Enterprise-Grade Architecture

-  Monorepo with apps, packages, services, and infrastructure modules
-  Microservices for NPHIES, OASES, GIVC AI, fraud detection, notifications, and more
-  Infrastructure as code (Docker, Kubernetes, Terraform)
-  Security hardening: certificate management, secrets isolation, audit trails
-  Monitoring: health checks, metrics endpoints, alerting hooks

---

##  Architecture

```
BrainSAIT-NPHIES-GIVC Ultimate Platform
 apps/                    # Frontend applications
    web/                 # Main web application
    admin/               # Administrative console
    api-gateway/         # API gateway UI
 packages/                # Shared packages (UI, utils, config)
 services/                # Backend microservices
    nphies-integration/  # FHIR-compliant NPHIES service
    givc-ultrathink/     # AI validation and optimization
    oasis-integration/   # OASES automation workflows
    fraud-detection/     # Predictive analytics modules
 infrastructure/          # Docker, Kubernetes, Terraform stacks
 app/                     # FastAPI integration gateway
    connectors/          # Portal connectors (NPHIES, OASES, etc.)
    services/            # Orchestration logic
    models/              # Pydantic schemas
    api/                 # REST endpoints
 config/                  # Environment & portal configuration
 docs/                    # Technical documentation
 tests/                   # Unit and integration tests
```

###  Data Flow

```
Patient Intake  AI Validation  Smart Routing  Portal Submission  Status Tracking
                                                                        
   FHIR Builder    Ultrathink AI     Strategy Engine   NPHIES/OASES     Monitoring & Alerts
```

---

##  Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- NPHIES production certificates

### 1. Navigate to Repository

```powershell
cd C:\Users\rcmrejection3\nphies-rcm\GIVC
```

### 2. Configure Environment

```powershell
# Copy environment template
copy .env.example .env

# Edit settings
notepad .env
```

### 3. Install Dependencies

```powershell
# Backend
pip install -r requirements.txt

# Frontend monorepo
npm install
```

### 4. Place Certificates

```powershell
mkdir certificates
copy C:\path\to\nphies_production.pem certificates\
copy C:\path\to\nphies_production_key.pem certificates\
```

### 5. Run Development Servers

```powershell
# FastAPI backend
python main.py

# Frontend (monorepo turbo workspace)
npm run dev
```

### 6. Access Interfaces

- API Docs: <http://localhost:8000/docs>
- Health Check: <http://localhost:8000/api/v1/health/>
- Frontend: <http://localhost:3000>

---

##  Documentation

### Core References

- [`ULTIMATE_INTEGRATION_GUIDE.md`](ULTIMATE_INTEGRATION_GUIDE.md)
- [`docs/NPHIES_INTEGRATION_GUIDE.md`](docs/NPHIES_INTEGRATION_GUIDE.md)
- [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md)
- [`QUICKSTART.md`](QUICKSTART.md)

### Operational Guides

- [`GIT_UPDATE_README.md`](GIT_UPDATE_README.md)
- [`GIT_UPDATE_GUIDE.md`](GIT_UPDATE_GUIDE.md)
- [`PRE_PUSH_CHECKLIST.md`](PRE_PUSH_CHECKLIST.md)
- [`docs/OASIS_STATUS_REPORT.md`](docs/OASIS_STATUS_REPORT.md)
- [`docs/OASIS_AUTOMATION_READY.md`](docs/OASIS_AUTOMATION_READY.md)
- [`docs/PLATFORM_IMPLEMENTATION_COMPLETE.md`](docs/PLATFORM_IMPLEMENTATION_COMPLETE.md)

### Analysis & Intelligence

- [`COMPREHENSIVE_ORGANIZATIONAL_ANALYSIS.md`](COMPREHENSIVE_ORGANIZATIONAL_ANALYSIS.md)
- [`DEEP_ORGANIZATIONAL_INSIGHTS.md`](DEEP_ORGANIZATIONAL_INSIGHTS.md)
- [`RCM_INTEGRATION_ENHANCEMENT.md`](RCM_INTEGRATION_ENHANCEMENT.md)

---

##  Configuration

### Environment Variables (`.env`)

```ini
# NPHIES
NPHIES_HOSPITAL_ID=10000000000988
NPHIES_CHI_ID=1048
NPHIES_LICENSE=7000911508
NPHIES_CERT_PATH=./certificates/nphies_production.pem
NPHIES_KEY_PATH=./certificates/nphies_production_key.pem
NPHIES_CERT_PASSWORD=change-me

# GIVC
GIVC_ULTRATHINK_ENABLED=true
GIVC_API_KEY=change-me

# OASES  unified U2415 credentials for all branches
OASES_RIYADH_USERNAME=U2415
OASES_RIYADH_PASSWORD=U2415
OASES_MADINAH_USERNAME=U2415
OASES_MADINAH_PASSWORD=U2415
OASES_UNAIZAH_USERNAME=U2415
OASES_UNAIZAH_PASSWORD=U2415
OASES_KHAMIS_USERNAME=U2415
OASES_KHAMIS_PASSWORD=U2415
OASES_JIZAN_USERNAME=U2415
OASES_JIZAN_PASSWORD=U2415
OASES_ABHA_USERNAME=U2415
OASES_ABHA_PASSWORD=U2415

# Optional services
DATABASE_URL=postgresql://user:pass@localhost:5432/brainsait
REDIS_URL=redis://localhost:6379/0

# Application
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### Portal Configuration (`config/config.yaml`)

```yaml
nphies:
  base_url: "https://HSB.nphies.sa"
  auth_url: "https://sso.nphies.sa"
  realm: "sehaticoreprod"
  client_id: "community"
  endpoints:
    eligibility: "/eligibility/v1/check"
    prior_authorization: "/priorauth/v1/create"
    claims: "/claim/v1/submit"
    communication: "/communication/v1/send"
    poll: "/poll/v1/status"

givc:
  base_url: "https://4d31266d.givc-platform-static.pages.dev"
  ultrathink_enabled: true

hospital:
  nphies_id: "10000000000988"
  chi_id: "1048"
  license: "7000911508"
  ftp_host: "172.25.11.15"
```

---

##  Testing

### Backend

```powershell
python -m pytest tests/
python -m pytest tests/test_nphies_integration.py -v
python -m pytest --cov=app --cov-report=html
```

### Integration Diagnostics

```powershell
python -c "from app.connectors.nphies import NPHIESConnector; print('NPHIES OK')"
python -c "from app.services.givc import GIVCService; print('GIVC OK')"
python -c "from services.oasis_integration.service import OASISService; print('OASES OK')"
```

### Health Checks

```powershell
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/health/portal/nphies
curl http://localhost:8000/api/v1/health/portal/oases
curl http://localhost:8000/api/v1/health/branch/riyadh
```

---

##  Deployment

### Development Mode

```powershell
python main.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Containerized

```powershell
# Docker image
docker build -t brainsait-nphies-givc .
docker run -p 8000:8000 brainsait-nphies-givc

# Docker Compose
docker-compose up -d
```

### Cloud

```powershell
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

cd ..\k8s
kubectl apply -f .
```

### CI/CD

- GitHub Actions pipelines under `.github/workflows/`
- Use `git-update.bat` or `push-to-remote.bat` for standardized pushes

---

##  Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/xyz`
3. Make changes with tests: `python -m pytest`
4. Commit: `git commit -am "feat: add xyz"`
5. Push: `git push origin feature/xyz`
6. Open a pull request

### Standards

- Python: PEP 8, type hints, descriptive docstrings
- JavaScript/TypeScript: ESLint + Prettier
- Testing:  80% coverage for modified modules
- Documentation: Update README and integration guides for new features

---

##  License

Proprietary software for Al Hayat Hospital. Unauthorized distribution prohibited.

---

##  Support

- Technical Support  IT Department
- NPHIES Operations  NPHIES Support Team
- Security Incidents  Security Operations Center

Helpful links:

- [NPHIES Portal](https://portal.nphies.sa)
- [GIVC Platform](https://4d31266d.givc-platform-static.pages.dev/)
- [FHIR R4 Specification](https://hl7.org/fhir/R4/)

Health endpoints:

- `/api/v1/health/`
- `/api/v1/health/portal/{portal}`
- `/api/v1/health/branch/{branch}`

---

##  Roadmap

### Phase 1  Foundation 

- NPHIES v2.0 integration
- GIVC AI enablement
- OASES automation
- Monorepo baseline

### Phase 2  Enhancement 

- Advanced AI models
- Real-time analytics dashboards
- Mobile application support
- Multi-tenant architecture

### Phase 3  Scale 

- Cloud-native global deployment
- Fraud detection ML pipelines
- Blockchain-backed audit registry
- Partner API marketplace

---

**Built with  for Al Hayat Hospital**  *Unifying healthcare integration with AI-powered compliance.*
