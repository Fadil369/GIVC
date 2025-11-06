# NPHIES Integration Specification

**Version:** 1.0  
**Phase:** 3 - NPHIES Sandbox Integration  
**Owner:** Integration Team & Compliance Office  
**Status:** Implementation Ready  
**NPHIES IG Version:** v0.4.0

---

## 📋 Overview

This document specifies the integration architecture for Saudi Arabia's National Platform for Health Information Exchange (NPHIES), ensuring full compliance with FHIR R4 profiles, mTLS security requirements, and PDPL data protection standards.

---

## 🎯 Integration Objectives

| Objective | Description | Compliance |
|:----------|:------------|:-----------|
| **Eligibility Verification** | Real-time insurance coverage checks | NPHIES IG §3.2 |
| **Pre-Authorization** | Submit and track prior authorization requests | NPHIES IG §3.3 |
| **Claim Submission** | Submit professional and institutional claims | NPHIES IG §3.4 |
| **Payment Reconciliation** | Track and reconcile payments | NPHIES IG §3.6 |
| **Audit Trail** | Complete transaction logging | PDPL Art 17 |

---

## 🏗️ Architecture

### Integration Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    ClaimLinc-GIVC FastAPI                       │
│                  (FHIR Resource Builder)                        │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼ JWT + mTLS
┌────────────────────────────────────────────────────────────────┐
│                      NPHIES Gateway                             │
│                (Saudi MOH/CCHI Platform)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Endpoints:                                               │  │
│  │ - POST /EligibilityRequest                               │  │
│  │ - POST /CoverageEligibilityRequest                       │  │
│  │ - POST /Claim                                            │  │
│  │ - POST /ClaimResponse                                    │  │
│  │ - GET  /PaymentReconciliation                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Payer Systems  │
                    │  (Bupa, etc.)   │
                    └─────────────────┘
```

---

## 🔐 Security Implementation

### mTLS Configuration

**Client Certificate Requirements:**
- X.509 v3 certificate issued by NPHIES CA
- Key size: RSA 2048-bit minimum
- Validity: 1 year maximum
- Subject DN must include organization identifier

**Certificate Storage:**
- Certificates stored in Vault PKI engine
- Automatic renewal 30 days before expiry
- Certificate rotation without service interruption

### JWT Authentication

**Token Structure:**
```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "nphies-signing-key-001"
}
{
  "iss": "https://claimlinc.brainsait.io",
  "sub": "provider-license-12345",
  "aud": "https://nphies.sa",
  "exp": 1699456789,
  "iat": 1699453189,
  "jti": "unique-token-id",
  "scope": "eligibility claim payment"
}
```

**Signing:**
- Algorithm: RS256
- Private key stored in Vault
- Token TTL: 60 minutes
- No token reuse allowed

---

## 📦 FHIR Resource Profiles

### EligibilityRequest (v0.4.0)

**Profile:** `http://nphies.sa/fhir/ksa/nphies-fs/StructureDefinition/eligibility-request`

**Required Elements:**
```json
{
  "resourceType": "CoverageEligibilityRequest",
  "id": "eligibility-{{uuid}}",
  "meta": {
    "profile": ["http://nphies.sa/fhir/ksa/nphies-fs/StructureDefinition/eligibility-request"]
  },
  "identifier": [{
    "system": "http://claimlinc.brainsait.io/eligibility-request",
    "value": "ELG-{{timestamp}}-{{sequence}}"
  }],
  "status": "active",
  "purpose": ["benefits"],
  "patient": {
    "reference": "Patient/{{patient-id}}"
  },
  "servicedDate": "{{date}}",
  "created": "{{timestamp}}",
  "provider": {
    "reference": "Organization/{{provider-id}}"
  },
  "insurer": {
    "reference": "Organization/{{payer-id}}"
  },
  "insurance": [{
    "focal": true,
    "coverage": {
      "reference": "Coverage/{{coverage-id}}"
    }
  }]
}
```

### Claim (v0.4.0)

**Profile:** `http://nphies.sa/fhir/ksa/nphies-fs/StructureDefinition/claim`

**Required Elements:**
```json
{
  "resourceType": "Claim",
  "id": "claim-{{uuid}}",
  "meta": {
    "profile": ["http://nphies.sa/fhir/ksa/nphies-fs/StructureDefinition/claim"]
  },
  "identifier": [{
    "system": "http://claimlinc.brainsait.io/claim",
    "value": "CLM-{{timestamp}}-{{sequence}}"
  }],
  "status": "active",
  "type": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/claim-type",
      "code": "professional"
    }]
  },
  "use": "claim",
  "patient": {
    "reference": "Patient/{{patient-id}}"
  },
  "created": "{{timestamp}}",
  "provider": {
    "reference": "Organization/{{provider-id}}"
  },
  "priority": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/processpriority",
      "code": "normal"
    }]
  },
  "insurance": [{
    "sequence": 1,
    "focal": true,
    "coverage": {
      "reference": "Coverage/{{coverage-id}}"
    }
  }],
  "item": [
    {
      "sequence": 1,
      "productOrService": {
        "coding": [{
          "system": "http://nphies.sa/terminology/CodeSystem/services",
          "code": "{{service-code}}"
        }]
      },
      "servicedDate": "{{service-date}}",
      "unitPrice": {
        "value": {{amount}},
        "currency": "SAR"
      },
      "net": {
        "value": {{total}},
        "currency": "SAR"
      }
    }
  ],
  "total": {
    "value": {{total-amount}},
    "currency": "SAR"
  }
}
```

---

## 🔄 Transaction Workflows

### Eligibility Check Workflow

```
1. Build Patient + Coverage resources
2. Create EligibilityRequest with references
3. Sign JWT with nphies-signing-key
4. Establish mTLS connection
5. POST to /CoverageEligibilityRequest
6. Receive EligibilityResponse (sync)
7. Parse coverage details and limitations
8. Store response with correlation ID
9. Log audit event (PDPL compliance)
```

**Expected Response Time:** < 5 seconds  
**Retry Policy:** 3 attempts, 5-second intervals  
**Idempotency:** Request ID in identifier field

### Claim Submission Workflow

```
1. Validate eligibility (prerequisite)
2. Build Claim Bundle with:
   - Claim resource
   - Patient resource
   - Coverage resource
   - Organization (provider) resource
   - Practitioner resource (if applicable)
   - Supporting documentation (if required)
3. Sign JWT
4. Establish mTLS connection
5. POST Bundle to /Claim
6. Receive Claim acknowledgment (async possible)
7. If async: Schedule polling task
8. Store claim reference and correlation ID
9. Log audit event
```

**Expected Response Time:** < 30 seconds (sync), 5-30 minutes (async)  
**Retry Policy:** 5 attempts, exponential backoff  
**Idempotency:** Claim identifier + hash of content

### Polling for Async Responses

```
1. Wait initial interval (5 minutes)
2. GET /ClaimResponse?identifier={{claim-id}}
3. Check response status:
   - "pending": Retry after interval
   - "complete": Process adjudication
   - "error": Handle rejection
4. Max polling attempts: 20 (100 minutes total)
5. On timeout: Send to DLQ for manual review
```

---

## 🧪 Testing & Validation

### Sandbox Environment

**Endpoint:** `https://sandbox.nphies.sa/fhir`  
**Authentication:** Sandbox credentials from CCHI  
**Certificate:** Sandbox-specific certificate chain

### Test Scenarios

| Test Case | Description | Expected Result |
|:----------|:------------|:----------------|
| **ELG-001** | Valid eligibility request | Active coverage returned |
| **ELG-002** | Invalid member ID | OperationOutcome with error |
| **ELG-003** | Expired coverage | Inactive coverage status |
| **CLM-001** | Valid professional claim | Claim accepted (ACK) |
| **CLM-002** | Claim exceeds coverage limits | Partial rejection |
| **CLM-003** | Missing required fields | Validation error |
| **CLM-004** | Duplicate claim submission | Idempotent response |
| **SEC-001** | Invalid JWT signature | 401 Unauthorized |
| **SEC-002** | Expired certificate | TLS handshake failure |

### Conformance Validation

**Validator:** HAPI FHIR Validator v6.2.0  
**Profiles:** NPHIES IG v0.4.0 package  
**Validation Level:** Strict (no warnings ignored)

**Validation Script:**
```bash
java -jar validator_cli.jar \
  -version 4.0.1 \
  -ig nphies-ig-0.4.0.tgz \
  -profile http://nphies.sa/fhir/ksa/nphies-fs/StructureDefinition/claim \
  claim-example.json
```

---

## 📊 Monitoring & Metrics

### Key Performance Indicators

| Metric | Target | Alert Threshold |
|:-------|:-------|:----------------|
| Eligibility Success Rate | > 99% | < 95% |
| Claim Submission Success | > 98% | < 95% |
| Average Response Time | < 10s | > 30s |
| Certificate Expiry | > 30 days | < 7 days |
| Token Generation Failures | 0 | > 5/hour |

### Audit Logging

**Log Format:**
```json
{
  "timestamp": "2025-11-05T10:30:45.123Z",
  "correlation_id": "uuid-v4",
  "event_type": "nphies_eligibility_request",
  "patient_id": "hashed",
  "payer_code": "7001071327",
  "request_id": "ELG-20251105-001",
  "response_status": "success",
  "response_time_ms": 1234,
  "errors": []
}
```

**Retention:** 6 years (HIPAA/PDPL requirement)  
**Storage:** Encrypted at rest in `logs/audit/nphies/`

---

## ✅ Compliance Checklist

- [ ] FHIR R4 resources validate against NPHIES v0.4.0 profiles
- [ ] mTLS certificates issued and stored in Vault
- [ ] JWT signing keys rotated quarterly
- [ ] All transactions logged with correlation IDs
- [ ] PHI encrypted in transit (TLS 1.3) and at rest (AES-256)
- [ ] Consent obtained and recorded per PDPL Art 14
- [ ] Data minimization enforced (only required fields)
- [ ] Retention policy enforced (6-year audit logs)
- [ ] Incident response plan includes NPHIES outage scenarios
- [ ] Monthly conformance testing against sandbox

---

## 📚 References

* [NPHIES Implementation Guide v0.4.0](https://nphies.sa/ImplementationGuide/)
* [FHIR R4 Specification](https://www.hl7.org/fhir/R4/)
* [Saudi PDPL Law](https://sdaia.gov.sa/en/PDPL/Pages/default.aspx)
* [CCHI Provider Guidelines](https://www.cchi.gov.sa/)

---

**Last Updated:** 2025-11-05  
**Next Review:** 2025-12-05  
**Document Owner:** Integration Team
