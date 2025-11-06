# 🚀 BrainSAIT RCM - Quick Deployment Guide

## ⚡ TL;DR - Deploy in 5 Minutes

```bash
# 1. Make script executable
chmod +x deploy.sh

# 2. Run deployment
./deploy.sh

# 3. Done! ✅
```

---

## 📋 Pre-Deployment Checklist

Before running the deployment script, ensure you have:

- [ ] VM Access: `ssh root@82.25.101.65` (password: Fadil12345678#)
- [ ] Domain name ready (e.g., brainsait.yourdomain.com)
- [ ] NPHIES API credentials
- [ ] SMTP email credentials for notifications
- [ ] Admin email and password ready

---

## 🎯 Deployment Steps

### Step 1: Prepare Locally

```bash
# Navigate to project directory
cd /path/to/oaises+

# Edit .env.production with your credentials
nano .env.production

# Update these critical values:
# - NPHIES_API_KEY
# - SMTP_USER and SMTP_PASSWORD
# - Your domain name
# - OASIS+ credentials (if different)
```

### Step 2: Run Deployment

```bash
# Make script executable (first time only)
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

The script will prompt you for:
1. Domain name
2. Admin email
3. Admin password

### Step 3: Update DNS

Point your domain to the server IP:
```
Type: A Record
Name: @ (or your subdomain)
Value: 82.25.101.65
```

### Step 4: Verify

```bash
# Check health
curl https://yourdomain.com/health

# Check API docs
# Visit: https://yourdomain.com/docs

# Login with admin credentials
# Visit: https://yourdomain.com
```

---

## 🔑 Important Credentials

### MongoDB
- Host: localhost:27017
- Database: brainsait
- User: brainsait_admin
- Password: (Generated during deployment)

### Admin User
- Email: (You specify during deployment)
- Password: (You specify during deployment)
- Role: SUPER_ADMIN

### Application URLs
- Frontend: https://yourdomain.com
- API: https://yourdomain.com/api
- API Docs: https://yourdomain.com/docs
- Health Check: https://yourdomain.com/health

---

## 🔧 Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f web

# Nginx logs
tail -f /var/log/nginx/brainsait-error.log
```

### Restart Services
```bash
cd /opt/brainsait

# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
docker-compose restart web
```

### Check Status
```bash
# Container status
docker-compose ps

# System resources
docker stats

# Disk usage
df -h
```

### Database Backup
```bash
# Manual backup
docker exec brainsait-mongodb mongodump \
    --uri="mongodb://brainsait_admin:YOUR_PASSWORD@localhost:27017/brainsait?authSource=admin" \
    --out=/tmp/backup

# Automated daily backups are configured via cron
```

---

## 🐛 Quick Troubleshooting

### API Not Responding
```bash
docker-compose restart api
docker-compose logs api
```

### Frontend Not Loading
```bash
docker-compose restart web
docker-compose logs web
```

### Database Connection Failed
```bash
docker-compose restart mongodb
docker-compose logs mongodb
```

### SSL Certificate Issues
```bash
certbot renew --force-renewal
systemctl reload nginx
```

### Can't Access from Internet
```bash
# Check firewall
ufw status

# Open ports if needed
ufw allow 80/tcp
ufw allow 443/tcp
```

---

## 📊 Health Check Endpoints

Test these URLs after deployment:

- `https://yourdomain.com/health` - API health
- `https://yourdomain.com/` - Frontend
- `https://yourdomain.com/docs` - API documentation
- `https://yourdomain.com/metrics` - Prometheus metrics (localhost only)

---

## 🔒 Security Notes

1. **Change Default Passwords**: The deployment script generates secure secrets automatically
2. **Firewall**: UFW is configured to allow only ports 22, 80, and 443
3. **SSL**: Let's Encrypt certificate is installed automatically
4. **Rate Limiting**: API endpoints are rate-limited (100 req/min, 5 login/min)
5. **Account Lockout**: 5 failed login attempts = 30-minute lockout

---

## 📞 Need Help?

### Quick Fixes
1. **Try restarting**: `docker-compose restart`
2. **Check logs**: `docker-compose logs -f`
3. **Verify env**: `cat /opt/brainsait/.env`

### Documentation
- Full deployment guide: `DEPLOYMENT.md`
- Audit report: `AUDIT_AND_FIXES.md`
- API docs: https://yourdomain.com/docs

### Support
- Email: support@brainsait.com
- Check container status: `docker-compose ps`
- Check system: `systemctl status nginx docker`

---

## ✅ Post-Deployment Checklist

After successful deployment:

- [ ] Can access frontend via HTTPS
- [ ] Can log in with admin credentials
- [ ] API health check returns "healthy"
- [ ] Can create a test user
- [ ] Can submit a test rejection
- [ ] Email notifications work (test SMTP)
- [ ] SSL certificate is valid (check browser)
- [ ] Backups are scheduled (check cron)
- [ ] Firewall is active (`ufw status`)
- [ ] All containers are running (`docker-compose ps`)

---

## 🎉 You're Live!

Your BrainSAIT RCM system is now running in production!

**Next Steps**:
1. Create additional user accounts
2. Configure NPHIES integration
3. Test OASIS+ integration
4. Import existing data (if any)
5. Train staff on the system
6. Monitor logs for the first few days

---

**Remember**: The automated deployment script handles 90% of the work. The remaining 10% is configuring your specific credentials and domain.

**Deploy Time**: ~5-10 minutes (including SSL certificate generation)

**Questions?** See `DEPLOYMENT.md` for detailed information.
