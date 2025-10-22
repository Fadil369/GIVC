#!/bin/bash

echo "🔧 Fixing empty TSX files by restoring from git history..."

# Find all empty TSX files
EMPTY_FILES=$(find frontend/src/components -name "*.tsx" -type f -empty)

for tsx_file in $EMPTY_FILES; do
  # Try to find the corresponding JSX file in git history
  jsx_file="${tsx_file%.tsx}.jsx"
  
  echo "  📦 Processing: $tsx_file"
  
  # Try to restore from git history (various commits back)
  for commit in HEAD~1 HEAD~2 HEAD~3 origin/main; do
    if git show "$commit:$jsx_file" > "$tsx_file.tmp" 2>/dev/null && [ -s "$tsx_file.tmp" ]; then
      mv "$tsx_file.tmp" "$tsx_file"
      echo "  ✅ Restored $tsx_file from $commit"
      break
    fi
    rm -f "$tsx_file.tmp"
  done
  
  # If still empty, try to restore the TSX version from git
  if [ ! -s "$tsx_file" ]; then
    for commit in HEAD~1 HEAD~2 HEAD~3 origin/main; do
      if git show "$commit:$tsx_file" > "$tsx_file.tmp" 2>/dev/null && [ -s "$tsx_file.tmp" ]; then
        mv "$tsx_file.tmp" "$tsx_file"
        echo "  ✅ Restored $tsx_file (tsx version) from $commit"
        break
      fi
      rm -f "$tsx_file.tmp"
    done
  fi
  
  # If still empty, mark for deletion
  if [ ! -s "$tsx_file" ]; then
    echo "  ⚠️  Could not restore $tsx_file - keeping empty for now"
  fi
done

echo ""
echo "✅ Fix attempt complete"
