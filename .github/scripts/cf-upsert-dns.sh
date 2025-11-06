#!/usr/bin/env bash
set -euo pipefail

# Enhanced DNS Management Script for GIVC Healthcare Platform
# Creates or updates DNS records for givc.brainsait.com in Cloudflare
# Supports A, CNAME, and TXT records with comprehensive error handling

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate required environment variables
validate_env() {
    local missing=()
    
    [ -z "${CF_API_TOKEN:-}" ] && missing+=("CF_API_TOKEN")
    [ -z "${CF_ZONE_ID:-}" ] && missing+=("CF_ZONE_ID")
    [ -z "${CF_DOMAIN:-}" ] && missing+=("CF_DOMAIN")
    [ -z "${TARGET_HOST:-}" ] && missing+=("TARGET_HOST")
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing required environment variables: ${missing[*]}"
        echo ""
        echo "Required variables:"
        echo "  CF_API_TOKEN  - Cloudflare API token with DNS edit permissions"
        echo "  CF_ZONE_ID    - Cloudflare Zone ID for your domain"
        echo "  CF_DOMAIN     - Domain name (e.g., givc.brainsait.com)"
        echo "  TARGET_HOST   - Target host/IP for DNS record"
        echo ""
        echo "Optional variables:"
        echo "  RECORD_TYPE   - DNS record type (default: CNAME)"
        echo "  TTL           - Time to live in seconds (default: 1 = auto)"
        echo "  PROXIED       - Enable Cloudflare proxy (default: true)"
        exit 1
    fi
}

# Set default values
RECORD_TYPE="${RECORD_TYPE:-CNAME}"
TTL="${TTL:-1}"
PROXIED="${PROXIED:-true}"

# API configuration
AUTH_HDR="Authorization: Bearer ${CF_API_TOKEN}"
API="https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records"

# Main DNS upsert function
upsert_dns_record() {
    log_info "Starting DNS record management for ${CF_DOMAIN}"
    log_info "Record Type: ${RECORD_TYPE}, Target: ${TARGET_HOST}, Proxied: ${PROXIED}"
    
    # Check for existing record
    log_info "Checking for existing DNS record..."
    local existing_response=$(curl -sS -X GET \
        "${API}?type=${RECORD_TYPE}&name=${CF_DOMAIN}" \
        -H "${AUTH_HDR}" \
        -H "Content-Type: application/json")
    
    # Validate API response
    local success=$(echo "$existing_response" | jq -r '.success // false')
    if [ "$success" != "true" ]; then
        log_error "Failed to query DNS records"
        echo "$existing_response" | jq .
        exit 1
    fi
    
    local existing_id=$(echo "$existing_response" | jq -r '.result[0].id // empty')
    
    # Prepare DNS record data
    local dns_data=$(jq -n \
        --arg type "${RECORD_TYPE}" \
        --arg name "${CF_DOMAIN}" \
        --arg content "${TARGET_HOST}" \
        --arg ttl "${TTL}" \
        --argjson proxied "${PROXIED}" \
        '{
            type: $type,
            name: $name,
            content: $content,
            ttl: ($ttl|tonumber),
            proxied: $proxied
        }')
    
    log_info "DNS Record Configuration:"
    echo "$dns_data" | jq .
    
    # Update or create record
    local response
    if [ -n "$existing_id" ]; then
        log_info "Updating existing DNS record (ID: ${existing_id})"
        response=$(curl -sS -X PUT \
            "${API}/${existing_id}" \
            -H "${AUTH_HDR}" \
            -H "Content-Type: application/json" \
            --data "$dns_data")
    else
        log_info "Creating new DNS record"
        response=$(curl -sS -X POST \
            "${API}" \
            -H "${AUTH_HDR}" \
            -H "Content-Type: application/json" \
            --data "$dns_data")
    fi
    
    # Validate response
    local operation_success=$(echo "$response" | jq -r '.success // false')
    if [ "$operation_success" = "true" ]; then
        log_success "DNS record successfully configured!"
        log_success "Domain: ${CF_DOMAIN} → ${TARGET_HOST}"
        
        # Display record details
        local record_id=$(echo "$response" | jq -r '.result.id')
        local proxied_status=$(echo "$response" | jq -r '.result.proxied')
        local ttl_value=$(echo "$response" | jq -r '.result.ttl')
        
        log_info "Record Details:"
        echo "  - ID: ${record_id}"
        echo "  - Type: ${RECORD_TYPE}"
        echo "  - Proxied: ${proxied_status}"
        echo "  - TTL: ${ttl_value} seconds"
        
        # Show full response if verbose
        if [ "${VERBOSE:-false}" = "true" ]; then
            log_info "Full API Response:"
            echo "$response" | jq .
        fi
    else
        log_error "Failed to configure DNS record"
        echo "$response" | jq .
        exit 1
    fi
}

# Create additional DNS records for common subdomains
create_subdomain_records() {
    log_info "Creating additional subdomain records..."
    
    # API subdomain
    if [ "${CREATE_API_SUBDOMAIN:-true}" = "true" ]; then
        log_info "Creating API subdomain: api.${CF_DOMAIN}"
        CF_DOMAIN="api.${CF_DOMAIN}" \
        TARGET_HOST="${API_TARGET_HOST:-givc.brainsait.workers.dev}" \
        RECORD_TYPE="CNAME" \
        upsert_dns_record
    fi
    
    # WWW subdomain
    if [ "${CREATE_WWW_SUBDOMAIN:-false}" = "true" ]; then
        log_info "Creating WWW subdomain: www.${CF_DOMAIN}"
        CF_DOMAIN="www.${CF_DOMAIN}" \
        TARGET_HOST="${TARGET_HOST}" \
        RECORD_TYPE="CNAME" \
        upsert_dns_record
    fi
}

# Verify DNS propagation
verify_dns() {
    log_info "Verifying DNS record..."
    
    sleep 2  # Brief pause to allow Cloudflare to process
    
    local dns_result=$(dig +short "${CF_DOMAIN}" @1.1.1.1 | head -n1)
    
    if [ -n "$dns_result" ]; then
        log_success "DNS record is resolving: ${CF_DOMAIN} → ${dns_result}"
    else
        log_warning "DNS record not yet propagating (this is normal and may take a few minutes)"
    fi
}

# Main execution
main() {
    echo "================================================"
    echo "  GIVC Healthcare Platform - DNS Manager"
    echo "  © Dr. Al Fadil (BRAINSAIT LTD)"
    echo "================================================"
    echo ""
    
    # Validate environment
    validate_env
    
    # Execute DNS operations
    upsert_dns_record
    
    # Create additional records if requested
    if [ "${CREATE_SUBDOMAINS:-false}" = "true" ]; then
        create_subdomain_records
    fi
    
    # Verify DNS
    if [ "${SKIP_VERIFICATION:-false}" != "true" ]; then
        verify_dns
    fi
    
    echo ""
    log_success "DNS configuration completed successfully!"
    log_info "Note: DNS propagation may take up to 24 hours globally"
    echo "================================================"
}

# Run main function
main
