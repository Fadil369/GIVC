#!/bin/bash

# Fix imports in all jsx files
cd /Users/fadil369/GIVC/frontend/src

# Fix component imports
find . -name "*.jsx" -type f -exec sed -i '' "s|from '@/components/|from '../components/|g" {} \;
find . -name "*.jsx" -type f -exec sed -i '' "s|from '@/hooks/|from '../hooks/|g" {} \;
find . -name "*.jsx" -type f -exec sed -i '' "s|from '@/config/|from '../config/|g" {} \;
find . -name "*.jsx" -type f -exec sed -i '' "s|from '@/types|from '../types/index.js|g" {} \;

# Add .jsx extensions to component imports in all files
find . -name "*.jsx" -type f -exec sed -i '' "s|from '\([^']*\)';|from '\1.jsx';|g" {} \; 2>/dev/null || true

echo "Import fixes completed"
