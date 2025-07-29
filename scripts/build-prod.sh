#!/bin/bash

# GIVC Healthcare Platform - Production Build Script
# © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited

set -e

echo "🏥 Building GIVC Healthcare Platform for production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Environment check
if [ -z "$NODE_ENV" ]; then
    export NODE_ENV=production
fi

print_status "Building in $NODE_ENV mode..."

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf dist/
rm -rf .vite-cache/

# Install dependencies
print_status "Installing production dependencies..."
npm ci --only=production

# Type checking
print_status "Running type check..."
npm run type-check

# Linting
print_status "Running linting..."
npm run lint

# Security audit
print_status "Running security audit..."
npm audit --audit-level high || {
    print_warning "Security vulnerabilities found. Please review and fix."
}

# Run tests
print_status "Running tests..."
npm run test:run

# Build application
print_status "Building application..."
npm run build:production

# Verify build
if [ ! -d "dist" ]; then
    print_error "Build failed - dist directory not found"
    exit 1
fi

if [ ! -f "dist/index.html" ]; then
    print_error "Build failed - index.html not found"
    exit 1
fi

# Calculate build size
BUILD_SIZE=$(du -sh dist/ | cut -f1)
print_success "Build completed successfully!"
print_status "Build size: $BUILD_SIZE"

# List build artifacts
print_status "Build artifacts:"
ls -la dist/

# Generate build report
print_status "Generating build report..."
echo "GIVC Healthcare Platform Build Report" > build-report.txt
echo "=====================================" >> build-report.txt
echo "Build Date: $(date)" >> build-report.txt
echo "Node.js Version: $(node --version)" >> build-report.txt
echo "npm Version: $(npm --version)" >> build-report.txt
echo "Build Size: $BUILD_SIZE" >> build-report.txt
echo "Environment: $NODE_ENV" >> build-report.txt
echo "" >> build-report.txt
echo "Build Artifacts:" >> build-report.txt
ls -la dist/ >> build-report.txt

print_success "Production build completed successfully!"
print_status "Build report saved to build-report.txt"

# Optional: Run bundle analyzer
if command -v npx &> /dev/null; then
    read -p "Run bundle analyzer? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Running bundle analyzer..."
        npm run build:analyze
    fi
fi
