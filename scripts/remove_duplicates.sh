#!/bin/bash

# Phase 1: Remove duplicate .jsx files where .tsx exists
echo "🔍 Phase 1: Removing duplicate JSX/TSX files..."

DUPLICATES=(
  "frontend/src/components/UI/LoadingSkeleton.jsx"
  "frontend/src/components/UI/EmptyState.jsx"
  "frontend/src/components/UI/Toast.jsx"
  "frontend/src/components/UI/Modal.jsx"
  "frontend/src/components/CustomerSupport/CustomerSupport.jsx"
  "frontend/src/components/ClaimsProcessing/ClaimsProcessing.jsx"
  "frontend/src/components/ErrorBoundary/ErrorBoundary.jsx"
  "frontend/src/components/Auth/Login.jsx"
  "frontend/src/components/Layout/Layout.jsx"
  "frontend/src/components/Dashboard/DashboardEnhanced.jsx"
  "frontend/src/components/LandingPage.jsx"
  "frontend/src/hooks/useAuth.jsx"
  "frontend/src/main.jsx"
)

REMOVED=0
for file in "${DUPLICATES[@]}"; do
  if [ -f "$file" ]; then
    TSX_VERSION="${file%.jsx}.tsx"
    if [ -f "$TSX_VERSION" ]; then
      echo "  ❌ Removing: $file (TSX version exists)"
      rm "$file"
      ((REMOVED++))
    else
      echo "  ⚠️  Skipping: $file (no TSX version found)"
    fi
  else
    echo "  ℹ️  Already removed: $file"
  fi
done

echo ""
echo "✅ Phase 1 Complete: Removed $REMOVED duplicate files"
echo ""
echo "📊 Current Status:"
JSX_COUNT=$(find frontend/src -name "*.jsx" -type f 2>/dev/null | wc -l | tr -d ' ')
TSX_COUNT=$(find frontend/src -name "*.tsx" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "  JSX files remaining: $JSX_COUNT"
echo "  TSX files: $TSX_COUNT"
