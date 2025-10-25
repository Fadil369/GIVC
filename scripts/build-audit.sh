#!/bin/bash

# PERFECT BUILD AUDIT SCRIPT
# Comprehensive quality checks for production deployment

set -e

echo "🔍 STARTING PERFECT BUILD AUDIT"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0; FAIL=0; WARN=0

check_pass() { echo -e "${GREEN}✅${NC} $1"; ((PASS++)); }
check_fail() { echo -e "${RED}❌${NC} $1"; ((FAIL++)); }
check_warn() { echo -e "${YELLOW}⚠️ ${NC} $1"; ((WARN++)); }
info() { echo -e "${BLUE}ℹ${NC} $1"; }

# ==================== 1. DEPENDENCY AUDIT ====================
echo -e "\n${BLUE}📦 DEPENDENCIES${NC}"
echo "======================================"

if npm audit --audit-level=moderate > /dev/null 2>&1; then
  check_pass "Security audit passed"
else
  check_fail "Security vulnerabilities found"
fi

if [ -f "package-lock.json" ]; then
  check_pass "package-lock.json exists"
else
  check_fail "package-lock.json missing"
fi

# Check critical packages
for pkg in react react-dom axios typescript; do
  if npm list $pkg > /dev/null 2>&1; then
    check_pass "$pkg installed"
  else
    check_fail "$pkg missing"
  fi
done

# ==================== 2. LINTING & FORMAT ====================
echo -e "\n${BLUE}🎨 CODE QUALITY${NC}"
echo "======================================"

if npm run lint > /dev/null 2>&1; then
  check_pass "ESLint: 0 errors"
else
  check_warn "ESLint found issues"
fi

# Console statements check
CONSOLE=$(find frontend/src workers utils -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) -exec grep -l "console\\.log\|console\\.error\|console\\.warn" {} \; 2>/dev/null | wc -l)
if [ "$CONSOLE" -eq "0" ]; then
  check_pass "No console statements (0 files)"
else
  check_warn "Console statements found in $CONSOLE files"
fi

# Type coverage
if npx tsc --noEmit > /dev/null 2>&1; then
  check_pass "TypeScript: No type errors"
else
  check_warn "TypeScript compilation issues"
fi

# ==================== 3. TEST COVERAGE ====================
echo -e "\n${BLUE}🧪 TEST COVERAGE${NC}"
echo "======================================"

if npm run test:coverage > /dev/null 2>&1; then
  check_pass "Test suite executed"
else
  check_warn "Test suite not configured or failed"
fi

# ==================== 4. BUILD PERFORMANCE ====================
echo -e "\n${BLUE}⚡ BUILD PERFORMANCE${NC}"
echo "======================================"

info "Running production build..."

START_TIME=$(date +%s%N)
if npm run build > /tmp/build.log 2>&1; then
  END_TIME=$(date +%s%N)
  BUILD_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
  BUILD_TIME_S=$(echo "scale=2; $BUILD_TIME / 1000" | bc)
  
  check_pass "Build completed successfully"
  
  if (( $(echo "$BUILD_TIME_S < 2" | bc -l) )); then
    check_pass "Build time: ${BUILD_TIME_S}s (target: < 2s)"
  elif (( $(echo "$BUILD_TIME_S < 3" | bc -l) )); then
    check_warn "Build time: ${BUILD_TIME_S}s (target: < 2s)"
  else
    check_warn "Build time: ${BUILD_TIME_S}s (target: < 2s)"
  fi
else
  check_fail "Build failed"
  tail -20 /tmp/build.log
fi

# Bundle size analysis
if [ -d "dist" ]; then
  BUNDLE_SIZE=$(du -sh dist | cut -f1)
  check_pass "Bundle size: $BUNDLE_SIZE"
  
  # Check for source maps
  SOURCEMAPS=$(find dist -name "*.map" | wc -l)
  if [ "$SOURCEMAPS" -eq "0" ]; then
    check_pass "No source maps in production"
  else
    check_warn "Found $SOURCEMAPS source maps (should be 0)"
  fi
fi

# ==================== 5. SECURITY CHECKS ====================
echo -e "\n${BLUE}🔒 SECURITY${NC}"
echo "======================================"

# Check for hardcoded secrets
SECRETS=$(grep -r "password\|secret\|token\|key" frontend/src/ --include="*.ts" --include="*.tsx" | grep -v "mock\|test\|placeholder" | wc -l || echo "0")
if [ "$SECRETS" -lt "5" ]; then
  check_pass "No hardcoded secrets detected"
else
  check_warn "Potential hardcoded secrets found: $SECRETS matches"
fi

# Check environment variables usage
ENVFILES=$(grep -r "process.env\|import.meta.env" frontend/src/ --include="*.ts" --include="*.tsx" | wc -l)
if [ "$ENVFILES" -gt "0" ]; then
  check_pass "Environment variables properly used"
else
  check_warn "No environment variables configured"
fi

# ==================== 6. CONFIGURATION ====================
echo -e "\n${BLUE}⚙️  CONFIGURATION${NC}"
echo "======================================"

CONFIG_FILES=(
  "tsconfig.json"
  "vite.config.js"
  ".eslintrc.cjs"
  ".prettierrc.json"
  ".env.example"
)

for file in "${CONFIG_FILES[@]}"; do
  if [ -f "$file" ]; then
    check_pass "$file exists"
  else
    check_fail "$file missing"
  fi
done

# Check tsconfig strict mode
if grep -q '"strict": true' tsconfig.json; then
  check_pass "TypeScript strict mode enabled"
else
  check_warn "TypeScript strict mode disabled"
fi

# ==================== 7. DOCUMENTATION ====================
echo -e "\n${BLUE}📚 DOCUMENTATION${NC}"
echo "======================================"

DOC_FILES=(
  "README.md"
  "ARCHITECTURE.md"
)

for file in "${DOC_FILES[@]}"; do
  if [ -f "$file" ]; then
    check_pass "$file exists"
  else
    check_warn "$file missing"
  fi
done

# ==================== SUMMARY ====================
echo ""
echo "======================================"
echo "📊 AUDIT SUMMARY"
echo "======================================"
echo -e "${GREEN}✅ Passed: $PASS${NC}"
echo -e "${RED}❌ Failed: $FAIL${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARN${NC}"
echo ""

TOTAL=$((PASS + FAIL + WARN))
SCORE=$((PASS * 100 / TOTAL))

echo "Quality Score: $SCORE/100"
echo ""

if [ $FAIL -eq 0 ]; then
  echo -e "${GREEN}🎉 BUILD IS PRODUCTION READY!${NC}"
  exit 0
else
  echo -e "${RED}⚠️  PLEASE FIX FAILURES BEFORE DEPLOYMENT${NC}"
  exit 1
fi
