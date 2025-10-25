# GIVC Platform - Directory Structure

**Last Updated:** October 22, 2025

---

## 📁 Project Organization

```
GIVC/
├── 📄 Configuration Files (Root)
│   ├── package.json              # Node.js dependencies
│   ├── tsconfig.json             # TypeScript config
│   ├── vite.config.js            # Vite build config
│   ├── tailwind.config.js        # Tailwind CSS config
│   ├── .eslintrc.cjs             # ESLint config
│   ├── .gitignore                # Git ignore rules
│   └── .env                      # Environment variables
│
├── 📚 Documentation (Root - Essential)
│   ├── README.md                 # Main project README
│   ├── LICENSE                   # GPL-3.0 license
│   ├── CONTRIBUTING.md           # Contribution guidelines
│   ├── SECURITY.md               # Security policies
│   ├── PHASE1_PROGRESS.md        # Phase 1 status
│   ├── PHASE2_PROGRESS.md        # Phase 2 status
│   └── CLEANUP_AUDIT.md          # Cleanup audit
│
├── 📖 docs/                       # Additional Documentation
│   ├── ARCHITECTURE.md           # System architecture
│   ├── API_DOCUMENTATION.md      # API reference
│   ├── DESIGN_SYSTEM.md          # UI/UX guidelines
│   ├── DEPLOYMENT_GUIDE.md       # Deployment instructions
│   ├── GETTING_STARTED.md        # Quick start guide
│   ├── QUICK_START.md            # Quick setup
│   ├── oasis_integration/        # OASIS docs
│   └── archive/                  # Historical docs (31 files)
│
├── 🎨 Frontend (React + TypeScript)
│   └── frontend/
│       ├── index.html            # HTML entry point
│       ├── public/               # Static assets
│       └── src/
│           ├── main.tsx          # App entry point
│           ├── App.tsx           # Root component
│           ├── components/       # React components
│           ├── services/         # API services
│           │   ├── api.js
│           │   ├── logger.js
│           │   └── oasisApi.ts   # Backend API client
│           ├── contexts/         # React contexts
│           ├── hooks/            # Custom hooks
│           ├── config/           # Frontend config
│           ├── styles/           # CSS/styling
│           └── types/            # TypeScript types
│
├── 🐍 Backend (Python + FastAPI)
│   ├── fastapi_app.py            # Main FastAPI app
│   ├── main.py                   # NPHIES integration
│   ├── main_enhanced.py          # Enhanced features
│   ├── venv/                     # Python virtual env
│   ├── auth/                     # Authentication
│   │   ├── auth_manager.py
│   │   └── cert_manager.py
│   ├── services/                 # Business logic
│   │   ├── eligibility.py
│   │   ├── claims.py
│   │   ├── prior_authorization.py
│   │   ├── analytics.py
│   │   └── ...
│   ├── config/                   # Configuration
│   │   ├── settings.py
│   │   ├── endpoints.py
│   │   ├── payer_config.py
│   │   └── ...
│   ├── models/                   # Data models
│   │   └── bundle_builder.py
│   ├── pipeline/                 # Data pipeline
│   │   ├── extractor.py
│   │   └── data_processor.py
│   └── utils/                    # Utilities
│       ├── logger.py
│       ├── helpers.py
│       └── validators.py
│
├── 🔧 Scripts & Tools
│   ├── scripts/
│   │   ├── deploy-production.sh
│   │   ├── deploy.sh
│   │   ├── remove_duplicates.sh
│   │   ├── restore_components.sh
│   │   ├── fix_empty_tsx.sh
│   │   ├── phase1_commit.sh
│   │   ├── fix-imports.sh
│   │   └── analysis/             # Analysis tools
│   │       ├── analyze_rcm_data.py
│   │       ├── deep_organizational_analyzer.py
│   │       └── quick_deep_analysis.py
│
├── 📊 Data & Analysis
│   ├── analysis_data/            # Analysis datasets
│   │   ├── MOH NPHIES.xlsx
│   │   ├── TAWUNIYA *.xlsx
│   │   ├── Accounts.xlsx
│   │   ├── network_share_deep_analysis.csv
│   │   ├── RCM_ANALYSIS_INSIGHTS.json
│   │   └── DEEP_ORGANIZATIONAL_INSIGHTS.json
│   └── data/                     # Application data
│       ├── claims_sample.json
│       └── members_sample.csv
│
├── 🧪 Tests
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── setup.ts
│   │   ├── test_auth/
│   │   └── unit/
│   ├── pytest.ini               # Pytest config
│   └── vitest.config.ts         # Vitest config
│
├── 🚀 Deployment & Infrastructure
│   ├── docker/                   # Docker configs
│   ├── workers/                  # Cloudflare Workers
│   │   ├── router.js
│   │   ├── router.ts
│   │   ├── agents/
│   │   ├── middleware/
│   │   └── utils/
│   ├── .github/                  # GitHub Actions
│   │   ├── workflows/
│   │   └── scripts/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── wrangler.toml
│
└── 📦 Build & Dependencies
    ├── dist/                     # Build output
    ├── node_modules/             # Node dependencies
    ├── venv/                     # Python dependencies
    ├── requirements.txt          # Python packages
    ├── requirements_core.txt     # Core Python packages
    └── pyproject.toml            # Python project config
```

---

## 🎯 Key Directories

### Frontend (`frontend/src/`)
- **components/** - React UI components (24 JSX, 12 TSX files)
- **services/** - API clients and utilities
- **contexts/** - React Context providers
- **hooks/** - Custom React hooks
- **config/** - Frontend configuration

### Backend (Root + subdirectories)
- **auth/** - NPHIES authentication & certificates
- **services/** - Business logic (8 services)
- **config/** - Backend configuration (9 config files)
- **models/** - Data models and FHIR bundles
- **pipeline/** - Data extraction and processing
- **utils/** - Helper functions and utilities

### Documentation (`docs/`)
- **Root level** - Essential, current documentation
- **docs/** - Technical documentation
- **docs/archive/** - Historical documentation (31 archived files)

### Scripts (`scripts/`)
- **Root level** - Deployment and utility scripts
- **analysis/** - Data analysis and reporting tools

---

## 📝 File Counts

- **Total Markdown**: 12 (root) + 6 (docs/) + 31 (archived)
- **Python Files**: 39 (excluding venv)
- **JS/TS Files**: 190 (excluding node_modules)
- **React Components**: 36 files
- **Services**: 8 backend + 3 frontend
- **Configuration**: 15 files

---

## 🚀 Quick Navigation

| Purpose | Location |
|---------|----------|
| **Start Development** | `npm run dev` (frontend) |
| **Start Backend** | `python3 fastapi_app.py` |
| **Run Tests** | `npm test` or `pytest` |
| **Build Production** | `npm run build` |
| **View API Docs** | http://localhost:8000/api/docs |
| **Main README** | ./README.md |
| **Architecture** | ./docs/ARCHITECTURE.md |
| **API Reference** | ./docs/API_DOCUMENTATION.md |

---

**Status:** ✅ Organized and Clean  
**Last Cleanup:** October 22, 2025
