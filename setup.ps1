# PowerShell setup script for NPHIES Integration
# Run this script to set up the project

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  NPHIES Integration Platform Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  Virtual environment already exists" -ForegroundColor Gray
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ Pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Error installing dependencies" -ForegroundColor Red
    exit 1
}

# Create directories
Write-Host ""
Write-Host "Creating required directories..." -ForegroundColor Yellow
$directories = @("logs", "output", "certs", "examples/output")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "  ✓ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  Directory exists: $dir" -ForegroundColor Gray
    }
}

# Create .env file if not exists
Write-Host ""
Write-Host "Setting up environment configuration..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file from template" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Please edit .env file with your credentials" -ForegroundColor Yellow
} else {
    Write-Host "  .env file already exists" -ForegroundColor Gray
}

# Test import
Write-Host ""
Write-Host "Testing installation..." -ForegroundColor Yellow
$testScript = @"
import sys
try:
    from config.settings import settings
    from auth.auth_manager import auth_manager
    print('✓ Imports successful')
    sys.exit(0)
except Exception as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"@

$testScript | python
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Installation test passed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Installation test failed (may need to configure .env)" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Edit .env file with your NPHIES credentials" -ForegroundColor White
Write-Host "2. Run: python main.py" -ForegroundColor White
Write-Host "3. Check: README.md for documentation" -ForegroundColor White
Write-Host ""
Write-Host "Quick commands:" -ForegroundColor White
Write-Host "  Activate venv:  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  Run main:       python main.py" -ForegroundColor Gray
Write-Host "  Run examples:   python examples\usage_examples.py" -ForegroundColor Gray
Write-Host ""
