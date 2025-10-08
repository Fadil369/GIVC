#!/bin/bash

# GIVC Healthcare Platform - Build Validation Script
# Validates that the build output is complete and ready for deployment

set -e

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

print_status "🔍 Validating build output for Cloudflare Pages deployment..."

# Check if dist directory exists
if [ ! -d "dist" ]; then
    print_error "Build validation failed: dist directory not found"
    print_status "Please run 'npm run build' first"
    exit 1
fi

# Check if index.html exists
if [ ! -f "dist/index.html" ]; then
    print_error "Build validation failed: dist/index.html not found"
    exit 1
fi

# Check if assets directory exists (Vite creates this)
if [ ! -d "dist/assets" ]; then
    print_warning "Assets directory not found - this might indicate an incomplete build"
fi

# Check for essential files
REQUIRED_FILES=("dist/index.html")
OPTIONAL_FILES=("dist/manifest.json" "dist/sw.js" "dist/workbox-*.js")

print_status "Checking required files..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ Found: $file"
    else
        print_error "✗ Missing: $file"
        exit 1
    fi
done

print_status "Checking optional files..."
for pattern in "${OPTIONAL_FILES[@]}"; do
    if ls $pattern 1> /dev/null 2>&1; then
        print_success "✓ Found: $pattern"
    else
        print_warning "○ Optional file not found: $pattern"
    fi
done

# Calculate and display build size
BUILD_SIZE=$(du -sh dist/ | cut -f1)
print_status "Build size: $BUILD_SIZE"

# Count files in build
FILE_COUNT=$(find dist -type f | wc -l)
print_status "Total files: $FILE_COUNT"

# Check for common issues
print_status "Checking for common build issues..."

# Check if build is too small (might indicate failed build)
DIST_SIZE_BYTES=$(du -s dist/ | cut -f1)
if [ "$DIST_SIZE_BYTES" -lt 100 ]; then
    print_warning "Build size seems unusually small ($BUILD_SIZE) - please verify build completed successfully"
fi

# Check if index.html has content
INDEX_SIZE=$(wc -c < "dist/index.html")
if [ "$INDEX_SIZE" -lt 500 ]; then
    print_warning "index.html seems unusually small - please verify build completed successfully"
fi

# List build contents for verification
print_status "Build contents:"
ls -la dist/

print_success "✅ Build validation completed successfully!"
print_status "Build is ready for Cloudflare Pages deployment"

# Optional: Display deployment command
echo ""
print_status "To deploy to Cloudflare Pages, run:"
echo "  wrangler pages deploy dist"
echo "  or"
echo "  npm run deploy"