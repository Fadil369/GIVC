# HashiCorp Vault Deployment Guide

**Version:** 1.0  
**Phase:** 1 - Vault Security Foundation  
**Owner:** Security Engineering & CloudOps  
**Status:** Implementation Ready

---

## 📋 Overview

This document details the deployment and operational procedures for the ClaimLinc-GIVC HashiCorp Vault HA cluster, providing centralized secrets management compliant with HIPAA §164.308/312 and PDPL Art 14-17.

---

## 🏗️ Architecture Design

### High Availability Configuration

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (TLS 1.3)                  │
│                      vault.claimlinc.local                    │
└────────────────────────────┬────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
    ┌───────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
    │  Vault Node  │  │ Vault Node │  │ Vault Node │
    │   (Active)   │  │ (Standby)  │  │ (Standby)  │
    │  10.0.1.10   │  │ 10.0.1.11  │  │ 10.0.1.12  │
    └──────┬───────┘  └──────┬─────┘  └──────┬─────┘
           │                 │                │
           └─────────────────┼────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │  Consul Storage   │
                   │   Backend (HA)    │
                   └───────────────────┘
```

### Specifications

| Component | Specification | Rationale |
|:----------|:-------------|:----------|
| **Nodes** | 3 nodes (1 active, 2 standby) | HA with quorum consensus |
| **vCPU** | 4 cores per node | Encryption/decryption overhead |
| **Memory** | 16 GB per node | Token cache + audit buffer |
| **Storage** | 500 GB SSD per node | Audit logs (6-year retention) |
| **Network** | 10 Gbps, private subnet | Low-latency replication |
| **TLS** | 1.3, mutual auth required | HIPAA §164.312 compliance |

---

## 🔧 Installation & Bootstrapping

### 1. Install Vault Binary

```bash
# Download and verify Vault
wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip
wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_SHA256SUMS
sha256sum -c vault_1.15.0_SHA256SUMS 2>&1 | grep OK

# Install
unzip vault_1.15.0_linux_amd64.zip
sudo mv vault /usr/local/bin/
sudo chmod +x /usr/local/bin/vault

# Create vault user
sudo useradd --system --home /etc/vault.d --shell /bin/false vault
```

### 2. Configure Vault Server

Create `/etc/vault.d/vault.hcl`:

```hcl
# Storage backend - Consul for HA
storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"
  
  # TLS for Consul communication
  tls_ca_file   = "/etc/vault.d/tls/consul-ca.pem"
  tls_cert_file = "/etc/vault.d/tls/consul-cert.pem"
  tls_key_file  = "/etc/vault.d/tls/consul-key.pem"
}

# API listener
listener "tcp" {
  address         = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  
  tls_cert_file      = "/etc/vault.d/tls/vault-cert.pem"
  tls_key_file       = "/etc/vault.d/tls/vault-key.pem"
  tls_client_ca_file = "/etc/vault.d/tls/ca.pem"
  
  tls_min_version = "tls13"
  tls_require_and_verify_client_cert = true
}

# Seal configuration - Auto-unseal with Cloud KMS
seal "azurekeyvault" {
  tenant_id      = "AZURE_TENANT_ID"
  client_id      = "AZURE_CLIENT_ID"
  client_secret  = "AZURE_CLIENT_SECRET"
  vault_name     = "claimlinc-vault-unseal"
  key_name       = "vault-unseal-key"
}

# Telemetry
telemetry {
  prometheus_retention_time = "24h"
  disable_hostname          = false
}

# Cluster settings
api_addr     = "https://VAULT_NODE_IP:8200"
cluster_addr = "https://VAULT_NODE_IP:8201"

# UI
ui = true

# Log level
log_level = "info"
```

### 3. Create Systemd Service

Create `/etc/systemd/system/vault.service`:

```ini
[Unit]
Description=HashiCorp Vault - Secrets Management
Documentation=https://www.vaultproject.io/docs/
Requires=network-online.target
After=network-online.target
ConditionFileNotEmpty=/etc/vault.d/vault.hcl

[Service]
User=vault
Group=vault
ProtectSystem=full
ProtectHome=read-only
PrivateTmp=yes
PrivateDevices=yes
SecureBits=keep-caps
AmbientCapabilities=CAP_IPC_LOCK
CapabilityBoundingSet=CAP_SYSLOG CAP_IPC_LOCK
NoNewPrivileges=yes
ExecStart=/usr/local/bin/vault server -config=/etc/vault.d/vault.hcl
ExecReload=/bin/kill --signal HUP $MAINPID
KillMode=process
KillSignal=SIGINT
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
StartLimitInterval=60
StartLimitBurst=3
LimitNOFILE=65536
LimitMEMLOCK=infinity

[Install]
WantedBy=multi-user.target
```

### 4. Initialize and Unseal Vault

```bash
# Start Vault
sudo systemctl enable vault
sudo systemctl start vault

# Initialize (run on one node only)
export VAULT_ADDR='https://vault.claimlinc.local:8200'
vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -recovery-shares=5 \
  -recovery-threshold=3

# Save recovery keys securely
# Auto-unseal will handle unsealing automatically
```

---

## 🔐 AppRole Authentication Setup

### 1. Enable AppRole Auth Method

```bash
vault auth enable approle
```

### 2. Create Policies

#### FastAPI Service Policy

Create `policies/fastapi-policy.hcl`:

```hcl
# Database credentials
path "database/creds/claimlinc-db" {
  capabilities = ["read"]
}

# JWT signing keys
path "secret/data/jwt/*" {
  capabilities = ["read"]
}

# API keys
path "secret/data/api-keys/*" {
  capabilities = ["read"]
}

# NPHIES credentials
path "secret/data/nphies/*" {
  capabilities = ["read"]
}
```

Apply policy:

```bash
vault policy write fastapi-service policies/fastapi-policy.hcl
```

#### Celery Worker Policy

Create `policies/celery-policy.hcl`:

```hcl
# RabbitMQ credentials
path "rabbitmq/creds/celery-worker" {
  capabilities = ["read"]
}

# Redis credentials
path "database/creds/redis" {
  capabilities = ["read"]
}

# Task encryption keys
path "transit/encrypt/celery-tasks" {
  capabilities = ["update"]
}

path "transit/decrypt/celery-tasks" {
  capabilities = ["update"]
}
```

Apply policy:

```bash
vault policy write celery-worker policies/celery-policy.hcl
```

### 3. Create AppRoles

```bash
# FastAPI AppRole
vault write auth/approle/role/fastapi-service \
  token_ttl=1h \
  token_max_ttl=4h \
  token_policies="fastapi-service" \
  bind_secret_id=true \
  secret_id_ttl=0 \
  token_num_uses=0

# Celery AppRole
vault write auth/approle/role/celery-worker \
  token_ttl=1h \
  token_max_ttl=4h \
  token_policies="celery-worker" \
  bind_secret_id=true \
  secret_id_ttl=0 \
  token_num_uses=0

# Retrieve Role IDs (save securely)
vault read auth/approle/role/fastapi-service/role-id
vault read auth/approle/role/celery-worker/role-id

# Generate Secret IDs
vault write -f auth/approle/role/fastapi-service/secret-id
vault write -f auth/approle/role/celery-worker/secret-id
```

---

## 🔄 Secret Rotation Configuration

### 1. Database Dynamic Secrets

```bash
# Enable database secrets engine
vault secrets enable database

# Configure PostgreSQL connection
vault write database/config/claimlinc-db \
  plugin_name=postgresql-database-plugin \
  allowed_roles="claimlinc-app" \
  connection_url="postgresql://{{username}}:{{password}}@postgres.claimlinc.local:5432/claimlinc" \
  username="vault-admin" \
  password="VAULT_DB_PASSWORD" \
  password_authentication="scram-sha-256"

# Create role with 30-day rotation
vault write database/roles/claimlinc-app \
  db_name=claimlinc-db \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}' IN ROLE claimlinc_app;" \
  default_ttl="720h" \
  max_ttl="720h"
```

### 2. RabbitMQ Dynamic Secrets

```bash
# Enable RabbitMQ secrets engine
vault secrets enable rabbitmq

# Configure RabbitMQ connection
vault write rabbitmq/config/connection \
  connection_uri="https://rabbitmq.claimlinc.local:15672" \
  username="vault-admin" \
  password="VAULT_RABBITMQ_PASSWORD"

# Create role
vault write rabbitmq/roles/celery-worker \
  vhosts='{"/claimlinc": {"write": ".*", "read": ".*", "configure": ".*"}}' \
  ttl="720h" \
  max_ttl="720h"
```

### 3. Automated Rotation Script

Create `scripts/rotate-secrets.sh`:

```bash
#!/bin/bash
set -euo pipefail

export VAULT_ADDR='https://vault.claimlinc.local:8200'

# Rotate database root credentials
vault write -f database/rotate-root/claimlinc-db

# Rotate RabbitMQ root credentials
vault write -f rabbitmq/rotate-root

# Log rotation event
echo "$(date -Iseconds) - Secret rotation completed" >> /var/log/vault/rotation.log

# Send notification
curl -X POST https://monitoring.claimlinc.local/api/events \
  -H "Content-Type: application/json" \
  -d '{"event": "vault_rotation", "status": "success", "timestamp": "'$(date -Iseconds)'"}'
```

Schedule via cron:

```bash
# Run rotation monthly
0 2 1 * * /etc/vault.d/scripts/rotate-secrets.sh
```

---

## 📊 Audit Logging

### 1. Enable Audit Device

```bash
# File audit backend
vault audit enable file file_path=/var/log/vault/audit.log

# Syslog audit backend (backup)
vault audit enable syslog tag="vault" facility="AUTH"
```

### 2. Audit Log Rotation

Create `/etc/logrotate.d/vault`:

```
/var/log/vault/audit.log {
    daily
    rotate 2190  # 6 years
    compress
    delaycompress
    notifempty
    create 0600 vault vault
    postrotate
        systemctl reload vault
    endscript
}
```

### 3. Export to Centralized Logging

Create `scripts/export-audit-logs.sh`:

```bash
#!/bin/bash
# Export audit logs to S3/Azure Blob for long-term retention

DATE=$(date +%Y-%m-%d)
LOG_FILE="/var/log/vault/audit.log.${DATE}.gz"
DEST="s3://claimlinc-compliance-logs/vault-audit/${DATE}/"

if [ -f "$LOG_FILE" ]; then
    aws s3 cp "$LOG_FILE" "$DEST" --sse AES256
    echo "$(date -Iseconds) - Audit log exported: ${LOG_FILE}" >> /var/log/vault/export.log
fi
```

---

## 🚨 Monitoring & Alerting

### Prometheus Scrape Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'vault'
    metrics_path: '/v1/sys/metrics'
    params:
      format: ['prometheus']
    scheme: https
    tls_config:
      ca_file: /etc/prometheus/tls/ca.pem
      cert_file: /etc/prometheus/tls/client-cert.pem
      key_file: /etc/prometheus/tls/client-key.pem
    static_configs:
      - targets:
        - 'vault-1.claimlinc.local:8200'
        - 'vault-2.claimlinc.local:8200'
        - 'vault-3.claimlinc.local:8200'
```

### Alert Rules

Create `alerts/vault-alerts.yml`:

```yaml
groups:
  - name: vault
    interval: 30s
    rules:
      - alert: VaultSealed
        expr: vault_core_unsealed == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Vault is sealed on {{ $labels.instance }}"
          
      - alert: VaultAuthFailures
        expr: rate(vault_core_handle_request_count{path=~"auth/.*", status="permission_denied"}[5m]) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High authentication failure rate on {{ $labels.instance }}"
          
      - alert: VaultTokenExpirationHigh
        expr: vault_token_count_by_ttl{creation_ttl="+Inf"} > 100
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "High number of long-lived tokens"
```

---

## 🔄 Disaster Recovery

### Backup Procedures

```bash
# Automated snapshot script
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/backup/vault"

# Take Consul snapshot (Vault storage)
consul snapshot save "${BACKUP_DIR}/consul-${DATE}.snap"

# Encrypt and upload
gpg --encrypt --recipient vault-backup@claimlinc.local "${BACKUP_DIR}/consul-${DATE}.snap"
aws s3 cp "${BACKUP_DIR}/consul-${DATE}.snap.gpg" s3://claimlinc-dr-backups/vault/

# Retain local backups for 7 days
find "$BACKUP_DIR" -name "consul-*.snap*" -mtime +7 -delete

# Log backup completion
echo "$(date -Iseconds) - Vault backup completed: consul-${DATE}.snap" >> /var/log/vault/backup.log
```

Schedule via cron:

```bash
# Daily backups at 3 AM
0 3 * * * /etc/vault.d/scripts/backup-vault.sh
```

### Recovery Procedures

1. **Restore Consul Snapshot**
   ```bash
   consul snapshot restore /backup/vault/consul-YYYYMMDD-HHMMSS.snap
   ```

2. **Restart Vault Nodes**
   ```bash
   sudo systemctl restart vault
   ```

3. **Verify Cluster Health**
   ```bash
   vault status
   vault operator raft list-peers  # if using Raft storage
   ```

---

## ✅ Validation Checklist

- [ ] All 3 Vault nodes operational and in HA mode
- [ ] Auto-unseal configured and tested
- [ ] AppRole authentication enabled with policies applied
- [ ] Database secrets engine configured with rotation
- [ ] RabbitMQ secrets engine configured with rotation
- [ ] Audit logging enabled to both file and syslog
- [ ] Log rotation configured (6-year retention)
- [ ] Prometheus metrics endpoint accessible
- [ ] Alert rules deployed and tested
- [ ] Backup automation configured and tested
- [ ] DR recovery procedure documented and tested

---

## 📚 References

* [Vault Production Hardening](https://developer.hashicorp.com/vault/tutorials/operations/production-hardening)
* [Vault HA with Consul](https://developer.hashicorp.com/vault/tutorials/raft/raft-deployment-guide)
* [AppRole Auth Method](https://developer.hashicorp.com/vault/docs/auth/approle)
* [Database Secrets Engine](https://developer.hashicorp.com/vault/docs/secrets/databases)

---

**Last Updated:** 2025-11-05  
**Next Review:** 2025-12-05  
**Document Owner:** Security Engineering Team
