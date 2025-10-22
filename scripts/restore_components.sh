#!/bin/bash

echo "🔄 Restoring components from git history..."

# List of empty TSX files to restore from their JSX counterparts
COMPONENTS=(
  "frontend/src/components/UI/Toast"
  "frontend/src/components/UI/Modal"
  "frontend/src/components/UI/LoadingSkeleton"
  "frontend/src/components/UI/EmptyState"
)

for comp in "${COMPONENTS[@]}"; do
  echo "  📦 Restoring ${comp}.tsx from git history..."
  git show HEAD~2:${comp}.jsx > ${comp}.tsx.tmp 2>/dev/null
  if [ $? -eq 0 ] && [ -s ${comp}.tsx.tmp ]; then
    mv ${comp}.tsx.tmp ${comp}.tsx
    echo "  ✅ Restored ${comp}.tsx"
  else
    rm -f ${comp}.tsx.tmp
    echo "  ⚠️  Could not restore ${comp}.tsx from git - file may need manual creation"
  fi
done

echo ""
echo "✅ Restoration complete"
