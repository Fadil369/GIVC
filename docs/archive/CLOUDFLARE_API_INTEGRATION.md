# Cloudflare API Integration - GIVC Platform

**Integration Date:** October 24, 2025  
**Status:** ✅ Active & Integrated  
**Token Type:** Workers API Token

---

## 🔐 Credentials

**Securely stored in:** `/home/pi/GIVC/.env`

```bash
CLOUDFLARE_ACCOUNT_ID=87a79e73521fc85dab488b2c700554e3
CLOUDFLARE_API_TOKEN=nUxMcbX6PJUBbqeBT6Uwb_8rd2hCRDjsgZt4nkqH
CLOUDFLARE_TUNNEL_ID=8d76575f-8fcb-4a90-9fbd-31c4fe1bbc3b
CLOUDFLARE_TUNNEL_NAME=mypi-tunnel
CLOUDFLARE_DOMAIN=brainsait.com
```

⚠️ **Security:** File permissions set to `600` (owner read/write only)

---

## 🛠️ Available Tools

### 1. Cloudflare API Manager (`cloudflare-api.sh`)

Comprehensive tool for managing Cloudflare resources via API.

**Usage:**
```bash
./cloudflare-api.sh <command>
```

**Commands:**
```bash
verify           # Verify API token is valid
status           # Show platform status summary
zones            # List all zones (domains)
tunnels          # List all Cloudflare Tunnels
tunnel-info      # Get detailed tunnel information
dns-records <id> # List DNS records for a zone
workers          # List Cloudflare Workers scripts
help             # Show help message
```

**Examples:**
```bash
# Check if API token is working
./cloudflare-api.sh verify

# Get complete platform status
./cloudflare-api.sh status

# List all your domains
./cloudflare-api.sh zones

# List all tunnels
./cloudflare-api.sh tunnels

# Get detailed tunnel info
./cloudflare-api.sh tunnel-info
```

---

### 2. Workers Deployment Tool (`workers-deploy.sh`)

Deploy and manage Cloudflare Workers scripts.

**Usage:**
```bash
./workers-deploy.sh <command> [options]
```

**Commands:**
```bash
deploy <name> <path>  # Deploy a Worker script
list                  # List all Workers scripts
```

**Examples:**
```bash
# Deploy a Worker
./workers-deploy.sh deploy givc-api ./workers/api/index.js

# List deployed Workers
./workers-deploy.sh list
```

---

## 💡 Capabilities & Use Cases

### What You Can Do

With this API integration, you can programmatically:

#### 1. **DNS Management**
- Create, update, delete DNS records
- Automate subdomain creation
- Bulk DNS operations
- Dynamic DNS updates

#### 2. **Workers Deployment**
- Deploy serverless functions
- Update Workers scripts
- Manage Worker routes
- Configure KV namespaces

#### 3. **Tunnel Management**
- Monitor tunnel status
- Get tunnel analytics
- Manage tunnel connections
- Configure ingress rules

#### 4. **Analytics & Monitoring**
- Get traffic statistics
- Monitor performance
- Track errors and logs
- Real-time insights

#### 5. **Security**
- Manage firewall rules
- Configure rate limiting
- Set up DDoS protection
- SSL/TLS management

---

## 🚀 Integration Enhancements

### Automated DNS Management

Create dynamic subdomains for deployments:

```bash
#!/bin/bash
# auto-dns.sh - Automatically create DNS records

source .env

create_dns_record() {
    local name="$1"
    local target="$2"
    local zone_id="$3"
    
    curl -X POST "https://api.cloudflare.com/client/v4/zones/${zone_id}/dns_records" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data "{
            \"type\": \"CNAME\",
            \"name\": \"${name}\",
            \"content\": \"${target}\",
            \"proxied\": true
        }"
}

# Example: Create new subdomain
create_dns_record "dev.givc" "${CLOUDFLARE_TUNNEL_ID}.cfargotunnel.com" "<zone-id>"
```

### Worker Auto-Deployment

Integrate with Git for automatic deployments:

```bash
#!/bin/bash
# git-deploy-worker.sh - Deploy Workers on git push

cd workers/api
git pull origin main

# Deploy updated Worker
./workers-deploy.sh deploy givc-api ./index.js

echo "✅ Worker deployed from latest commit"
```

### Tunnel Health Monitoring

Monitor tunnel status and get alerts:

```bash
#!/bin/bash
# monitor-tunnel.sh - Check tunnel health

source .env

status=$(curl -s "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/cfd_tunnel/${CLOUDFLARE_TUNNEL_ID}" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}")

if echo "$status" | grep -q "healthy"; then
    echo "✅ Tunnel is healthy"
else
    echo "⚠️ Tunnel issue detected"
    # Send alert (email, Slack, etc.)
fi
```

---

## 🔒 Security Best Practices

### Token Security

1. **Never commit `.env` to Git**
   - Already in `.gitignore`
   - File permissions: `600`
   - Only accessible by owner

2. **Rotate tokens regularly**
   ```bash
   # Create new token in Cloudflare dashboard
   # Update .env file
   # Test with: ./cloudflare-api.sh verify
   ```

3. **Use limited scope tokens**
   - Current token: Workers API only
   - Create separate tokens for different services
   - Revoke unused tokens

4. **Monitor token usage**
   ```bash
   ./cloudflare-api.sh verify  # Check token status
   ```

### API Rate Limits

Cloudflare API limits:
- **Free Plan:** 1,200 requests per 5 minutes
- **Pro Plan:** 2,400 requests per 5 minutes

Implement rate limiting in your scripts:
```bash
# Add delay between requests
sleep 1
```

---

## 📊 Monitoring & Analytics

### Get Zone Analytics

```bash
#!/bin/bash
source .env

ZONE_ID="<your-zone-id>"

curl -s "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/analytics/dashboard" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" | jq .
```

### Track Tunnel Metrics

```bash
# Get tunnel connections
./cloudflare-api.sh tunnel-info

# Monitor in real-time
watch -n 30 './cloudflare-api.sh tunnel-info'
```

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Workers

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy Worker
        env:
          CF_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CF_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
        run: |
          curl -X PUT \
            "https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/workers/scripts/givc-api" \
            -H "Authorization: Bearer ${CF_API_TOKEN}" \
            -H "Content-Type: application/javascript" \
            --data-binary @workers/api/index.js
```

---

## 🎯 Advanced Use Cases

### 1. Dynamic Subdomain Creation

Automatically create subdomains for each deployment:

```bash
# When deploying a new feature
FEATURE="new-feature"
./create-subdomain.sh "${FEATURE}.givc.brainsait.com"
```

### 2. Blue-Green Deployments

Use Workers for zero-downtime deployments:

```bash
# Deploy to blue environment
./workers-deploy.sh deploy givc-api-blue ./build/v2.js

# Switch traffic via DNS
./update-dns.sh givc.brainsait.com givc-api-blue
```

### 3. Automated SSL Management

Monitor and renew SSL certificates:

```bash
# Check SSL status
./check-ssl.sh brainsait.com

# Auto-renew if needed
./renew-ssl.sh brainsait.com
```

### 4. Geo-Routing with Workers

Route traffic based on user location:

```javascript
// workers/geo-router.js
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const country = request.cf.country
  
  // Route based on location
  if (country === 'SA') {
    return fetch('https://sa-backend.givc.local', request)
  } else {
    return fetch('https://global-backend.givc.local', request)
  }
}
```

---

## 📝 API Documentation

### Official Cloudflare API Docs

- **API Reference:** https://developers.cloudflare.com/api/
- **Workers Docs:** https://developers.cloudflare.com/workers/
- **Tunnel Docs:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

### Useful Endpoints

```bash
# Verify token
GET /client/v4/user/tokens/verify

# List zones
GET /client/v4/zones

# List DNS records
GET /client/v4/zones/:zone_id/dns_records

# Create DNS record
POST /client/v4/zones/:zone_id/dns_records

# Deploy Worker
PUT /client/v4/accounts/:account_id/workers/scripts/:script_name

# List tunnels
GET /client/v4/accounts/:account_id/cfd_tunnel

# Get tunnel info
GET /client/v4/accounts/:account_id/cfd_tunnel/:tunnel_id
```

---

## 🛟 Troubleshooting

### Token Not Working

```bash
# Verify token
./cloudflare-api.sh verify

# Check expiration
curl "https://api.cloudflare.com/client/v4/accounts/<account-id>/tokens/verify" \
  -H "Authorization: Bearer <token>"
```

### API Rate Limit Exceeded

```bash
# Check rate limit headers
curl -I "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer <token>"
```

### Tunnel Not Responding

```bash
# Check tunnel status
./cloudflare-api.sh tunnel-info

# Check local service
systemctl status cloudflared

# Check logs
sudo journalctl -u cloudflared -n 50
```

---

## ✅ Integration Checklist

- [x] API token created and verified
- [x] Credentials stored securely in `.env`
- [x] File permissions set to `600`
- [x] Cloudflare API scripts created
- [x] Workers deployment tool created
- [x] Token verification tested
- [x] Documentation created
- [ ] Set up automated DNS management
- [ ] Configure Worker deployment pipeline
- [ ] Set up monitoring alerts
- [ ] Create backup/disaster recovery plan
- [ ] Document custom automation scripts

---

## 🎉 Summary

Your GIVC Platform now has full Cloudflare API integration!

**What's Enabled:**
- ✅ API token securely stored
- ✅ Management scripts ready to use
- ✅ Workers deployment capability
- ✅ DNS automation possible
- ✅ Tunnel monitoring available
- ✅ Analytics access enabled

**Next Steps:**
1. Test the API tools
2. Create automation scripts for your workflows
3. Set up monitoring and alerts
4. Explore advanced features

**Get Started:**
```bash
# Quick start
./cloudflare-api.sh status

# View all commands
./cloudflare-api.sh help
```

---

**Last Updated:** October 24, 2025  
**Integration Status:** ✅ Complete & Operational
