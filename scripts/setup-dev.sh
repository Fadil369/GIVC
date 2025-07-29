#!/bin/bash

# GIVC Healthcare Platform - Development Setup Script
# © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited

set -e

echo "🏥 Setting up GIVC Healthcare Platform for development..."

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

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2)
REQUIRED_VERSION="18.0.0"

if ! node -e "process.exit(require('semver').gte('$NODE_VERSION', '$REQUIRED_VERSION'))" 2>/dev/null; then
    print_error "Node.js version $NODE_VERSION is not supported. Please install Node.js 18 or higher."
    exit 1
fi

print_success "Node.js version $NODE_VERSION is supported"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

# Install dependencies
print_status "Installing dependencies..."
npm install --legacy-peer-deps

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    print_status "Creating .env.local from .env.example..."
    cp .env.example .env.local
    print_warning "Please update .env.local with your actual configuration values"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p dist
mkdir -p coverage

# Set up Git hooks (if in a Git repository)
if [ -d .git ]; then
    print_status "Setting up Git hooks..."
    npx husky install
    npx husky add .husky/pre-commit "npm run pre-commit"
    npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
fi

# Run type checking
print_status "Running type check..."
npm run type-check

# Run linting
print_status "Running linting..."
npm run lint

# Run tests
print_status "Running tests..."
npm run test:run

print_success "Development environment setup complete!"
print_status "You can now run:"
echo "  npm run dev        - Start development server"
echo "  npm run build      - Build for production"
echo "  npm run test       - Run tests"
echo "  npm run lint       - Run linting"
echo ""
print_status "For Docker development:"
echo "  docker-compose --profile dev up   - Start with Docker"
echo ""
print_warning "Don't forget to configure your .env.local file with proper values!"
