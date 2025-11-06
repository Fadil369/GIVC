# ClaimLinc API Documentation

## Overview

The ClaimLinc API is a comprehensive healthcare claims processing platform that provides normalized, validated, and automated claim submission services across multiple Saudi Arabian payers including Bupa Arabia, GlobeMed Saudi Arabia, and Tawuniya Insurance Company.

**Base URL:** `http://localhost:8000` (development)
**API Version:** v1.0.0
**Authentication:** API Key based authentication

## Quick Start

### Authentication

All API requests require authentication using API keys:

```bash
curl -H "Authorization: Bearer ck_bupa_abc123.secretkey" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/normalize
```

### Generate API Key

```bash
curl -X POST http://localhost:8000/api/v1/auth/generate-key \
     -H "Content-Type: application/json" \
     -d '{"service": "bupa", "permissions": ["read", "write"]}'
```

## Core Endpoints

### 1. Claim Normalization

Normalize raw claim data from various payer formats to a standard internal format.

#### POST `/api/v1/normalize`

Normalize a single claim to standard format.

**Request Body:**
```json
{
  "claim_data": {
    "claim_id": "BPA-2025-0001",
    "provider": {
      "name": "Al Hayat Hospital",
      "code": "AH001",
      "branch": "MainRiyadh"
    },
    "patient": {
      "member_id": "BP123456789",
      "name": "Ahmed Al-Rashid"
    },
    "claim_details": {
      "service_date": "2025-01-15",
      "total_amount": 12500.00,
      "currency": "SAR",
      "diagnosis_codes": ["I10", "E11.9"],
      "procedure_codes": ["99213", "36415"]
    }
  },
  "source_format": "bupa",
  "validation_required": true
}
```

**Response:**
```json
{
  "claim_id": "BPA-2025-0001",
  "normalized_data": {
    "claim_id": "BPA-2025-0001",
    "provider": {
      "name": "Al Hayat Hospital",
      "code": "AH001",
      "branch": "MainRiyadh"
    },
    "patient": {
      "member_id": "BP123456789",
      "name": "Ahmed Al-Rashid",
      "national_id": null,
      "date_of_birth": null,
      "gender": null
    },
    "claim_details": {
      "service_date": "2025-01-15T00:00:00",
      "admission_date": null,
      "discharge_date": null,
      "type": "outpatient",
      "total_amount": 12500.00,
      "currency": "SAR",
      "diagnosis_codes": ["I10", "E11.9"],
      "procedure_codes": ["99213", "36415"]
    },
    "payer": {
      "name": "Bupa Arabia",
      "insurance_type": "health",
      "policy_number": null
    },
    "submission": {
      "method": "portal",
      "timestamp": "2025-11-05T12:28:00Z",
      "batch_id": null,
      "status": "submitted"
    },
    "metadata": {
      "normalized_at": "2025-11-05T12:28:00Z",
      "source_format": "bupa",
      "validation_status": "validation_passed"
    }
  },
  "validation_result": {
    "claim_id": "BPA-2025-0001",
    "validation_status": "PASS",
    "validation_score": 100.0,
    "compliance_status": "COMPLIANT",
    "errors": [],
    "warnings": [],
    "recommendations": ["Claim data meets all validation requirements"],
    "data_quality_metrics": {
      "completeness_score": 80.0,
      "encoding_score": 100.0,
      "required_fields_filled": "4/5",
      "error_count": 0,
      "warning_count": 0
    }
  },
  "processing_time": 0.023,
  "source_format": "bupa",
  "metadata": {
    "processed_at": "2025-11-05T12:28:00Z",
    "api_version": "1.0.0"
  }
}
```

### 2. Claim Validation

Validate claim data for completeness, accuracy, and compliance.

#### POST `/api/v1/validate`

Validate claim data for quality and compliance.

**Request Body:**
```json
{
  "claim_id": "BPA-2025-0001",
  "provider": {
    "name": "Al Hayat Hospital",
    "code": "AH001",
    "branch": "MainRiyadh"
  },
  "patient": {
    "member_id": "BP123456789",
    "name": "Ahmed Al-Rashid"
  },
  "claim_details": {
    "service_date": "2025-01-15",
    "total_amount": 12500.00,
    "currency": "SAR"
  }
}
```

**Response:**
```json
{
  "claim_id": "BPA-2025-0001",
  "validation_status": "PASS",
  "validation_score": 100.0,
  "compliance_status": "COMPLIANT",
  "errors": [],
  "warnings": [],
  "recommendations": ["Claim data meets all validation requirements"],
  "data_quality_metrics": {
    "completeness_score": 80.0,
    "encoding_score": 100.0,
    "required_fields_filled": "4/5",
    "error_count": 0,
    "warning_count": 0
  },
  "validation_timestamp": "2025-11-05T12:28:00Z"
}
```

### 3. Batch Processing

Process multiple claims in a single request.

#### POST `/api/v1/batch`

Process multiple claims in batch.

**Request Body:**
```json
{
  "claims_data": [
    {
      "claim_id": "BPA-2025-0001",
      "provider": {"name": "Al Hayat Hospital", "code": "AH001"},
      "patient": {"member_id": "BP123456789", "name": "Ahmed Al-Rashid"},
      "claim_details": {"service_date": "2025-01-15", "total_amount": 12500.00}
    },
    {
      "claim_id": "GLB-2025-0002",
      "providerInfo": {"providerName": "Al Hayat Hospital", "providerCode": "AH001"},
      "subscriberInfo": {"memberId": "GM987654321", "memberName": "Fatima Al-Zahra"},
      "claimDetails": {"serviceDate": "2025-01-16", "totalAmount": 8900.00}
    }
  ],
  "source_format": "mixed",
  "validation_required": true
}
```

**Response:**
```json
{
  "total_claims": 2,
  "successfully_processed": 2,
  "failed": 0,
  "processing_time": 0.045,
  "results": [
    {
      "claim_id": "BPA-2025-0001",
      "normalized_data": { /* normalized claim 1 */ },
      "validation_result": { /* validation result 1 */ },
      "batch_index": 0
    },
    {
      "claim_id": "GLB-2025-0002",
      "normalized_data": { /* normalized claim 2 */ },
      "validation_result": { /* validation result 2 */ },
      "batch_index": 1
    }
  ],
  "summary_report": {
    "total_claims": 2,
    "successfully_processed": 2,
    "failed": 0,
    "success_rate": 100.0,
    "average_processing_time": 0.022
  }
}
```

### 4. Test Data Generation

Generate synthetic test data for development and testing.

#### POST `/api/v1/test-data/generate`

Generate synthetic test data.

**Request Body:**
```json
{
  "count": 10,
  "payer_format": "bupa",
  "include_rejection_cases": true
}
```

**Response:**
```json
{
  "generated_claims": 12,
  "claims": [
    {
      "claim_id": "BPA-2025-1105-1234",
      "provider": {
        "name": "Al Hayat Hospital",
        "code": "AH001",
        "branch": "MainRiyadh"
      },
      "patient": {
        "member_id": "BP123456789",
        "name": "Ahmed Al-Rashid",
        "national_id": "1234567890"
      },
      "claim_details": {
        "service_date": "2025-01-15",
        "total_amount": 12500.00,
        "currency": "SAR",
        "diagnosis_codes": ["I10", "E11.9"],
        "procedure_codes": ["99213", "36415"]
      }
    }
    // ... 11 more claims
  ],
  "report": "reports/summary_report_20251105_122827.json",
  "payer_format": "bupa",
  "generated_at": "2025-11-05T12:28:27Z"
}
```

### 5. Claim Submission

Submit processed claims to payer automation workflows.

#### POST `/api/v1/automation/submit/{payer}`

Submit claim to specific payer automation workflow.

**Path Parameters:**
- `payer` (string): Target payer (bupa, globemed, waseel)

**Request Body:**
```json
{
  "claim_id": "BPA-2025-0001",
  "provider": {
    "name": "Al Hayat Hospital",
    "code": "AH001",
    "branch": "MainRiyadh"
  },
  "patient": {
    "member_id": "BP123456789",
    "name": "Ahmed Al-Rashid"
  },
  "claim_details": {
    "service_date": "2025-01-15",
    "total_amount": 12500.00,
    "currency": "SAR"
  }
}
```

**Response:**
```json
{
  "status": "submitted",
  "payer": "bupa",
  "submission_id": "BUPA-20251105-a1b2c3d4",
  "normalized_claim": { /* normalized claim data */ },
  "validation_result": { /* validation result */ },
  "next_steps": [
    "Monitor submission status",
    "Check for rejections",
    "Review payment processing"
  ]
}
```

### 6. Workflow Status

Check status of submitted workflow.

#### GET `/api/v1/workflow/status/{submission_id}`

Check status of submitted workflow.

**Path Parameters:**
- `submission_id` (string): Submission ID returned from claim submission

**Response:**
```json
{
  "submission_id": "BUPA-20251105-a1b2c3d4",
  "status": "processing",
  "current_step": "claim_submission",
  "estimated_completion": "2-5 minutes",
  "next_steps": ["portal_login", "claim_upload", "confirmation"]
}
```

### 7. Data Export

Export processed claims to CSV format.

#### POST `/api/v1/export/csv`

Export claims to CSV format.

**Request Body:**
```json
{
  "claims_data": [ /* array of claim objects */ ],
  "filename": "export_claims_20251105.csv"
}
```

**Response:**
```json
{
  "export_result": "Successfully exported 10 normalized claims to ./exports/export_claims_20251105.csv",
  "file_path": "./exports/export_claims_20251105.csv",
  "download_url": "/api/v1/download/export_claims_20251105.csv",
  "generated_at": "2025-11-05T12:28:27Z"
}
```

#### GET `/api/v1/download/{filename}`

Download exported file.

### 8. Reports

Generate various analytical reports.

#### GET `/api/v1/reports/summary`

Generate and return summary report.

**Query Parameters:**
- `claims_data` (array): Array of claim objects to analyze

**Response:**
```json
{
  "report": {
    "report_metadata": {
      "report_type": "Summary Report",
      "generated_at": "2025-11-05T12:28:27Z",
      "total_claims": 10,
      "report_period": "2025-01-15 to 2025-01-25"
    },
    "financial_summary": {
      "total_amount": 125000.00,
      "average_amount": 12500.00,
      "currency": "SAR"
    },
    "distribution_analysis": {
      "payer_distribution": {
        "Bupa Arabia": 6,
        "GlobeMed Saudi Arabia": 4
      },
      "branch_distribution": {
        "MainRiyadh": 5,
        "Unaizah": 3,
        "Abha": 2
      },
      "claim_type_distribution": {
        "outpatient": 7,
        "inpatient": 3
      }
    }
  },
  "report_file": "reports/summary_report_20251105_122827.json",
  "generated_at": "2025-11-05T12:28:27Z"
}
```

## System Endpoints

### Health Check

#### GET `/health`

System health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T12:28:27Z",
  "services": {
    "normalizer": "operational",
    "validator": "operational",
    "test_generator": "operational"
  }
}
```

### System Statistics

#### GET `/api/v1/system/stats`

Get system statistics and health metrics.

**Response:**
```json
{
  "uptime": "Running",
  "memory_usage": "Normal",
  "processing_capacity": "Available",
  "supported_payers": ["bupa", "globemed", "waseel"],
  "api_version": "1.0.0",
  "endpoints_available": [
    "/api/v1/normalize",
    "/api/v1/validate",
    "/api/v1/batch",
    "/api/v1/test-data/generate",
    "/api/v1/automation/submit/{payer}",
    "/api/v1/export/csv"
  ],
  "timestamp": "2025-11-05T12:28:27Z"
}
```

### API Documentation

#### GET `/docs`

Interactive API documentation using Swagger UI.

#### GET `/redoc`

Alternative API documentation using ReDoc.

## Data Formats

### Supported Payer Formats

#### Bupa Arabia Format
```json
{
  "claim_id": "BPA-2025-0001",
  "provider": {
    "name": "Al Hayat Hospital",
    "code": "AH001",
    "branch": "MainRiyadh"
  },
  "patient": {
    "member_id": "BP123456789",
    "name": "Ahmed Al-Rashid",
    "national_id": "1234567890"
  },
  "claim_details": {
    "service_date": "2025-01-15",
    "total_amount": 12500.00,
    "currency": "SAR",
    "diagnosis_codes": ["I10", "E11.9"],
    "procedure_codes": ["99213", "36415"]
  }
}
```

#### GlobeMed Format
```json
{
  "claimId": "GLB-2025-0001",
  "providerInfo": {
    "providerCode": "AH001",
    "providerName": "Al Hayat Hospital",
    "branch": "MainRiyadh"
  },
  "subscriberInfo": {
    "memberId": "GM123456789",
    "memberName": "Ahmed Al-Rashid",
    "nationalId": "1234567890"
  },
  "claimDetails": {
    "serviceType": "outpatient",
    "serviceDate": "2025-01-15",
    "totalAmount": 12500.00,
    "currency": "SAR"
  },
  "diagnosisInformation": [
    {
      "sequence": 1,
      "diagnosisCode": "I10",
      "diagnosisDescription": "Essential hypertension"
    }
  ]
}
```

#### Waseel/Tawuniya FHIR Format
```json
{
  "resourceType": "Bundle",
  "id": "WSE-CLAIM-2025-0001",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Claim",
        "id": "WSE-2025-0001",
        "status": "active",
        "patient": {
          "reference": "Patient/P001",
          "display": "Ahmed Al-Rashid"
        },
        "provider": {
          "reference": "Organization/AH001",
          "display": "Al Hayat Hospital"
        },
        "total": {
          "value": 12500.00,
          "currency": "SAR"
        },
        "diagnosis": [
          {
            "sequence": 1,
            "diagnosisCodeableConcept": {
              "coding": [
                {
                  "system": "http://hl7.org/fhir/sid/icd-10",
                  "code": "I10",
                  "display": "Essential hypertension"
                }
              ]
            }
          }
        ]
      }
    }
  ]
}
```

### Standard Internal Format

All claims are normalized to this internal format:

```json
{
  "claim_id": "string",
  "provider": {
    "name": "string",
    "code": "string",
    "branch": "string"
  },
  "patient": {
    "member_id": "string",
    "name": "string",
    "national_id": "string",
    "date_of_birth": "string (ISO date)",
    "gender": "string (M/F)"
  },
  "claim_details": {
    "service_date": "string (ISO date)",
    "admission_date": "string (ISO date)",
    "discharge_date": "string (ISO date)",
    "type": "string (inpatient/outpatient/emergency/surgery/consultation)",
    "total_amount": "number",
    "currency": "string (SAR/USD/EUR)",
    "diagnosis_codes": ["array of strings"],
    "procedure_codes": ["array of strings"]
  },
  "payer": {
    "name": "string",
    "insurance_type": "string",
    "policy_number": "string"
  },
  "submission": {
    "method": "string (portal/api)",
    "timestamp": "string (ISO timestamp)",
    "batch_id": "string",
    "status": "string"
  },
  "metadata": {
    "normalized_at": "string (ISO timestamp)",
    "source_format": "string",
    "validation_status": "string"
  }
}
```

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "error": "Error Type",
  "detail": "Detailed error message",
  "timestamp": "2025-11-05T12:28:27Z",
  "request_id": "req_123456789"
}
```

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (validation errors, invalid format)
- `401` - Unauthorized (invalid or missing API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource not found)
- `422` - Unprocessable Entity (validation failed)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable

### Common Error Scenarios

#### Validation Error (400)
```json
{
  "error": "Validation Error",
  "detail": "Missing required field: patient.member_id",
  "timestamp": "2025-11-05T12:28:27Z",
  "request_id": "req_123456789"
}
```

#### Authentication Error (401)
```json
{
  "error": "Authentication Error",
  "detail": "Invalid or missing API key",
  "timestamp": "2025-11-05T12:28:27Z",
  "request_id": "req_123456789"
}
```

#### Rate Limit Error (429)
```json
{
  "error": "Rate Limit Exceeded",
  "detail": "Too many requests. Rate limit: 100 requests per minute",
  "timestamp": "2025-11-05T12:28:27Z",
  "request_id": "req_123456789"
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Requests per minute:** 100
- **Burst limit:** 10 requests
- **Rate limit headers** are included in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets

## SDK Examples

### Python SDK Example

```python
import requests
import json

class ClaimLincClient:
    def __init__(self, api_key, base_url="http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def normalize_claim(self, claim_data, source_format="bupa"):
        """Normalize a single claim"""
        payload = {
            "claim_data": claim_data,
            "source_format": source_format,
            "validation_required": True
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/normalize",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.json()}")
    
    def batch_process(self, claims_data, source_format="mixed"):
        """Process multiple claims in batch"""
        payload = {
            "claims_data": claims_data,
            "source_format": source_format,
            "validation_required": True
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/batch",
            headers=self.headers,
            json=payload
        )
        
        return response.json()
    
    def submit_to_payer(self, payer, claim_data):
        """Submit claim to payer automation"""
        response = requests.post(
            f"{self.base_url}/api/v1/automation/submit/{payer}",
            headers=self.headers,
            json=claim_data
        )
        
        return response.json()

# Usage example
client = ClaimLincClient("ck_bupa_abc123.secretkey")

# Normalize a claim
claim = {
    "claim_id": "BPA-2025-0001",
    "provider": {"name": "Al Hayat Hospital", "code": "AH001"},
    "patient": {"member_id": "BP123456789", "name": "Ahmed Al-Rashid"},
    "claim_details": {"service_date": "2025-01-15", "total_amount": 12500.00}
}

normalized = client.normalize_claim(claim, "bupa")
print(f"Normalized claim ID: {normalized['claim_id']}")

# Submit to Bupa automation
submission = client.submit_to_payer("bupa", normalized['normalized_data'])
print(f"Submission ID: {submission['submission_id']}")
```

### JavaScript/Node.js SDK Example

```javascript
class ClaimLincClient {
    constructor(apiKey, baseUrl = 'http://localhost:8000') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async normalizeClaim(claimData, sourceFormat = 'bupa') {
        const payload = {
            claim_data: claimData,
            source_format: sourceFormat,
            validation_required: true
        };
        
        const response = await fetch(`${this.baseUrl}/api/v1/normalize`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(`Error: ${await response.text()}`);
        }
    }
    
    async batchProcess(claimsData, sourceFormat = 'mixed') {
        const payload = {
            claims_data: claimsData,
            source_format: sourceFormat,
            validation_required: true
        };
        
        const response = await fetch(`${this.baseUrl}/api/v1/batch`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    }
    
    async submitToPayer(payer, claimData) {
        const response = await fetch(`${this.baseUrl}/api/v1/automation/submit/${payer}`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(claimData)
        });
        
        return await response.json();
    }
}

// Usage example
const client = new ClaimLincClient('ck_bupa_abc123.secretkey');

const claim = {
    claim_id: 'BPA-2025-0001',
    provider: { name: 'Al Hayat Hospital', code: 'AH001' },
    patient: { member_id: 'BP123456789', name: 'Ahmed Al-Rashid' },
    claim_details: { service_date: '2025-01-15', total_amount: 12500.00 }
};

client.normalizeClaim(claim, 'bupa')
    .then(normalized => {
        console.log(`Normalized claim ID: ${normalized.claim_id}`);
        return client.submitToPayer('bupa', normalized.normalized_data);
    })
    .then(submission => {
        console.log(`Submission ID: ${submission.submission_id}`);
    })
    .catch(error => {
        console.error('Error:', error);
    });
```

## Integration Examples

### Complete Workflow Example

```python
import json
from claimlinc_client import ClaimLincClient

def process_claims_workflow(claims_file):
    """Complete workflow from raw claims to submission"""
    
    # Initialize client
    client = ClaimLincClient("ck_bupa_abc123.secretkey")
    
    # Load raw claims
    with open(claims_file, 'r') as f:
        raw_claims = json.load(f)
    
    # Step 1: Detect formats and batch process
    print("Step 1: Batch processing claims...")
    batch_result = client.batch_process(raw_claims, "mixed")
    
    print(f"Processed {batch_result['successfully_processed']} out of {batch_result['total_claims']} claims")
    
    # Step 2: Filter successful claims
    successful_claims = []
    failed_claims = []
    
    for result in batch_result['results']:
        if 'error' not in result:
            successful_claims.append(result['normalized_data'])
        else:
            failed_claims.append(result)
    
    # Step 3: Export successful claims
    if successful_claims:
        print("Step 2: Exporting successful claims...")
        export_result = client.export_to_csv(successful_claims, "processed_claims.csv")
        print(f"Exported to: {export_result['file_path']}")
    
    # Step 4: Submit to payers
    print("Step 3: Submitting claims to payers...")
    submission_results = []
    
    for claim in successful_claims:
        # Determine payer from normalized data
        payer_name = claim.get('payer', {}).get('name', '').lower()
        
        if 'bupa' in payer_name:
            payer = 'bupa'
        elif 'globemed' in payer_name:
            payer = 'globemed'
        elif 'tawuniya' in payer_name or 'waseel' in payer_name:
            payer = 'waseel'
        else:
            print(f"Unknown payer for claim {claim['claim_id']}")
            continue
        
        try:
            submission = client.submit_to_payer(payer, claim)
            submission_results.append(submission)
            print(f"Submitted {claim['claim_id']} to {payer}")
        except Exception as e:
            print(f"Failed to submit {claim['claim_id']}: {str(e)}")
    
    # Step 5: Generate summary report
    print("Step 4: Generating summary report...")
    summary = {
        'total_processed': len(raw_claims),
        'successful': len(successful_claims),
        'failed': len(failed_claims),
        'submissions': len(submission_results),
        'failure_reasons': [f['error'] for f in failed_claims if 'error' in f]
    }
    
    print(f"Workflow complete: {json.dumps(summary, indent=2)}")
    return summary

# Run the workflow
if __name__ == "__main__":
    results = process_claims_workflow("sample_claims.json")
```

## Support and Resources

### Interactive Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example Files
- Sample claims: `/tests/sample-data/`
- Test scripts: `/examples/`

### Monitoring and Logs
- Health check: `GET /health`
- System stats: `GET /api/v1/system/stats`
- Audit logs: `/config/security/audit.log`

### Getting Help
- Check the interactive API documentation
- Review error messages for specific details
- Ensure API key has proper permissions
- Verify claim data format matches expected structure

---

**API Version:** 1.0.0  
**Last Updated:** 2025-11-05  
**Contact:** ClaimLinc Support Team
