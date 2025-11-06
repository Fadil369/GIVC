# ClaimLinc-GIVC Compliance Audit Trail

**Version:** 1.0  
**Phase:** 4 - Audit Readiness & Governance  
**Last Updated:** 2025-11-06

---

## 📋 Purpose

This directory maintains comprehensive audit evidence for HIPAA §164.308/312 and Saudi PDPL Art 14-17 compliance, supporting regulatory audits and internal governance reviews.

---

## 📁 Directory Structure

```
audit-trail/
├── README.md (this file)
├── policies/
│   ├── access-control-policy.md
│   ├── data-retention-policy.md
│   ├── incident-response-policy.md
│   └── change-management-policy.md
├── evidence/
│   ├── vault-rotation-logs/
│   ├── access-reviews/
│   ├── security-assessments/
│   └── compliance-reports/
├── governance/
│   ├── governance-calendar.md
│   ├── escalation-matrix.md
│   ├── committee-minutes/
│   └── sign-offs/
└── tests/
    ├── dr-test-results/
    ├── penetration-test-reports/
    └── conformance-test-reports/
```

---

## 🔐 Compliance Control Mapping

| Control Domain | Evidence Location | Retention Period |
|:---------------|:------------------|:-----------------|
| **HIPAA §164.308(a)(1)** - Security Management | `evidence/security-assessments/` | 6 years |
| **HIPAA §164.308(a)(3)** - Workforce Security | `evidence/access-reviews/` | 6 years |
| **HIPAA §164.308(a)(4)** - Information Access | `policies/access-control-policy.md` | 6 years |
| **HIPAA §164.312(a)(1)** - Access Control | `evidence/vault-rotation-logs/` | 6 years |
| **HIPAA §164.312(b)** - Audit Controls | System audit logs (Vault, RabbitMQ, NPHIES) | 6 years |
| **HIPAA §164.312(e)** - Transmission Security | TLS configs, certificate audits | 6 years |
| **PDPL Art 14** - Consent Management | FHIR Consent resources in NPHIES logs | 6 years |
| **PDPL Art 15** - Data Minimization | Schema reviews, field mapping docs | 6 years |
| **PDPL Art 16** - Data Quality | Validation test results | 6 years |
| **PDPL Art 17** - Retention & Deletion | `policies/data-retention-policy.md` | Permanent |

---

## 📊 Audit Log Collection

### System Audit Logs

| System | Log Location | Format | Collection Method |
|:-------|:------------|:-------|:------------------|
| **Vault** | `/var/log/vault/audit.log` | JSON | Daily export to S3/Azure Blob |
| **RabbitMQ** | `/var/log/rabbitmq/audit.log` | JSON | Daily export |
| **Redis** | `/var/log/redis/commands.log` | AOF | Retained on replica |
| **Celery** | `/var/log/celery/worker.log` | JSON | Centralized logging (ELK) |
| **NPHIES** | `logs/audit/nphies/` | JSON | Per-transaction logging |
| **FastAPI** | `/var/log/claimlinc/api.log` | JSON | Centralized logging |

### Audit Log Schema

```json
{
  "timestamp": "2025-11-06T10:30:45.123Z",
  "correlation_id": "uuid-v4",
  "event_type": "vault_secret_access | nphies_request | claim_submission",
  "actor": {
    "user_id": "hashed",
    "role": "celery_worker | api_service",
    "ip_address": "hashed"
  },
  "resource": {
    "type": "secret | claim | patient_data",
    "id": "hashed",
    "action": "read | write | delete"
  },
  "outcome": "success | failure",
  "details": { ... }
}
```

---

## 🗓️ Governance Calendar

### Recurring Activities

| Activity | Frequency | Owner | Last Completed | Next Due |
|:---------|:----------|:------|:---------------|:---------|
| **Vault Secret Rotation** | Monthly | Security Eng. | 2025-11-01 | 2025-12-01 |
| **Access Rights Review** | Quarterly | Security Eng. + HR | 2025-10-15 | 2026-01-15 |
| **DR Test Execution** | Quarterly | DevOps + SRE | 2025-10-20 | 2026-01-20 |
| **Compliance Audit** | Annual | Compliance Office | 2025-01-10 | 2026-01-10 |
| **Penetration Testing** | Annual | External Auditor | 2025-03-15 | 2026-03-15 |
| **Policy Review** | Annual | PMO + Legal | 2025-06-01 | 2026-06-01 |
| **NPHIES Conformance Test** | Monthly | Integration Team | 2025-11-01 | 2025-12-01 |
| **Certificate Renewal** | As needed | Security Eng. | N/A | Monitor alerts |

---

## 🚨 Incident Response & Escalation

### Severity Levels

| Severity | Definition | Response Time | Escalation Path |
|:---------|:-----------|:-------------|:----------------|
| **Critical** | PHI breach, system outage, NPHIES failure | < 15 min | Security Lead → CISO → CEO |
| **High** | Vault seal, auth failure, data corruption | < 1 hour | Team Lead → Security Lead |
| **Medium** | Performance degradation, queue backlog | < 4 hours | On-call Engineer → Team Lead |
| **Low** | Non-critical warnings, cert expiry alerts | < 24 hours | Team Lead |

### Incident Log Template

**Location:** `evidence/incidents/YYYY-MM-DD-incident-NNN.md`

```markdown
# Incident Report: [Title]

**Incident ID:** INC-YYYYMMDD-NNN  
**Severity:** Critical | High | Medium | Low  
**Detected:** YYYY-MM-DD HH:MM:SS UTC  
**Resolved:** YYYY-MM-DD HH:MM:SS UTC  
**Duration:** X hours Y minutes

## Summary
Brief description of the incident.

## Impact
- Systems affected
- Users/transactions impacted
- Data integrity status

## Root Cause
Technical root cause analysis.

## Resolution
Steps taken to resolve.

## Prevention
Measures to prevent recurrence.

## Evidence
- Logs: [link]
- Metrics: [link]
- Communications: [link]

**Approved By:** [Name], [Title]  
**Date:** YYYY-MM-DD
```

---

## ✅ Compliance Checklist (Quarterly Review)

### HIPAA §164.308 - Administrative Safeguards

- [ ] Risk assessment conducted and documented
- [ ] Security policies reviewed and updated
- [ ] Workforce security training completed
- [ ] Access authorization reviews performed
- [ ] Contingency plan tested
- [ ] Business associate agreements current

### HIPAA §164.312 - Technical Safeguards

- [ ] Unique user identification enforced (AppRole, JWT)
- [ ] Emergency access procedures documented
- [ ] Automatic logoff configured (token expiry)
- [ ] Encryption verified (TLS 1.3, AES-256)
- [ ] Audit log integrity validated
- [ ] Transmission security tested (mTLS)

### PDPL Compliance

- [ ] Consent mechanisms validated (FHIR Consent)
- [ ] Data minimization enforced (schema review)
- [ ] Retention policies applied
- [ ] Data subject rights procedures tested
- [ ] Cross-border transfer controls reviewed
- [ ] Privacy impact assessment updated

---

## 📈 Metrics & KPIs

### Security Metrics

| Metric | Target | Current | Trend |
|:-------|:-------|:--------|:------|
| Vault Token Rotation Success | 100% | TBD | N/A |
| Failed Authentication Attempts | < 5/day | TBD | N/A |
| Audit Log Completeness | 100% | TBD | N/A |
| Certificate Expiry Warnings | 0 | TBD | N/A |
| Encryption Coverage | 100% | TBD | N/A |

### Operational Metrics

| Metric | Target | Current | Trend |
|:-------|:-------|:--------|:------|
| DR Test Success Rate | 100% | TBD | N/A |
| Policy Compliance Score | > 95% | TBD | N/A |
| Incident Response Time (Critical) | < 15 min | TBD | N/A |
| Audit Findings (Open) | 0 | TBD | N/A |

---

## 📚 Referenced Documents

* [Vault Deployment Guide](../security/vault_deployment.md)
* [Celery Architecture](../runtime/celery_architecture.md)
* [NPHIES Integration Spec](../compliance/nphies_integration_spec.md)
* [Access Control Policy](policies/access-control-policy.md)
* [Data Retention Policy](policies/data-retention-policy.md)

---

## 🔄 Review & Approval

| Role | Name | Signature | Date |
|:-----|:-----|:----------|:-----|
| **Compliance Officer** | | | |
| **Security Lead** | | | |
| **PMO Director** | | | |
| **CTO** | | | |

---

**Document Classification:** Internal - Confidential  
**Next Review Date:** 2026-02-06
