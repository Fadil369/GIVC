# GIVC Platform - Cloudflare Pages Deployment Guide

## 🚀 Quick Deploy to Cloudflare Pages

### Prerequisites
- Cloudflare account
- GitHub repository access
- Wrangler CLI installed (optional)

### Option 1: Deploy via Cloudflare Dashboard (Recommended)

1. **Connect Repository**
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - Navigate to **Pages** > **Create a project**
   - Connect your GitHub account
   - Select the `Fadil369/GIVC` repository
   - Select the `main` or `copilot/build-dynamic-branded-ui` branch

2. **Configure Build Settings**
   ```
   Framework preset: None (Static HTML)
   Build command: (leave empty)
   Build output directory: /
   Root directory: /
   ```

3. **Environment Variables**
   Add these in the Cloudflare Pages settings:
   ```
   ENVIRONMENT=production
   HIPAA_COMPLIANCE_LEVEL=strict
   RCM_ACCREDITATION=enabled
   ```

4. **Deploy**
   - Click **Save and Deploy**
   - Wait for deployment to complete
   - Your site will be live at: `https://givc.pages.dev`

### Option 2: Deploy via Wrangler CLI

```bash
# Install Wrangler (if not already installed)
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy to Cloudflare Pages
wrangler pages deploy . --project-name=givc

# Or use npm script
npm run deploy
```

### Option 3: Direct Upload

```bash
# Deploy current directory
wrangler pages deploy . --project-name=givc --branch=main
```

## 🔧 Post-Deployment Configuration

### 1. Custom Domain Setup
- Go to **Pages** > **Custom domains**
- Add your domain: `givc.thefadil.site`
- Configure DNS records as instructed

### 2. Enable Workers Integration
For the RCM API features to work properly:

1. Deploy the Cloudflare Workers:
   ```bash
   cd workers
   wrangler deploy
   ```

2. Configure the Worker route in Pages settings:
   - Go to **Settings** > **Functions**
   - Add route: `/api/*` → Your Worker

### 3. Configure R2 Storage (for MediVault)
```bash
# Create R2 bucket
wrangler r2 bucket create medical-files

# Bind to Pages
# In Cloudflare Dashboard: Pages > Settings > Functions > R2 bucket bindings
# Add binding: MEDICAL_FILES → medical-files
```

### 4. Configure KV Namespaces
```bash
# Create KV namespaces
wrangler kv:namespace create "MEDICAL_METADATA"
wrangler kv:namespace create "AUDIT_LOGS"

# Add bindings in Pages Settings > Functions > KV namespace bindings
```

### 5. Configure D1 Database
```bash
# Create D1 database
wrangler d1 create healthcare-db

# Add binding in Pages Settings > Functions > D1 database bindings
```

## 🌐 Repository Sync Setup

### Automatic Deployments
Cloudflare Pages automatically deploys on:
- Push to main branch
- Pull request creation (preview deployment)
- Branch updates

### Configure Build Settings
1. Go to **Pages** > **Settings** > **Builds & deployments**
2. Enable:
   - ✅ Automatic deployments
   - ✅ Preview deployments
   - ✅ Deploy hooks

### GitHub Actions Integration (Optional)
The repository includes GitHub Actions workflows in `.github/workflows/`:
- `deploy.yml` - Automated deployment on push
- `test.yml` - Run tests before deployment

## 🔐 Security Configuration

### Headers
The `_headers` file configures:
- CORS for API integration
- Security headers (CSP, X-Frame-Options, etc.)
- Caching policies

### Environment Variables
Ensure these are set in Cloudflare Pages:
```
ENVIRONMENT=production
HIPAA_COMPLIANCE_LEVEL=strict
RCM_ACCREDITATION=enabled
ENCRYPTION_KEY=<your-encryption-key>
JWT_SECRET=<your-jwt-secret>
```

## 📊 Monitoring & Analytics

### Enable Cloudflare Analytics
1. Go to **Pages** > **Analytics**
2. Enable:
   - Web Analytics
   - Real-time logs
   - Error tracking

### Configure Alerts
Set up alerts for:
- Deployment failures
- High error rates
- Performance issues

## 🧪 Testing the Deployment

### 1. Basic Functionality
Visit your deployed site and test:
- ✅ Page loads correctly
- ✅ Navigation works
- ✅ RCM section displays
- ✅ API test buttons work
- ✅ Toast notifications appear

### 2. API Integration
Test each API endpoint:
```bash
# Health check
curl https://your-site.pages.dev/api/v1/health

# Authentication
curl https://your-site.pages.dev/api/v1/auth

# MediVault
curl https://your-site.pages.dev/api/v1/medivault
```

### 3. Performance Testing
Use Cloudflare's built-in tools:
- Speed testing
- Mobile responsiveness
- SEO checks

## 🔄 Updates & Maintenance

### Deploy Updates
1. Push changes to GitHub
2. Cloudflare Pages automatically deploys
3. Monitor deployment status in dashboard

### Rollback
If needed, rollback to previous version:
1. Go to **Pages** > **Deployments**
2. Select previous deployment
3. Click **Rollback to this deployment**

### Manual Deploy
```bash
# From local machine
wrangler pages deploy . --project-name=givc --branch=main
```

## 🔗 Integration with brainsait-rcm

The platform integrates with the [brainsait-rcm](https://github.com/Fadil369/brainsait-rcm) repository:

### Setup Integration
1. Ensure brainsait-rcm is deployed
2. Update API endpoint in `assets/js/rcm-integration.js`:
   ```javascript
   baseURL: 'https://api.givc.workers.dev'
   ```
3. Configure CORS on brainsait-rcm API
4. Test integration using the API testing panel

## 📚 Additional Resources

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [GIVC Platform Documentation](./README.md)
- [brainsait-rcm Repository](https://github.com/Fadil369/brainsait-rcm)

## 🆘 Troubleshooting

### Deployment Fails
- Check build logs in Cloudflare dashboard
- Verify repository permissions
- Ensure no syntax errors in HTML/CSS/JS

### API Endpoints Not Working
- Verify Workers are deployed
- Check environment variables
- Review CORS configuration
- Test endpoints directly

### Performance Issues
- Enable Cloudflare caching
- Optimize images
- Minify CSS/JS
- Use CDN for assets

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/Fadil369/GIVC/issues
- Email: github@brainsait.io
- Documentation: https://givc.thefadil.site/docs

---

© 2025 BRAINSAIT LTD - RCM Accredited Healthcare Technology Provider
