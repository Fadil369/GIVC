# BrainSAIT RCM System - Automated Setup Script
# Run this script to set up the development environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BrainSAIT RCM System - Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check if MongoDB is running
Write-Host "Checking MongoDB connection..." -ForegroundColor Yellow
try {
    $mongoTest = mongosh --eval "db.version()" --quiet 2>&1
    if ($?) {
        Write-Host "✓ MongoDB is accessible" -ForegroundColor Green
    } else {
        Write-Host "⚠ MongoDB not found or not running. You can:" -ForegroundColor Yellow
        Write-Host "  1. Install MongoDB locally" -ForegroundColor Yellow
        Write-Host "  2. Use MongoDB Atlas (update DATABASE_URL in .env)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ MongoDB check skipped" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Backend API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Navigate to API directory
Set-Location -Path "apps\api"

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt

Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Install Playwright browsers
Write-Host "Installing Playwright browsers for OASIS+ integration..." -ForegroundColor Yellow
playwright install chromium
Write-Host "✓ Playwright browsers installed" -ForegroundColor Green

# Go back to root
Set-Location -Path "..\\.."

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Frontend Web App" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Navigate to web directory
Set-Location -Path "apps\web"

# Install npm dependencies
Write-Host "Installing Node.js dependencies (this may take a few minutes)..." -ForegroundColor Yellow
npm install

Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green

# Go back to root
Set-Location -Path "..\\.."

# Copy .env.example if .env doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠ IMPORTANT: Edit .env file with your actual credentials!" -ForegroundColor Yellow
    Write-Host "  - Update MongoDB credentials" -ForegroundColor Yellow
    Write-Host "  - Set JWT_SECRET to a secure random string" -ForegroundColor Yellow
    Write-Host "  - Add NPHIES API key if available" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the system:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Start Backend API (Terminal 1):" -ForegroundColor White
Write-Host "   cd apps\api" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start Frontend (Terminal 2):" -ForegroundColor White
Write-Host "   cd apps\web" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Access the application:" -ForegroundColor White
Write-Host "   Web App: http://localhost:3000" -ForegroundColor Gray
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Login with demo credentials:" -ForegroundColor White
Write-Host "   Email: admin@brainsait.com" -ForegroundColor Gray
Write-Host "   Password: admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed instructions, see QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
