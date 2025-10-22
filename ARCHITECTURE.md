# BrainSAIT Unified Healthcare System - Architecture

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BrainSAIT Unified Healthcare Platform                     │
│                     (Consolidated GIVC + SDK + UNIFIED SYSTEM)              │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
                              │ API Gateway (FastAPI)
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                          Core Services Layer                                │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │ Claims Mgmt     │  │ Eligibility     │  │ Provider Integ  │            │
│  │ (from GIVC)     │  │ & Coverage      │  │ (from SDK)      │            │
│  │                 │  │ (from GIVC)     │  │                 │            │
│  │ • Submission    │  │ • Verification  │  │ • NPHIES API    │            │
│  │ • Processing    │  │ • Pre-auth      │  │ • Insurance     │            │
│  │ • Fraud AI      │  │ • Coverage      │  │ • Network Mgmt  │            │
│  │ • Appeals       │  │ • Real-time     │  │ • FHIR R4       │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │ Analytics &     │  │ Compliance &    │  │ BrainSAIT       │            │
│  │ Reporting       │  │ Audit           │  │ AI Agents       │            │
│  │ (UNIFIED SYS)   │  │ (All Repos)     │  │ Integration     │            │
│  │                 │  │                 │  │                 │            │
│  │ • Dashboards    │  │ • HIPAA Logs    │  │ • MASTERLINC    │            │
│  │ • KPI Tracking  │  │ • NPHIES        │  │ • HEALTHCARELINC│            │
│  │ • Predictive    │  │ • FHIR Valid    │  │ • CLINICALLINC  │            │
│  │ • Metrics       │  │ • Audit Trail   │  │ • COMPLIANCELINC│            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
                              │ Secure Communication (TLS 1.2+)
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                        External Integrations                                │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │ NPHIES Portal   │  │ Insurance       │  │ Healthcare      │            │
│  │                 │  │ Providers       │  │ Providers       │            │
│  │ • Saudi Arabia  │  │                 │  │                 │            │
│  │ • FHIR R4       │  │ • Multiple      │  │ • Hospitals     │            │
│  │ • Certificate   │  │ • Real-time     │  │ • Clinics       │            │
│  │ • Messaging     │  │ • Batch         │  │ • EHR Systems   │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📁 Repository Structure (Post-Consolidation)

```
brainsait-unified-healthcare/
├── src/
│   ├── backend/          # FastAPI microservices
│   │   ├── api/
│   │   ├── services/     # NPHIES, Claims, Eligibility, Analytics
│   │   ├── models/       # FHIR R4 + MongoDB schemas
│   │   ├── middleware/   # HIPAA audit logging, auth, encryption
│   │   └── core/         # Config, logging, database
│   ├── frontend/         # React 19 + TypeScript unified UI
│   │   ├── components/
│   │   ├── pages/
│   │   ├── contexts/     # Claims, NPHIES, Theme
│   │   ├── services/     # API clients
│   │   └── styles/       # Tailwind + glass morphism
│   └── shared/           # SDK utilities, types, validators
│       ├── types/        # FHIR R4 types + NPHIES extensions
│       ├── utils/        # Healthcare utilities
│       └── validators/   # HIPAA, FHIR, NPHIES validation
├── packages/
│   ├── sdk/              # Reusable healthcare SDK
│   └── validators/       # Medical validators
├── infrastructure/
│   ├── docker/           # Docker Compose files
│   ├── kubernetes/       # K8s manifests
│   └── scripts/          # Deployment automation
├── docs/
│   ├── INTEGRATION.md    # Consolidation decisions
│   ├── CHANGELOG.md      # Changes tracking
│   ├── ARCHITECTURE.md   # THIS FILE
│   ├── API.md           # API endpoints
│   ├── DEPLOYMENT.md    # Deployment guides
│   └── COMPLIANCE.md    # HIPAA/NPHIES/FHIR
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── config/
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── kubernetes/
│   └── .env.sample
└── .github/workflows/    # CI/CD pipelines
```

## 🛠️ Tech Stack with Rationale

### Backend
- **FastAPI** - Unified Python framework (from GIVC)
- **MongoDB** - NoSQL for flexible healthcare documents
- **Redis** - Caching for eligibility checks (sub-2s response)
- **Pydantic** - Type-safe data validation

### Frontend
- **React 19** - Latest with concurrent rendering (from UNIFIED SYSTEM)
- **TypeScript** - Type safety across UI
- **Tailwind CSS 4** - Utility-first styling (from SDK)
- **Shadcn/UI** - Accessible component library
- **react-i18next** - Bilingual support (Arabic RTL + English LTR)
- **React Query** - Server state management with caching

### Healthcare Integrations
- **FHIR R4** - HL7 standard for healthcare data (GIVC + SDK)
- **NPHIES** - Saudi Arabia insurance platform
- **AI Agents** - BrainSAIT orchestration (MASTERLINC, HEALTHCARELINC)

### DevOps & Infrastructure
- **Docker Compose** - Local development (FastAPI + React + MongoDB)
- **Kubernetes** - Production deployment (Deployments, Services, Ingress)
- **GitHub Actions** - CI/CD (build, test, security scan, deploy)
- **Nginx** - Reverse proxy + load balancing

## 🎯 Domain-Driven Design (DDD) Architecture

### Core Domains

#### 1. Claims Management (from GIVC)
- Claim submission, processing, denial tracking
- Fraud detection with AI
- Appeal management

#### 2. Eligibility & Coverage (from GIVC)
- Real-time member eligibility verification
- Coverage verification
- Pre-authorization management

#### 3. Provider Integration (from SDK)
- NPHIES connectivity
- Insurance provider APIs
- Network management

#### 4. Analytics & Reporting (from UNIFIED SYSTEM)
- Dashboard metrics
- KPI tracking (FPCCR, DRR, etc.)
- Predictive analytics

#### 5. Compliance & Audit (All repos)
- HIPAA logging
- NPHIES compliance
- FHIR validation

## 📝 Naming Conventions

### Code (Python - snake_case)
```python
# Services
eligibility_service.py
claims_service.py
nphies_integration.py

# Models
patient_model.py
claim_bundle_builder.py

# Utilities
healthcare_validators.py
audit_logger.py
```

### Code (TypeScript - camelCase)
```typescript
// Components
ClaimsPanel.tsx
EligibilityVerifier.tsx

// Services
claimsApiClient.ts
nphiesService.ts

// Types
FHIRPatient.ts
NPHIESClaim.ts
```

### Configuration (kebab-case)
```
brainsait.config.json
docker-compose.yml
kubernetes-deployment.yaml
```

## 🔄 Data Flow & Workflows

### Claim Submission Flow
```
Patient → Healthcare Provider → GIVC Platform
  ↓
1. AI Fraud Detection (GIVC)
2. FHIR R4 Validation (SDK)
3. NPHIES Message Building (SDK)
  ↓
NPHIES Platform → Insurance Company
  ↓
Response → Analytics → Provider Dashboard
```

### Eligibility Verification Flow
```
Provider Request → GIVC API
  ↓
1. Member ID Lookup (MongoDB)
2. Coverage Check (Cached in Redis)
3. NPHIES Real-time Query (if needed)
  ↓
Response (<2 seconds)
```

## 🛡️ Compliance Modules (HIPAA, NPHIES, FHIR)

### HIPAA Level 3 Audit Logging
- All PHI access logged with user ID, timestamp, action
- Immutable audit trail (append-only)
- 7-year retention policy
- Automated monthly compliance reports

### NPHIES Integration
- Certificate-based TLS 1.2+ authentication
- FHIR Bundle message signing
- Saudi-specific terminology (ICD-10-SA, CPT-SA)
- Arabic clinical names support

### FHIR R4 Validation
- Strict resource validation (Patient, Claim, Coverage, etc.)
- Extension validation (NPHIES-specific extensions)
- Reference integrity checks
- Coding system validation (SNOMED CT, ICD-10, CPT)

## 🔐 Security Architecture

### Data Protection
- **At Rest**: AES-256 encryption for PHI in MongoDB
- **In Transit**: TLS 1.2+ with certificate pinning
- **Access**: Role-based permissions (Admin, Provider, Patient, Auditor)

### Authentication & Authorization
- JWT tokens with 1-hour expiry
- Multi-factor authentication (optional)
- OAuth2 for third-party integrations
- API key rotation every 90 days

### Audit & Monitoring
- Centralized logging (ELK stack or CloudWatch)
- Real-time security alerts
- Monthly compliance audits
- Breach notification workflow

## ⚡ Performance Optimization

### Caching Strategy
- Redis for eligibility checks (TTL: 24 hours)
- Browser caching for static assets (1 year)
- API response caching (30-60 seconds)

### Database Optimization
- MongoDB indexes on frequently queried fields
- Partitioning by claim date range
- Query optimization with aggregation pipelines

### Frontend Performance
- Code splitting by route (React.lazy)
- Image optimization (WebP + compression)
- Lazy loading for below-the-fold content
- 60fps animations with GPU acceleration

## 🚀 Deployment Architecture

### Development (Docker Compose)
- Single docker-compose.yml file
- FastAPI on port 8000
- React dev server on port 5173
- MongoDB on port 27017
- Redis on port 6379

### Staging (Kubernetes)
- 2 replicas for high availability
- Service mesh (Istio optional)
- Persistent volumes for MongoDB
- Ingress with TLS termination

### Production (Kubernetes + Cloudflare)
- 3+ replicas with auto-scaling
- Multi-region deployment (optional)
- Disaster recovery (backup/restore)
- CDN for static assets

## 🌐 Bilingual & RTL Support

### UI Components
- All text in `BilingualText` type: `{ ar: string, en: string }`
- Automatic LTR/RTL layout switching
- Arabic fonts (IBM Plex Sans Arabic)
- Numeric formatting (Western/Eastern Arabic digits)

### API Responses
- Support `Accept-Language` header
- Error messages in both languages
- Clinical terminology translated

## 🤖 Integration Points with BrainSAIT Agents

### MASTERLINC - Orchestration
- Coordinates multi-step workflows
- Manages claim lifecycle

### HEALTHCARELINC - Workflows
- Pre-authorization workflows
- Claims processing workflows
- Denial appeals workflows

### CLINICALLINC - Decision Support
- Medical necessity validation
- Coding accuracy checking
- Fraud detection scoring

### COMPLIANCELINC - Compliance
- HIPAA audit trail generation
- NPHIES compliance validation
- FHIR resource validation

## 🔧 Extensibility & Future Growth

### Plugin Architecture
- Custom insurance provider adapters
- Third-party EHR integrations
- Machine learning model plugins
- Custom reporting engines

### API Versioning
- v1, v2, v3 endpoints (backward compatible)
- Deprecation notices 12 months in advance
- Gradual feature rollout with feature flags

## ✅ Success Criteria

✅ Clear architectural vision for consolidated platform  
✅ DDD structure aligns GIVC + SDK + UNIFIED SYSTEM  
✅ Compliance (HIPAA, NPHIES, FHIR) built-in  
✅ Performance targets (<2.5s page load, sub-2s eligibility checks)  
✅ Bilingual readiness (English + Arabic)  
✅ Deployment-ready (Docker + K8s)  
✅ Extensible for future BrainSAIT agent integrations

---

**This comprehensive architecture enables seamless integration of the consolidated BrainSAIT unified healthcare platform!**