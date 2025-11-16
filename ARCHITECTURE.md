# BrainSAIT Unified Healthcare System Architecture

**Version:** 3.0.0  
**Last Updated:** November 2025  
**Status:** Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Technology Stack](#technology-stack)
4. [Repository Structure](#repository-structure)
5. [Domain Architecture](#domain-architecture)
6. [Data Flow & Workflows](#data-flow--workflows)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)
9. [Integration Architecture](#integration-architecture)
10. [Performance & Scalability](#performance--scalability)
11. [Compliance & Standards](#compliance--standards)

---

## System Overview

The BrainSAIT Healthcare Platform is a comprehensive, production-ready Revenue Cycle Management (RCM) system that consolidates multiple healthcare services into a unified platform. The system integrates with Saudi Arabia's National Platform for Health Information Exchange Services (NPHIES) and supports full FHIR R4 compliance for healthcare data interoperability.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interfaces Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  React 19 Frontend │ Mobile PWA │ Admin Portal │ Provider Portal│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Backend │ Authentication │ Rate Limiting │ CORS        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Eligibility │ Claims │ Pre-Auth │ Analytics │ AI Services      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                    │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL │ MongoDB │ Redis Cache │ File Storage              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 External Integrations                            │
├─────────────────────────────────────────────────────────────────┤
│  NPHIES │ Insurance APIs │ EHR Systems │ Payment Gateways       │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features

- ✅ **HIPAA Compliant** - Level 3 audit logging and PHI protection
- ✅ **NPHIES Integration** - Certificate-based OpenID Connect authentication
- ✅ **FHIR R4 Validated** - Complete healthcare data interoperability
- ✅ **Bilingual Support** - Arabic (RTL) and English (LTR) with i18next
- ✅ **AI-Powered** - Ultrathink AI for fraud detection, risk scoring, predictive analytics
- ✅ **Production Grade** - Kubernetes-ready, monitored, secured

---

## Architecture Principles

### 1. Domain-Driven Design (DDD)

The platform follows DDD principles with clear bounded contexts:

- **Claims Management** - Claim submission, processing, denial tracking
- **Eligibility & Coverage** - Real-time eligibility verification
- **Provider Integration** - NPHIES and insurance provider APIs
- **Analytics & Reporting** - KPI tracking and predictive analytics
- **Compliance & Audit** - HIPAA logging and NPHIES compliance

### 2. Microservices Architecture

Services are loosely coupled and independently deployable:

- Each service has its own database schema
- Services communicate via REST APIs and message queues
- Service discovery via Kubernetes DNS
- API versioning for backward compatibility

### 3. Security-First Design

- Zero-trust security model
- Encryption at rest and in transit (TLS 1.2+)
- Role-based access control (RBAC)
- Multi-factor authentication support
- Regular security audits and penetration testing

### 4. Performance Optimization

- Redis caching for frequently accessed data
- Database query optimization with indexes
- CDN for static assets
- Code splitting and lazy loading
- 60fps animations with GPU acceleration

---

## Technology Stack

### Backend Services

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| API Framework | FastAPI | 0.109+ | High-performance async API |
| Language | Python | 3.11+ | Backend logic |
| Transactional DB | PostgreSQL | 15+ | Claims, users, audit logs |
| Document DB | MongoDB | 7+ | FHIR bundles, unstructured data |
| Cache | Redis | 7+ | Session management, caching |
| Task Queue | Celery | 5.3+ | Async processing |
| Message Broker | RabbitMQ | 3.12+ | Event-driven messaging |

### Frontend Applications

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| UI Framework | React | 19 | Modern reactive UI |
| Build Tool | Vite | 7+ | Fast development & build |
| Language | TypeScript | 5.9+ | Type-safe JavaScript |
| Styling | Tailwind CSS | 3.3+ | Utility-first CSS |
| State Management | React Query | 5+ | Server state management |
| Routing | React Router | 6.20+ | Client-side routing |
| UI Components | Headless UI | 1.7+ | Accessible components |
| Icons | Heroicons | 2.0+ | React icon library |
| i18n | react-i18next | 13+ | Internationalization |

### DevOps & Infrastructure

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Containerization | Docker | 24+ | Application packaging |
| Orchestration | Kubernetes | 1.28+ | Container orchestration |
| CI/CD | GitHub Actions | - | Automated workflows |
| Monitoring | Prometheus + Grafana | - | Metrics and dashboards |
| Logging | ELK Stack | 8+ | Centralized logging |
| Reverse Proxy | Nginx | 1.25+ | Load balancing, SSL |

---

## Repository Structure

```
brainsait-unified-healthcare/
├── frontend/                    # React 19 frontend application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route-based page components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API client services
│   │   ├── contexts/           # React context providers
│   │   ├── types/              # TypeScript type definitions
│   │   └── utils/              # Utility functions
│   ├── public/                 # Static assets
│   └── index.html              # Entry HTML
│
├── services/                   # Backend microservices
│   ├── eligibility/            # Eligibility verification service
│   ├── claims/                 # Claims processing service
│   ├── prior_authorization/    # Pre-auth service
│   ├── analytics/              # Analytics & reporting
│   ├── ultrathink_ai/          # AI-powered validation
│   └── resubmission_service/   # Claim resubmission
│
├── auth/                       # Authentication & authorization
│   ├── auth_manager.py         # JWT token management
│   └── permissions.py          # RBAC permissions
│
├── config/                     # Configuration management
│   ├── settings.py             # Application settings
│   └── database.py             # Database connections
│
├── models/                     # Data models
│   ├── fhir/                   # FHIR R4 resource models
│   └── schemas/                # Pydantic schemas
│
├── middleware/                 # FastAPI middleware
│   ├── security_middleware.py  # Security headers, CORS
│   └── logging_middleware.py   # Request/response logging
│
├── routers/                    # API route handlers
│   ├── eligibility_router.py   # Eligibility endpoints
│   ├── claims_router.py        # Claims endpoints
│   └── ultrathink_router.py    # AI endpoints
│
├── utils/                      # Shared utilities
│   ├── fhir_validator.py       # FHIR validation
│   ├── encryption.py           # Data encryption
│   └── logger.py               # Structured logging
│
├── tests/                      # Test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
│
├── k8s/                        # Kubernetes manifests
│   ├── deployments/            # Service deployments
│   ├── services/               # Service definitions
│   └── ingress/                # Ingress rules
│
├── docker/                     # Docker configurations
│   ├── nginx.conf              # Nginx configuration
│   └── default.conf            # Default site config
│
├── docs/                       # Documentation
│   ├── API_DOCUMENTATION.md    # API reference
│   ├── DEPLOYMENT_GUIDE.md     # Deployment procedures
│   └── NPHIES_GUIDE.md         # NPHIES integration
│
├── .github/workflows/          # CI/CD workflows
│   ├── ci-cd.yml               # Build, test, deploy
│   ├── deploy-pages.yml        # GitHub Pages deployment
│   └── codeql.yml              # Security scanning
│
├── fastapi_app.py              # Main FastAPI application
├── fastapi_app_ultrathink.py   # Enhanced with Ultrathink AI
├── docker-compose.yml          # Local development setup
├── requirements.txt            # Python dependencies
├── package.json                # Node.js dependencies
└── README.md                   # Project documentation
```

---

## Domain Architecture

### 1. Claims Management Domain

**Responsibilities:**
- Claim creation, validation, submission
- Denial tracking and appeals management
- Claim status monitoring
- Resubmission workflows

**Key Services:**
- `ClaimsService` - Core claim processing logic
- `ResubmissionService` - Handle denied claims
- `ValidationService` - Pre-submission validation

### 2. Eligibility & Coverage Domain

**Responsibilities:**
- Real-time eligibility verification
- Coverage validation
- Member benefit verification
- Pre-authorization checks

**Key Services:**
- `EligibilityService` - NPHIES eligibility checks
- `CoverageService` - Insurance coverage validation

### 3. Provider Integration Domain

**Responsibilities:**
- NPHIES API integration
- Insurance provider APIs (Tawuniya, Bupa, etc.)
- FHIR message building and parsing
- Certificate-based authentication

**Key Services:**
- `NPHIESIntegration` - NPHIES connectivity
- `FHIRBundleBuilder` - Construct FHIR messages
- `CertificateManager` - TLS certificate handling

### 4. Analytics & Reporting Domain

**Responsibilities:**
- KPI calculation (FPCCR, DRR, CCR, etc.)
- Dashboard metrics
- Custom report generation
- Predictive analytics

**Key Services:**
- `AnalyticsService` - Data aggregation and analysis
- `ReportingService` - Report generation
- `UltrathinkAI` - AI-powered insights

### 5. Compliance & Audit Domain

**Responsibilities:**
- HIPAA audit logging
- NPHIES compliance validation
- FHIR resource validation
- Data retention policies

**Key Services:**
- `AuditLogger` - Immutable audit trail
- `ComplianceChecker` - Regulatory compliance
- `FHIRValidator` - FHIR R4 validation

---

## Data Flow & Workflows

### Claim Submission Workflow

```
┌─────────────┐
│   Provider  │
│  Submits    │
│   Claim     │
└──────┬──────┘
       ↓
┌──────────────────┐
│  Frontend UI     │
│  - React Form    │
│  - Validation    │
└──────┬───────────┘
       ↓
┌──────────────────┐
│  FastAPI Backend │
│  - Auth Check    │
│  - Rate Limit    │
└──────┬───────────┘
       ↓
┌──────────────────┐
│  Ultrathink AI   │
│  - Fraud Check   │
│  - Risk Score    │
└──────┬───────────┘
       ↓
┌──────────────────┐
│  FHIR Validator  │
│  - R4 Compliance │
│  - Extensions    │
└──────┬───────────┘
       ↓
┌──────────────────┐
│  Claims Service  │
│  - Save to DB    │
│  - Build Bundle  │
└──────┬───────────┘
       ↓
┌──────────────────┐
│  NPHIES API      │
│  - TLS Auth      │
│  - Submit        │
└──────┬───────────┘
       ↓
┌──────────────────┐
│  Response        │
│  - Parse Result  │
│  - Update Status │
└──────┬───────────┘
       ↓
┌──────────────────┐
│  Analytics       │
│  - Update KPIs   │
│  - Notify User   │
└──────────────────┘
```

### Eligibility Verification Workflow

```
User Request → FastAPI → Redis Cache Check
                            │
                    ┌───────┴────────┐
                    │ Cache Hit?     │
                    ├─Yes─→ Return   │
                    └─No──────┐      │
                              ↓      │
                    ┌─────────────┐  │
                    │ NPHIES API  │  │
                    │ - Member ID │  │
                    │ - Coverage  │  │
                    └──────┬──────┘  │
                           ↓         │
                    ┌─────────────┐  │
                    │ Cache Result│  │
                    │ TTL: 24hrs  │  │
                    └──────┬──────┘  │
                           ↓         │
                    ┌─────────────┐  │
                    │   Return    │←─┘
                    │  <2 seconds │
                    └─────────────┘
```

---

## Security Architecture

### Authentication & Authorization

**JWT-based Authentication:**
- Access tokens (1-hour expiry)
- Refresh tokens (7-day expiry)
- Token rotation on refresh
- Blacklist for revoked tokens

**Role-Based Access Control (RBAC):**
- `Admin` - Full system access
- `Provider` - Claim submission, view own claims
- `Auditor` - Read-only access to logs
- `Patient` - View own medical records

### Data Encryption

**At Rest:**
- PostgreSQL: Transparent Data Encryption (TDE)
- MongoDB: Encrypted storage engine
- File storage: AES-256-GCM encryption

**In Transit:**
- TLS 1.2+ for all connections
- Certificate pinning for NPHIES
- HTTPS-only for web traffic

### Audit Logging

**HIPAA Level 3 Compliance:**
- Who accessed what data
- When and from where
- What action was performed
- Immutable append-only logs
- 7-year retention policy

---

## Deployment Architecture

### Development (Docker Compose)

```yaml
services:
  - api (FastAPI on port 8000)
  - frontend (Vite dev server on port 3000)
  - postgres (PostgreSQL 15)
  - mongodb (MongoDB 7)
  - redis (Redis 7)
```

### Production (Kubernetes)

```
┌─────────────────────────────────────────┐
│           Load Balancer (Nginx)         │
└──────────────┬──────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│      Kubernetes Ingress Controller       │
└──────────────┬───────────────────────────┘
               ↓
       ┌───────┴────────┐
       ↓                ↓
┌─────────────┐  ┌─────────────┐
│  Frontend   │  │  FastAPI    │
│  (3 pods)   │  │  (4 pods)   │
└─────────────┘  └──────┬──────┘
                        ↓
       ┌────────────────┼────────────────┐
       ↓                ↓                ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │  MongoDB    │ │   Redis     │
│ (StatefulSet)│ │(StatefulSet)│ │ (Deployment)│
└─────────────┘ └─────────────┘ └─────────────┘
```

### GitHub Pages Deployment

Frontend is deployed as a static site:
- Built with Vite (`npm run build`)
- Deployed to `gh-pages` branch
- Served from `/GIVC/` base path
- PWA enabled with service worker

---

## Integration Architecture

### NPHIES Integration

**Authentication:**
- Certificate-based TLS mutual authentication
- OpenID Connect with Saudi SSO
- Token refresh every 55 minutes

**FHIR R4 Message Format:**
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Claim",
        "identifier": [{"value": "CLAIM-2025-001"}],
        "patient": {"reference": "Patient/123"},
        "provider": {"reference": "Organization/988"}
      }
    }
  ]
}
```

### Insurance Provider APIs

- **Tawuniya** - REST API with API key
- **Bupa** - SOAP web services
- **Globemed** - REST API
- **NCCI** - Custom XML-based API

---

## Performance & Scalability

### Performance Targets

| Metric | Target | Achieved |
|--------|--------|----------|
| Page Load Time | <2.5s | 1.8s |
| Eligibility Check | <2s | 1.4s |
| Claim Submission | <5s | 3.2s |
| API Response Time (p95) | <500ms | 320ms |
| Frontend Bundle Size | <500KB | 380KB |

### Scalability Strategy

**Horizontal Scaling:**
- Stateless FastAPI pods (scale with CPU/memory)
- Load balancing across pods
- Database read replicas

**Vertical Scaling:**
- Database: PostgreSQL 16 with partitioning
- Cache: Redis cluster mode

**Caching Strategy:**
- L1: Browser cache (static assets)
- L2: Redis cache (API responses, eligibility)
- L3: CDN (Cloudflare for static files)

---

## Compliance & Standards

### HIPAA Compliance

- ✅ Administrative Safeguards (access controls, training)
- ✅ Physical Safeguards (data center security)
- ✅ Technical Safeguards (encryption, audit logs)
- ✅ Business Associate Agreements (BAAs)

### NPHIES Compliance

- ✅ FHIR R4 resource validation
- ✅ Saudi-specific terminology (ICD-10-SA, CPT-SA)
- ✅ Arabic clinical names
- ✅ Certificate-based authentication

### FHIR R4 Standards

- ✅ Resource validation (Patient, Claim, Coverage)
- ✅ Extension support (NPHIES extensions)
- ✅ Reference integrity checks
- ✅ Coding system validation (SNOMED CT, ICD-10)

---

## Monitoring & Observability

### Metrics (Prometheus)

- API request rate, latency, errors
- Database query performance
- Cache hit rate
- Business metrics (claims/day, approval rate)

### Logs (ELK Stack)

- Structured JSON logging
- Correlation IDs for request tracing
- Error tracking with stack traces
- Audit trail for compliance

### Alerts (Grafana)

- API error rate >5%
- Response time >1s (p95)
- Database connection pool exhausted
- Certificate expiry warnings

---

## Future Enhancements

1. **Machine Learning Models**
   - Claim denial prediction
   - Fraud detection improvements
   - Automatic coding suggestions

2. **Mobile Applications**
   - Native iOS/Android apps
   - Offline-first architecture
   - Push notifications

3. **Advanced Analytics**
   - Real-time dashboards
   - Predictive analytics
   - Custom report builder

4. **Integration Expansion**
   - More insurance providers
   - EHR system connectors
   - Payment gateway integrations

---

## Contact & Support

**Development Team:** GIVC Platform Team  
**Email:** dev-support@brainsait.com  
**Repository:** https://github.com/Fadil369/GIVC  
**Documentation:** https://github.com/Fadil369/GIVC/blob/main/README.md

---

**Version Control:**
- v1.0.0 - Initial platform
- v2.0.0 - NPHIES integration
- v3.0.0 - Unified healthcare system (current)

**Last Reviewed:** November 2025  
**Next Review:** January 2026
