#!/bin/bash
# Vault AppRole Configuration Script
# Creates AppRoles for all ClaimLinc-GIVC services

set -euo pipefail

export VAULT_ADDR="${VAULT_ADDR:-https://vault.claimlinc.local:8200}"
export VAULT_TOKEN="${VAULT_TOKEN:-}"

if [ -z "$VAULT_TOKEN" ]; then
    echo "Error: VAULT_TOKEN environment variable must be set"
    exit 1
fi

echo "=== Configuring Vault AppRoles for ClaimLinc-GIVC ==="
echo "Vault Address: $VAULT_ADDR"
echo ""

# Enable AppRole auth method
echo "[1/7] Enabling AppRole authentication method..."
vault auth enable -path=approle approle 2>/dev/null || echo "AppRole already enabled"

# Create policies directory
mkdir -p /etc/vault.d/policies

# FastAPI Service Policy
echo "[2/7] Creating FastAPI service policy..."
cat > /etc/vault.d/policies/fastapi-service.hcl <<'EOF'
# Database credentials
path "database/creds/claimlinc-db" {
  capabilities = ["read"]
}

# JWT signing keys
path "secret/data/jwt/*" {
  capabilities = ["read"]
}

# API keys for external services
path "secret/data/api-keys/*" {
  capabilities = ["read"]
}

# NPHIES credentials
path "secret/data/nphies/*" {
  capabilities = ["read"]
}

# Encryption transit
path "transit/encrypt/api-data" {
  capabilities = ["update"]
}

path "transit/decrypt/api-data" {
  capabilities = ["update"]
}
EOF

vault policy write fastapi-service /etc/vault.d/policies/fastapi-service.hcl

# Celery Worker Policy
echo "[3/7] Creating Celery worker policy..."
cat > /etc/vault.d/policies/celery-worker.hcl <<'EOF'
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

# Access to task-related secrets
path "secret/data/celery/*" {
  capabilities = ["read"]
}
EOF

vault policy write celery-worker /etc/vault.d/policies/celery-worker.hcl

# NPHIES Integration Policy
echo "[4/7] Creating NPHIES integration policy..."
cat > /etc/vault.d/policies/nphies-integration.hcl <<'EOF'
# NPHIES certificates and keys
path "pki/issue/nphies-client" {
  capabilities = ["create", "update"]
}

# NPHIES credentials
path "secret/data/nphies/*" {
  capabilities = ["read"]
}

# JWT signing for NPHIES
path "secret/data/jwt/nphies-signing-key" {
  capabilities = ["read"]
}

# mTLS certificates
path "pki/cert/*" {
  capabilities = ["read"]
}
EOF

vault policy write nphies-integration /etc/vault.d/policies/nphies-integration.hcl

# Create AppRoles
echo "[5/7] Creating FastAPI AppRole..."
vault write auth/approle/role/fastapi-service \
    token_ttl=1h \
    token_max_ttl=4h \
    token_policies="fastapi-service" \
    bind_secret_id=true \
    secret_id_ttl=0 \
    token_num_uses=0

echo "[6/7] Creating Celery AppRole..."
vault write auth/approle/role/celery-worker \
    token_ttl=1h \
    token_max_ttl=4h \
    token_policies="celery-worker" \
    bind_secret_id=true \
    secret_id_ttl=0 \
    token_num_uses=0

echo "[7/7] Creating NPHIES Integration AppRole..."
vault write auth/approle/role/nphies-integration \
    token_ttl=2h \
    token_max_ttl=6h \
    token_policies="nphies-integration" \
    bind_secret_id=true \
    secret_id_ttl=0 \
    token_num_uses=0

# Retrieve and display Role IDs
echo ""
echo "=== AppRole Configuration Complete ==="
echo ""
echo "Role IDs (save these securely):"
echo "--------------------------------"

echo -n "FastAPI Service Role ID: "
vault read -field=role_id auth/approle/role/fastapi-service/role-id

echo -n "Celery Worker Role ID: "
vault read -field=role_id auth/approle/role/celery-worker/role-id

echo -n "NPHIES Integration Role ID: "
vault read -field=role_id auth/approle/role/nphies-integration/role-id

echo ""
echo "To generate Secret IDs for each service, run:"
echo "  vault write -f auth/approle/role/fastapi-service/secret-id"
echo "  vault write -f auth/approle/role/celery-worker/secret-id"
echo "  vault write -f auth/approle/role/nphies-integration/secret-id"
echo ""
echo "Store Role IDs and Secret IDs in a secure location (e.g., encrypted config management)"
