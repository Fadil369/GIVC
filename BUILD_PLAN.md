# 🧠 ClaimLinc-GIVC Comprehensive Build Plan

**Version:** 1.1  
**Date:** 2025-11-05  
**Prepared By:** BrainSAIT Engineering & Compliance PMO

---

## 🎯 Mission Snapshot

Deliver a **production-ready ClaimLinc-GIVC platform** that fulfills

* **HIPAA §164.308/312** (administrative & technical safeguards)
* **Saudi PDPL Art 14–17** (data consent, retention, minimization)
* **NPHIES transport & security controls** (mTLS, JWT, FHIR conformance)

by rolling out **Vault-managed secrets**, **resilient Celery / RabbitMQ pipelines**, and **auditable NPHIES integrations** across staged environments.

---

## 🔑 Prerequisites & Approvals

| Domain           | Requirement                                                                | Owner                            | Status    |
| :--------------- | :------------------------------------------------------------------------- | :------------------------------- | :-------- |
| **Hosting**      | Approve cloud provider + SLA for 3-node Vault and RabbitMQ quorum clusters | CloudOps + Security              | ❗ Pending |
| **NPHIES**       | Secure official onboarding toolkit, sandbox credentials, SDKs              | Compliance Office                | ❗ Pending |
| **Hardware**     | Confirm vCPU/RAM/IO budget for RabbitMQ nodes & Redis replicas             | Runtime Eng. + Procurement       | ❗ Pending |
| **Policies**     | Define certificate lifecycle, DR frequency, change-control matrix          | Security Eng. + PMO + Compliance | ❗ Pending |
| **Environments** | Approve Stage → Prod rollout order for Vault/Celery adoption               | DevOps + PMO                     | ❗ Pending |

---

## 🗺️ Phase Breakdown & Deliverables

| Phase                                            | Scope                                                                    | Key Deliverables                                                                                                                                                                                                                | Dependencies                                    | Owners                       |
| :----------------------------------------------- | :----------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------- | :--------------------------- |
| **1. Vault Security Foundation (Weeks 1–2)**     | Deploy managed 3-node Vault HA cluster; enforce AppRole + rotation       | • `docs/security/vault_deployment.md` updated<br>• Vault agents + AppRole mappings + rotation jobs<br>• Audit export to `logs/audit/` (6-year retention)<br>• Automated failover snapshots                                      | Cloud provider approval, TLS certs              | Security Eng., CloudOps      |
| **2. Celery / RabbitMQ Runtime (Weeks 3–5)**     | Provision RabbitMQ quorum + Redis AOF clusters; connect FastAPI ↔ Celery | • `docs/runtime/celery_architecture.md` updated<br>• TLS 1.3 broker/result paths via Vault secrets<br>• DLQs + retry policies (max 5)<br>• Prometheus exporter + Flower dashboards<br>• Structured logging with correlation IDs | Vault operational; certs issued; hardware ready | Runtime Eng., DevOps, SRE    |
| **3. NPHIES Sandbox Integration (Weeks 6–8)**    | Build `nphies-sim/`; validate FHIR v0.4.0 profiles and flows             | • `docs/compliance/nphies_integration_spec.md` updated<br>• Eligibility / claim / payment workflow coverage<br>• JWT signing + mTLS certs in Vault<br>• Conformance report + errata log                                         | NPHIES artifacts; Vault available               | Integration Team, Compliance |
| **4. Audit Readiness & Governance (Weeks 9–10)** | Consolidate evidence & monitoring; establish governance                  | • `/docs/compliance/audit-trail/` repository<br>• Governance calendar + escalation matrix<br>• Monitoring alerts (Vault, queues, FHIR errors)<br>• Quarterly DR test schedule                                                   | Policy approvals; monitoring stack              | Compliance Office, PMO, SRE  |

---

## 🛠️ Execution Playbook (Condensed)

1. **Finalize Vault HA design** (storage backend, networking, seal method) → update `vault_deployment.md`.
2. **Bootstrap Vault ops** (unseal workflow, AppRoles, rotation jobs, alert hooks).
3. **Refactor secret distribution** → replace `.env`; deploy Vault Agents / CI env-inject; enforce TLS 1.3 mTLS.
4. **Provision RabbitMQ & Redis** → quorum queues × 3 nodes + AOF replicas ≥ 2; register in Vault; validate TLS.
5. **Harden Celery runtime** → `task_acks_late`, DLQs, idempotency keys, retry backoff, metrics + logs.
6. **Build NPHIES sandbox** → `nphies-sim/` with FHIR validation, ACK/REJECT, JWT/mTLS tests.
7. **Compile compliance evidence** → audit trails, rotation logs, FHIR archives, monitoring screenshots, DR reports.

---

## 🔐 Compliance Alignment Matrix

| Control Domain                 | Implemented By                                                | Evidence Artifacts                        |
| :----------------------------- | :------------------------------------------------------------ | :---------------------------------------- |
| **HIPAA §164.308 (Admin)**     | Vault access control & credential rotation policies           | Policy exports, rotation logs             |
| **HIPAA §164.312 (Technical)** | AES-256 at rest + TLS 1.3 in transit + audit logging          | TLS configs, audit exports, alert reports |
| **PDPL Art 14–17**             | Consent via FHIR Consent, retention enforcement, minimization | `nphies-sim/` logs, schema reviews        |
| **NPHIES IG v0.4.0**           | mTLS certs + JWT signing + FHIR conformance                   | Cert audits, test reports                 |
| **Operational Integrity**      | RabbitMQ quorum + Redis AOF + DLQs + monitoring               | Broker dashboards, metrics, policies      |

---

## 🔄 Integration Touchpoints

| Interface                     | Payloads                               | Security Mechanism     | Notes                                |
| :---------------------------- | :------------------------------------- | :--------------------- | :----------------------------------- |
| Vault ↔ FastAPI               | DB URIs, JWT keys                      | AppRole + Vault Agent  | 30-day rotation; short-lived tokens  |
| Vault ↔ Celery/RabbitMQ/Redis | Broker + result credentials, TLS certs | Dynamic Secrets Engine | Auto-renew via Celery beat           |
| FastAPI ↔ Celery              | Task payloads + callbacks              | TLS 1.3 + mutual auth  | Include correlation IDs for audit    |
| Celery ↔ NPHIES Harness       | FHIR Bundles                           | JWT + mTLS             | Idempotent processing + DLQ fallback |
| Vault ↔ NPHIES                | PKI certs, client secrets              | PKI Secrets Engine     | Follow certificate lifecycle policy  |

---

## 📈 Monitoring & Alerting Blueprint

* **Vault:** audit events, token issuance, auth failures, seal status
* **RabbitMQ:** quorum health, queue depth, consumer lag, DLQ size
* **Redis:** replication lag, AOF rewrite, memory usage
* **Celery:** failure rate, retry counts, worker heartbeat
* **NPHIES Harness:** submission success %, latency
* **Alerting Stack:** Prometheus + Grafana; escalation matrix owned by PMO & SRE

---

## 🧪 Testing & Validation Gates

| Stage                 | Test Suite                                            | Success Criteria                                          |
| :-------------------- | :---------------------------------------------------- | :-------------------------------------------------------- |
| **Vault Go-Live**     | Unseal + rotation drills + AppRole auth               | All services pull secrets after rotation; audits recorded |
| **Messaging Runtime** | Synthetic load + failover + DLQ tests                 | Zero message loss; policy-compliant retries; alerts fire  |
| **NPHIES Sandbox**    | Eligibility / claim / payment flows via `nphies-sim/` | v0.4.0 profiles validate; reject handling logged          |
| **Compliance Audit**  | Evidence review + DR simulation                       | HIPAA/PDPL checklist pass; RTO ≤ SLA target               |

---

## ⚠️ Risk Register & Mitigations

| Risk                              | Impact             | Mitigation                                                      |
| :-------------------------------- | :----------------- | :-------------------------------------------------------------- |
| **Vault hosting approval delay**  | Blocks Phase 1     | Escalate to CloudOps board; prepare staging fallback            |
| **RabbitMQ resource shortfall**   | Throughput drop    | Pre-size cluster; load-test; early procurement                  |
| **NPHIES toolkit access lag**     | Phase 3 delay      | Compliance to engage MOH/CCHI immediately; parallel sandbox dev |
| **Certificate renewal oversight** | Integration outage | Define lifecycle policy; monitor expiry alerts                  |
| **Engineer bandwidth limits**     | Phase slip         | PMO to assign dedicated resources; weekly syncs                 |

---

## 🧭 Governance & Communications

* **Weekly Sync:** Vault (Security) / Runtime (Celery–RabbitMQ) / Compliance (NPHIES) / PMO
* **Change Control:** Dual approval (Security + Compliance) before prod changes
* **Documentation:** Centralize under `docs/security/`, `docs/runtime/`, `docs/compliance/`, `/docs/compliance/audit-trail/`
* **Incident Response:** Follow BrainSAIT SOC runbooks with contact registry attached
* **Sign-Offs:** Phase closure requires stakeholder acceptance + evidence upload

---

## 📅 Timeline Overview

| Phase              | Duration | Theme Color (GitHub Pages) |
| :----------------- | :------- | :------------------------- |
| Vault Security     | 2 weeks  | 🔵 Blue                    |
| Celery Runtime     | 3 weeks  | 🟢 Green                   |
| NPHIES Integration | 3 weeks  | 🟠 Orange                  |
| Audit Governance   | 2 weeks  | 🟣 Purple                  |

---

## ✅ Completion Criteria

* Vault HA cluster operational with rotations, audit logs, and DR playbooks.
* Celery / RabbitMQ runtime TLS-secured with DLQs and Vault secret injection.
* NPHIES sandbox validated against FHIR v0.4.0 with mTLS / JWT controls.
* Compliance evidence archived and governance cadence locked.

Once pending approvals (hosting, hardware, NPHIES artifacts, policies) are granted, teams proceed sequentially through phases to achieve a fully compliant, production-ready ClaimLinc-GIVC deployment.

---

## 📂 Implementation Status

This document serves as the master plan. Individual phase implementations are tracked in:
- `docs/security/` - Phase 1 artifacts
- `docs/runtime/` - Phase 2 artifacts
- `docs/compliance/` - Phase 3 & 4 artifacts
- `deployment/` - Infrastructure and deployment configs
- `monitoring/` - Observability and alerting configs

**Last Updated:** 2025-11-05  
**Status:** Implementation In Progress
