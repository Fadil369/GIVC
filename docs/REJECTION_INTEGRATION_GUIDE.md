# ClaimLinc Payer Portal Rejection Management Integration Guide

**Version:** 2.1
**Date:** 2025-11-08
**Author:** Dr. Fadil — BrainSAIT LTD
**Status:** Integration Guide for Developers

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [API Endpoints](#api-endpoints)
7. [Integration Guide](#integration-guide)
8. [Deployment](#deployment)
9. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
10. [Best Practices](#best-practices)

---

## 🎯 Overview

The **Payer Portal Rejection Management System** is a comprehensive automated solution for:

- **Continuous Monitoring:** Real-time detection of rejection sheets from payer portals
- **Automated Extraction:** Download and normalize Excel/CSV rejection reports
- **AI-Driven Analysis:** Identify patterns, root causes, and corrective actions
- **Branch Routing:** Distribute actionable intelligence to hospital branches
- **Resubmission Tracking:** Queue and monitor corrected claim resubmissions
- **Compliance Auditing:** Full audit trail for regulatory compliance

### Key Features

✅ Automated portal monitoring for Bupa, GlobeMed, Waseel/NPHIES
✅ Multi-format rejection sheet normalization (Excel, CSV, FHIR)
✅ AI-powered root cause analysis and recommendations
✅ Real-time branch notifications via email & Teams
✅ Rejection resubmission queue management
✅ PostgreSQL-backed persistent storage
✅ Grafana/Prometheus monitoring integration
✅ PDPL & HIPAA compliance built-in

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   Payer Portals (Bupa, GlobeMed, Waseel)│
└──────────────────┬──────────────────────┘
                   │ Monitor & Download
┌──────────────────▼──────────────────────┐
│    Portal Monitoring Service             │
│    (Playwright Bots + RejectionMonitor)  │
└──────────────────┬──────────────────────┘
                   │ Files
┌──────────────────▼──────────────────────┐
│    Rejection Processor                   │
│    (Normalize & Validate)                │
└──────────────────┬──────────────────────┘
                   │ Records
┌──────────────────▼──────────────────────┐
│    AI Analyzer                           │
│    (Pattern Detection & Insights)        │
└──────────────────┬──────────────────────┘
                   │ Analysis
┌──────────────────▼──────────────────────┐
│    Branch Router & Notifications         │
│    (Email, Teams, Internal)              │
└──────────────────┬──────────────────────┘
                   │ Acknowledgments
┌──────────────────▼──────────────────────┐
│    Resubmission Queue                    │
│    (Corrections & Tracking)              │
└─────────────────────────────────────────┘
```

---

## 🧩 Components

### 1. **Rejection Processor** (`scripts/data-processing/rejection_processor.py`)

Handles extraction and normalization of rejection sheets.

**Key Classes:**
- `RejectionProcessor`: Main processor for all payer formats
- `RejectionRecord`: Standardized rejection record
- `RejectionReasonCode`: Enumeration of standardized rejection codes
- `RejectionSeverity`: Severity classification (critical, high, medium, low)

**Supported Formats:**
- Bupa Arabia Excel exports
- GlobeMed CSV/Excel reports
- Waseel/Tawuniya FHIR-based responses
- Generic Excel/CSV (auto-detection)

### 2. **AI Analyzer** (`automation/ai-analyzer/rejection_analyzer.py`)

Performs AI-driven analysis of rejection patterns.

**Key Capabilities:**
- Root cause analysis
- Pattern detection
- Predictions and trends
- Actionable recommendations
- Branch-specific insights

### 3. **Portal Monitoring** (`automation/portal-bots/rejection_monitor.py`)

Extends existing portal bots to monitor rejection sheets.

**Key Classes:**
- `RejectionMonitor`: Base monitoring class
- `BupaRejectionMonitor`: Bupa-specific monitoring
- `GlobeMedRejectionMonitor`: GlobeMed-specific monitoring
- `WaseelRejectionMonitor`: Waseel/NPHIES-specific monitoring
- `RejectionMonitoringService`: Orchestration service

### 4. **Notification Service** (`api/services/notification_service.py`)

Routes rejection reports to appropriate channels and branches.

**Key Classes:**
- `EmailService`: Email notifications
- `TeamsNotificationService`: Microsoft Teams integration
- `NotificationRouter`: Intelligent routing to branches
- `BranchConfig`: Centralized branch configuration

### 5. **API Endpoints** (`api/routers/rejection_operations.py`)

RESTful API for rejection management operations.

**Key Endpoints:**
- `POST /api/v1/rejections/upload` - Upload rejection sheet
- `GET /api/v1/rejections/analysis/{branch}` - Get branch analysis
- `POST /api/v1/rejections/acknowledge` - Acknowledge report
- `POST /api/v1/rejections/resubmit` - Prepare resubmission
- `POST /api/v1/rejections/run-full-cycle` - Execute monitoring cycle

### 6. **Monitoring & Metrics** (`api/monitoring/rejection_metrics.py`)

Prometheus metrics and health checks.

**Key Features:**
- Rejection processing metrics
- Portal health monitoring
- System health checks
- Alert generation

---

## 📦 Installation & Setup

### Prerequisites

```bash
# System requirements
- Python 3.9+
- PostgreSQL 13+
- Redis 6.0+
- Playwright (browser automation)

# Python dependencies
pip install -r deployment/requirements-secure.txt
pip install -e .
```

### Step 1: Install Dependencies

```bash
# Install core dependencies
pip install fastapi uvicorn pydantic

# Install data processing dependencies
pip install pandas openpyxl sqlalchemy psycopg2-binary

# Install Playwright for portal automation
pip install playwright
playwright install chromium

# Install monitoring
pip install prometheus-client
```

### Step 2: Database Setup

```bash
# Run migration to create rejection tracking tables
psql -h localhost -U postgres -d claimlinc < deployment/migrations/001_add_rejection_tracking.sql

# Verify tables created
psql -h localhost -U postgres -d claimlinc -c "\dt rejection*"
```

### Step 3: Environment Configuration

```bash
# Copy template to .env
cp .env.rejection.template .env.local

# Edit with your values
nano .env.local

# Required variables:
# - BUPA_USERNAME, BUPA_PASSWORD
# - GLOBEMED_USERNAME, GLOBEMED_PASSWORD
# - WASEEL_USERNAME, WASEEL_PASSWORD
# - DATABASE_URL
# - EMAIL_OPS_* (branch email addresses)
```

### Step 4: Verify Installation

```bash
# Test rejection processor
python -c "from scripts.data_processing.rejection_processor import RejectionProcessor; print('✅ RejectionProcessor imported successfully')"

# Test AI analyzer
python -c "from automation.ai_analyzer.rejection_analyzer import RejectionAnalyzer; print('✅ RejectionAnalyzer imported successfully')"

# Test notification service
python -c "from api.services.notification_service import NotificationRouter; print('✅ NotificationRouter imported successfully')"
```

---

## ⚙️ Configuration

### Environment Variables

See `.env.rejection.template` for complete reference. Key sections:

#### Payer Credentials (Vault in production)
```env
BUPA_USERNAME=your_bupa_username
BUPA_PASSWORD=your_bupa_password
GLOBEMED_USERNAME=your_globemed_username
GLOBEMED_PASSWORD=your_globemed_password
WASEEL_USERNAME=your_waseel_username
WASEEL_PASSWORD=your_waseel_password
```

#### Branch Routing
```env
EMAIL_OPS_RIYADH=ops.riyadh@alhayat.example
TEAMS_RIYADH=teams://AlHayat/MainRiyadh/Claims
# ... repeat for other branches
```

#### Portal Monitoring
```env
ENABLE_REJECTION_MONITORING=true
BUPA_MONITORING_INTERVAL=1800        # 30 minutes
GLOBEMED_MONITORING_INTERVAL=1800    # 30 minutes
WASEEL_MONITORING_INTERVAL=3600      # 1 hour
REJECTION_CYCLE_SCHEDULE=0 */6 * * *  # Every 6 hours
```

#### Database
```env
DATABASE_URL=postgresql://user:password@localhost:5432/claimlinc_rejections
```

---

## 🔌 API Endpoints

### Upload Rejection Sheet

```bash
POST /api/v1/rejections/upload

# Request
curl -X POST http://localhost:8088/api/v1/rejections/upload \
  -F "payer=bupa" \
  -F "branch=MainRiyadh" \
  -F "file=@rejections_2025_11_08.xlsx"

# Response
{
  "status": "success",
  "message": "Successfully processed 23 rejection records from bupa",
  "data": {
    "records_processed": 23,
    "summary": { ... },
    "analysis": { ... }
  }
}
```

### Get Branch Analysis

```bash
GET /api/v1/rejections/analysis/{branch}

# Example
curl http://localhost:8088/api/v1/rejections/analysis/MainRiyadh?days=30

# Response includes full analysis with recommendations
```

### Acknowledge Report

```bash
POST /api/v1/rejections/acknowledge

curl -X POST http://localhost:8088/api/v1/rejections/acknowledge \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "MainRiyadh",
    "user": "ops_manager@example.com",
    "comments": "Received and will process"
  }'
```

### Prepare Resubmission

```bash
POST /api/v1/rejections/resubmit

curl -X POST http://localhost:8088/api/v1/rejections/resubmit \
  -H "Content-Type: application/json" \
  -d '{
    "rejection_ids": ["CLM-001", "CLM-002"],
    "corrections": {
      "CLM-001": { "member_id": "corrected_id" }
    },
    "target_submission_date": "2025-11-09"
  }'
```

### Run Full Cycle

```bash
POST /api/v1/rejections/run-full-cycle

curl -X POST http://localhost:8088/api/v1/rejections/run-full-cycle

# Returns cycle_id to track progress
```

---

## 🔗 Integration Guide

### 1. Integrate with Main API (`api/main.py`)

```python
from api.routers.rejection_operations import router as rejection_router

# In app initialization
app.include_router(rejection_router)
```

### 2. Set Up Scheduled Rejection Monitoring

Using Celery or APScheduler:

```python
from automation.portal_bots.rejection_monitor import RejectionMonitoringService
import asyncio

@scheduler.scheduled_job('cron', hour='*/6')
def scheduled_rejection_cycle():
    """Run full rejection monitoring cycle every 6 hours"""
    service = RejectionMonitoringService()
    credentials = {
        "bupa": {"username": os.getenv("BUPA_USERNAME"), "password": os.getenv("BUPA_PASSWORD")},
        "globemed": {"username": os.getenv("GLOBEMED_USERNAME"), "password": os.getenv("GLOBEMED_PASSWORD")},
        "waseel": {"username": os.getenv("WASEEL_USERNAME"), "password": os.getenv("WASEEL_PASSWORD")}
    }
    result = asyncio.run(service.monitor_all_payers(credentials))
    print(f"✅ Rejection cycle completed: {result}")
```

### 3. Integrate with n8n Workflows

Create n8n workflow to:

1. Trigger API endpoint
2. Process results
3. Send notifications
4. Update database

```
[Trigger] → [Call API] → [Process Data] → [Send Notifications] → [Update DB]
```

### 4. Dashboard Integration

Add rejection metrics to your dashboard:

```html
<!-- Add to dashboard HTML -->
<div id="rejection-stats">
  <div class="stat">
    <span class="label">Critical Rejections (7d)</span>
    <span class="value" id="critical-count">0</span>
  </div>
  <div class="stat">
    <span class="label">Amount at Risk</span>
    <span class="value" id="at-risk-amount">SAR 0</span>
  </div>
</div>

<script>
// Fetch rejection metrics
fetch('/api/v1/rejections/summary/MainRiyadh?days=7')
  .then(r => r.json())
  .then(data => {
    document.getElementById('critical-count').textContent =
      data.data.by_severity.critical;
    document.getElementById('at-risk-amount').textContent =
      `SAR ${data.data.total_at_risk.toLocaleString()}`;
  });
</script>
```

---

## 🚀 Deployment

### Development Environment

```bash
# Terminal 1: Start FastAPI server
cd /home/user/GIVC
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8088

# Terminal 2: Run scheduled jobs (if using Celery)
celery -A api.tasks worker --loglevel=info

# Terminal 3: Optional - Run monitoring manually
python -c "
from automation.portal_bots.rejection_monitor import monitor_payer_rejections
import asyncio
result = asyncio.run(monitor_payer_rejections('bupa', username, password))
print(result)
"
```

### Docker Deployment

```dockerfile
# Create Dockerfile with rejection services
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY deployment/requirements-secure.txt .
RUN pip install -r requirements-secure.txt
RUN playwright install chromium

# Copy application
COPY . .

# Expose API port
EXPOSE 8088

# Run API server
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8088"]
```

### Coolify Deployment

```yaml
# coolify-compose.yml
version: '3.8'
services:
  api:
    image: claimlinc-api:latest
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/claimlinc
      - BUPA_USERNAME=${BUPA_USERNAME}
      - BUPA_PASSWORD=${BUPA_PASSWORD}
      # ... other env vars
    ports:
      - "8088:8088"
    depends_on:
      - db
      - redis

  celery:
    image: claimlinc-api:latest
    command: celery -A api.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/claimlinc
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: claimlinc
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 📊 Monitoring & Troubleshooting

### Health Checks

```bash
# Check system health
curl http://localhost:8088/api/v1/rejections/health

# Check portal status
curl http://localhost:8088/api/v1/rejections/portal-status

# Check metrics
curl http://localhost:8088/metrics
```

### Common Issues

#### Issue: Portal Login Failures
```
Solution: Verify credentials in .env, check if payer changed portal URL
```

#### Issue: Rejection Files Not Detected
```
Solution: Check portal patterns in RejectionMonitor class, enable debug mode
```

#### Issue: Notifications Not Sent
```
Solution: Verify SMTP/Teams credentials, check email logs
```

#### Issue: Database Connection Error
```
Solution: Verify DATABASE_URL, ensure PostgreSQL is running, check permissions
```

### Logging

```bash
# Enable debug logging
export DEBUG_MODE=true
export API_LOG_LEVEL=DEBUG

# View logs
tail -f /var/log/claimlinc/api.log

# Search for errors
grep "ERROR" /var/log/claimlinc/api.log
```

---

## 📋 Best Practices

### Security

✅ **Credential Management**
- Use HashiCorp Vault in production
- Never commit credentials to git
- Rotate credentials every 90 days

✅ **PHI Protection**
- Enable PHI masking in production
- Hash patient identifiers before logging
- Encrypt data at rest (AES-256)

✅ **Audit Logging**
- All operations logged with user/timestamp
- Maintain 6-year audit trail per PDPL
- Regular audit log reviews

### Performance

✅ **Database**
- Add indexes on frequently queried columns
- Archive old records (>1 year) to separate storage
- Monitor query performance with EXPLAIN ANALYZE

✅ **Portal Monitoring**
- Use async/await for concurrent monitoring
- Set reasonable timeouts (5 min per portal)
- Implement exponential backoff for retries

✅ **API**
- Rate limit API endpoints (100 req/min)
- Use pagination for large result sets
- Cache frequently accessed data in Redis

### Operations

✅ **Monitoring**
- Set up Grafana dashboards
- Create alerts for critical issues
- Review metrics daily

✅ **Maintenance**
- Weekly backup of rejection data
- Monthly review of rejection patterns
- Quarterly performance optimization

✅ **Updates**
- Test updates in staging first
- Plan maintenance windows
- Document all changes

---

## 📞 Support

For issues or questions:

1. **Check logs:** `/var/log/claimlinc/api.log`
2. **Review docs:** This guide and inline code comments
3. **Test manually:** Use cURL/Postman to test endpoints
4. **Contact:** support@brainsait.io

---

## 🔄 Changelog

### v2.1 (2025-11-08)
- ✨ Initial release with payer portal integration
- ✨ AI-driven rejection analysis
- ✨ Branch routing and notifications
- ✨ Comprehensive monitoring

---

**Last Updated:** 2025-11-08
**Maintainer:** Dr. Fadil — BrainSAIT LTD
