# NPHIES Integration - Architecture & Data Flow

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your Healthcare Platform                      │
│  (Hospital Management System / Insurance Platform / Clinic)     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ API Calls / Data Requests
                     │
┌────────────────────▼────────────────────────────────────────────┐
│              NPHIES Integration Platform                         │
│                  (This Solution)                                 │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐         │
│  │   Services  │  │   Pipeline   │  │      Auth     │         │
│  │             │  │              │  │               │         │
│  │ • Eligib.   │  │ • Extractor  │  │ • Auth Mgr    │         │
│  │ • Claims    │  │ • Processor  │  │ • Cert Mgr    │         │
│  │ • Comm.     │  │              │  │               │         │
│  └─────────────┘  └──────────────┘  └───────────────┘         │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐         │
│  │   Models    │  │    Utils     │  │    Config     │         │
│  │             │  │              │  │               │         │
│  │ • Bundle    │  │ • Logger     │  │ • Settings    │         │
│  │   Builder   │  │ • Validators │  │ • Endpoints   │         │
│  │             │  │ • Helpers    │  │               │         │
│  └─────────────┘  └──────────────┘  └───────────────┘         │
│                                                                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ HTTPS / TLS 1.2+ / Certificate Auth
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                     NPHIES Portal                                │
│         (National Platform for Health Insurance)                │
│                                                                  │
│  • https://NPHIES.sa/api/fs/fhir/$process-message              │
│  • FHIR R4 Compliant                                            │
│  • Saudi Healthcare Integration                                 │
└──────────────────────────────────────────────────────────────────┘
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
