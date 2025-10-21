# 🔐 GitHub Secrets Configuration Guide

## Required Secrets for GIVC Deployment

This document outlines all the secrets that need to be configured in GitHub for the enhanced deployment workflow.

## 📍 How to Add Secrets

1. Navigate to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the name and value
5. Click **Add secret**

## 🔑 Required Secrets

### Cloudflare Configuration

#### `CLOUDFLARE_API_TOKEN`
- **Description**: Cloudflare API token with DNS, Workers, and Pages permissions
- **How to get**:
  1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/)
  2. Go to **My Profile** → **API Tokens**
  3. Click **Create Token**
  4. Use "Edit Cloudflare Workers" template or create custom token with:
     - Zone - DNS - Edit
     - Account - Cloudflare Pages - Edit
     - Account - Cloudflare Workers Scripts - Edit
     - Zone - Zone - Read
  5. Copy the generated token
- **Example**: `xyz123abc456def789...`

#### `CLOUDFLARE_ACCOUNT_ID`
- **Description**: Your Cloudflare Account ID
- **How to get**:
  1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/)
  2. Select any domain
  3. Look for "Account ID" in the right sidebar (Overview page)
  4. Or go to **Workers & Pages** → **Overview** → Account ID is displayed
- **Example**: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

#### `CF_ZONE_ID`
- **Description**: Zone ID for brainsait.com domain
- **How to get**:
  1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/)
  2. Select **brainsait.com** domain
  3. Scroll down on the Overview page
  4. Find "Zone ID" in the API section (right sidebar)
- **Example**: `zone1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6`

### Google Tag Manager Configuration (Optional)

#### `GTM_CONTAINER_ID`
- **Description**: Google Tag Manager Container ID
- **How to get**:
  1. Log in to [Google Tag Manager](https://tagmanager.google.com/)
  2. Select your container
  3. Look for Container ID in the top right (format: GTM-XXXXXXX)
- **Example**: `GTM-ABC123X`
- **Required**: Only if using Google Tag Manager integration
- **Default behavior**: If not set, GTM configuration step will be skipped

#### `GTM_GATEWAY_ENDPOINT`
- **Description**: API endpoint for Google Tag Gateway configuration
- **How to set**:
  - Use your GTM server-side endpoint
  - Or your custom GTM configuration API
- **Example**: `https://api.yourdomain.com/gtm/config`
- **Required**: Only if using Google Tag Manager integration

#### `GTM_API_TOKEN`
- **Description**: API token for authenticating with GTM Gateway
- **How to get**:
  - Generate from your GTM Gateway service
  - Or use your custom API authentication token
- **Example**: `gtm_1234567890abcdef...`
- **Required**: Only if using Google Tag Manager integration

## 🔍 Verification Checklist

After adding all secrets, verify:

- [ ] `CLOUDFLARE_API_TOKEN` is added (REQUIRED)
- [ ] `CLOUDFLARE_ACCOUNT_ID` is added (REQUIRED)
- [ ] `CF_ZONE_ID` is added (REQUIRED)
- [ ] `GTM_CONTAINER_ID` is added (if using GTM)
- [ ] `GTM_GATEWAY_ENDPOINT` is added (if using GTM)
- [ ] `GTM_API_TOKEN` is added (if using GTM)
- [ ] All secrets are saved without extra spaces or newlines
- [ ] Token permissions are correctly configured in Cloudflare

## 🧪 Testing Secrets

### Test Cloudflare API Token

```bash
# Test with curl (replace YOUR_TOKEN with actual token)
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Expected response:
# {"success":true,"errors":[],"messages":[{"code":10000,"message":"This API Token is valid and active"}],...}
```

### Test Cloudflare Account Access

```bash
# Test account access
curl -X GET "https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Test Zone Access

```bash
# Test zone access
curl -X GET "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

## 🚨 Security Best Practices

### Secret Management

1. **Never commit secrets to repository**
   - Secrets should only be in GitHub Secrets
   - Never in `.env` files committed to git
   - Add `.env` to `.gitignore`

2. **Rotate tokens regularly**
   - Rotate API tokens every 90 days
   - Update GitHub secrets when rotating

3. **Use least privilege principle**
   - Only grant necessary permissions to API tokens
   - Avoid using Global API Key

4. **Monitor token usage**
   - Check Cloudflare audit logs
   - Review GitHub Actions logs

### Token Permissions Matrix

| Resource | Permission | Required For |
|----------|-----------|-------------|
| Zone - DNS | Edit | DNS record management |
| Zone - Zone | Read | Zone information queries |
| Account - Workers | Edit | Worker deployment |
| Account - Pages | Edit | Pages deployment |

## 🔄 Updating Secrets

To update a secret:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Find the secret to update
3. Click the **Update** button
4. Enter the new value
5. Click **Update secret**

## ❓ Troubleshooting

### "Context access might be invalid" Error

This is a GitHub Actions linting warning that appears when secrets are referenced in workflow files. This is **normal** and expected. The secrets will work correctly at runtime when they're configured in GitHub.

### "Unauthorized" or "Forbidden" Errors

1. Verify token has correct permissions
2. Check token hasn't expired
3. Ensure Account ID and Zone ID are correct
4. Test token with curl commands above

### Workflow Skips GTM Configuration

This is expected if `GTM_CONTAINER_ID` is not set. The workflow includes:

```yaml
if: ${{ secrets.GTM_CONTAINER_ID != '' }}
```

This condition ensures GTM configuration only runs when the secret is configured.

## 📚 Additional Resources

- [Cloudflare API Tokens Documentation](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)
- [GitHub Encrypted Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Google Tag Manager Server-Side Setup](https://developers.google.com/tag-platform/tag-manager/server-side)

## ✅ Ready to Deploy

Once all required secrets are configured:

```bash
git add .
git commit -m "Configure deployment secrets and workflow"
git push origin main
```

The workflow will automatically trigger and use the configured secrets.

---

**© 2024 Dr. Al Fadil - BRAINSAIT LTD**  
**GIVC Healthcare Platform**
