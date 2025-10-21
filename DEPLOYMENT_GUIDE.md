# 🚀 GIVC Healthcare Platform - Enhanced Deployment Guide

## 📋 Overview

This guide covers the complete deployment workflow for the GIVC Healthcare Platform with:
- ✅ Automated Cloudflare Pages deployment
- ✅ Cloudflare Workers deployment
- ✅ DNS management and configuration
- ✅ Google Tag Manager Gateway integration
- ✅ Cloudflare Access JWT validation
- ✅ HIPAA-compliant security features

## 🔑 Prerequisites

### Required Accounts & Tokens

1. **GitHub Repository**
   - Repository: `Fadil369/GIVC`
   - Branch: `main` (default)

2. **Cloudflare Account**
   - Account ID: Required for API calls
   - API Token with permissions:
     - DNS: Edit
     - Workers: Edit
     - Pages: Edit
     - Zone: Read

3. **Google Tag Manager** (Optional)
   - Container ID
   - Gateway API endpoint
   - API token

### Required GitHub Secrets

Navigate to: `Settings → Secrets and variables → Actions → New repository secret`

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token | `xyz123...` |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Account ID | `a1b2c3d4...` |
| `CF_ZONE_ID` | Cloudflare Zone ID for brainsait.com | `zone123...` |
| `GTM_CONTAINER_ID` | Google Tag Manager Container ID | `GTM-XXXXXXX` |
| `GTM_GATEWAY_ENDPOINT` | GTM Gateway API endpoint | `https://api.example.com/gtm/config` |
| `GTM_API_TOKEN` | GTM Gateway API token | `gtm_token...` |

## 📁 Project Structure

```
GIVC/
├── .github/
│   ├── workflows/
│   │   ├── deploy-enhanced.yml    # Main deployment workflow
│   │   ├── ci-cd.yml              # CI/CD pipeline
│   │   └── deploy.yml             # Simple deployment
│   └── scripts/
│       └── cf-upsert-dns.sh       # DNS management script
├── workers/
│   ├── router.js                   # Main API router
│   ├── access-validator.js         # CF Access JWT validation
│   ├── agents/                     # AI agents
│   └── middleware/                 # Security middleware
├── frontend/
│   └── src/                        # React application
├── dist/                           # Build output (created by build)
└── package.json
```

## 🛠️ Setup Instructions

### Step 1: Clone Repository

```bash
git clone https://github.com/Fadil369/GIVC.git
cd GIVC
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Configure Environment Variables

Create `.env` file in project root:

```env
# Cloudflare Configuration
CLOUDFLARE_API_TOKEN=your_api_token_here
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CF_ZONE_ID=your_zone_id_here

# Domain Configuration
CF_DOMAIN=givc.brainsait.com
TARGET_HOST=givc-healthcare.pages.dev

# Google Tag Manager (Optional)
GTM_CONTAINER_ID=GTM-XXXXXXX
GTM_GATEWAY_ENDPOINT=https://api.example.com/gtm/config
GTM_API_TOKEN=your_gtm_token_here

# Cloudflare Access
ACCESS_AUD=5bc270d16bb84f830d04e92712d45cfdbf3527f3fdb8aecba8ec30296add9b22
ACCESS_TEAM_DOMAIN=https://fadil369.cloudflareaccess.com
```

### Step 4: Configure GitHub Secrets

1. Go to GitHub repository settings
2. Navigate to: **Settings → Secrets and variables → Actions**
3. Add each secret from the table above
4. Verify all secrets are added correctly

### Step 5: Test Build Locally

```bash
# Test build
npm run build:production

# Verify build output
ls -la dist/

# Test locally (optional)
npm run preview
```

## 🚀 Deployment

### Automatic Deployment (Recommended)

Push to `main` branch to trigger automatic deployment:

```bash
git add .
git commit -m "Deploy GIVC platform with enhanced workflow"
git push origin main
```

The workflow will automatically:
1. ✅ Build the application
2. ✅ Deploy to Cloudflare Pages
3. ✅ Configure DNS records
4. ✅ Deploy Cloudflare Workers
5. ✅ Configure Google Tag Gateway
6. ✅ Set up Cloudflare Access validation
7. ✅ Run health checks
8. ✅ Generate deployment report

### Manual Deployment

```bash
# Build application
npm run build:production

# Deploy to Cloudflare Pages
wrangler pages deploy dist --project-name=givc-healthcare

# Deploy Workers
cd workers
wrangler deploy router.js --name givc-router
wrangler deploy access-validator.js --name givc-access-validator

# Configure DNS (requires environment variables)
chmod +x .github/scripts/cf-upsert-dns.sh
./.github/scripts/cf-upsert-dns.sh
```

## 🌐 DNS Configuration

### Automatic DNS Setup

The workflow automatically creates/updates:
- `givc.brainsait.com` → Cloudflare Pages (A record with proxy)
- `api.givc.brainsait.com` → Workers (CNAME with proxy)

### Manual DNS Configuration

```bash
# Set required environment variables
export CF_API_TOKEN="your_token"
export CF_ZONE_ID="your_zone_id"
export CF_DOMAIN="givc.brainsait.com"
export TARGET_HOST="givc-healthcare.pages.dev"
export RECORD_TYPE="CNAME"
export PROXIED="true"

# Run DNS script
./.github/scripts/cf-upsert-dns.sh
```

### DNS Verification

```bash
# Check DNS resolution
nslookup givc.brainsait.com

# Check with Cloudflare DNS
dig @1.1.1.1 givc.brainsait.com

# Check API subdomain
dig @1.1.1.1 api.givc.brainsait.com
```

## 🏷️ Google Tag Manager Integration

### Configuration

The workflow automatically configures GTM with:
- Container ID from secrets
- Consent mode settings (HIPAA-compliant)
- Server-side tracking endpoint
- Analytics tracking enabled

### Custom GTM Configuration

Edit `.github/workflows/deploy-enhanced.yml` to customize:

```yaml
GTM_PAYLOAD=$(jq -n \
  --arg containerId "${{ secrets.GTM_CONTAINER_ID }}" \
  --arg domain "${{ env.DOMAIN }}" \
  --argjson consentMode true \
  '{
    containerId: $containerId,
    domain: $domain,
    config: {
      consentMode: {
        enabled: $consentMode,
        defaultConsent: {
          ad_storage: "denied",           # No advertising
          analytics_storage: "granted",   # Analytics allowed
          functionality_storage: "granted",
          personalization_storage: "denied",
          security_storage: "granted"
        }
      }
    }
  }')
```

## 🔐 Cloudflare Access Integration

### JWT Validation Setup

The `access-validator.js` worker validates JWT tokens from Cloudflare Access:

```javascript
// Configuration
const ACCESS_CONFIG = {
  AUD: '5bc270d16bb84f830d04e92712d45cfdbf3527f3fdb8aecba8ec30296add9b22',
  TEAM_DOMAIN: 'https://fadil369.cloudflareaccess.com',
  CERTS_URL: 'https://fadil369.cloudflareaccess.com/cdn-cgi/access/certs'
};
```

### Testing JWT Validation

```bash
# Get JWT token from Cloudflare Access
# Then test validation:

curl -X GET https://givc.brainsait.workers.dev/validate \
  -H "cf-access-jwt-assertion: YOUR_JWT_TOKEN"
```

### Integrating with Your Application

Add JWT validation to your Express app:

```javascript
const express = require("express");
const jose = require("jose");

const AUD = process.env.POLICY_AUD;
const TEAM_DOMAIN = process.env.TEAM_DOMAIN;
const CERTS_URL = `${TEAM_DOMAIN}/cdn-cgi/access/certs`;

const JWKS = jose.createRemoteJWKSet(new URL(CERTS_URL));

const verifyToken = async (req, res, next) => {
  if (!AUD) {
    return res.status(403).send({
      status: false,
      message: "missing required audience"
    });
  }

  const token = req.headers["cf-access-jwt-assertion"];

  if (!token) {
    return res.status(403).send({
      status: false,
      message: "missing required cf authorization token"
    });
  }

  try {
    const result = await jose.jwtVerify(token, JWKS, {
      issuer: TEAM_DOMAIN,
      audience: AUD
    });

    req.user = result.payload;
    next();
  } catch (err) {
    return res.status(403).send({
      status: false,
      message: "invalid token"
    });
  }
};

app.use(verifyToken);
```

## 📊 Workflow Jobs Overview

### 1. Build & Deploy
- Installs dependencies
- Builds production bundle
- Deploys to Cloudflare Pages
- Outputs deployment URL

### 2. DNS Configuration
- Creates/updates A record for main domain
- Creates/updates CNAME for API subdomain
- Enables Cloudflare proxy
- Verifies DNS resolution

### 3. Deploy Workers
- Deploys main router worker
- Deploys AI agent workers
- Deploys access validation worker
- Configures worker routes

### 4. GTM Configuration
- Sends PATCH request to GTM Gateway
- Configures container settings
- Sets up consent mode
- Enables server-side tracking

### 5. Access Configuration
- Deploys JWT validation worker
- Configures Access application
- Sets up authentication flow
- Enables security features

### 6. Verification
- Checks DNS propagation
- Tests health endpoints
- Verifies Workers deployment
- Generates deployment report

## 🔍 Monitoring & Debugging

### View Workflow Logs

1. Go to GitHub repository
2. Click **Actions** tab
3. Select latest workflow run
4. View logs for each job

### Check Deployment Status

```bash
# Check Pages deployment
curl https://givc.brainsait.com/api/v1/health

# Check Workers deployment
curl https://givc.brainsait.workers.dev/api/v1/health

# Check Access validation
curl https://givc.brainsait.workers.dev/health
```

### Common Issues

#### DNS Not Propagating
```bash
# Force DNS flush (Windows PowerShell)
ipconfig /flushdns

# Force DNS flush (Linux/Mac)
sudo dscacheutil -flushcache

# Wait 5-10 minutes for Cloudflare propagation
```

#### Build Failures
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build:production
```

#### Worker Deployment Issues
```bash
# Check wrangler authentication
wrangler whoami

# Re-authenticate if needed
wrangler login

# Manually deploy worker
wrangler deploy workers/router.js --name givc-router
```

## 📈 Optimization Tips

### Build Output Directory

The workflow uses `dist/` as the build directory. If using Next.js or another framework:

**Next.js Static Export:**
```json
// next.config.js
module.exports = {
  output: 'export',
  distDir: 'out'
}
```

Update workflow:
```yaml
env:
  BUILD_DIR: 'out'
```

**Vite (Current Setup):**
```javascript
// vite.config.js
export default defineConfig({
  build: {
    outDir: 'dist'
  }
})
```

### Performance Optimization

1. **Enable Cloudflare Proxy**: Already enabled in DNS config
2. **Configure Caching**: Set in `_headers` file
3. **Enable Compression**: Automatic with Cloudflare
4. **Optimize Images**: Use Cloudflare Images or R2

### Security Enhancements

1. **Enable Rate Limiting**: Configure in Workers
2. **Set up WAF Rules**: In Cloudflare dashboard
3. **Configure HSTS**: Already in security headers
4. **Enable DDoS Protection**: Automatic with Cloudflare

## 📚 Additional Resources

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Cloudflare Access Documentation](https://developers.cloudflare.com/cloudflare-one/)
- [Cloudflare DNS API Documentation](https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-list-dns-records)
- [Google Tag Manager Server-Side](https://developers.google.com/tag-platform/tag-manager/server-side)

## 🤝 Support

For issues or questions:
1. Check workflow logs in GitHub Actions
2. Review Cloudflare dashboard for errors
3. Check DNS propagation status
4. Verify all secrets are configured
5. Test locally before deploying

---

**© 2024 Dr. Al Fadil - BRAINSAIT LTD. All rights reserved.**  
**GIVC - Transforming Healthcare Through Technology** 🏥✨
