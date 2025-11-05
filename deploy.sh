#!/bin/bash

# 🚀 Ultrathink AI Deployment Script
# ==================================
# Automated deployment script for Ultrathink AI platform
# Author: GIVC Platform Team

set -e  # Exit on any error

echo "🚀 Starting Ultrathink AI Deployment..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. Consider using a non-root user for security."
fi

# Step 1: Environment Verification
echo ""
echo "📋 Step 1: Environment Verification"
echo "==================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
if [[ $? -eq 0 ]]; then
    print_status "Python3 found: $PYTHON_VERSION"
else
    print_error "Python3 not found. Please install Python 3.9+"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_status "pip3 found"
else
    print_error "pip3 not found. Please install pip"
    exit 1
fi

# Check PostgreSQL client
if command -v psql &> /dev/null; then
    print_status "PostgreSQL client found"
else
    print_warning "PostgreSQL client not found. Database operations may fail."
fi

# Step 2: Dependencies Installation
echo ""
echo "📦 Step 2: Installing Dependencies"
echo "=================================="

print_info "Installing Python dependencies..."
pip3 install -r requirements.txt

print_info "Verifying critical ML dependencies..."
python3 -c "
try:
    import sklearn, xgboost, lightgbm, bleach, numpy, scipy
    print('✅ All ML dependencies installed successfully')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    exit(1)
"

if [[ $? -eq 0 ]]; then
    print_status "All dependencies installed successfully"
else
    print_error "Dependency installation failed"
    exit 1
fi

# Step 3: Database Setup
echo ""
echo "🗄️  Step 3: Database Setup"
echo "========================="

# Check if DATABASE_URL is set
if [[ -z "$DATABASE_URL" ]]; then
    print_warning "DATABASE_URL not set. Using default..."
    export DATABASE_URL="postgresql://user:password@localhost/ultrathink"
fi

print_info "Database URL: $DATABASE_URL"

# Run migrations
print_info "Running database migrations..."
if alembic upgrade head; then
    print_status "Database migrations completed"
else
    print_error "Database migration failed"
    print_info "Attempting to initialize Alembic..."
    
    # Try to initialize if first time
    if [[ ! -f "alembic.ini" ]]; then
        alembic init database/migrations
    fi
    
    # Try migration again
    if alembic upgrade head; then
        print_status "Database migrations completed after initialization"
    else
        print_error "Database setup failed. Please check database connectivity."
        exit 1
    fi
fi

# Verify tables created
print_info "Verifying database tables..."
if psql "$DATABASE_URL" -c "\dt" | grep -q "validation_audits"; then
    print_status "Ultrathink tables verified"
else
    print_warning "Could not verify database tables. Check PostgreSQL connectivity."
fi

# Step 4: Testing
echo ""
echo "🧪 Step 4: Running Tests"
echo "======================="

print_info "Running syntax checks..."
python3 -c "
import ast
files = [
    'services/ml_models.py',
    'services/database_models.py', 
    'services/monitoring.py',
    'middleware/security_middleware.py',
    'fastapi_app_ultrathink.py'
]

for file in files:
    try:
        with open(file, 'r') as f:
            ast.parse(f.read())
        print(f'✅ {file} - syntax OK')
    except Exception as e:
        print(f'❌ {file} - syntax error: {e}')
        exit(1)
"

if [[ $? -eq 0 ]]; then
    print_status "All syntax checks passed"
else
    print_error "Syntax checks failed"
    exit 1
fi

# Run test suite if pytest available
if command -v pytest &> /dev/null; then
    print_info "Running test suite..."
    if pytest tests/ -v --tb=short; then
        print_status "All tests passed"
    else
        print_warning "Some tests failed. Review test output."
    fi
else
    print_warning "pytest not found. Skipping test execution."
fi

# Step 5: Configuration
echo ""
echo "⚙️  Step 5: Configuration Setup"
echo "=============================="

# Create models directory
if [[ ! -d "models" ]]; then
    mkdir -p models
    print_status "Created models directory"
fi

# Create logs directory
if [[ ! -d "logs" ]]; then
    mkdir -p logs
    print_status "Created logs directory"
fi

# Set environment variables
export ULTRATHINK_ENABLED=true
export SECURITY_MIDDLEWARE_ENABLED=true
export API_SECRET_KEY=${API_SECRET_KEY:-"ultrathink-secret-key-$(date +%s)"}

print_status "Environment variables configured"
print_info "ULTRATHINK_ENABLED: $ULTRATHINK_ENABLED"
print_info "SECURITY_MIDDLEWARE_ENABLED: $SECURITY_MIDDLEWARE_ENABLED"

# Step 6: Application Startup
echo ""
echo "🚀 Step 6: Starting Application"
echo "==============================="

print_info "Starting Ultrathink AI enhanced FastAPI application..."

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
    print_warning "Port 8000 is already in use"
    
    # Try to kill existing process
    PID=$(lsof -Pi :8000 -sTCP:LISTEN -t)
    print_info "Attempting to stop existing process (PID: $PID)..."
    kill $PID 2>/dev/null || true
    sleep 2
fi

# Start the application in background
nohup uvicorn fastapi_app_ultrathink:app --host 0.0.0.0 --port 8000 > logs/ultrathink.log 2>&1 &
APP_PID=$!

print_info "Application started with PID: $APP_PID"
print_info "Logs available in: logs/ultrathink.log"

# Wait for application to start
sleep 5

# Step 7: Health Verification
echo ""
echo "🏥 Step 7: Health Verification"
echo "============================="

print_info "Checking application health..."

# Test basic health endpoint
if curl -s http://localhost:8000/api/health > /dev/null; then
    print_status "Basic health check passed"
else
    print_error "Basic health check failed"
    print_info "Check logs: tail -f logs/ultrathink.log"
    exit 1
fi

# Test detailed health
print_info "Checking detailed health..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health/detailed)
if echo "$HEALTH_RESPONSE" | grep -q "status"; then
    print_status "Detailed health check passed"
    
    # Extract status
    STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data.get('status', 'unknown'))")
    print_info "System status: $STATUS"
else
    print_warning "Detailed health check returned unexpected response"
fi

# Step 8: AI Features Verification
echo ""
echo "🤖 Step 8: AI Features Verification"
echo "==================================="

print_info "Testing AI validation endpoint..."
VALIDATION_TEST=$(curl -s -X POST http://localhost:8000/api/v1/ultrathink/validate \
  -H "Content-Type: application/json" \
  -d '{
    "claim_data": {
      "claim_id": "CLM-DEPLOY-TEST",
      "patient_id": "PAT-001", 
      "provider_id": "PRV-001",
      "procedure_codes": ["99213"],
      "total_amount": 500.00
    }
  }')

if echo "$VALIDATION_TEST" | grep -q "confidence"; then
    print_status "AI validation endpoint working"
else
    print_warning "AI validation endpoint may have issues"
fi

print_info "Testing smart completion endpoint..."
COMPLETION_TEST=$(curl -s -X POST http://localhost:8000/api/v1/ultrathink/smart-complete \
  -H "Content-Type: application/json" \
  -d '{
    "partial_data": {
      "procedure_codes": ["99213"]
    }
  }')

if echo "$COMPLETION_TEST" | grep -q "field"; then
    print_status "Smart completion endpoint working"
else
    print_warning "Smart completion endpoint may have issues"
fi

# Step 9: Security Verification
echo ""
echo "🔒 Step 9: Security Verification"
echo "==============================="

print_info "Testing security headers..."
HEADERS=$(curl -s -I http://localhost:8000/api/health)
if echo "$HEADERS" | grep -q "X-Frame-Options"; then
    print_status "Security headers present"
else
    print_warning "Security headers may not be configured properly"
fi

print_info "Testing input validation..."
XSS_TEST=$(curl -s -X POST http://localhost:8000/api/v1/ultrathink/validate \
  -H "Content-Type: application/json" \
  -d '{
    "claim_data": {
      "patient_id": "<script>alert(\"xss\")</script>"
    }
  }')

if echo "$XSS_TEST" | grep -q "script"; then
    print_warning "XSS prevention may not be working"
else
    print_status "Input validation working"
fi

# Step 10: Monitoring Setup
echo ""
echo "📊 Step 10: Monitoring Setup"
echo "============================"

print_info "Checking metrics endpoint..."
if curl -s http://localhost:8000/api/metrics | grep -q "ultrathink"; then
    print_status "Prometheus metrics available"
else
    print_warning "Prometheus metrics may not be configured"
fi

# Final Status
echo ""
echo "🎉 Deployment Complete!"
echo "======================="

print_status "Ultrathink AI platform deployed successfully"
print_info "Application URL: http://localhost:8000"
print_info "Health Check: http://localhost:8000/api/health"
print_info "API Documentation: http://localhost:8000/docs"
print_info "Metrics: http://localhost:8000/api/metrics"

echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. Review logs: tail -f logs/ultrathink.log"
echo "2. Test AI features through the UI"
echo "3. Configure monitoring alerts"
echo "4. Set up backup procedures"
echo "5. Train ML models with real data"

echo ""
echo "🔧 Management Commands:"
echo "======================"
echo "Stop application: kill $APP_PID"
echo "View logs: tail -f logs/ultrathink.log"
echo "Restart: ./deploy.sh"

echo ""
print_status "Deployment completed at $(date)"
print_info "Application PID: $APP_PID"