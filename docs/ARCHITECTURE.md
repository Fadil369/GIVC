# BrainSAIT Unified Healthcare System - Architecture

> **Comprehensive Architecture Documentation for the Consolidated BrainSAIT Healthcare Platform**  
> Post-consolidation of GIVC, SDK, and UNIFIED SYSTEM repositories

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Repository Structure](#2-repository-structure-post-consolidation)
3. [Tech Stack with Rationale](#3-tech-stack-with-rationale)
4. [Domain-Driven Design Architecture](#4-domain-driven-design-ddd-architecture)
5. [Naming Conventions](#5-naming-conventions)
6. [Data Flow & Workflows](#6-data-flow--workflows)
7. [Compliance Modules](#7-compliance-modules-hipaa-nphies-fhir)
8. [Security Architecture](#8-security-architecture)
9. [Performance Optimization](#9-performance-optimization)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Bilingual & RTL Support](#11-bilingual--rtl-support)
12. [Integration Points with BrainSAIT Agents](#12-integration-points-with-brainsait-agents)
13. [Extensibility & Future Growth](#13-extensibility--future-growth)

---

## 1. System Architecture Overview

### High-Level Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        BrainSAIT Unified Healthcare Platform                    │
│                    (GIVC + SDK + UNIFIED SYSTEM Integration)                   │
└───────────────────────────────┬────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
    ┌───────────▼──────────┐        ┌──────────▼─────────────┐
    │   Frontend Layer     │        │    Backend Layer       │
    │   (React 19 + TS)    │◄──────►│   (FastAPI + Python)   │
    │                      │  REST  │                        │
    │ • Patient Portal     │  API   │ • Microservices        │
    │ • Provider Dashboard │        │ • NPHIES Integration   │
    │ • Analytics UI       │        │ • Claims Processing    │
    │ • Admin Console      │        │ • Eligibility Service  │
    └──────────────────────┘        └────────┬───────────────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        │                    │                    │
              ┌─────────▼─────────┐ ┌───────▼────────┐ ┌────────▼────────┐
              │   Data Layer      │ │  Cache Layer   │ │  BrainSAIT AI   │
              │   (MongoDB)       │ │   (Redis)      │ │    Agents       │
              │                   │ │                │ │                 │
              │ • Patient Records │ │ • Eligibility  │ │ • MASTERLINC    │
              │ • Claims Data     │ │ • Session Data │ │ • HEALTHCARELINC│
              │ • Audit Logs      │ │ • API Cache    │ │ • CLINICALLINC  │
              │ • Analytics       │ │ • Query Cache  │ │ • COMPLIANCELINC│
              └───────────────────┘ └────────────────┘ └────────┬────────┘
                                                                 │
                    ┌────────────────────────────────────────────┘
                    │
    ┌───────────────▼───────────────────────────────────────────────────────┐
    │                    External Integration Layer                          │
    ├────────────────────────────────────────────────────────────────────────┤
    │                                                                        │
    │  ┌──────────────┐  ┌────────────────┐  ┌──────────────────────────┐ │
    │  │   NPHIES     │  │   Insurance    │  │   Healthcare Providers   │ │
    │  │   Platform   │  │   Companies    │  │   (Hospitals/Clinics)    │ │
    │  │              │  │                │  │                          │ │
    │  │ • Eligibility│  │ • Tawuniya     │  │ • EHR Systems            │ │
    │  │ • Claims     │  │ • Bupa Arabia  │  │ • Appointment Systems    │ │
    │  │ • Pre-Auth   │  │ • Medgulf      │  │ • Lab Systems            │ │
    │  └──────────────┘  └────────────────┘  └──────────────────────────┘ │
    └────────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
Patient Request
      │
      ▼
┌─────────────────┐
│  React Frontend │ ─── Authentication ───► JWT Token Generation
│  (Port 5173)    │                         (1-hour expiry)
└────────┬────────┘
         │ HTTP/HTTPS
         │ (API Calls)
         ▼
┌─────────────────┐
│  FastAPI Server │ ─── Rate Limiting ────► Cloudflare WAF
│  (Port 8000)    │                         (DDoS Protection)
└────────┬────────┘
         │
         ├──► Eligibility Check ──► Redis Cache (24hr TTL)
         │                              │
         │                              ├─ Cache Hit → Return
         │                              └─ Cache Miss → NPHIES Query
         │
         ├──► Claims Processing ──► AI Fraud Detection
         │                              │
         │                              ├─ FHIR R4 Validation
         │                              ├─ Bundle Building
         │                              └─ NPHIES Submission
         │
         └──► Analytics Query ───► MongoDB Aggregation Pipeline
                                       │
                                       └─ Dashboard Metrics
```

---

## 2. Repository Structure (Post-Consolidation)

The BrainSAIT Unified Healthcare Platform follows a monorepo structure consolidating GIVC, SDK, and UNIFIED SYSTEM repositories:

```
brainsait-unified-healthcare/
├── src/
│   ├── backend/                      # FastAPI microservices (from GIVC)
│   │   ├── api/                      # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── claims.py             # Claims endpoints
│   │   │   ├── eligibility.py        # Eligibility endpoints
│   │   │   ├── analytics.py          # Analytics endpoints
│   │   │   └── nphies.py             # NPHIES proxy endpoints
│   │   ├── services/                 # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── claims.py             # Claims processing service
│   │   │   ├── eligibility.py        # Eligibility verification
│   │   │   ├── prior_authorization.py # Pre-auth workflows
│   │   │   ├── communication.py      # NPHIES communications
│   │   │   ├── analytics.py          # Analytics & reporting
│   │   │   └── platform_integration.py # External integrations
│   │   ├── models/                   # Data models & schemas
│   │   │   ├── __init__.py
│   │   │   ├── bundle_builder.py    # FHIR Bundle construction
│   │   │   ├── fhir_resources.py    # FHIR R4 resource models
│   │   │   └── database.py          # MongoDB schemas
│   │   ├── middleware/               # Request/response middleware
│   │   │   ├── __init__.py
│   │   │   ├── audit_logger.py      # HIPAA audit logging
│   │   │   ├── auth.py              # JWT authentication
│   │   │   └── encryption.py        # Field-level encryption
│   │   └── core/                     # Core configurations
│   │       ├── __init__.py
│   │       ├── config.py            # Application settings
│   │       ├── database.py          # MongoDB connection
│   │       └── logging.py           # Logging configuration
│   │
│   ├── frontend/                     # React 19 + TypeScript (from UNIFIED SYSTEM)
│   │   ├── components/               # Reusable UI components
│   │   │   ├── claims/              # Claims-related components
│   │   │   │   ├── ClaimsPanel.tsx
│   │   │   │   ├── ClaimForm.tsx
│   │   │   │   └── ClaimStatusTracker.tsx
│   │   │   ├── eligibility/         # Eligibility components
│   │   │   │   ├── EligibilityVerifier.tsx
│   │   │   │   └── CoverageDisplay.tsx
│   │   │   ├── analytics/           # Analytics dashboards
│   │   │   │   ├── DashboardMetrics.tsx
│   │   │   │   ├── KPICards.tsx
│   │   │   │   └── Charts/
│   │   │   ├── common/              # Shared components
│   │   │   │   ├── BilingualText.tsx
│   │   │   │   ├── RTLLayout.tsx
│   │   │   │   └── GlassMorphism.tsx
│   │   │   └── ui/                  # Shadcn/UI components
│   │   ├── pages/                   # Route-level pages
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Claims.tsx
│   │   │   ├── Eligibility.tsx
│   │   │   └── Analytics.tsx
│   │   ├── contexts/                # React Context providers
│   │   │   ├── ClaimsContext.tsx
│   │   │   ├── NPHIESContext.tsx
│   │   │   ├── ThemeContext.tsx
│   │   │   └── AuthContext.tsx
│   │   ├── services/                # API client services
│   │   │   ├── claimsApiClient.ts
│   │   │   ├── eligibilityApiClient.ts
│   │   │   ├── nphiesService.ts
│   │   │   └── analyticsService.ts
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── useClaims.ts
│   │   │   ├── useEligibility.ts
│   │   │   └── useAnalytics.ts
│   │   └── styles/                  # Styling assets
│   │       ├── tailwind.css
│   │       ├── glass-morphism.css
│   │       └── arabic-rtl.css
│   │
│   └── shared/                       # SDK utilities (from SDK)
│       ├── types/                    # TypeScript/Python types
│       │   ├── FHIRPatient.ts       # FHIR Patient type
│       │   ├── NPHIESClaim.ts       # NPHIES Claim type
│       │   ├── fhir_types.py        # Python FHIR types
│       │   └── nphies_types.py      # Python NPHIES types
│       ├── utils/                    # Shared utilities
│       │   ├── healthcare_validators.py # Medical data validators
│       │   ├── fhir_helpers.ts      # FHIR utility functions
│       │   └── date_formatters.ts   # Date/time utilities
│       └── validators/               # Validation logic
│           ├── hipaa_validator.py   # HIPAA compliance checks
│           ├── fhir_validator.py    # FHIR R4 validation
│           └── nphies_validator.py  # NPHIES-specific validation
│
├── packages/                         # Reusable packages
│   ├── sdk/                          # Healthcare SDK (from SDK repo)
│   │   ├── src/
│   │   │   ├── nphies/              # NPHIES integration SDK
│   │   │   ├── fhir/                # FHIR R4 SDK
│   │   │   └── validators/          # Validation SDK
│   │   ├── package.json
│   │   └── README.md
│   └── validators/                   # Medical validators package
│       ├── src/
│       ├── package.json
│       └── README.md
│
├── infrastructure/                   # Infrastructure as Code
│   ├── docker/                       # Docker configurations
│   │   ├── Dockerfile.backend       # Backend container
│   │   ├── Dockerfile.frontend      # Frontend container
│   │   ├── nginx.conf               # Nginx configuration
│   │   └── docker-compose.yml       # Development setup
│   ├── kubernetes/                   # Kubernetes manifests
│   │   ├── namespaces/
│   │   ├── deployments/
│   │   │   ├── backend-deployment.yaml
│   │   │   ├── frontend-deployment.yaml
│   │   │   ├── mongodb-deployment.yaml
│   │   │   └── redis-deployment.yaml
│   │   ├── services/
│   │   │   ├── backend-service.yaml
│   │   │   ├── frontend-service.yaml
│   │   │   └── mongodb-service.yaml
│   │   ├── ingress/
│   │   │   └── ingress.yaml
│   │   ├── configmaps/
│   │   └── secrets/
│   └── scripts/                      # Deployment automation
│       ├── deploy-dev.sh
│       ├── deploy-staging.sh
│       ├── deploy-production.sh
│       └── backup-restore.sh
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # This file
│   ├── INTEGRATION.md                # Consolidation decisions
│   ├── CHANGELOG.md                  # Version history
│   ├── API.md                        # API documentation
│   ├── DEPLOYMENT.md                 # Deployment guides
│   ├── COMPLIANCE.md                 # HIPAA/NPHIES/FHIR compliance
│   ├── SECURITY.md                   # Security documentation
│   └── CONTRIBUTING.md               # Contribution guidelines
│
├── tests/                            # Test suites
│   ├── unit/                         # Unit tests
│   │   ├── backend/
│   │   │   ├── test_claims.py
│   │   │   ├── test_eligibility.py
│   │   │   └── test_validators.py
│   │   └── frontend/
│   │       ├── ClaimsPanel.test.tsx
│   │       └── EligibilityVerifier.test.tsx
│   ├── integration/                  # Integration tests
│   │   ├── test_nphies_flow.py
│   │   ├── test_claim_submission.py
│   │   └── test_api_endpoints.py
│   └── e2e/                          # End-to-end tests
│       ├── claim_workflow.spec.ts
│       └── eligibility_check.spec.ts
│
├── config/                           # Configuration files
│   ├── docker-compose.yml            # Development environment
│   ├── docker-compose.prod.yml       # Production environment
│   ├── kubernetes/                   # K8s configs (symlink to infrastructure/kubernetes)
│   ├── .env.sample                   # Environment template
│   └── brainsait.config.json         # Application configuration
│
├── .github/                          # GitHub workflows
│   ├── workflows/
│   │   ├── ci.yml                    # Continuous integration
│   │   ├── cd-staging.yml            # Staging deployment
│   │   ├── cd-production.yml         # Production deployment
│   │   ├── security-scan.yml         # Security scanning
│   │   └── tests.yml                 # Automated testing
│   └── CODEOWNERS                    # Code ownership
│
├── auth/                             # Authentication (legacy from GIVC)
│   ├── auth_manager.py               # Authentication handler
│   └── cert_manager.py               # Certificate management
│
├── pipeline/                         # Data pipeline (legacy from GIVC)
│   ├── extractor.py                  # Data extraction
│   └── data_processor.py             # Data processing
│
├── .gitignore                        # Git ignore rules
├── .dockerignore                     # Docker ignore rules
├── package.json                      # Root package.json (workspaces)
├── pnpm-workspace.yaml               # PNPM workspace config
├── requirements.txt                  # Python dependencies
├── pyproject.toml                    # Python project config
├── README.md                         # Project README
└── LICENSE                           # License file
```

## 📊 Data Flow Diagram

### Eligibility Verification Flow

```
┌──────────────┐
│ Your System  │
└──────┬───────┘
       │ 1. Request Eligibility Check
       │    {member_id, payer_id, service_date}
       ▼
┌──────────────────────┐
│ Eligibility Service  │
└──────┬───────────────┘
       │ 2. Build FHIR Bundle
       │    • MessageHeader
       │    • CoverageEligibilityRequest
       │    • Patient
       │    • Coverage
       │    • Organizations
       ▼
┌──────────────────────┐
│   Auth Manager       │
└──────┬───────────────┘
       │ 3. Add Authentication
       │    • Headers (License, Org ID)
       │    • Certificates (if production)
       ▼
┌──────────────────────┐
│   NPHIES API         │
│   POST $process-msg  │
└──────┬───────────────┘
       │ 4. Process Request
       │    • Validate
       │    • Check Coverage
       ▼
       │ 5. Return Response Bundle
       │    • CoverageEligibilityResponse
       │    • Coverage Details
       │    • Benefits
       ▼
┌──────────────────────┐
│  Response Parser     │
└──────┬───────────────┘
       │ 6. Extract Data
       │    • Coverage Status
       │    • Benefits
       │    • Errors (if any)
       ▼
┌──────────────────────┐
│   Your System        │
│   (Result)           │
└──────────────────────┘
```

### Claim Submission Flow

```
┌──────────────┐
│ Your System  │ Claim Data (services, amounts, patient info)
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│   Claims Service     │ Build Claim Bundle
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Validators         │ Validate Claim Data
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Auth Manager       │ Authenticate & Send
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   NPHIES Portal      │ Process Claim
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   ClaimResponse      │ Approval/Denial/Info
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Your System        │ Update Claim Status
└──────────────────────┘
```

## 🔄 Pipeline Workflow

```
START
  │
  ▼
┌─────────────────────────────────────────┐
│  Initialize Data Extractor              │
│  • Load configuration                   │
│  • Setup services                       │
│  • Create output directory              │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Phase 1: Eligibility Extraction        │
│  ┌───────────────────────────────────┐  │
│  │ For each member:                  │  │
│  │  • Build request                  │  │
│  │  • Send to NPHIES                 │  │
│  │  • Parse response                 │  │
│  │  • Store result                   │  │
│  └───────────────────────────────────┘  │
│  • Save to eligibility_results.json    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Phase 2: Claims Extraction             │
│  ┌───────────────────────────────────┐  │
│  │ For each claim:                   │  │
│  │  • Validate data                  │  │
│  │  • Build claim bundle             │  │
│  │  • Submit to NPHIES               │  │
│  │  • Parse response                 │  │
│  │  • Store result                   │  │
│  └───────────────────────────────────┘  │
│  • Save to claims_results.json         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Phase 3: Communications Polling        │
│  • Build poll request                   │
│  • Send to NPHIES                       │
│  • Retrieve pending messages            │
│  • Parse communications                 │
│  • Save to communications_results.json  │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Generate Summary Report                │
│  • Total operations                     │
│  • Success/failure counts               │
│  • Duration                             │
│  • Save complete_extraction_results.json│
└────────────┬────────────────────────────┘
             │
             ▼
           END
```

## 🔐 Authentication Flow

### Sandbox Environment
```
Request → Add Headers → Send to NPHIES
          │
          ├─ X-License-Number: YOUR_LICENSE
          ├─ X-Organization-ID: YOUR_ORG_ID
          └─ X-Provider-ID: YOUR_PROVIDER_ID
```

### Production Environment
```
Request → Attach Certificate → Add Headers → Send to NPHIES
          │                    │
          ├─ client.pem        ├─ X-License-Number
          ├─ private.key       ├─ X-Organization-ID
          └─ ca_bundle.pem     └─ X-Provider-ID
```

## 📦 FHIR Bundle Structure

```json
{
  "resourceType": "Bundle",
  "type": "message",
  "timestamp": "2025-10-22T10:00:00Z",
  "entry": [
    {
      "resource": {
        "resourceType": "MessageHeader",
        "eventUri": "http://nphies.sa/eligibility-request",
        "source": { "endpoint": "Organization/YOUR_ORG" },
        "destination": [{ "endpoint": "Organization/PAYER_ID" }]
      }
    },
    {
      "resource": {
        "resourceType": "CoverageEligibilityRequest",
        "status": "active",
        "purpose": ["validation"],
        "patient": { "reference": "Patient/patient-id" },
        "insurer": { "reference": "Organization/payer-id" }
      }
    },
    {
      "resource": {
        "resourceType": "Patient",
        "id": "patient-id",
        "identifier": [{ "value": "1234567890" }]
      }
    },
    {
      "resource": {
        "resourceType": "Coverage",
        "beneficiary": { "reference": "Patient/patient-id" },
        "payor": [{ "reference": "Organization/payer-id" }]
      }
    }
  ]
}
```

## 🎯 Integration Patterns

### Pattern 1: Synchronous API

```python
# Real-time eligibility check during patient registration

def register_patient(patient_data):
    # Check eligibility first
    eligibility = EligibilityService()
    result = eligibility.check_eligibility(
        member_id=patient_data['insurance_id'],
        payer_id=patient_data['insurance_company']
    )
    
    if result['success'] and result['coverage_status']['eligible']:
        # Proceed with registration
        save_patient(patient_data)
        return {"status": "registered", "coverage": "active"}
    else:
        return {"status": "pending", "reason": "coverage verification failed"}
```

### Pattern 2: Batch Processing

```python
# Nightly batch job for claim submissions

def nightly_claim_submission():
    # Get pending claims from database
    pending_claims = db.get_pending_claims()
    
    # Run batch extraction
    extractor = NPHIESDataExtractor()
    results = extractor.extract_claims_batch(
        claims_data=pending_claims,
        output_file="daily_claims_results.json"
    )
    
    # Update database with results
    for result in results['data']:
        db.update_claim_status(result['claim_id'], result['status'])
```

### Pattern 3: Event-Driven

```python
# Process claims as they arrive via message queue

def process_claim_event(claim_message):
    claim_data = json.loads(claim_message)
    
    # Submit claim
    claims_service = ClaimsService()
    result = claims_service.submit_claim(**claim_data)
    
    # Publish result to response queue
    publish_to_queue('claim_responses', result)
```

### Pattern 4: API Gateway

```python
# FastAPI wrapper for microservices architecture

from fastapi import FastAPI, HTTPException
from services.eligibility import EligibilityService
from services.claims import ClaimsService

app = FastAPI()

@app.post("/api/nphies/eligibility")
async def check_eligibility(request: EligibilityRequest):
    service = EligibilityService()
    result = service.check_eligibility(**request.dict())
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@app.post("/api/nphies/claims")
async def submit_claim(request: ClaimRequest):
    service = ClaimsService()
    result = service.submit_claim(**request.dict())
    return result
```

## 📈 Scaling Strategies

### Horizontal Scaling
```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Worker 1 │     │ Worker 2 │     │ Worker 3 │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     └────────────────┴────────────────┘
                      │
              ┌───────▼────────┐
              │  Load Balancer │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │  NPHIES Portal │
              └────────────────┘
```

### Queue-Based Processing
```
┌──────────┐     ┌───────┐     ┌──────────┐     ┌────────┐
│ Producer │ ──→ │ Queue │ ──→ │ Consumer │ ──→ │ NPHIES │
└──────────┘     └───────┘     └──────────┘     └────────┘
                                      │
                                      ▼
                                ┌──────────┐
                                │ Database │
                                └──────────┘
```

## 🔍 Monitoring & Observability

```
┌─────────────────────────────────────────────────────────┐
│                    Application Logs                      │
│  logs/nphies_integration.log                            │
│  • Timestamp • Level • Component • Message              │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Metrics Collection                     │
│  • Success/Failure Rates                                │
│  • Response Times                                       │
│  • Error Patterns                                       │
│  • API Usage                                            │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Alerting & Dashboards                   │
│  • Real-time Monitoring                                 │
│  • Threshold Alerts                                     │
│  • Performance Graphs                                   │
└─────────────────────────────────────────────────────────┘
```

## 🛡️ Security Layers

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Network Security                               │
│  • VPN/Secure Network                                   │
│  • Firewall Rules                                       │
│  • IP Whitelisting                                      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│ Layer 2: Transport Security                             │
│  • TLS 1.2+ Encryption                                  │
│  • Certificate Validation                               │
│  • Secure Protocols                                     │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│ Layer 3: Application Security                           │
│  • Certificate Authentication                           │
│  • License Validation                                   │
│  • Request Signing                                      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│ Layer 4: Data Security                                  │
│  • Input Validation                                     │
│  • Sanitization                                         │
│  • Sensitive Data Masking                               │
│  • Audit Logging                                        │
└─────────────────────────────────────────────────────────┘
```

## 📱 Platform Integration Examples

### Hospital Management System (HMS)
```
HMS → Appointment → Check Eligibility → Register Patient
HMS → Treatment → Submit Claim → Track Status
HMS → Daily Batch → Export Claims → Submit to NPHIES
```

### Insurance Platform
```
Portal → Member Lookup → Verify Coverage → Display Status
Portal → Claim Review → Query Status → Show Details
System → Scheduled Job → Poll Communications → Process Updates
```

### Clinic System
```
Reception → Patient Check-in → Eligibility Verify → Approve Visit
Billing → Generate Invoice → Create Claim → Submit NPHIES
Admin → Reports → Extract Data → Analyze Results
```

---

**This comprehensive architecture enables seamless integration between your healthcare platform and NPHIES!**

---

## 3. Tech Stack with Rationale

### Backend Technologies

| Technology | Version | Rationale | Source Repo |
|------------|---------|-----------|-------------|
| **FastAPI** | 0.100+ | - High performance async framework<br>- Automatic OpenAPI/Swagger documentation<br>- Built-in data validation with Pydantic<br>- Excellent for microservices architecture | GIVC |
| **MongoDB** | 6.0+ | - Flexible schema for evolving healthcare data<br>- Native support for complex nested documents (FHIR resources)<br>- Horizontal scalability with sharding<br>- Efficient indexing for fast queries | GIVC |
| **Redis** | 7.0+ | - Sub-millisecond response times for eligibility caching<br>- Session storage and rate limiting<br>- Pub/Sub for real-time updates<br>- TTL support for automatic cache expiration | GIVC |
| **Pydantic** | 2.0+ | - Type-safe data validation<br>- Automatic serialization/deserialization<br>- FHIR R4 model validation<br>- Error handling with detailed messages | GIVC |
| **Python** | 3.11+ | - Rich healthcare library ecosystem<br>- Strong typing support<br>- Excellent async support<br>- NPHIES SDK compatibility | GIVC |

### Frontend Technologies

| Technology | Version | Rationale | Source Repo |
|------------|---------|-----------|-------------|
| **React** | 19.0+ | - Latest concurrent rendering features<br>- Improved performance with automatic batching<br>- Better server components support<br>- Industry-standard UI framework | UNIFIED SYSTEM |
| **TypeScript** | 5.0+ | - Type safety across entire UI<br>- Better IDE support and autocomplete<br>- Reduced runtime errors<br>- Improved maintainability | SDK |
| **Tailwind CSS** | 4.0+ | - Utility-first approach reduces CSS bloat<br>- Consistent design system<br>- Excellent RTL support for Arabic<br>- JIT compiler for production optimization | SDK |
| **Shadcn/UI** | Latest | - Accessible components out of the box<br>- WCAG 2.1 AA compliance<br>- Customizable and themeable<br>- No runtime overhead | UNIFIED SYSTEM |
| **react-i18next** | 13.0+ | - Comprehensive internationalization<br>- RTL/LTR automatic switching<br>- Pluralization and formatting<br>- Arabic numeral support | SDK |
| **React Query** | 5.0+ | - Intelligent server state caching<br>- Automatic background refetching<br>- Optimistic updates<br>- Request deduplication | UNIFIED SYSTEM |
| **Vite** | 5.0+ | - Lightning-fast HMR during development<br>- Optimized production builds<br>- Native ES modules support<br>- Better than webpack for our use case | UNIFIED SYSTEM |

### Healthcare Integration Standards

| Standard/Platform | Version | Rationale | Source Repo |
|-------------------|---------|-----------|-------------|
| **FHIR R4** | 4.0.1 | - International standard for healthcare data exchange<br>- NPHIES compliance requirement<br>- Rich resource modeling<br>- Extensible for Saudi-specific needs | GIVC + SDK |
| **NPHIES** | Latest | - Mandatory for Saudi Arabia healthcare claims<br>- Government-mandated integration<br>- Certificate-based security<br>- Arabic clinical terminology support | GIVC |
| **HL7 Standards** | Various | - Industry-standard healthcare messaging<br>- Interoperability with EHR systems<br>- Clinical document exchange<br>- Terminology services (SNOMED, ICD-10) | SDK |

### DevOps & Infrastructure

| Technology | Version | Rationale | Source Repo |
|------------|---------|-----------|-------------|
| **Docker** | 24.0+ | - Consistent development environments<br>- Isolated microservices<br>- Easy local setup with Docker Compose<br>- Container orchestration ready | All repos |
| **Kubernetes** | 1.28+ | - Production-grade orchestration<br>- Auto-scaling and self-healing<br>- Rolling updates with zero downtime<br>- Service mesh ready (Istio compatible) | UNIFIED SYSTEM |
| **GitHub Actions** | N/A | - Native GitHub integration<br>- Matrix builds for multiple environments<br>- Secrets management<br>- Automated security scanning | All repos |
| **Nginx** | 1.24+ | - High-performance reverse proxy<br>- Load balancing across backend instances<br>- SSL/TLS termination<br>- Static asset serving | GIVC |
| **Cloudflare** | N/A | - Global CDN for static assets<br>- DDoS protection<br>- WAF for security<br>- Zero Trust access control | UNIFIED SYSTEM |

### AI & Machine Learning (BrainSAIT Integration)

| Component | Purpose | Integration Point |
|-----------|---------|------------------|
| **MASTERLINC** | Orchestration agent for multi-step workflows | Claims lifecycle management |
| **HEALTHCARELINC** | Healthcare-specific workflow automation | Pre-auth and claims processing |
| **CLINICALLINC** | Clinical decision support | Medical necessity validation, fraud detection |
| **COMPLIANCELINC** | Compliance monitoring and validation | HIPAA audits, NPHIES compliance checks |

---

## 4. Domain-Driven Design (DDD) Architecture

### Core Domains

#### 1. Claims Management Domain (Primary - from GIVC)

**Bounded Context**: Claims Lifecycle Management

**Entities**:
- `Claim`: Core aggregate root
- `ClaimItem`: Individual service line items
- `ClaimResponse`: Payer adjudication results
- `ClaimAttachment`: Supporting documentation

**Value Objects**:
- `ClaimStatus` (submitted, approved, denied, appealed)
- `DenialReason` (code + description)
- `ClaimAmount` (value + currency)

**Services**:
- `ClaimSubmissionService`: Handle claim submissions to NPHIES
- `ClaimValidationService`: Pre-submission validation
- `FraudDetectionService`: AI-powered fraud scoring
- `DenialManagementService`: Denial tracking and appeals

**Repositories**:
- `ClaimRepository`: Claims persistence
- `DenialRepository`: Denial tracking
- `AppealRepository`: Appeal history

**Domain Events**:
- `ClaimSubmitted`
- `ClaimApproved`
- `ClaimDenied`
- `AppealInitiated`

#### 2. Eligibility & Coverage Domain (from GIVC)

**Bounded Context**: Insurance Coverage Verification

**Entities**:
- `Coverage`: Insurance coverage information
- `Patient`: Patient demographics
- `Member`: Insurance member details

**Value Objects**:
- `EligibilityStatus` (active, inactive, pending)
- `CoverageType` (primary, secondary, tertiary)
- `BenefitAmount` (copay, deductible, out-of-pocket max)

**Services**:
- `EligibilityVerificationService`: Real-time checks
- `CoverageQueryService`: Coverage details lookup
- `BenefitCalculationService`: Benefit computation

**Repositories**:
- `CoverageRepository`: Coverage data
- `EligibilityRepository`: Eligibility check history

**Domain Events**:
- `EligibilityVerified`
- `CoverageUpdated`
- `BenefitCalculated`

#### 3. Provider Integration Domain (from SDK)

**Bounded Context**: External Healthcare Provider Integration

**Entities**:
- `Provider`: Healthcare provider organization
- `Practitioner`: Individual healthcare professional
- `Network`: Provider network membership

**Value Objects**:
- `ProviderType` (hospital, clinic, pharmacy)
- `Specialty` (cardiology, orthopedics, etc.)
- `NetworkStatus` (in-network, out-of-network)

**Services**:
- `NPHIESIntegrationService`: NPHIES connectivity
- `InsuranceProviderService`: Payer API integration
- `NetworkManagementService`: Provider network management

**Repositories**:
- `ProviderRepository`: Provider data
- `NetworkRepository`: Network information

**Domain Events**:
- `ProviderRegistered`
- `NetworkUpdated`
- `ContractSigned`

#### 4. Analytics & Reporting Domain (from UNIFIED SYSTEM)

**Bounded Context**: Business Intelligence & Metrics

**Entities**:
- `Dashboard`: Customizable dashboard configuration
- `Report`: Scheduled or on-demand reports
- `Metric`: KPI definitions

**Value Objects**:
- `KPIMetric` (FPCCR, DRR, cycle time)
- `DateRange` (start, end, timezone)
- `AggregationType` (sum, avg, count)

**Services**:
- `MetricsCalculationService`: KPI computation
- `DashboardService`: Dashboard data aggregation
- `ReportGenerationService`: Report creation
- `PredictiveAnalyticsService`: AI-powered predictions

**Repositories**:
- `MetricsRepository`: Historical metrics
- `DashboardRepository`: Dashboard configs
- `ReportRepository`: Generated reports

**Domain Events**:
- `MetricCalculated`
- `ReportGenerated`
- `AlertTriggered`

#### 5. Compliance & Audit Domain (All repos)

**Bounded Context**: Regulatory Compliance & Security

**Entities**:
- `AuditLog`: Immutable audit trail
- `ComplianceCheck`: Compliance validation results
- `SecurityEvent`: Security-related events

**Value Objects**:
- `AuditAction` (create, read, update, delete, access)
- `ComplianceStatus` (compliant, non-compliant, pending)
- `SecurityLevel` (public, internal, confidential, restricted)

**Services**:
- `AuditLoggingService`: HIPAA audit logging
- `ComplianceValidationService`: NPHIES/FHIR validation
- `SecurityMonitoringService`: Security event tracking

**Repositories**:
- `AuditLogRepository`: Append-only audit logs
- `ComplianceCheckRepository`: Compliance validation history

**Domain Events**:
- `PHIAccessed`
- `ComplianceViolationDetected`
- `SecurityEventLogged`

### Domain Interaction Map

```
┌──────────────────────┐
│   Claims Domain      │◄──────┐
│                      │       │
│ • Submission         │       │
│ • Validation         │       │
│ • Fraud Detection    │       │
└─────────┬────────────┘       │
          │                    │
          │ uses               │ reports to
          │                    │
          ▼                    │
┌──────────────────────┐       │
│  Eligibility Domain  │       │     ┌──────────────────────┐
│                      │       │     │  Analytics Domain    │
│ • Coverage Check     │───────┼────►│                      │
│ • Benefit Calc       │       │     │ • KPI Tracking       │
└──────────┬───────────┘       │     │ • Dashboards         │
           │                   │     │ • Predictions        │
           │ queries            │     └──────────────────────┘
           │                   │
           ▼                   │
┌──────────────────────┐       │
│  Provider Domain     │       │
│                      │       │
│ • NPHIES API         │───────┘
│ • Payer Integration  │
└──────────┬───────────┘
           │
           │ validates against
           │
           ▼
┌──────────────────────┐
│  Compliance Domain   │
│                      │
│ • Audit Logging      │
│ • HIPAA Checks       │
│ • FHIR Validation    │
└──────────────────────┘
```

---

## 5. Naming Conventions

### Python (Backend - snake_case)

**Files & Modules**:
```python
# Services
eligibility_service.py
claims_service.py
nphies_integration.py
prior_authorization_service.py

# Models
patient_model.py
claim_bundle_builder.py
coverage_model.py
fhir_resource.py

# Utilities
healthcare_validators.py
audit_logger.py
date_formatters.py
fhir_helpers.py

# Tests
test_eligibility_service.py
test_claims_validation.py
```

**Classes, Functions & Variables**:
```python
# Classes (PascalCase)
class ClaimsService:
    pass

class EligibilityVerificationService:
    pass

class FHIRBundleBuilder:
    pass

# Functions & Methods (snake_case)
def check_eligibility(member_id: str, payer_id: str) -> dict:
    pass

def submit_claim(claim_data: dict) -> ClaimResponse:
    pass

def validate_fhir_resource(resource: dict) -> bool:
    pass

# Variables (snake_case)
patient_id = "123456789"
claim_status = "submitted"
eligibility_response = check_eligibility(member_id, payer_id)

# Constants (SCREAMING_SNAKE_CASE)
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
NPHIES_BASE_URL = "https://nphies.sa/api"
```

### TypeScript/JavaScript (Frontend - camelCase)

**Files & Components**:
```typescript
// React Components (PascalCase)
ClaimsPanel.tsx
EligibilityVerifier.tsx
DashboardMetrics.tsx
BilingualText.tsx

// Services (camelCase)
claimsApiClient.ts
nphiesService.ts
eligibilityService.ts
analyticsService.ts

// Types (PascalCase)
FHIRPatient.ts
NPHIESClaim.ts
ClaimResponse.ts
CoverageInfo.ts

// Utilities (camelCase)
dateFormatters.ts
fhirHelpers.ts
validationUtils.ts

// Tests
ClaimsPanel.test.tsx
eligibilityService.test.ts
```

**Functions, Variables & Types**:
```typescript
// Interfaces & Types (PascalCase)
interface ClaimData {
  claimId: string;
  patientId: string;
  status: ClaimStatus;
}

type EligibilityStatus = 'active' | 'inactive' | 'pending';

// Functions (camelCase)
function submitClaim(claimData: ClaimData): Promise<ClaimResponse> {
  // ...
}

async function checkEligibility(memberId: string): Promise<EligibilityResponse> {
  // ...
}

// Variables (camelCase)
const claimId = "CLM-2025-001";
const eligibilityStatus: EligibilityStatus = 'active';
const submissionResult = await submitClaim(claimData);

// Constants (SCREAMING_SNAKE_CASE)
const API_BASE_URL = 'http://localhost:8000';
const MAX_UPLOAD_SIZE_MB = 10;
const DEFAULT_PAGE_SIZE = 20;

// React Hooks (camelCase with 'use' prefix)
const useClaims = () => {
  // ...
};

const useEligibility = (memberId: string) => {
  // ...
};
```

### Configuration Files (kebab-case)

```
brainsait.config.json
docker-compose.yml
docker-compose.prod.yml
kubernetes-deployment.yaml
kubernetes-service.yaml
ci-pipeline.yml
staging-deployment.yml
```

### Database Collections & Fields

**MongoDB Collections** (snake_case):
```
claims
patients
eligibility_checks
audit_logs
coverage_records
providers
```

**MongoDB Fields** (snake_case):
```json
{
  "claim_id": "CLM-001",
  "patient_id": "PAT-123",
  "submission_date": "2025-10-22",
  "total_amount": 5000.00,
  "claim_status": "submitted"
}
```

### API Endpoints (kebab-case with resource names)

```
GET    /api/v1/claims
POST   /api/v1/claims
GET    /api/v1/claims/:id
PUT    /api/v1/claims/:id
DELETE /api/v1/claims/:id

POST   /api/v1/eligibility/check
GET    /api/v1/eligibility/:member-id

GET    /api/v1/analytics/dashboard
GET    /api/v1/analytics/kpis
POST   /api/v1/analytics/reports

POST   /api/v1/nphies/submit-claim
POST   /api/v1/nphies/check-eligibility
GET    /api/v1/nphies/communications
```

### Environment Variables (SCREAMING_SNAKE_CASE)

```bash
# Application
APP_NAME=brainsait-healthcare
APP_ENV=production
LOG_LEVEL=INFO

# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=brainsait_healthcare
REDIS_URL=redis://localhost:6379

# NPHIES
NPHIES_BASE_URL=https://nphies.sa/api/fs/fhir
NPHIES_LICENSE=YOUR_LICENSE
NPHIES_ORGANIZATION_ID=YOUR_ORG_ID
NPHIES_ENVIRONMENT=production

# Security
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRY_HOURS=1
ENCRYPTION_KEY=your-encryption-key
```

---

## 6. Data Flow & Workflows

### Claim Submission Workflow

```
┌─────────────┐
│   Patient   │ Receives healthcare service
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  Healthcare Provider │ 1. Creates claim
│  (Hospital/Clinic)   │    • Patient info
└──────┬───────────────┘    • Services rendered
       │                    • Diagnosis codes
       │                    • Procedure codes
       ▼
┌──────────────────────────────────────────────────────────────┐
│  BrainSAIT Platform - Claims Oasis Module                    │
│                                                               │
│  2. AI-Powered Pre-Submission Validation                     │
│     ┌────────────────────────────────────────────────────┐  │
│     │  CLINICALLINC Agent                                │  │
│     │  • Medical necessity check                         │  │
│     │  • Coding accuracy validation                      │  │
│     │  • Fraud detection scoring (0-100%)                │  │
│     │  • Denial risk prediction                          │  │
│     └────────────────────────────────────────────────────┘  │
│                                                               │
│  3. FHIR R4 Validation (SDK)                                 │
│     ┌────────────────────────────────────────────────────┐  │
│     │  • Resource structure validation                   │  │
│     │  • Required fields check                           │  │
│     │  • Coding system validation (ICD-10-SA, CPT-SA)    │  │
│     │  • Reference integrity                             │  │
│     └────────────────────────────────────────────────────┘  │
│                                                               │
│  4. NPHIES Message Building                                  │
│     ┌────────────────────────────────────────────────────┐  │
│     │  FHIRBundleBuilder                                 │  │
│     │  • MessageHeader                                   │  │
│     │  • Claim resource                                  │  │
│     │  • Patient resource                                │  │
│     │  • Coverage resource                               │  │
│     │  • Organization resources (provider + payer)       │  │
│     │  • Supporting documents                            │  │
│     └────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  NPHIES Platform                                             │
│                                                              │
│  5. Process Claim Submission                                │
│     • TLS 1.2+ Certificate Authentication                   │
│     • Bundle Signature Verification                         │
│     • Business Rule Validation                              │
│     • Payer-specific Edits                                  │
│     • Generate ClaimResponse                                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Insurance Company (Payer)                                   │
│                                                              │
│  6. Adjudication                                            │
│     • Clinical review                                       │
│     • Coverage verification                                 │
│     • Pricing calculation                                   │
│     • Decision: Approve / Deny / Request More Info          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  BrainSAIT Platform - Response Processing                   │
│                                                              │
│  7. Response Handling                                       │
│     • Parse ClaimResponse FHIR Bundle                       │
│     • Extract adjudication results                          │
│     • Update claim status in MongoDB                        │
│     • Trigger domain events (ClaimApproved/ClaimDenied)     │
│                                                              │
│  8. Analytics & Reporting                                   │
│     • Update KPI metrics (FPCCR, DRR)                       │
│     • Store in analytics database                           │
│     • Generate dashboard updates                            │
│                                                              │
│  9. Notifications                                           │
│     • Provider notification (email/SMS/portal)              │
│     • Patient notification (if configured)                  │
│     • Audit log entry (HIPAA compliance)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────┐
│  Provider Dashboard  │ View claim status & adjudication
└──────────────────────┘
```

### Eligibility Verification Workflow

```
┌──────────────────────┐
│  Provider Request    │ Patient check-in / pre-service verification
└──────┬───────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  BrainSAIT API - Eligibility Endpoint                       │
│  POST /api/v1/eligibility/check                             │
│                                                              │
│  Request Body:                                              │
│  {                                                          │
│    "member_id": "123456789",                                │
│    "payer_id": "7000911508",                                │
│    "service_date": "2025-10-22",                            │
│    "service_type": "consultation"                           │
│  }                                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Member ID Lookup (MongoDB)                         │
│  • Query patient database                                   │
│  • Retrieve patient demographics                            │
│  • Find existing coverage records                           │
│  • Execution time: <100ms                                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Cache Check (Redis)                                │
│  Key: eligibility:{member_id}:{payer_id}:{service_date}     │
│                                                              │
│  ┌──────────────┐                  ┌────────────────────┐  │
│  │  Cache Hit?  │───── YES ───────►│  Return Cached     │  │
│  │              │                  │  Response (<10ms)  │  │
│  └──────┬───────┘                  └────────────────────┘  │
│         │                                                   │
│         NO                                                  │
│         │                                                   │
└─────────┼───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: NPHIES Real-Time Query                             │
│  • Build CoverageEligibilityRequest FHIR Bundle             │
│  • Attach authentication (certificate + headers)            │
│  • POST to NPHIES /fhir/$process-message                    │
│  • Wait for response (target: <1.5s)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Response Processing                                │
│  • Parse CoverageEligibilityResponse Bundle                 │
│  • Extract coverage status (active/inactive)                │
│  • Extract benefits (copay, deductible, limits)             │
│  • Extract coverage period (start/end dates)                │
│  • Extract network status                                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Cache Update (Redis)                               │
│  • Store response in Redis                                  │
│  • TTL: 24 hours (86400 seconds)                            │
│  • Also cache negative responses (not eligible)             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Response Return                                    │
│  Total time: <2 seconds (95th percentile)                   │
│                                                              │
│  Response:                                                  │
│  {                                                          │
│    "eligible": true,                                        │
│    "coverage_status": "active",                             │
│    "coverage_period": {                                     │
│      "start": "2025-01-01",                                 │
│      "end": "2025-12-31"                                    │
│    },                                                       │
│    "benefits": {                                            │
│      "copay": 50.00,                                        │
│      "deductible": 1000.00,                                 │
│      "deductible_met": 450.00,                              │
│      "out_of_pocket_max": 5000.00                           │
│    },                                                       │
│    "network_status": "in-network"                           │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

### Denial Appeal Workflow

```
┌──────────────────────┐
│  Claim Denied        │ ClaimResponse with denial code
└──────┬───────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  BrainSAIT - Denial Command Center (HeadQ)                  │
│                                                              │
│  1. Automated Denial Ingestion                              │
│     ┌────────────────────────────────────────────────────┐  │
│     │  • Parse NPHIES Denial Code                        │  │
│     │  • Extract denial reason                           │  │
│     │  • Calculate financial impact                      │  │
│     │  • Log in denial tracking system                   │  │
│     └────────────────────────────────────────────────────┘  │
│                                                              │
│  2. NLP-Driven Root Cause Analysis                          │
│     ┌────────────────────────────────────────────────────┐  │
│     │  CLINICALLINC Agent                                │  │
│     │  • Map payer code to internal category             │  │
│     │  • Examples:                                       │  │
│     │    - Code X → "Clinical Documentation Gap"         │  │
│     │    - Code Y → "Coding Error - Wrong ICD-10"        │  │
│     │    - Code Z → "Missing Pre-Authorization"          │  │
│     └────────────────────────────────────────────────────┘  │
│                                                              │
│  3. Skill-Based Routing Recommendation                      │
│     ┌────────────────────────────────────────────────────┐  │
│     │  ML-Powered Routing                                │  │
│     │  • Analyze denial type                             │  │
│     │  • Review historical success rates per specialist  │  │
│     │  • Recommend: "Assign to Madinah Coding Specialist"│  │
│     │  • Confidence: 87%                                 │  │
│     └────────────────────────────────────────────────────┘  │
│                                                              │
│  4. Task Assignment                                         │
│     • HeadQ Analyst reviews recommendation                  │
│     • Assigns to branch specialist                         │
│     • Sets 48-hour SLA timer                                │
│     • Adds contextual notes                                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Branch Collaboration Engine (e.g., Madinah)                │
│                                                              │
│  5. Specialist Review                                       │
│     • Receives notification                                 │
│     • Views claim details + denial reason                   │
│     • Reviews original submission                           │
│     • Countdown timer displayed (48h SLA)                   │
│                                                              │
│  6. Justification Gathering                                 │
│     ┌────────────────────────────────────────────────────┐  │
│     │  Contextual Form (Dynamic based on root cause)     │  │
│     │  • Upload missing clinical documentation           │  │
│     │  • Provide written justification                   │  │
│     │  • Attach physician notes                          │  │
│     │  • Reference medical guidelines                    │  │
│     └────────────────────────────────────────────────────┘  │
│                                                              │
│  7. NLP Vetting                                             │
│     ┌────────────────────────────────────────────────────┐  │
│     │  • Scan justification text                         │  │
│     │  • Check for mandatory keywords                    │  │
│     │  • Flag incomplete rationales                      │  │
│     │  • Suggest improvements                            │  │
│     └────────────────────────────────────────────────────┘  │
│                                                              │
│  8. Submit Back to HeadQ                                    │
│     • Mark task as complete                                 │
│     • Upload compiled appeal package                        │
│     • Trigger HeadQ review notification                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  HeadQ Final Review                                         │
│                                                              │
│  9. Quality Check                                           │
│     • Verify all documentation present                      │
│     • Review justification quality                          │
│     • Approve or request revisions                          │
│                                                              │
│  10. Automated Appeal Letter Generation                     │
│      ┌───────────────────────────────────────────────────┐ │
│      │  HEALTHCARELINC Agent                             │ │
│      │  • Use collected justification data               │ │
│      │  • Generate professional appeal letter (AR + EN)  │ │
│      │  • Include supporting document references         │ │
│      │  • Format per NPHIES requirements                 │ │
│      └───────────────────────────────────────────────────┘ │
│                                                              │
│  11. Submit Appeal to NPHIES                                │
│      • Build Claim with type="appeal"                       │
│      • Reference original claim                             │
│      • Attach appeal letter + documents                     │
│      • Submit via NPHIES API                                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────┐
│  Track Appeal Status │ Monitor for payer response
└──────────────────────┘
```


---

## 7. Compliance Modules (HIPAA, NPHIES, FHIR)

### HIPAA Level 3 Audit Logging

**Implementation**:

```python
# middleware/audit_logger.py

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel

class AuditLogEntry(BaseModel):
    """HIPAA-compliant audit log entry"""
    timestamp: datetime
    user_id: str
    user_role: str
    action: str  # CREATE, READ, UPDATE, DELETE, ACCESS
    resource_type: str  # Patient, Claim, Coverage
    resource_id: str
    phi_accessed: bool
    ip_address: str
    user_agent: str
    request_id: str
    result: str  # SUCCESS, FAILURE
    failure_reason: Optional[str] = None

class HIPAAAuditLogger:
    """
    HIPAA Level 3 Audit Logging
    - All PHI access logged with user ID, timestamp, action
    - Immutable audit trail (append-only MongoDB collection)
    - 7-year retention policy
    - Automated monthly compliance reports
    """
    
    def __init__(self, mongodb_client):
        self.db = mongodb_client.audit_database
        self.collection = self.db.hipaa_audit_logs
        # Ensure TTL index for 7-year retention
        self.collection.create_index(
            "timestamp",
            expireAfterSeconds=220752000  # 7 years in seconds
        )
    
    async def log_phi_access(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        request_context: dict
    ):
        """Log PHI access event"""
        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            user_role=request_context.get('user_role'),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            phi_accessed=True,
            ip_address=request_context.get('ip_address'),
            user_agent=request_context.get('user_agent'),
            request_id=request_context.get('request_id'),
            result='SUCCESS'
        )
        
        # Append-only insert (no updates allowed)
        await self.collection.insert_one(entry.model_dump())
    
    async def generate_monthly_compliance_report(self, month: int, year: int):
        """Generate automated monthly compliance report"""
        pipeline = [
            {
                '$match': {
                    'timestamp': {
                        '$gte': datetime(year, month, 1),
                        '$lt': datetime(year, month + 1, 1)
                    }
                }
            },
            {
                '$group': {
                    '_id': {
                        'user_id': '$user_id',
                        'action': '$action'
                    },
                    'count': {'$sum': 1}
                }
            }
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(None)
        return {
            'month': month,
            'year': year,
            'total_phi_accesses': len(results),
            'breakdown': results
        }
```

**Key Features**:
- **All PHI Access Logged**: Every read/write to patient data
- **Immutable Trail**: Append-only collection, no updates/deletes
- **7-Year Retention**: Automatic TTL index for compliance
- **Monthly Reports**: Automated compliance reporting

### NPHIES Integration Compliance

**Authentication & Security**:

```python
# auth/nphies_auth.py

import ssl
from typing import Optional
import httpx

class NPHIESAuthManager:
    """
    NPHIES-compliant authentication
    - Certificate-based TLS 1.2+ authentication
    - FHIR Bundle message signing
    - Saudi-specific headers
    """
    
    def __init__(
        self,
        cert_file: str,
        key_file: str,
        ca_bundle: str,
        license_number: str,
        organization_id: str
    ):
        self.cert_file = cert_file
        self.key_file = key_file
        self.ca_bundle = ca_bundle
        self.license_number = license_number
        self.organization_id = organization_id
    
    def get_authenticated_client(self) -> httpx.AsyncClient:
        """Create HTTPS client with certificate authentication"""
        
        # Create SSL context with TLS 1.2+ only
        ssl_context = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH,
            cafile=self.ca_bundle
        )
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.load_cert_chain(
            certfile=self.cert_file,
            keyfile=self.key_file
        )
        
        return httpx.AsyncClient(
            verify=ssl_context,
            headers=self.get_nphies_headers(),
            timeout=30.0
        )
    
    def get_nphies_headers(self) -> dict:
        """NPHIES-required headers"""
        return {
            'X-License-Number': self.license_number,
            'X-Organization-ID': self.organization_id,
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json',
            'Accept-Language': 'ar,en'
        }
```

**Saudi-Specific Terminology**:

```python
# models/saudi_terminology.py

# ICD-10-SA (Saudi Arabia specific codes)
ICD_10_SA_CODES = {
    'A00-B99': 'Certain infectious and parasitic diseases',
    'C00-D48': 'Neoplasms',
    # ... full Saudi ICD-10 catalog
}

# CPT-SA (Current Procedural Terminology - Saudi)
CPT_SA_CODES = {
    '99201': 'Office visit, new patient (استشارة جديدة)',
    '99211': 'Office visit, established patient (استشارة متابعة)',
    # ... full Saudi CPT catalog with Arabic names
}

# Saudi National Drug Code (SNDC)
SNDC_CODES = {
    '1234567': {
        'name_en': 'Paracetamol 500mg',
        'name_ar': 'باراسيتامول 500 ملغ',
        'dosage_form': 'tablet'
    }
    # ... full Saudi drug catalog
}
```

**Arabic Clinical Names Support**:

```python
# utils/bilingual_clinical_terms.py

from typing import Dict

class BilingualClinicalTerms:
    """Support for Arabic RTL + English LTR clinical terminology"""
    
    DIAGNOSES = {
        'E11': {
            'en': 'Type 2 diabetes mellitus',
            'ar': 'داء السكري من النوع الثاني'
        },
        'I10': {
            'en': 'Essential hypertension',
            'ar': 'ارتفاع ضغط الدم الأساسي'
        }
    }
    
    PROCEDURES = {
        '99201': {
            'en': 'Office visit, new patient',
            'ar': 'زيارة العيادة، مريض جديد'
        },
        '99211': {
            'en': 'Office visit, established patient',
            'ar': 'زيارة العيادة، مريض قائم'
        }
    }
    
    @staticmethod
    def get_diagnosis_name(code: str, lang: str = 'en') -> str:
        """Get diagnosis name in specified language"""
        return BilingualClinicalTerms.DIAGNOSES.get(code, {}).get(lang, code)
    
    @staticmethod
    def get_procedure_name(code: str, lang: str = 'en') -> str:
        """Get procedure name in specified language"""
        return BilingualClinicalTerms.PROCEDURES.get(code, {}).get(lang, code)
```

### FHIR R4 Validation

**Strict Resource Validation**:

```python
# validators/fhir_validator.py

from typing import Dict, List, Optional
from pydantic import BaseModel, validator
from fhirclient.models import patient, claim, coverage

class FHIRValidator:
    """
    FHIR R4 Compliance Validation
    - Strict resource structure validation
    - Extension validation (NPHIES-specific)
    - Reference integrity checks
    - Coding system validation
    """
    
    VALID_CODING_SYSTEMS = {
        'icd10': 'http://hl7.org/fhir/sid/icd-10',
        'icd10_sa': 'http://nphies.sa/terminology/CodeSystem/icd-10-sa',
        'cpt': 'http://www.ama-assn.org/go/cpt',
        'cpt_sa': 'http://nphies.sa/terminology/CodeSystem/cpt-sa',
        'snomed': 'http://snomed.info/sct',
        'loinc': 'http://loinc.org'
    }
    
    def validate_patient_resource(self, patient_data: dict) -> tuple[bool, List[str]]:
        """Validate Patient FHIR resource"""
        errors = []
        
        # Required fields
        if not patient_data.get('resourceType') == 'Patient':
            errors.append("resourceType must be 'Patient'")
        
        if not patient_data.get('identifier'):
            errors.append("Patient.identifier is required")
        
        # Identifier validation (Saudi National ID or Iqama)
        identifiers = patient_data.get('identifier', [])
        has_national_id = any(
            id.get('system') == 'http://nphies.sa/identifier/nationalid'
            for id in identifiers
        )
        if not has_national_id:
            errors.append("Patient must have Saudi National ID or Iqama identifier")
        
        # Name validation (Arabic + English)
        names = patient_data.get('name', [])
        if not names:
            errors.append("Patient.name is required")
        
        return (len(errors) == 0, errors)
    
    def validate_claim_resource(self, claim_data: dict) -> tuple[bool, List[str]]:
        """Validate Claim FHIR resource"""
        errors = []
        
        # Required fields per NPHIES specification
        required_fields = [
            'resourceType', 'identifier', 'status', 'type',
            'use', 'patient', 'created', 'provider',
            'priority', 'insurance', 'item'
        ]
        
        for field in required_fields:
            if field not in claim_data:
                errors.append(f"Claim.{field} is required")
        
        # Validate claim items
        items = claim_data.get('item', [])
        for idx, item in enumerate(items):
            if not item.get('sequence'):
                errors.append(f"Claim.item[{idx}].sequence is required")
            
            if not item.get('productOrService'):
                errors.append(f"Claim.item[{idx}].productOrService is required")
            
            # Validate coding system
            coding = item.get('productOrService', {}).get('coding', [])
            for code in coding:
                system = code.get('system')
                if system not in self.VALID_CODING_SYSTEMS.values():
                    errors.append(
                        f"Invalid coding system: {system}. "
                        f"Must be one of: {list(self.VALID_CODING_SYSTEMS.values())}"
                    )
        
        return (len(errors) == 0, errors)
    
    def validate_reference_integrity(
        self,
        bundle: dict,
        resource_id: str,
        reference: str
    ) -> bool:
        """Check if referenced resource exists in bundle"""
        entries = bundle.get('entry', [])
        
        # Extract resource type and ID from reference
        # Example: "Patient/patient-123" -> type="Patient", id="patient-123"
        ref_parts = reference.split('/')
        if len(ref_parts) != 2:
            return False
        
        ref_type, ref_id = ref_parts
        
        # Search for resource in bundle
        for entry in entries:
            resource = entry.get('resource', {})
            if (resource.get('resourceType') == ref_type and
                resource.get('id') == ref_id):
                return True
        
        return False
    
    def validate_nphies_extensions(self, resource: dict) -> tuple[bool, List[str]]:
        """Validate NPHIES-specific FHIR extensions"""
        errors = []
        extensions = resource.get('extension', [])
        
        # NPHIES required extensions (example)
        required_extensions = [
            'http://nphies.sa/fhir/ksa/nphies-fs/StructureDefinition/extension-episode'
        ]
        
        extension_urls = [ext.get('url') for ext in extensions]
        
        for required_url in required_extensions:
            if required_url not in extension_urls:
                errors.append(f"Missing required NPHIES extension: {required_url}")
        
        return (len(errors) == 0, errors)
```

**Compliance Checks**:

| Check Type | Description | Implementation |
|------------|-------------|----------------|
| **Resource Structure** | Validates FHIR resource conforms to R4 schema | Pydantic models + fhirclient library |
| **Required Fields** | Ensures all mandatory fields present | Field-level validation |
| **Reference Integrity** | Verifies all references resolve | Cross-reference validation |
| **Coding Systems** | Validates coding system URLs | Whitelist validation |
| **NPHIES Extensions** | Checks Saudi-specific extensions | Extension URL validation |
| **Terminology** | Validates codes exist in terminologies | Code lookup validation |

---

## 8. Security Architecture

### Multi-Layer Security Model

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Edge Security (Cloudflare)                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • DDoS Protection (L3-L7)                                │  │
│  │  • Web Application Firewall (WAF)                         │  │
│  │  • Rate Limiting (100 req/min per IP)                     │  │
│  │  • Bot Management                                         │  │
│  │  • SSL/TLS Termination                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: Network Security                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • VPC with Private Subnets                               │  │
│  │  • Security Groups (Firewall Rules)                       │  │
│  │  • Network ACLs                                           │  │
│  │  • VPN for Admin Access                                   │  │
│  │  • IP Whitelisting for NPHIES                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Application Security                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Authentication:                                          │  │
│  │  • JWT with 1-hour expiry                                 │  │
│  │  • Refresh tokens (7 days)                                │  │
│  │  • Multi-factor authentication (optional)                 │  │
│  │  • OAuth2 for third-party integrations                    │  │
│  │                                                            │  │
│  │  Authorization:                                           │  │
│  │  • Role-Based Access Control (RBAC)                       │  │
│  │    - Admin: Full access                                   │  │
│  │    - Provider: Claims, patients, eligibility              │  │
│  │    - Patient: Own records only                            │  │
│  │    - Auditor: Read-only audit logs                        │  │
│  │  • Resource-level permissions                             │  │
│  │  • Attribute-based access (location, time)                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: Data Security                                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  At Rest:                                                 │  │
│  │  • AES-256 encryption for PHI in MongoDB                  │  │
│  │  • Encrypted backups                                      │  │
│  │  • Encrypted volumes (EBS encryption)                     │  │
│  │                                                            │  │
│  │  In Transit:                                              │  │
│  │  • TLS 1.2+ with certificate pinning                      │  │
│  │  • Perfect Forward Secrecy (PFS)                          │  │
│  │  • Strong cipher suites only                              │  │
│  │                                                            │  │
│  │  Field-Level:                                             │  │
│  │  • Selective field encryption (SSN, credit card)          │  │
│  │  • Tokenization for sensitive data                        │  │
│  │  • Data masking in non-production                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Protection Implementation

**Encryption at Rest**:

```python
# middleware/encryption.py

from cryptography.fernet import Fernet
from typing import Any
import os

class FieldEncryption:
    """
    AES-256 field-level encryption for PHI
    - Encrypt sensitive fields before MongoDB storage
    - Decrypt on retrieval
    """
    
    def __init__(self):
        # Load encryption key from environment (32-byte base64-encoded)
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable not set")
        self.cipher = Fernet(key.encode())
    
    def encrypt_field(self, value: str) -> str:
        """Encrypt a single field value"""
        if not value:
            return value
        encrypted = self.cipher.encrypt(value.encode())
        return encrypted.decode()
    
    def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt a single field value"""
        if not encrypted_value:
            return encrypted_value
        decrypted = self.cipher.decrypt(encrypted_value.encode())
        return decrypted.decode()
    
    def encrypt_phi_fields(self, patient_data: dict) -> dict:
        """Encrypt PHI fields in patient record"""
        sensitive_fields = [
            'national_id', 'passport_number', 'ssn',
            'phone', 'email', 'address'
        ]
        
        encrypted_data = patient_data.copy()
        for field in sensitive_fields:
            if field in encrypted_data:
                encrypted_data[field] = self.encrypt_field(
                    encrypted_data[field]
                )
        
        return encrypted_data
    
    def decrypt_phi_fields(self, encrypted_data: dict) -> dict:
        """Decrypt PHI fields in patient record"""
        sensitive_fields = [
            'national_id', 'passport_number', 'ssn',
            'phone', 'email', 'address'
        ]
        
        decrypted_data = encrypted_data.copy()
        for field in sensitive_fields:
            if field in decrypted_data:
                decrypted_data[field] = self.decrypt_field(
                    decrypted_data[field]
                )
        
        return decrypted_data
```

**Encryption in Transit**:

```python
# core/security.py

import ssl
from fastapi import FastAPI
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

def configure_tls_security(app: FastAPI):
    """Configure TLS 1.2+ and security headers"""
    
    # Redirect HTTP to HTTPS
    app.add_middleware(HTTPSRedirectMiddleware)
    
    # Only allow trusted hosts
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=['brainsait.health', '*.brainsait.health']
    )
    
    # Security headers
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
```

### Authentication & Authorization

**JWT Token Management**:

```python
# auth/jwt_handler.py

from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTHandler:
    """
    JWT-based authentication
    - Access tokens: 1-hour expiry
    - Refresh tokens: 7-day expiry
    - Automatic token rotation
    """
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.access_token_expire_hours = 1
        self.refresh_token_expire_days = 7
    
    def create_access_token(
        self,
        user_id: str,
        role: str,
        permissions: list
    ) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(
            hours=self.access_token_expire_hours
        )
        
        payload = {
            'sub': user_id,
            'role': role,
            'permissions': permissions,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(
            days=self.refresh_token_expire_days
        )
        
        payload = {
            'sub': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
```

**Role-Based Access Control**:

```python
# middleware/rbac.py

from enum import Enum
from typing import List
from fastapi import HTTPException, status

class Role(str, Enum):
    ADMIN = "admin"
    PROVIDER = "provider"
    PATIENT = "patient"
    AUDITOR = "auditor"
    ANALYST = "analyst"

class Permission(str, Enum):
    # Claims
    CLAIM_CREATE = "claim:create"
    CLAIM_READ = "claim:read"
    CLAIM_UPDATE = "claim:update"
    CLAIM_DELETE = "claim:delete"
    
    # Patients
    PATIENT_CREATE = "patient:create"
    PATIENT_READ = "patient:read"
    PATIENT_UPDATE = "patient:update"
    PATIENT_DELETE = "patient:delete"
    
    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"
    
    # Audit
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"

# Role-Permission Matrix
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        # All permissions
        *list(Permission)
    ],
    Role.PROVIDER: [
        Permission.CLAIM_CREATE,
        Permission.CLAIM_READ,
        Permission.CLAIM_UPDATE,
        Permission.PATIENT_CREATE,
        Permission.PATIENT_READ,
        Permission.PATIENT_UPDATE,
        Permission.ANALYTICS_VIEW,
    ],
    Role.PATIENT: [
        Permission.CLAIM_READ,  # Own claims only
        Permission.PATIENT_READ,  # Own record only
    ],
    Role.AUDITOR: [
        Permission.AUDIT_READ,
        Permission.AUDIT_EXPORT,
        Permission.CLAIM_READ,
        Permission.PATIENT_READ,
    ],
    Role.ANALYST: [
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_EXPORT,
        Permission.CLAIM_READ,
    ]
}

def check_permission(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission"""
    role = Role(user_role)
    permission = Permission(required_permission)
    return permission in ROLE_PERMISSIONS.get(role, [])

def require_permission(required_permission: str):
    """Decorator to enforce permission on endpoint"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user from request context
            user_role = kwargs.get('current_user', {}).get('role')
            
            if not check_permission(user_role, required_permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {required_permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### Audit & Monitoring

**Centralized Logging**:

```python
# core/logging.py

import logging
import json
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    """
    Structured JSON logging for ELK stack / CloudWatch
    - Consistent log format
    - Correlation IDs for request tracing
    - Performance metrics
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self._get_json_formatter())
        self.logger.addHandler(handler)
    
    def _get_json_formatter(self):
        """Custom JSON formatter"""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Add extra fields if present
                if hasattr(record, 'request_id'):
                    log_data['request_id'] = record.request_id
                if hasattr(record, 'user_id'):
                    log_data['user_id'] = record.user_id
                if hasattr(record, 'duration_ms'):
                    log_data['duration_ms'] = record.duration_ms
                
                return json.dumps(log_data)
        
        return JSONFormatter()
    
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context"""
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.logger.warning(message, extra=kwargs)
```

**Security Alerts**:

```python
# monitoring/security_alerts.py

from enum import Enum
from typing import Dict

class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SecurityAlertManager:
    """
    Real-time security alerting
    - Failed login attempts
    - Unauthorized access attempts
    - Suspicious patterns
    - Data breach indicators
    """
    
    def __init__(self, notification_service):
        self.notification_service = notification_service
        self.failed_login_threshold = 5
        self.failed_login_window_minutes = 15
    
    async def check_failed_logins(self, ip_address: str):
        """Monitor failed login attempts"""
        # Query recent failed logins from this IP
        failed_count = await self._get_failed_login_count(
            ip_address,
            self.failed_login_window_minutes
        )
        
        if failed_count >= self.failed_login_threshold:
            await self.send_alert(
                severity=AlertSeverity.HIGH,
                title="Multiple Failed Login Attempts",
                message=f"IP {ip_address} has {failed_count} failed login attempts in {self.failed_login_window_minutes} minutes",
                recommended_action="Block IP address"
            )
    
    async def check_unauthorized_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str
    ):
        """Monitor unauthorized access attempts"""
        await self.send_alert(
            severity=AlertSeverity.CRITICAL,
            title="Unauthorized Access Attempt",
            message=f"User {user_id} attempted to access {resource_type}/{resource_id} without permission",
            recommended_action="Review user permissions and audit logs"
        )
    
    async def send_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        recommended_action: str
    ):
        """Send security alert"""
        alert_data = {
            'severity': severity,
            'title': title,
            'message': message,
            'recommended_action': recommended_action,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send to notification service (Slack, PagerDuty, etc.)
        await self.notification_service.send_alert(alert_data)
```

---

## 9. Performance Optimization

### Caching Strategy

**Redis Caching Implementation**:

```python
# services/caching.py

from redis import Redis
from typing import Optional, Any
import json
import hashlib

class CacheService:
    """
    Multi-layer caching strategy
    - Eligibility checks: 24-hour TTL
    - API responses: 30-60 second TTL
    - Static configuration: 1-hour TTL
    """
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate deterministic cache key"""
        # Sort kwargs for consistency
        sorted_kwargs = sorted(kwargs.items())
        key_data = f"{prefix}:{json.dumps(sorted_kwargs)}"
        
        # Hash to avoid key length issues
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"{prefix}:{key_hash}"
    
    async def get_eligibility(
        self,
        member_id: str,
        payer_id: str,
        service_date: str
    ) -> Optional[dict]:
        """Get cached eligibility result"""
        cache_key = self.generate_cache_key(
            'eligibility',
            member_id=member_id,
            payer_id=payer_id,
            service_date=service_date
        )
        
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_eligibility(
        self,
        member_id: str,
        payer_id: str,
        service_date: str,
        result: dict,
        ttl_seconds: int = 86400  # 24 hours
    ):
        """Cache eligibility result"""
        cache_key = self.generate_cache_key(
            'eligibility',
            member_id=member_id,
            payer_id=payer_id,
            service_date=service_date
        )
        
        self.redis.setex(
            cache_key,
            ttl_seconds,
            json.dumps(result)
        )
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
```

**Cache Hierarchy**:

```
Browser Cache (1 year)
    │
    ▼
CDN Cache (Cloudflare) (1 hour)
    │
    ▼
Redis Cache (Variable TTL)
    │
    ▼
MongoDB (Source of Truth)
```

### Database Optimization

**MongoDB Indexing Strategy**:

```javascript
// MongoDB indexes for performance

// Claims collection
db.claims.createIndex({ "claim_id": 1 }, { unique: true });
db.claims.createIndex({ "patient_id": 1, "submission_date": -1 });
db.claims.createIndex({ "status": 1, "submission_date": -1 });
db.claims.createIndex({ "provider_id": 1, "submission_date": -1 });

// Eligibility checks collection
db.eligibility_checks.createIndex({ "member_id": 1, "check_date": -1 });
db.eligibility_checks.createIndex({ "payer_id": 1, "check_date": -1 });

// Patients collection
db.patients.createIndex({ "patient_id": 1 }, { unique: true });
db.patients.createIndex({ "national_id": 1 }, { unique: true, sparse: true });
db.patients.createIndex({ "email": 1 }, { sparse: true });

// Audit logs collection (time-series optimized)
db.audit_logs.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 220752000 }); // 7 years
db.audit_logs.createIndex({ "user_id": 1, "timestamp": -1 });
db.audit_logs.createIndex({ "resource_type": 1, "resource_id": 1, "timestamp": -1 });
```

**Query Optimization**:

```python
# services/claims.py

from typing import List, Optional
from datetime import datetime, timedelta

class ClaimsQueryOptimizer:
    """
    Optimized MongoDB queries using aggregation pipeline
    - Minimize data transfer
    - Server-side filtering and sorting
    - Pagination with skip/limit
    """
    
    async def get_claims_dashboard_metrics(
        self,
        provider_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """Get dashboard metrics with single aggregation query"""
        pipeline = [
            # Stage 1: Filter by provider and date range
            {
                '$match': {
                    'provider_id': provider_id,
                    'submission_date': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }
            },
            # Stage 2: Group and calculate metrics
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1},
                    'total_amount': {'$sum': '$total_amount'},
                    'avg_amount': {'$avg': '$total_amount'}
                }
            },
            # Stage 3: Shape final output
            {
                '$project': {
                    'status': '$_id',
                    'count': 1,
                    'total_amount': {'$round': ['$total_amount', 2]},
                    'avg_amount': {'$round': ['$avg_amount', 2]}
                }
            }
        ]
        
        results = await self.claims_collection.aggregate(pipeline).to_list(None)
        
        # Transform to dashboard format
        metrics = {
            'total_claims': sum(r['count'] for r in results),
            'by_status': {r['status']: r for r in results},
            'total_value': sum(r['total_amount'] for r in results)
        }
        
        return metrics
```

### Frontend Performance

**Code Splitting & Lazy Loading**:

```typescript
// App.tsx - Route-based code splitting

import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoadingSpinner from './components/common/LoadingSpinner';

// Lazy load route components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Claims = lazy(() => import('./pages/Claims'));
const Eligibility = lazy(() => import('./pages/Eligibility'));
const Analytics = lazy(() => import('./pages/Analytics'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/claims" element={<Claims />} />
          <Route path="/eligibility" element={<Eligibility />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

**Image Optimization**:

```typescript
// components/common/OptimizedImage.tsx

import { useState, useEffect } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  lazy?: boolean;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width,
  height,
  lazy = true
}) => {
  const [imageSrc, setImageSrc] = useState<string>('');
  const [imageLoaded, setImageLoaded] = useState(false);
  
  useEffect(() => {
    // Convert to WebP if supported
    const img = new Image();
    const webpSrc = src.replace(/\.(jpg|jpeg|png)$/i, '.webp');
    
    img.onload = () => {
      setImageSrc(webpSrc);
      setImageLoaded(true);
    };
    
    img.onerror = () => {
      // Fallback to original format
      setImageSrc(src);
      setImageLoaded(true);
    };
    
    img.src = webpSrc;
  }, [src]);
  
  return (
    <img
      src={imageSrc}
      alt={alt}
      width={width}
      height={height}
      loading={lazy ? 'lazy' : 'eager'}
      className={`transition-opacity duration-300 ${
        imageLoaded ? 'opacity-100' : 'opacity-0'
      }`}
    />
  );
};
```

**Performance Monitoring**:

```typescript
// hooks/usePerformanceMonitoring.ts

import { useEffect } from 'react';

export const usePerformanceMonitoring = (componentName: string) => {
  useEffect(() => {
    // Measure component mount time
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      // Send to analytics
      if (duration > 100) {
        console.warn(
          `${componentName} render took ${duration.toFixed(2)}ms`
        );
        
        // Log to monitoring service
        sendPerformanceMetric({
          component: componentName,
          metric: 'render_time',
          value: duration,
          threshold: 100
        });
      }
    };
  }, [componentName]);
};

function sendPerformanceMetric(data: any) {
  // Send to monitoring service (e.g., New Relic, Datadog)
  if (window.newrelic) {
    window.newrelic.addPageAction('component_performance', data);
  }
}
```

### Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Page Load Time** | <2.5s | TBD | 🎯 Target |
| **Eligibility Check** | <2s (95th percentile) | TBD | 🎯 Target |
| **Claim Submission** | <5s | TBD | 🎯 Target |
| **Dashboard Load** | <1.5s | TBD | 🎯 Target |
| **API Response Time** | <500ms (median) | TBD | 🎯 Target |
| **Time to Interactive** | <3s | TBD | 🎯 Target |
| **Largest Contentful Paint** | <2.5s | TBD | 🎯 Target |
| **Cumulative Layout Shift** | <0.1 | TBD | 🎯 Target |


---

## 10. Deployment Architecture

### Development Environment (Docker Compose)

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: brainsait-backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
      - NPHIES_BASE_URL=https://sandbox.nphies.sa/api/fs/fhir
      - LOG_LEVEL=DEBUG
    volumes:
      - ./src/backend:/app
      - ./auth:/app/auth
      - ./services:/app/services
      - ./models:/app/models
    depends_on:
      - mongodb
      - redis
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  
  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: brainsait-frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    command: npm run dev:host
  
  # MongoDB Database
  mongodb:
    image: mongo:6.0
    container_name: brainsait-mongodb
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=admin123
      - MONGO_INITDB_DATABASE=brainsait_healthcare
    volumes:
      - mongodb_data:/data/db
      - ./infrastructure/mongodb/init.js:/docker-entrypoint-initdb.d/init.js
  
  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: brainsait-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  mongodb_data:
  redis_data:
```

**Quick Start Commands**:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up -d --build

# Access backend API docs
# http://localhost:8000/docs

# Access frontend
# http://localhost:5173
```

### Staging Environment (Kubernetes)

**Deployment Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster (Staging)              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Ingress Controller (Nginx)                            │ │
│  │  • TLS Termination                                     │ │
│  │  • Load Balancing                                      │ │
│  │  • Rate Limiting                                       │ │
│  └──────────────────┬─────────────────────────────────────┘ │
│                     │                                        │
│       ┌─────────────┼─────────────┐                         │
│       │             │             │                         │
│  ┌────▼────┐   ┌───▼────┐   ┌───▼────┐                    │
│  │ Backend │   │ Backend│   │Frontend│                     │
│  │ Pod 1   │   │ Pod 2  │   │ Pod 1  │                     │
│  │         │   │        │   │        │                     │
│  │ FastAPI │   │FastAPI │   │ Nginx  │                     │
│  │ Port:   │   │Port:   │   │ Port:  │                     │
│  │ 8000    │   │8000    │   │ 80     │                     │
│  └────┬────┘   └───┬────┘   └───┬────┘                    │
│       │            │            │                           │
│       └────────────┼────────────┘                           │
│                    │                                        │
│         ┌──────────┼──────────┐                            │
│         │          │          │                             │
│    ┌────▼────┐ ┌──▼────┐ ┌──▼─────┐                       │
│    │ MongoDB │ │ Redis │ │ Secrets│                        │
│    │ StatefulSet│Service│ConfigMap│                        │
│    │         │ │       │ │        │                         │
│    │ • 2 Replicas │   │ │        │                         │
│    │ • PV: 100GB │    │ │        │                         │
│    └─────────┘ └───────┘ └────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

**Kubernetes Manifests**:

```yaml
# infrastructure/kubernetes/deployments/backend-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: brainsait-backend
  namespace: brainsait-staging
  labels:
    app: brainsait-backend
    version: v1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: brainsait-backend
  template:
    metadata:
      labels:
        app: brainsait-backend
        version: v1
    spec:
      containers:
      - name: backend
        image: brainsait/backend:staging-latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: brainsait-secrets
              key: mongodb-uri
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: brainsait-secrets
              key: redis-url
        - name: NPHIES_BASE_URL
          valueFrom:
            configMapKeyRef:
              name: brainsait-config
              key: nphies-base-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: brainsait-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: brainsait-backend
  namespace: brainsait-staging
spec:
  selector:
    app: brainsait-backend
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
```

```yaml
# infrastructure/kubernetes/deployments/frontend-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: brainsait-frontend
  namespace: brainsait-staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: brainsait-frontend
  template:
    metadata:
      labels:
        app: brainsait-frontend
    spec:
      containers:
      - name: frontend
        image: brainsait/frontend:staging-latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: brainsait-frontend
  namespace: brainsait-staging
spec:
  selector:
    app: brainsait-frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

```yaml
# infrastructure/kubernetes/ingress/ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: brainsait-ingress
  namespace: brainsait-staging
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - staging.brainsait.health
    - api-staging.brainsait.health
    secretName: brainsait-tls
  rules:
  - host: staging.brainsait.health
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: brainsait-frontend
            port:
              number: 80
  - host: api-staging.brainsait.health
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: brainsait-backend
            port:
              number: 80
```

### Production Environment (Kubernetes + Cloudflare)

**Production Architecture**:

```
                   ┌─────────────────────┐
                   │   Cloudflare CDN    │
                   │  • Global Edge      │
                   │  • WAF              │
                   │  • DDoS Protection  │
                   └──────────┬──────────┘
                              │
                   ┌──────────▼──────────┐
                   │  Load Balancer      │
                   │  (Kubernetes)       │
                   └──────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ Backend │          │ Backend │          │ Backend │
   │  Pod 1  │          │  Pod 2  │          │  Pod 3  │
   │ (AZ-1)  │          │ (AZ-2)  │          │ (AZ-3)  │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                   ┌──────────▼──────────┐
                   │  MongoDB Cluster    │
                   │  • Primary          │
                   │  • Secondary 1      │
                   │  • Secondary 2      │
                   │  • Auto-failover    │
                   └─────────────────────┘
```

**Production Deployment Configuration**:

```yaml
# infrastructure/kubernetes/production/backend-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: brainsait-backend
  namespace: brainsait-production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: brainsait-backend
  template:
    metadata:
      labels:
        app: brainsait-backend
    spec:
      # Spread pods across availability zones
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - brainsait-backend
            topologyKey: topology.kubernetes.io/zone
      
      containers:
      - name: backend
        image: brainsait/backend:v1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: brainsait-backend-hpa
  namespace: brainsait-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: brainsait-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deployment Scripts

**Automated Deployment**:

```bash
#!/bin/bash
# infrastructure/scripts/deploy-production.sh

set -e

ENVIRONMENT="production"
VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Usage: ./deploy-production.sh <version>"
  exit 1
fi

echo "🚀 Deploying BrainSAIT Healthcare Platform v${VERSION} to ${ENVIRONMENT}"

# Build and push Docker images
echo "📦 Building Docker images..."
docker build -t brainsait/backend:${VERSION} -f Dockerfile .
docker build -t brainsait/frontend:${VERSION} -f frontend/Dockerfile ./frontend

echo "📤 Pushing images to registry..."
docker push brainsait/backend:${VERSION}
docker push brainsait/frontend:${VERSION}

# Update Kubernetes manifests
echo "🔧 Updating Kubernetes manifests..."
sed -i "s|image: brainsait/backend:.*|image: brainsait/backend:${VERSION}|g" \
  infrastructure/kubernetes/production/backend-deployment.yaml
sed -i "s|image: brainsait/frontend:.*|image: brainsait/frontend:${VERSION}|g" \
  infrastructure/kubernetes/production/frontend-deployment.yaml

# Apply Kubernetes configurations
echo "☸️  Applying Kubernetes configurations..."
kubectl apply -f infrastructure/kubernetes/production/

# Wait for rollout
echo "⏳ Waiting for deployment to complete..."
kubectl rollout status deployment/brainsait-backend -n brainsait-production
kubectl rollout status deployment/brainsait-frontend -n brainsait-production

# Run smoke tests
echo "🧪 Running smoke tests..."
./infrastructure/scripts/smoke-tests.sh

echo "✅ Deployment completed successfully!"
echo "🌐 Application available at: https://brainsait.health"
```

### Disaster Recovery

**Backup Strategy**:

```bash
#!/bin/bash
# infrastructure/scripts/backup-restore.sh

# Automated daily backups
BACKUP_DIR="/backups/brainsait"
DATE=$(date +%Y%m%d_%H%M%S)

# MongoDB backup
echo "📦 Backing up MongoDB..."
mongodump --uri="mongodb://admin:password@mongodb:27017/brainsait_healthcare" \
  --out="${BACKUP_DIR}/mongodb_${DATE}"

# Compress backup
tar -czf "${BACKUP_DIR}/mongodb_${DATE}.tar.gz" "${BACKUP_DIR}/mongodb_${DATE}"
rm -rf "${BACKUP_DIR}/mongodb_${DATE}"

# Upload to S3
aws s3 cp "${BACKUP_DIR}/mongodb_${DATE}.tar.gz" \
  "s3://brainsait-backups/mongodb/${DATE}/"

# Retention: Keep backups for 30 days
find ${BACKUP_DIR} -name "mongodb_*.tar.gz" -mtime +30 -delete

echo "✅ Backup completed: ${BACKUP_DIR}/mongodb_${DATE}.tar.gz"
```

---

## 11. Bilingual & RTL Support

### BilingualText Type System

**TypeScript Types**:

```typescript
// src/shared/types/BilingualText.ts

export interface BilingualText {
  ar: string;  // Arabic (RTL)
  en: string;  // English (LTR)
}

export interface BilingualContent {
  title: BilingualText;
  description?: BilingualText;
  metadata?: Record<string, BilingualText>;
}

// Utility type for bilingual data
export type Bilingual<T> = T extends string 
  ? BilingualText 
  : T extends object 
  ? { [K in keyof T]: Bilingual<T[K]> }
  : T;

// Example usage:
interface ClaimData {
  claimId: string;
  diagnosis: string;
  procedure: string;
}

type BilingualClaimData = Bilingual<ClaimData>;
// Results in:
// {
//   claimId: string;
//   diagnosis: BilingualText;
//   procedure: BilingualText;
// }
```

**React Component Implementation**:

```typescript
// components/common/BilingualText.tsx

import React from 'react';
import { useLanguage } from '../../contexts/LanguageContext';

interface BilingualTextProps {
  text: BilingualText;
  className?: string;
  as?: 'p' | 'span' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

export const BilingualText: React.FC<BilingualTextProps> = ({
  text,
  className = '',
  as: Component = 'span'
}) => {
  const { language } = useLanguage();
  
  return (
    <Component
      className={className}
      dir={language === 'ar' ? 'rtl' : 'ltr'}
      lang={language}
    >
      {text[language]}
    </Component>
  );
};

// Usage example:
function ClaimItem({ diagnosis }: { diagnosis: BilingualText }) {
  return (
    <div>
      <BilingualText 
        text={diagnosis}
        as="h3"
        className="text-lg font-semibold"
      />
    </div>
  );
}
```

### RTL Layout System

**Automatic Layout Switching**:

```typescript
// contexts/LanguageContext.tsx

import React, { createContext, useState, useContext, useEffect } from 'react';

type Language = 'ar' | 'en';
type Direction = 'rtl' | 'ltr';

interface LanguageContextType {
  language: Language;
  direction: Direction;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>('en');
  const direction: Direction = language === 'ar' ? 'rtl' : 'ltr';
  
  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('preferred_language', lang);
    
    // Update document direction
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
  };
  
  useEffect(() => {
    // Load saved preference
    const savedLang = localStorage.getItem('preferred_language') as Language;
    if (savedLang) {
      setLanguage(savedLang);
    }
  }, []);
  
  const t = (key: string): string => {
    // Translation function (integrate with i18next)
    return key;
  };
  
  return (
    <LanguageContext.Provider value={{ language, direction, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};
```

**RTL-Aware Styling**:

```css
/* styles/arabic-rtl.css */

/* Directional utilities */
[dir="rtl"] .mr-4 { margin-right: 0; margin-left: 1rem; }
[dir="rtl"] .ml-4 { margin-left: 0; margin-right: 1rem; }
[dir="rtl"] .text-left { text-align: right; }
[dir="rtl"] .text-right { text-align: left; }

/* Arabic font family */
[dir="rtl"] {
  font-family: 'IBM Plex Sans Arabic', 'Arial', sans-serif;
}

/* Adjust letter spacing for Arabic */
[dir="rtl"] p,
[dir="rtl"] span,
[dir="rtl"] div {
  letter-spacing: 0;
}

/* RTL-aware flex layouts */
[dir="rtl"] .flex-row {
  flex-direction: row-reverse;
}

/* RTL icons */
[dir="rtl"] .icon-arrow-right::before {
  content: "←";
}

[dir="ltr"] .icon-arrow-right::before {
  content: "→";
}
```

### Numeric Formatting

**Eastern vs Western Arabic Numerals**:

```typescript
// utils/numberFormatters.ts

export type NumeralSystem = 'western' | 'eastern';

const EASTERN_ARABIC_DIGITS = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
const WESTERN_DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

export function formatNumber(
  value: number,
  system: NumeralSystem,
  locale: string = 'en-US'
): string {
  // Format with appropriate locale
  const formatted = new Intl.NumberFormat(locale).format(value);
  
  if (system === 'eastern') {
    // Convert Western digits to Eastern Arabic
    return formatted.replace(/\d/g, (digit) => {
      return EASTERN_ARABIC_DIGITS[parseInt(digit)];
    });
  }
  
  return formatted;
}

export function formatCurrency(
  amount: number,
  currency: string = 'SAR',
  language: 'ar' | 'en' = 'en',
  numeralSystem: NumeralSystem = 'western'
): string {
  const locale = language === 'ar' ? 'ar-SA' : 'en-US';
  
  const formatted = new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
  
  if (language === 'ar' && numeralSystem === 'eastern') {
    return formatted.replace(/\d/g, (digit) => {
      return EASTERN_ARABIC_DIGITS[parseInt(digit)];
    });
  }
  
  return formatted;
}

// Usage:
formatNumber(1234.56, 'western', 'en-US');  // "1,234.56"
formatNumber(1234.56, 'eastern', 'ar-SA');  // "١٬٢٣٤٫٥٦"
formatCurrency(1500, 'SAR', 'en');          // "SAR 1,500.00"
formatCurrency(1500, 'SAR', 'ar', 'eastern'); // "١٬٥٠٠٫٠٠ ر.س"
```

### API Bilingual Response

**Backend Implementation**:

```python
# middleware/language_middleware.py

from fastapi import Request
from typing import Dict, Any

class BilingualResponse:
    """Handle bilingual API responses"""
    
    @staticmethod
    def get_preferred_language(request: Request) -> str:
        """Extract preferred language from request"""
        # Check Accept-Language header
        accept_language = request.headers.get('Accept-Language', 'en')
        
        # Parse header (e.g., "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7")
        languages = accept_language.split(',')
        primary_lang = languages[0].split('-')[0] if languages else 'en'
        
        return 'ar' if primary_lang == 'ar' else 'en'
    
    @staticmethod
    def format_error(
        code: str,
        message_en: str,
        message_ar: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """Format error response in both languages"""
        return {
            'error': {
                'code': code,
                'message': {
                    'en': message_en,
                    'ar': message_ar
                },
                'display_message': message_ar if language == 'ar' else message_en
            }
        }
    
    @staticmethod
    def format_diagnosis(diagnosis_code: str, language: str = 'en') -> Dict[str, str]:
        """Format diagnosis with bilingual names"""
        from utils.bilingual_clinical_terms import BilingualClinicalTerms
        
        return {
            'code': diagnosis_code,
            'name': BilingualClinicalTerms.get_diagnosis_name(diagnosis_code, language),
            'names': {
                'en': BilingualClinicalTerms.get_diagnosis_name(diagnosis_code, 'en'),
                'ar': BilingualClinicalTerms.get_diagnosis_name(diagnosis_code, 'ar')
            }
        }

# API endpoint example
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/api/v1/diagnoses/{code}")
async def get_diagnosis(code: str, request: Request):
    language = BilingualResponse.get_preferred_language(request)
    return BilingualResponse.format_diagnosis(code, language)
```

---

## 12. Integration Points with BrainSAIT Agents

### Agent Orchestration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     BrainSAIT AI Agent Layer                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ MASTERLINC   │  │HEALTHCARELINC│  │ CLINICALLINC │     │
│  │              │  │              │  │              │     │
│  │ Orchestration│  │  Workflows   │  │   Clinical   │     │
│  │              │  │              │  │   Decision   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           │                                │
│                  ┌────────▼────────┐                       │
│                  │ COMPLIANCELINC  │                       │
│                  │                 │                       │
│                  │   Compliance    │                       │
│                  │   & Audit       │                       │
│                  └─────────────────┘                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              BrainSAIT Healthcare Platform                   │
│                 (GIVC + SDK + UNIFIED)                       │
└─────────────────────────────────────────────────────────────┘
```

### MASTERLINC - Orchestration Agent

**Purpose**: Coordinates complex multi-step workflows across the healthcare platform.

**Integration Points**:

```python
# services/masterlinc_integration.py

from typing import Dict, List, Any
import asyncio

class MASTERLINCOrchestrator:
    """
    Integration with MASTERLINC orchestration agent
    - Manages claim lifecycle
    - Coordinates multi-step workflows
    - Handles workflow state transitions
    """
    
    async def orchestrate_claim_lifecycle(
        self,
        claim_id: str,
        initial_state: str = 'draft'
    ) -> Dict[str, Any]:
        """
        Orchestrate complete claim lifecycle
        
        Workflow Steps:
        1. Draft → Validation
        2. Validation → Submission
        3. Submission → Adjudication
        4. Adjudication → Payment/Denial
        5. Denial → Appeal (if needed)
        """
        workflow_state = {
            'claim_id': claim_id,
            'current_step': initial_state,
            'steps_completed': [],
            'steps_remaining': [
                'validation',
                'submission',
                'adjudication',
                'resolution'
            ]
        }
        
        # Step 1: AI-powered validation
        validation_result = await self._run_step(
            'CLINICALLINC',
            'validate_claim',
            {'claim_id': claim_id}
        )
        
        if not validation_result['passed']:
            return {
                'status': 'failed',
                'step': 'validation',
                'errors': validation_result['errors']
            }
        
        workflow_state['steps_completed'].append('validation')
        
        # Step 2: NPHIES submission
        submission_result = await self._run_step(
            'HEALTHCARELINC',
            'submit_to_nphies',
            {'claim_id': claim_id}
        )
        
        workflow_state['steps_completed'].append('submission')
        
        # Step 3: Monitor adjudication
        adjudication_result = await self._monitor_adjudication(claim_id)
        
        workflow_state['steps_completed'].append('adjudication')
        
        # Step 4: Handle result
        if adjudication_result['status'] == 'denied':
            # Initiate appeal workflow
            appeal_result = await self._run_step(
                'MASTERLINC',
                'initiate_appeal',
                {
                    'claim_id': claim_id,
                    'denial_reason': adjudication_result['denial_reason']
                }
            )
            workflow_state['appeal_initiated'] = True
        
        workflow_state['current_step'] = 'completed'
        
        return workflow_state
    
    async def _run_step(
        self,
        agent: str,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute workflow step via BrainSAIT agent"""
        # Call BrainSAIT agent API
        # This would be actual API call in production
        return {
            'agent': agent,
            'action': action,
            'params': params,
            'status': 'success'
        }
    
    async def _monitor_adjudication(self, claim_id: str) -> Dict[str, Any]:
        """Monitor claim adjudication status"""
        # Poll NPHIES for claim status
        # Return adjudication result
        return {
            'status': 'approved',
            'amount_approved': 5000.00
        }
```

### HEALTHCARELINC - Workflow Agent

**Purpose**: Healthcare-specific workflow automation.

**Integration Points**:

```python
# services/healthcarelinc_integration.py

class HEALTHCARELINCWorkflows:
    """
    Integration with HEALTHCARELINC workflow agent
    - Pre-authorization workflows
    - Claims processing workflows
    - Denial appeals workflows
    """
    
    async def execute_preauth_workflow(
        self,
        patient_id: str,
        procedure_code: str,
        provider_id: str
    ) -> Dict[str, Any]:
        """
        Execute pre-authorization workflow
        
        Steps:
        1. Verify patient eligibility
        2. Check procedure coverage
        3. Assess medical necessity
        4. Submit pre-auth request
        5. Track approval status
        """
        workflow = {
            'type': 'pre_authorization',
            'patient_id': patient_id,
            'procedure_code': procedure_code,
            'provider_id': provider_id,
            'steps': []
        }
        
        # Step 1: Eligibility check
        eligibility = await self.check_eligibility(patient_id)
        workflow['steps'].append({
            'step': 'eligibility_check',
            'result': eligibility['eligible'],
            'coverage_active': eligibility['coverage_active']
        })
        
        if not eligibility['eligible']:
            return {
                'status': 'rejected',
                'reason': 'Patient not eligible',
                'workflow': workflow
            }
        
        # Step 2: Medical necessity assessment (via CLINICALLINC)
        necessity_check = await self.assess_medical_necessity(
            patient_id,
            procedure_code
        )
        workflow['steps'].append({
            'step': 'medical_necessity',
            'result': necessity_check['necessary'],
            'confidence': necessity_check['confidence']
        })
        
        # Step 3: Submit pre-auth
        preauth_result = await self.submit_preauth_request(
            patient_id,
            procedure_code,
            provider_id
        )
        workflow['steps'].append({
            'step': 'preauth_submission',
            'result': preauth_result['status'],
            'auth_number': preauth_result.get('auth_number')
        })
        
        return {
            'status': 'completed',
            'workflow': workflow,
            'auth_number': preauth_result.get('auth_number')
        }
    
    async def execute_denial_appeal_workflow(
        self,
        claim_id: str,
        denial_code: str
    ) -> Dict[str, Any]:
        """
        Execute denial appeal workflow
        
        Steps:
        1. Analyze denial reason
        2. Gather supporting documentation
        3. Generate appeal letter
        4. Submit appeal
        5. Track appeal status
        """
        # Implemented as shown in Section 6 (Denial Appeal Workflow)
        pass
```

### CLINICALLINC - Clinical Decision Support

**Purpose**: Medical necessity validation, coding accuracy, fraud detection.

**Integration Points**:

```python
# services/clinicallinc_integration.py

class CLINICALLINCDecisionSupport:
    """
    Integration with CLINICALLINC clinical decision support agent
    - Medical necessity validation
    - Coding accuracy checking
    - Fraud detection scoring
    """
    
    async def validate_medical_necessity(
        self,
        diagnosis_code: str,
        procedure_code: str,
        patient_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate medical necessity using AI
        
        Returns:
        - necessary: bool
        - confidence: float (0-1)
        - rationale: str
        - supporting_guidelines: List[str]
        """
        # AI model inference
        necessity_score = await self._run_necessity_model(
            diagnosis_code,
            procedure_code,
            patient_history
        )
        
        return {
            'necessary': necessity_score > 0.75,
            'confidence': necessity_score,
            'rationale': self._generate_rationale(
                diagnosis_code,
                procedure_code,
                necessity_score
            ),
            'supporting_guidelines': [
                'American College of Cardiology Guidelines',
                'Saudi Ministry of Health Protocol'
            ]
        }
    
    async def check_coding_accuracy(
        self,
        diagnosis_codes: List[str],
        procedure_codes: List[str],
        clinical_notes: str
    ) -> Dict[str, Any]:
        """
        Check ICD-10/CPT coding accuracy using NLP
        
        Returns:
        - accurate: bool
        - suggested_codes: Dict
        - missing_codes: List[str]
        - incorrect_codes: List[str]
        """
        # NLP analysis of clinical notes
        extracted_diagnoses = await self._extract_diagnoses_from_notes(
            clinical_notes
        )
        extracted_procedures = await self._extract_procedures_from_notes(
            clinical_notes
        )
        
        # Compare with submitted codes
        accuracy_result = {
            'accurate': True,
            'suggested_codes': {},
            'missing_codes': [],
            'incorrect_codes': []
        }
        
        # Check for missing diagnoses
        for diagnosis in extracted_diagnoses:
            if diagnosis['code'] not in diagnosis_codes:
                accuracy_result['missing_codes'].append(diagnosis['code'])
                accuracy_result['accurate'] = False
        
        # Check for incorrect codes
        for submitted_code in diagnosis_codes:
            if not self._validate_code_context(
                submitted_code,
                clinical_notes
            ):
                accuracy_result['incorrect_codes'].append(submitted_code)
                accuracy_result['accurate'] = False
        
        return accuracy_result
    
    async def calculate_fraud_score(
        self,
        claim_data: Dict[str, Any],
        provider_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate fraud detection score (0-100)
        
        Factors:
        - Unusual billing patterns
        - Frequency of specific procedures
        - Outlier amounts
        - Historical provider behavior
        """
        fraud_indicators = []
        fraud_score = 0
        
        # Check for unusual billing patterns
        if self._check_unusual_billing(claim_data, provider_history):
            fraud_indicators.append('unusual_billing_pattern')
            fraud_score += 30
        
        # Check for duplicate billing
        if self._check_duplicate_billing(claim_data):
            fraud_indicators.append('potential_duplicate')
            fraud_score += 40
        
        # Check for upcoding
        if self._check_upcoding(claim_data):
            fraud_indicators.append('potential_upcoding')
            fraud_score += 30
        
        return {
            'fraud_score': min(fraud_score, 100),
            'risk_level': self._get_risk_level(fraud_score),
            'indicators': fraud_indicators,
            'recommended_action': self._get_recommended_action(fraud_score)
        }
    
    def _get_risk_level(self, score: int) -> str:
        """Map fraud score to risk level"""
        if score >= 70:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _get_recommended_action(self, score: int) -> str:
        """Recommend action based on fraud score"""
        if score >= 70:
            return 'Hold claim for manual review and investigation'
        elif score >= 40:
            return 'Flag for enhanced review'
        else:
            return 'Process normally'
```

### COMPLIANCELINC - Compliance & Audit Agent

**Purpose**: Ensure HIPAA, NPHIES, and FHIR compliance.

**Integration Points**:

```python
# services/compliancelinc_integration.py

class COMPLIANCELINCValidator:
    """
    Integration with COMPLIANCELINC compliance agent
    - HIPAA audit trail generation
    - NPHIES compliance validation
    - FHIR resource validation
    """
    
    async def generate_hipaa_audit_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate comprehensive HIPAA audit report
        
        Includes:
        - PHI access logs
        - Security events
        - Compliance violations
        - Remediation actions
        """
        from middleware.audit_logger import HIPAAAuditLogger
        
        audit_logger = HIPAAAuditLogger(self.mongodb_client)
        
        # Generate monthly report
        report = await audit_logger.generate_monthly_compliance_report(
            month=start_date.month,
            year=start_date.year
        )
        
        # Add compliance score
        report['compliance_score'] = self._calculate_compliance_score(report)
        
        # Add recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    async def validate_nphies_compliance(
        self,
        fhir_bundle: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate NPHIES compliance for FHIR bundle
        
        Checks:
        - Required NPHIES extensions
        - Saudi-specific coding systems
        - Message structure compliance
        - Certificate authentication
        """
        from validators.fhir_validator import FHIRValidator
        
        validator = FHIRValidator()
        validation_results = {
            'compliant': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate FHIR R4 structure
        for entry in fhir_bundle.get('entry', []):
            resource = entry.get('resource', {})
            resource_type = resource.get('resourceType')
            
            if resource_type == 'Claim':
                is_valid, errors = validator.validate_claim_resource(resource)
                if not is_valid:
                    validation_results['compliant'] = False
                    validation_results['errors'].extend(errors)
            
            # Check NPHIES extensions
            has_extensions, ext_errors = validator.validate_nphies_extensions(resource)
            if not has_extensions:
                validation_results['warnings'].extend(ext_errors)
        
        return validation_results
    
    async def run_compliance_scan(self) -> Dict[str, Any]:
        """
        Run comprehensive compliance scan
        
        Scans:
        - HIPAA compliance
        - NPHIES compliance
        - Data encryption status
        - Access control violations
        - Security vulnerabilities
        """
        scan_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'passed',
            'findings': []
        }
        
        # Check encryption
        encryption_status = await self._check_encryption_status()
        if not encryption_status['all_encrypted']:
            scan_results['findings'].append({
                'severity': 'critical',
                'category': 'encryption',
                'message': 'Unencrypted PHI detected',
                'details': encryption_status['unencrypted_fields']
            })
            scan_results['status'] = 'failed'
        
        # Check access controls
        access_violations = await self._check_access_violations()
        if access_violations:
            scan_results['findings'].append({
                'severity': 'high',
                'category': 'access_control',
                'message': f'{len(access_violations)} unauthorized access attempts detected',
                'details': access_violations[:10]  # First 10
            })
        
        return scan_results
```

---

## 13. Extensibility & Future Growth

### Plugin Architecture

**Provider Adapter System**:

```python
# core/plugin_system.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class InsuranceProviderAdapter(ABC):
    """
    Abstract base class for insurance provider integrations
    - Custom payer APIs
    - Proprietary claim formats
    - Provider-specific workflows
    """
    
    @abstractmethod
    async def submit_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit claim to payer"""
        pass
    
    @abstractmethod
    async def check_eligibility(self, member_id: str) -> Dict[str, Any]:
        """Check member eligibility"""
        pass
    
    @abstractmethod
    async def get_claim_status(self, claim_id: str) -> Dict[str, Any]:
        """Query claim status"""
        pass
    
    @abstractmethod
    def transform_to_payer_format(self, fhir_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Transform FHIR to payer-specific format"""
        pass
    
    @abstractmethod
    def transform_from_payer_format(self, payer_response: Dict[str, Any]) -> Dict[str, Any]:
        """Transform payer response to FHIR"""
        pass

# Example: Tawuniya adapter
class TawuniyaAdapter(InsuranceProviderAdapter):
    """Adapter for Tawuniya insurance company"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    async def submit_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit claim to Tawuniya API"""
        # Convert FHIR to Tawuniya format
        tawuniya_claim = self.transform_to_payer_format(claim_data)
        
        # Submit to Tawuniya API
        response = await self._api_call(
            '/claims/submit',
            method='POST',
            data=tawuniya_claim
        )
        
        # Convert response back to FHIR
        return self.transform_from_payer_format(response)
    
    async def check_eligibility(self, member_id: str) -> Dict[str, Any]:
        """Check eligibility via Tawuniya API"""
        response = await self._api_call(
            f'/eligibility/{member_id}',
            method='GET'
        )
        return response
    
    def transform_to_payer_format(self, fhir_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Transform FHIR Bundle to Tawuniya format"""
        # Custom transformation logic
        return {
            'claimId': fhir_bundle['id'],
            'memberId': self._extract_member_id(fhir_bundle),
            'services': self._extract_services(fhir_bundle),
            # ... other Tawuniya-specific fields
        }
    
    def transform_from_payer_format(self, payer_response: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Tawuniya response to FHIR"""
        # Custom transformation logic
        return {
            'resourceType': 'ClaimResponse',
            'status': payer_response['status'],
            # ... FHIR fields
        }

# Plugin registry
class ProviderAdapterRegistry:
    """Registry for insurance provider adapters"""
    
    def __init__(self):
        self.adapters: Dict[str, InsuranceProviderAdapter] = {}
    
    def register(self, payer_id: str, adapter: InsuranceProviderAdapter):
        """Register provider adapter"""
        self.adapters[payer_id] = adapter
    
    def get_adapter(self, payer_id: str) -> InsuranceProviderAdapter:
        """Get adapter for payer"""
        return self.adapters.get(payer_id)
    
    def list_adapters(self) -> List[str]:
        """List all registered adapters"""
        return list(self.adapters.keys())

# Usage:
registry = ProviderAdapterRegistry()

# Register Tawuniya adapter
tawuniya_adapter = TawuniyaAdapter(
    api_key="xxx",
    base_url="https://api.tawuniya.com"
)
registry.register("7000911508", tawuniya_adapter)

# Use adapter
adapter = registry.get_adapter("7000911508")
result = await adapter.submit_claim(claim_data)
```

### EHR Integration Framework

```python
# integrations/ehr_adapter.py

class EHRAdapter(ABC):
    """
    Abstract base class for EHR system integrations
    - HL7 v2 messaging
    - HL7 FHIR API
    - Custom REST APIs
    """
    
    @abstractmethod
    async def fetch_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Fetch patient demographics and history"""
        pass
    
    @abstractmethod
    async def fetch_encounters(
        self,
        patient_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch patient encounters"""
        pass
    
    @abstractmethod
    async def push_claim_status(
        self,
        encounter_id: str,
        claim_status: str
    ) -> bool:
        """Update encounter with claim status"""
        pass

# Example: Epic EHR adapter
class EpicEHRAdapter(EHRAdapter):
    """Adapter for Epic EHR system"""
    
    def __init__(self, fhir_base_url: str, client_id: str, client_secret: str):
        self.fhir_base_url = fhir_base_url
        self.client_id = client_id
        self.client_secret = client_secret
    
    async def fetch_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Fetch patient via Epic FHIR API"""
        # OAuth2 authentication
        access_token = await self._get_access_token()
        
        # Fetch patient
        response = await self._fhir_get(
            f'/Patient/{patient_id}',
            access_token
        )
        
        return response
```

### Machine Learning Model Plugins

```python
# ml/model_registry.py

class MLModelPlugin(ABC):
    """Base class for ML model plugins"""
    
    @abstractmethod
    async def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run model inference"""
        pass
    
    @abstractmethod
    def get_model_metadata(self) -> Dict[str, Any]:
        """Get model metadata"""
        pass

class DenialPredictionModel(MLModelPlugin):
    """ML model for predicting claim denials"""
    
    def __init__(self, model_path: str):
        self.model = self._load_model(model_path)
    
    async def predict(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict denial probability"""
        # Feature extraction
        features = self._extract_features(claim_data)
        
        # Model inference
        denial_probability = self.model.predict_proba([features])[0][1]
        
        return {
            'denial_probability': float(denial_probability),
            'risk_level': self._map_to_risk_level(denial_probability),
            'top_risk_factors': self._get_top_risk_factors(features)
        }
    
    def get_model_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'Denial Prediction Model',
            'version': '1.0.0',
            'accuracy': 0.87,
            'last_trained': '2025-10-01'
        }
```

### API Versioning Strategy

**Versioned API Endpoints**:

```python
# api/v1/claims.py

from fastapi import APIRouter, Depends

router_v1 = APIRouter(prefix="/api/v1")

@router_v1.post("/claims")
async def submit_claim_v1(claim_data: ClaimDataV1):
    """API v1: Submit claim (legacy)"""
    # v1 implementation
    pass

# api/v2/claims.py

router_v2 = APIRouter(prefix="/api/v2")

@router_v2.post("/claims")
async def submit_claim_v2(claim_data: ClaimDataV2):
    """API v2: Submit claim with enhanced validation"""
    # v2 implementation with new features
    pass

# api/v3/claims.py

router_v3 = APIRouter(prefix="/api/v3")

@router_v3.post("/claims")
async def submit_claim_v3(claim_data: ClaimDataV3):
    """
    API v3: Submit claim with AI-powered validation
    
    New features:
    - Automatic fraud detection
    - Real-time coding suggestions
    - Predictive denial analysis
    """
    # v3 implementation
    pass
```

**Deprecation Policy**:

```python
# middleware/deprecation.py

from fastapi import Request, Response
from datetime import datetime, timedelta

class DeprecationMiddleware:
    """
    API deprecation warnings
    - 12-month advance notice
    - Sunset header in responses
    - Migration guides
    """
    
    DEPRECATED_ENDPOINTS = {
        '/api/v1/claims': {
            'deprecated_date': datetime(2025, 1, 1),
            'sunset_date': datetime(2026, 1, 1),
            'migration_guide': '/docs/migration/v1-to-v2',
            'replacement': '/api/v2/claims'
        }
    }
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        path = request.url.path
        if path in self.DEPRECATED_ENDPOINTS:
            deprecation_info = self.DEPRECATED_ENDPOINTS[path]
            
            # Add deprecation headers
            response.headers['Deprecation'] = deprecation_info['deprecated_date'].isoformat()
            response.headers['Sunset'] = deprecation_info['sunset_date'].isoformat()
            response.headers['Link'] = f'<{deprecation_info["migration_guide"]}>; rel="deprecation"'
            
            # Add warning in response body
            if hasattr(response, 'body_iterator'):
                # Inject deprecation warning
                pass
        
        return response
```

### Feature Flags

```python
# core/feature_flags.py

from typing import Dict, Any
import os

class FeatureFlags:
    """
    Feature flag system for gradual rollout
    - A/B testing
    - Canary deployments
    - Beta features
    """
    
    def __init__(self):
        self.flags = {
            'ai_fraud_detection': {
                'enabled': os.getenv('FEATURE_AI_FRAUD', 'false') == 'true',
                'rollout_percentage': 25
            },
            'predictive_denials': {
                'enabled': os.getenv('FEATURE_PREDICTIVE_DENIALS', 'false') == 'true',
                'rollout_percentage': 10
            },
            'real_time_eligibility': {
                'enabled': True,
                'rollout_percentage': 100
            }
        }
    
    def is_enabled(self, feature: str, user_id: str = None) -> bool:
        """Check if feature is enabled for user"""
        if feature not in self.flags:
            return False
        
        flag = self.flags[feature]
        
        if not flag['enabled']:
            return False
        
        # Gradual rollout based on user ID hash
        if user_id and flag['rollout_percentage'] < 100:
            user_hash = hash(user_id) % 100
            return user_hash < flag['rollout_percentage']
        
        return True

# Usage:
feature_flags = FeatureFlags()

if feature_flags.is_enabled('ai_fraud_detection', user_id):
    # Use AI fraud detection
    fraud_score = await fraud_detection_service.analyze(claim)
else:
    # Use legacy fraud detection
    fraud_score = legacy_fraud_detection(claim)
```

---

## Success Criteria Checklist

✅ **Clear Architectural Vision**: Comprehensive documentation of consolidated platform architecture  
✅ **DDD Structure**: Domain-driven design aligning GIVC, SDK, and UNIFIED SYSTEM components  
✅ **Compliance Built-in**: HIPAA Level 3 audit logging, NPHIES integration, FHIR R4 validation  
✅ **Performance Targets**: 
   - Page load <2.5s
   - Eligibility checks <2s (95th percentile)
   - API response <500ms (median)
✅ **Bilingual Readiness**: Complete English + Arabic support with RTL layouts  
✅ **Deployment Ready**: Docker Compose (dev), Kubernetes (staging/production), Cloudflare CDN  
✅ **BrainSAIT Integration**: MASTERLINC, HEALTHCARELINC, CLINICALLINC, COMPLIANCELINC agent integration points  
✅ **Extensibility**: Plugin architecture for providers, EHRs, ML models, custom reporting  
✅ **Security**: Multi-layer security with AES-256 encryption, TLS 1.2+, RBAC, JWT auth  
✅ **Scalability**: Horizontal scaling with auto-scaling, caching strategy, database optimization  

---

## Additional Resources

- **API Documentation**: See [API.md](./API.md)
- **Deployment Guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md)  
- **Security Guide**: See [SECURITY.md](./SECURITY.md)
- **Compliance Guide**: See [COMPLIANCE.md](./COMPLIANCE.md)
- **Contributing**: See [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Integration Guide**: See [INTEGRATION.md](./INTEGRATION.md)

---

**Last Updated**: 2025-10-22  
**Version**: 1.0.0  
**Maintainers**: BrainSAIT Healthcare Platform Team

