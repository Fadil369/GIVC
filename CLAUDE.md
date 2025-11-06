# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ClaimLinc-GIVC** is a comprehensive healthcare claims automation and management platform for the Saudi Arabian healthcare ecosystem. It combines a web-based SaaS dashboard, RESTful API backend, workflow orchestration, and automated payer portal integration.

### Technology Stack

**Backend:**
- FastAPI 0.104.1 + Uvicorn 0.24.0 (Python async web framework)
- SQLAlchemy 2.0 + PostgreSQL (data persistence)
- Celery 5.3.4 + RabbitMQ (distributed task queue)
- Redis (caching and Celery result backend)
- Playwright 1.40.0 (browser automation)

**Frontend:**
- Web Dashboard: Vanilla JavaScript (ES6+), HTML5, CSS3 (in `web-app/`)
- OAISES+ Project: Next.js 14.0.4 + React 18.2.0 (in `projects/oaises+/`)
- UI: Radix UI, Tailwind CSS, Framer Motion, Lucide React
- Charts: Chart.js 4.4.0, Recharts 2.10.3

**Workflow & Integration:**
- n8n (visual workflow orchestration)
- NPHIES API (Saudi National Platform for Health Insurance Exchange)
- FHIR R4 compliance

**Security & Monitoring:**
- HashiCorp Vault (secrets management)
- Prometheus + Flower (monitoring)
- Structlog (structured logging)

## Repository Structure

```
ClaimLinc-GIVC/
├── web-app/                      # Standalone web dashboard (HTML/JS/CSS)
│   ├── index.html               # Main dashboard with analytics and collaboration
│   ├── app.js                   # Application logic (1000+ lines)
│   └── styles.css               # Comprehensive styling
│
├── api/                         # FastAPI backend service
│   └── main.py                  # Main API with endpoints (see below)
│
├── automation/                  # Portal automation & workflows
│   ├── portal-bots/            # Playwright browser automation
│   │   ├── bupa_bot.py         # Bupa Arabia portal automation
│   │   ├── globemed_bot.py     # GlobeMed portal automation
│   │   └── waseel_bot.py       # Waseel/Tawuniya portal automation
│   └── workflows/              # n8n workflow definitions (JSON)
│
├── scripts/                     # Data processing utilities
│   └── data-processing/
│       ├── normalize_data.py   # Multi-format claim normalization
│       ├── validate_data.py    # Claim validation & compliance
│       └── generate_test_data.py # Test data generation
│
├── projects/                    # Larger integrated projects
│   └── oaises+/                # Next.js + FastAPI monorepo
│       ├── apps/               # web (Next.js), api (FastAPI), mobile (React Native)
│       ├── packages/           # claims-engine, rejection-tracker, compliance-reporter
│       └── docker-compose.yml  # Multi-container orchestration
│
├── nphies-data/                # NPHIES integration data
├── branches/                   # Branch-specific files (e.g., 484600-khamis/)
├── config/                     # Configuration and security
├── deployment/                 # Deployment artifacts
│   └── requirements-secure.txt # Locked Python dependencies
└── docs/                       # Project documentation
```

## Development Commands

### Python Backend (FastAPI)

```bash
# Install dependencies
pip install -r deployment/requirements-secure.txt

# Install Playwright browsers (required for portal automation)
playwright install chromium

# Start FastAPI development server
cd api
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API documentation available at:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Testing

```bash
# Run pytest tests
pytest

# Run with coverage
pytest --cov

# Run with async support
pytest --asyncio-mode=auto

# Lint and format
black .
flake8
mypy .

# Security scanning
bandit -r .
safety check
```

### Portal Automation Bots

```bash
# Test individual portal bots
cd automation/portal-bots

# Set credentials as environment variables
export BUPA_USERNAME="your_username"
export BUPA_PASSWORD="your_password"

# Run bot in non-headless mode for debugging
python bupa_bot.py
python globemed_bot.py
python waseel_bot.py
```

### Data Processing Scripts

```bash
# Normalize claim data
cd scripts/data-processing
python normalize_data.py

# Validate claims
python validate_data.py

# Generate test data
python generate_test_data.py
```

### OAISES+ Monorepo (Next.js)

```bash
cd projects/oaises+

# Install dependencies
npm install

# Start development servers
npm run dev              # Next.js web app (port 3000)

# Start with Docker
docker-compose up -d

# Database migrations
npm run db:migrate

# Build for production
npm run build
docker-compose build
```

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────┐
│  Presentation Layer                         │
│  - Web Dashboard (HTML/JS)                  │
│  - Next.js App (React)                      │
└─────────────────┬───────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────┐
│  API Gateway                                │
│  - FastAPI (api/main.py)                    │
│  - Endpoints: normalize, validate, batch    │
└─────────────────┬───────────────────────────┘
                  │ Task Queues
┌─────────────────▼───────────────────────────┐
│  Service Layer                              │
│  - Celery Workers                           │
│  - n8n Workflows                            │
│  - Portal Bots (Playwright)                 │
└─────────────────┬───────────────────────────┘
                  │ ORM/Cache
┌─────────────────▼───────────────────────────┐
│  Data Layer                                 │
│  - PostgreSQL (claims storage)              │
│  - MongoDB (OAISES+ project)                │
│  - Redis (cache + Celery backend)           │
└─────────────────────────────────────────────┘
```

### Core Data Flow: Claim Submission

1. **User submits claim** via Web Dashboard → FastAPI POST `/api/v1/normalize`
2. **API normalizes claim** using `ClaimDataNormalizer` (handles Bupa/GlobeMed/Waseel formats)
3. **API validates claim** using `ClaimDataValidator` (compliance & quality checks)
4. **Async task queued** → Celery → n8n webhook triggers workflow
5. **Portal bot executes** → Playwright automates payer portal login + upload
6. **Status update** → Webhook callback or polling → Dashboard notification

### API Endpoints (`api/main.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | System info and available endpoints |
| `/health` | GET | Health check with service status |
| `/api/v1/normalize` | POST | Normalize single claim to standard format |
| `/api/v1/validate` | POST | Validate claim for quality & compliance |
| `/api/v1/batch` | POST | Process multiple claims in batch |
| `/api/v1/test-data/generate` | POST | Generate synthetic test claims |
| `/api/v1/automation/submit/{payer}` | POST | Submit claim to payer (bupa/globemed/waseel) |
| `/api/v1/workflow/status/{submission_id}` | GET | Check workflow submission status |
| `/api/v1/export/csv` | POST | Export claims to CSV |
| `/api/v1/download/{filename}` | GET | Download exported file |
| `/api/v1/system/stats` | GET | System statistics and health metrics |

## Key Implementation Patterns

### 1. Claim Data Normalization

The `ClaimDataNormalizer` class (`scripts/data-processing/normalize_data.py`) converts multiple payer formats into a standardized internal format:

- **Standard Format Fields:**
  - `claim_id`, `provider` (name, code, branch)
  - `patient` (member_id, name, national_id, dob, gender)
  - `claim_details` (service_date, total_amount, diagnosis_codes, procedure_codes)
  - `payer` (name, insurance_type, policy_number)
  - `submission` (method, timestamp, batch_id, status)

- **Supported Formats:**
  - `bupa` → Bupa Arabia format
  - `globemed` → GlobeMed format
  - `waseel` → Waseel/Tawuniya FHIR format (handles FHIR Bundle resources)
  - `generic` → Auto-maps common field names

**Usage:**
```python
from scripts.normalize_data import ClaimDataNormalizer

normalizer = ClaimDataNormalizer()
normalized = normalizer.normalize_claim(raw_claim_data, source_format="bupa")
batch_normalized = normalizer.batch_normalize(claims_list, source_format="globemed")
```

### 2. Portal Automation Architecture

Each portal bot (`automation/portal-bots/*.py`) follows this pattern:

```python
async with BupaPortalBot(headless=True) as bot:
    # 1. Login
    success = await bot.login(username, password)

    # 2. Navigate to claims section
    await bot.navigate_to_claims_section()

    # 3. Upload claim file
    submission_id = await bot.upload_claim_file(file_path)

    # 4. Check status
    status = await bot.check_claim_status(submission_id)

    # 5. Download reports (optional)
    report_path = await bot.download_rejection_report()
```

**Portal Bot Features:**
- Async/await pattern with context managers
- Headless/headed mode toggle for debugging
- Robust selector fallbacks for UI changes
- Automatic error handling and logging
- Download management with timestamped files

### 3. Branch Name Normalization

The system standardizes branch names across all data sources:

```python
branch_mapping = {
    "riyadh" → "MainRiyadh",
    "unaizah" → "Unaizah",
    "abha" → "Abha",
    "madinah" → "Madinah",
    "khamis mushait" → "Khamis"
}
```

Always use standardized branch names when creating or processing claims.

### 4. n8n Workflow Integration

Workflows are defined in `automation/workflows/*.json` and triggered via webhooks:

- **Bupa Workflow:** `http://localhost:5678/webhook/claimlinc-bupa`
- **GlobeMed Workflow:** `http://localhost:5678/webhook/claimlinc-globemed`
- **Waseel Workflow:** `http://localhost:5678/webhook/claimlinc-waseel`

Workflow steps typically include:
1. Receive normalized claim data
2. Trigger corresponding portal bot
3. Monitor submission status
4. Update database with results
5. Send notifications

## Compliance & Security

### HIPAA & PDPL Compliance
- All patient data (PHI) must be encrypted at rest
- Audit logging required for all data access operations
- 6-year audit trail retention per Saudi regulations
- Never log sensitive data (PHI, credentials) to console/standard logs

### NPHIES Integration
- All claims must be validated against NPHIES FHIR R4 specifications
- 30-day response deadline per Saudi health insurance regulations
- Track reception mode: 'NPHIES', 'PORTAL', or 'EMAIL'
- Include NPHIES reference numbers in all compliance documents

### Secrets Management
- Store credentials in environment variables (never hardcode)
- Use HashiCorp Vault for production secrets (planned in BUILD_PLAN.md)
- Supported payer credentials: `BUPA_USERNAME`, `BUPA_PASSWORD`, `GLOBEMED_*`, `WASEEL_*`

### Security Best Practices
- JWT authentication for API endpoints (when implemented)
- TLS 1.3 encryption for all external communications
- Input validation on all API endpoints (Pydantic models)
- Rate limiting on public endpoints
- SQL injection prevention via SQLAlchemy ORM

## Common Development Tasks

### Adding a New Payer Integration

1. **Create Portal Bot:** Add new file in `automation/portal-bots/new_payer_bot.py`
   - Inherit common patterns from existing bots
   - Implement: `login()`, `navigate_to_claims_section()`, `upload_claim_file()`

2. **Create Normalizer:** Add method `_normalize_new_payer_format()` in `scripts/data-processing/normalize_data.py`
   - Map payer-specific fields to standard format
   - Handle payer-specific date formats and codes

3. **Create n8n Workflow:** Export workflow JSON to `automation/workflows/claimlinc-new-payer-workflow.json`

4. **Add API Endpoint:** Update `api/main.py` to handle new payer in `/api/v1/automation/submit/{payer}`

5. **Update Tests:** Add test cases for new payer format in test suite

### Running End-to-End Tests

```bash
# 1. Start all services
cd projects/oaises+ && docker-compose up -d
cd ../../api && python main.py

# 2. Generate test data
curl -X POST http://localhost:8000/api/v1/test-data/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 10, "payer_format": "bupa"}'

# 3. Submit test claim
curl -X POST http://localhost:8000/api/v1/automation/submit/bupa \
  -H "Content-Type: application/json" \
  -d @data/samples/bupa-claim-sample.json

# 4. Check status
curl http://localhost:8000/api/v1/workflow/status/{submission_id}
```

### Debugging Portal Automation

1. **Run bot in headed mode** (non-headless):
   ```python
   bot = BupaPortalBot(headless=False)  # Browser window will be visible
   ```

2. **Add screenshots at key steps:**
   ```python
   await self.page.screenshot(path=f"debug_{datetime.now()}.png")
   ```

3. **Increase timeout for slow portals:**
   ```python
   await self.page.wait_for_selector("#element", timeout=60000)  # 60 seconds
   ```

4. **Check browser console logs:**
   ```python
   self.page.on("console", lambda msg: print(f"Console: {msg.text}"))
   ```

## Multi-Project Workspace

This repository contains multiple related projects:

### 1. Root Level (Standalone Components)
- **web-app/**: Simple HTML/JS dashboard for quick deployment
- **api/**: FastAPI backend (can run independently)
- **automation/**: Portal bots and workflows (shared by all projects)
- **scripts/**: Data processing utilities (shared library)

### 2. OAISES+ Monorepo (`projects/oaises+/`)
- Full-featured Next.js application with React frontend
- See `projects/oaises+/CLAUDE.md` for specific guidance
- Includes rejection tracking, compliance reporting, mobile app
- Uses MongoDB + Redis (different from root-level PostgreSQL)

### 3. NPHIES Data (`nphies-data/`)
- Real production data for NPHIES submissions
- Organized by branch and submission period
- Do not modify without understanding impact on historical records

### 4. Branch-Specific Files (`branches/`)
- Files specific to individual hospital branches
- Example: `branches/484600-khamis/` for Khamis Mushait branch

## Testing Notes

- Mock external payer portals in tests (never hit real portals in CI/CD)
- Use `TestDataGenerator` class for consistent test data
- Test all three payer formats: Bupa, GlobeMed, Waseel
- Verify FHIR validation with valid/invalid test cases
- Test portal automation with VCR.py or similar HTTP recording

## Performance Considerations

- **Batch Processing**: Use `/api/v1/batch` endpoint for multiple claims (more efficient)
- **Async Tasks**: Long-running portal operations should use Celery (not synchronous API calls)
- **Caching**: Redis cache frequently accessed reference data (diagnosis codes, provider info)
- **Database Indexes**: Ensure indexes on `claim_id`, `patient.member_id`, `submission.timestamp`
- **Rate Limiting**: Portal bots should respect payer rate limits (avoid account suspension)

## Deployment

- **Development**: Run services locally (FastAPI + web-app)
- **Staging**: Use `projects/oaises+/docker-compose.yml` for multi-container setup
- **Production**: Follow BUILD_PLAN.md for Vault + Celery + NPHIES integration
- **Monitoring**: Check logs at `/var/log/brainsait/api.log` (structured JSON format)

## Contact & Support

- **Organization**: BrainSAIT LTD
- **Contact**: Dr. Fadil
- **Email**: support@brainsait.io

## Saudi Healthcare Context

- **30-Day Rule**: Insurance companies must respond to claims within 30 days (Saudi regulation)
- **NPHIES**: National platform mandated by Saudi Health Insurance Council
- **VAT**: 15% value-added tax on medical services
- **Currency**: SAR (Saudi Riyal)
- **Language**: All user-facing content must support Arabic (RTL) and English (LTR)
