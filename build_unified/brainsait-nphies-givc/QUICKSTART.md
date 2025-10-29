# ⚡ Quick Start Guide - BrainSAIT-NPHIES-GIVC Integration

Get started with the enhanced NPHIES integration platform in 5 minutes!

---

## 🚀 Prerequisites

- Python 3.9 or higher installed
- Windows PowerShell
- NPHIES production certificates (`.pem` files)
- Network access to portal endpoints

---

## 📥 Step 1: Navigate to Project

```powershell
cd C:\Users\rcmrejection3\nphies-rcm\brainsait-nphies-givc
```

---

## 🔧 Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
```

---

## 📦 Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (web framework)
- httpx & aiohttp (HTTP clients)
- Pydantic (data validation)
- PyJWT & cryptography (authentication)
- loguru (logging)
- And more...

---

## 🔐 Step 4: Configure Environment

### Create `.env` file:

```powershell
copy .env.example .env
notepad .env
```

### Update critical settings:

```ini
# NPHIES Configuration
NPHIES_HOSPITAL_ID=10000000000988
NPHIES_CHI_ID=1048
NPHIES_LICENSE=7000911508

# NPHIES Certificates (update paths)
NPHIES_CERT_PATH=./certificates/nphies_production.pem
NPHIES_KEY_PATH=./certificates/nphies_production_key.pem
NPHIES_CERT_PASSWORD=your-cert-password-here

# OASES Credentials (Already set to U2415/U2415)
# No changes needed - all branches use same credentials

# GIVC Platform
GIVC_ULTRATHINK_ENABLED=true

# Database (Optional - can leave empty for now)
DATABASE_URL=
REDIS_URL=
```

Save and close.

---

## 📜 Step 5: Place NPHIES Certificates

Copy your NPHIES certificates to the `certificates/` directory:

```powershell
# Create certificates directory if not exists
New-Item -ItemType Directory -Force -Path certificates

# Copy your certificate files
# Example:
copy "C:\path\to\your\nphies_production.pem" certificates\
copy "C:\path\to\your\nphies_production_key.pem" certificates\
```

**Required files**:
- `nphies_production.pem` - Production certificate
- `nphies_production_key.pem` - Private key

---

## ✅ Step 6: Verify Configuration

Check that config files are in place:

```powershell
# Check .env exists
Test-Path .env

# Check config.yaml exists
Test-Path config\config.yaml

# Check certificates (if you have them)
Test-Path certificates\nphies_production.pem
```

All should return `True`.

---

## 🎯 Step 7: Run the Application

### Development Mode (with auto-reload):

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode:

```powershell
python main.py
```

You should see:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🧪 Step 8: Test the API

### Open your browser:

**Swagger UI**: http://localhost:8000/docs  
**ReDoc**: http://localhost:8000/redoc

### Test with PowerShell:

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/ping"

# Root endpoint
Invoke-RestMethod -Uri "http://localhost:8000/"
```

### Test with curl (if installed):

```bash
# Health check
curl http://localhost:8000/api/v1/health/ping

# System health
curl http://localhost:8000/api/v1/health/
```

---

## 📋 Common Operations

### 1. Check Patient Eligibility

```powershell
$body = @{
    patient_id = "1234567890"
    insurance_id = "TAWUNIYA-12345"
    service_date = "2024-10-26"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/nphies/eligibility" -Body $body -ContentType "application/json"
```

### 2. Validate Claim with AI

```powershell
$claim = @{
    claim = @{
        patient_id = "1234567890"
        insurance_id = "TAWUNIYA-12345"
        service_date = "2024-10-26"
        items = @(
            @{
                code = "99213"
                description = "Office Visit"
                quantity = 1
                unit_price = 150.00
            }
        )
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/givc/validate" -Body $claim -ContentType "application/json"
```

### 3. Submit Claim (NPHIES-First Strategy)

```powershell
$submission = @{
    claim = @{
        patient_id = "1234567890"
        insurance_id = "TAWUNIYA-12345"
        service_date = "2024-10-26"
        items = @(
            @{
                code = "99213"
                description = "Office Visit"
                quantity = 1
                unit_price = 150.00
            }
        )
    }
    strategy = "nphies_first"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/claims/submit" -Body $submission -ContentType "application/json"
```

---

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Make sure virtual environment is activated

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Certificate file not found"

**Solution**: Check certificate paths in `.env`

```powershell
# Verify paths
Get-Content .env | Select-String "CERT_PATH"

# Check if files exist
Test-Path $env:NPHIES_CERT_PATH
```

### Issue: "Port 8000 already in use"

**Solution**: Use a different port or stop the conflicting process

```powershell
# Use different port
uvicorn main:app --reload --port 8001

# Or find and stop process using port 8000
Get-Process | Where-Object {$_.ProcessName -like "*python*"}
```

### Issue: "NPHIES authentication failed"

**Solution**: Check certificate validity and credentials

```powershell
# Verify certificate expiration
# Check in .env that paths are correct
# Ensure NPHIES_CERT_PASSWORD is set if certificate is encrypted
```

### Issue: "Connection timeout"

**Solution**: Check network connectivity

```powershell
# Test NPHIES connectivity
Test-NetConnection -ComputerName HSB.nphies.sa -Port 443

# Test OASES branch connectivity
Test-NetConnection -ComputerName 128.1.1.185 -Port 443
```

---

## 📊 Monitoring

### View Logs

```powershell
# View real-time logs
Get-Content logs\brainsait_nphies.log -Wait -Tail 50

# View recent errors
Get-Content logs\brainsait_nphies.log | Select-String "ERROR"
```

### Check System Health

```powershell
# All portals
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/"

# Specific portal
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/portal/nphies"

# Specific branch
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/branch/riyadh"
```

### View Active Sessions

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/sessions"
```

---

## 🛑 Stopping the Application

Press `Ctrl+C` in the terminal where the app is running.

Or find and stop the process:

```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process
```

---

## 📚 Next Steps

1. **Read Documentation**:
   - `README.md` - Complete platform overview
   - `docs/NPHIES_INTEGRATION_GUIDE.md` - NPHIES implementation details
   - `IMPLEMENTATION_SUMMARY.md` - What we built

2. **Configure Credentials**:
   - Update all portal credentials in `.env`
   - Test connectivity to each portal
   - Verify OASES U2415 credentials

3. **Test Integrations**:
   - Test NPHIES eligibility check
   - Test GIVC AI validation
   - Test claim submission

4. **Production Deployment**:
   - Set `DEBUG=False` in `.env`
   - Configure production database
   - Set up monitoring and alerts
   - Configure backup certificates

---

## 🆘 Need Help?

- **Logs**: Check `logs/brainsait_nphies.log`
- **API Docs**: http://localhost:8000/docs
- **Configuration**: Review `.env` and `config/config.yaml`
- **NPHIES Guide**: `docs/NPHIES_INTEGRATION_GUIDE.md`

---

## ✅ Verification Checklist

Before going to production:

- [ ] Application starts without errors
- [ ] API documentation accessible
- [ ] Health check returns "ok"
- [ ] NPHIES certificates valid
- [ ] All portal credentials configured
- [ ] Network connectivity verified
- [ ] Logs directory created
- [ ] Database connected (if using)
- [ ] Redis connected (if using)
- [ ] GIVC AI validation works
- [ ] Test claim submission successful

---

**You're all set! 🎉**

The BrainSAIT-NPHIES-GIVC integration platform is ready for testing and deployment.

**API Base URL**: http://localhost:8000  
**Documentation**: http://localhost:8000/docs  
**Version**: 2.0.0
