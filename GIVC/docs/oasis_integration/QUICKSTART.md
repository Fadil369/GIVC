# Quick Start Guide - BrainSAIT RCM System

## 🚀 Option 1: Local Development (Recommended for Testing)

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 6.0+ (or use MongoDB Atlas)
- Git

### Step 1: Clone and Setup

```powershell
# Navigate to the project directory
cd c:\Users\rcmrejection3\OneDrive\Desktop\oaises+

# Copy environment file
Copy-Item .env.example .env

# Edit .env with your settings (use notepad or any text editor)
notepad .env
```

### Step 2: Start MongoDB (if running locally)

```powershell
# If MongoDB is installed locally
mongod --dbpath C:\data\db

# Or use MongoDB Atlas (update DATABASE_URL in .env)
```

### Step 3: Start Backend API

```powershell
# Navigate to API directory
cd apps\api

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright for OASIS+ integration
playwright install chromium

# Start the API server
python main.py
```

The API will be available at: **http://localhost:8000**
API Documentation: **http://localhost:8000/docs**

### Step 4: Start Frontend (New Terminal)

```powershell
# Navigate to web directory
cd apps\web

# Install dependencies
npm install

# Start development server
npm run dev
```

The web app will be available at: **http://localhost:3000**

### Step 5: Test the System

1. Open browser: http://localhost:3000
2. Login with demo credentials:
   - **Email**: admin@brainsait.com
   - **Password**: admin123

---

## 🐳 Option 2: Docker Deployment (Production-Ready)

### Prerequisites
- Docker Desktop for Windows
- Docker Compose

### Step 1: Setup Environment

```powershell
cd c:\Users\rcmrejection3\OneDrive\Desktop\oaises+

# Copy environment file
Copy-Item .env.example .env

# Edit .env with production settings
notepad .env
```

### Step 2: Build and Start All Services

```powershell
# Build images and start containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Services will be available at:
- **Web App**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

### Step 3: Stop Services

```powershell
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: Deletes data)
docker-compose down -v
```

---

## 🔧 Configuration

### Essential Environment Variables

Edit `.env` file:

```bash
# Database
DATABASE_URL=mongodb://localhost:27017/brainsait
MONGO_USER=brainsait_admin
MONGO_PASSWORD=your_secure_password_here

# NPHIES Integration
NPHIES_API_KEY=your_nphies_api_key
NPHIES_BASE_URL=https://api.nphies.sa/v1

# Security (CHANGE THESE IN PRODUCTION!)
JWT_SECRET=your_jwt_secret_key_here_minimum_32_characters
ENCRYPTION_KEY=your_32_character_encryption_key

# API Configuration
API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 Testing OASIS+ Integration

The OASIS+ integration service automates claim submission to the legacy system.

### Test OASIS+ Client

```powershell
cd services\oasis-integration
python client.py
```

This will:
1. Open a browser window
2. Navigate to OASIS+ (http://128.1.1.185/prod/faces/Home)
3. Login with credentials (U29958/U29958)
4. Submit a test claim
5. Capture screenshots for audit

### Customize OASIS+ Settings

Edit `services/oasis-integration/client.py`:

```python
client = OASISClient(
    base_url="http://128.1.1.185/prod/faces/Home",
    username="U29958",
    password="U29958",
    headless=False  # Set to True for production
)
```

---

## 📊 Verify System Health

### Check API Health

```powershell
# Using curl
curl http://localhost:8000/health

# Using PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health | Select-Object -Expand Content
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:00:00Z",
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "api": "healthy"
  }
}
```

### Check Database Connection

```powershell
# Connect to MongoDB
mongosh mongodb://localhost:27017/brainsait

# List collections
show collections

# Check rejections
db.rejections.find().pretty()
```

---

## 🎯 Common Tasks

### Add Sample Data

```powershell
# Start Python with MongoDB access
python

# Then in Python:
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def add_sample_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.brainsait
    
    # Add sample rejection
    await db.rejections.insert_one({
        "claim_id": "CLM-001",
        "patient_id": "1234567890",
        "payer": "PAYER_A",
        "denial_code": "D001",
        "denial_reason": "Missing authorization",
        "amount": 500.00,
        "service_date": "2024-01-15",
        "branch": "HNH_UNAIZAH",
        "status": "PENDING",
        "created_at": "2024-01-20T10:00:00Z"
    })
    
    print("Sample data added!")

asyncio.run(add_sample_data())
```

### Reset Database

```powershell
# Connect to MongoDB
mongosh mongodb://localhost:27017/brainsait

# Drop database
db.dropDatabase()

# Restart API to recreate indexes
```

### View Logs

```powershell
# API logs (if running locally)
# Logs are displayed in the terminal

# Docker logs
docker-compose logs api
docker-compose logs web
docker-compose logs mongodb
```

---

## 🔐 Initial Super Admin Setup

After starting the system for the first time:

```powershell
# Create super admin (run once)
curl -X POST http://localhost:8000/api/v1/auth/super-admin/initialize `
  -H "Content-Type: application/json" `
  -d '{
    "email": "admin@brainsait.com",
    "password": "SecurePassword123!",
    "full_name": "System Administrator"
  }'
```

---

## 📱 Mobile-Friendly Testing

The web interface is fully responsive. Test on mobile:

1. Find your computer's IP address:
   ```powershell
   ipconfig
   ```

2. Access from mobile device on same network:
   ```
   http://YOUR_IP_ADDRESS:3000
   ```

---

## 🐛 Troubleshooting

### API Won't Start

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```powershell
cd apps\api
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Won't Build

**Problem**: `Cannot find module 'next'`

**Solution**:
```powershell
cd apps\web
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json
npm install
```

### Database Connection Failed

**Problem**: `ServerSelectionTimeoutError`

**Solutions**:
1. Verify MongoDB is running: `mongosh`
2. Check DATABASE_URL in .env
3. Check firewall settings

### OASIS+ Integration Not Working

**Problem**: Browser automation fails

**Solutions**:
1. Install Playwright browsers: `playwright install chromium`
2. Check OASIS+ URL is accessible: http://128.1.1.185/prod/faces/Home
3. Verify network connectivity to internal system
4. Update selectors in `client.py` to match actual OASIS+ UI

---

## 📞 Support

For issues or questions:
- Check logs: API terminal or Docker logs
- Review documentation: `/docs` folder
- API reference: http://localhost:8000/docs

---

## ✅ Checklist

- [ ] MongoDB running
- [ ] Redis running (for production)
- [ ] API running on port 8000
- [ ] Web running on port 3000
- [ ] Can access http://localhost:3000
- [ ] Can login with demo credentials
- [ ] Dashboard loads data successfully
- [ ] Health check returns "healthy"

---

**Next Steps**: See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference.
