# BrainSAIT RCM - OASIS+/NPHIES Claims Management System

## 🏥 Overview

Enterprise-grade Healthcare Revenue Cycle Management (RCM) platform for Saudi Arabia's healthcare ecosystem. Integrates with NPHIES (National Platform for Health Insurance Exchange Services) and OASIS+ legacy systems.

## 🎯 Key Features

- **Multi-Method Authentication**: OAuth (Google, GitHub), OTP (Email, SMS, WhatsApp), Traditional Email/Password
- **NPHIES Integration**: Full FHIR R4 compliance with NPHIES Minimum Data Set (MDS)
- **OASIS+ Bridge**: Automated integration with legacy OASIS+ system via UI automation
- **AI-Powered Intelligence**: Fraud detection, predictive analytics, denial risk scoring
- **Denial Command Center**: Real-time denial management with 48-hour SLA tracking
- **Bilingual Support**: Full Arabic/English localization with RTL support
- **Zero Trust Security**: Cloudflare Access, end-to-end encryption, comprehensive audit logging

## 📁 Project Structure

```
oaises+/
├── apps/
│   ├── api/                    # FastAPI Backend
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── lib/
│   └── web/                    # Next.js Frontend
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   └── lib/
│       ├── public/
│       └── package.json
├── services/
│   ├── oasis-integration/      # OASIS+ Bridge Service
│   ├── fhir-gateway/           # FHIR Validation & Mapping
│   ├── ai-ml/                  # AI/ML Models
│   └── audit/                  # Audit Logging
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   └── cloudflare/
├── docs/
└── tests/
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB 6.0+
- Redis 7.0+
- Docker & Docker Compose (optional)

### Installation

1. **Clone and setup environment**
```bash
git clone <repository>
cd oaises+
cp .env.example .env
# Edit .env with your credentials
```

2. **Backend Setup**
```bash
cd apps/api
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

3. **Frontend Setup**
```bash
cd apps/web
npm install
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Docker Deployment

```bash
docker-compose up -d
```

## 🔐 Authentication

### Super Admin Setup (First Time)
```bash
curl -X POST http://localhost:8000/api/v1/auth/super-admin/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@brainsait.com",
    "password": "SecurePassword123!",
    "full_name": "System Administrator"
  }'
```

### Login Methods

1. **Email/Password**
2. **Google OAuth**
3. **GitHub OAuth**
4. **Email OTP**
5. **SMS OTP**
6. **WhatsApp OTP**

## 📡 API Endpoints

### Core Services

- `POST /api/v1/auth/login` - Authenticate user
- `GET /api/rejections/current-month` - Get current rejections
- `POST /api/nphies/submit-claim` - Submit to NPHIES
- `POST /api/oasis/submit` - Submit to OASIS+
- `POST /api/ai/fraud-detection` - Run fraud analysis
- `POST /api/fhir/validate` - Validate FHIR resources
- `POST /api/appeals` - Create appeal
- `GET /api/analytics/dashboard` - Dashboard analytics

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference.

## 🏗️ Architecture

### Backend Stack
- **API Framework**: FastAPI (async)
- **Database**: MongoDB with Motor (async driver)
- **Caching**: Redis
- **Authentication**: JWT with refresh tokens
- **Validation**: Pydantic V2
- **AI/ML**: scikit-learn, transformers

### Frontend Stack
- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS, Framer Motion
- **State**: React Hooks, Context API
- **HTTP Client**: Axios
- **Localization**: next-intl (AR/EN)

### Integration Layer
- **NPHIES**: FHIR R4 REST API
- **OASIS+**: Playwright UI automation
- **Notifications**: Twilio (SMS, WhatsApp)
- **Document AI**: Tesseract OCR + spaCy NLP

## 🔒 Security

- **Encryption**: AES-256 for PHI data
- **Authentication**: Multi-factor with JWT
- **Authorization**: Role-Based Access Control (RBAC)
- **Network**: Cloudflare Zero Trust Access
- **Audit**: Comprehensive logging to immutable store
- **Compliance**: HIPAA, NPHIES, CHI standards

## 📊 Key Performance Indicators (KPIs)

- **FPCCR**: First Pass Clean Claim Rate
- **DRR**: Denial Recovery Rate
- **Appeal Cycle Time**: Average days to resolution
- **Denial Rate by Payer**: Percentage by insurance provider
- **Reimbursement Success Rate**: Approved claims percentage

## 🌐 OASIS+ Integration

The system integrates with the legacy OASIS+ platform:

- **URL**: http://128.1.1.185/prod/faces/Home
- **Method**: UI automation via Playwright
- **Authentication**: Credential-based login
- **Workflow**: Automated form filling and submission

See [OASIS_INTEGRATION_PLAN.md](./OASIS_INTEGRATION_PLAN.md) for details.

## 🧪 Testing

```bash
# Backend tests
cd apps/api
pytest tests/ -v --cov

# Frontend tests
cd apps/web
npm test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e
```

## 📦 Deployment

### Staging
```bash
npm run deploy:staging
```

### Production
```bash
npm run deploy:production
```

### Cloudflare Workers
```bash
cd apps/web
wrangler deploy
```

## 🔧 Configuration

### Environment Variables

Key variables in `.env`:

- `DATABASE_URL`: MongoDB connection string
- `NPHIES_API_KEY`: NPHIES authentication key
- `JWT_SECRET`: Secret for JWT signing
- `REDIS_URL`: Redis connection string
- `SMTP_*`: Email configuration for notifications

See `.env.example` for complete list.

## 📈 Monitoring

- **Health Check**: `/health` endpoint
- **Metrics**: Prometheus metrics at `/metrics`
- **Logs**: Structured JSON logging
- **Tracing**: OpenTelemetry instrumentation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

Proprietary - BrainSAIT Healthcare Technologies

## 📞 Support

- **Email**: support@brainsait.com
- **Documentation**: https://docs.brainsait.com
- **Status**: https://status.brainsait.com

## 🗺️ Roadmap

- [x] Core authentication system
- [x] NPHIES integration
- [x] OASIS+ bridge
- [x] AI fraud detection
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant support
- [ ] API rate limiting v2
- [ ] GraphQL API

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Maintainer**: BrainSAIT Development Team
