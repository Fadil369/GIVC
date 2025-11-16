# Repository Cleanup Recommendations

## Automated Cleanup Actions

### 1. Remove Build Artifacts
```bash
# Remove all build directories
rm -rf dist/
rm -rf build/
rm -rf .next/
rm -rf out/

# Remove coverage reports
rm -rf coverage/
rm -rf htmlcov/
rm -rf .nyc_output/
```

### 2. Clean Node Modules (if needed)
```bash
# Fresh install
rm -rf node_modules/
rm package-lock.json
npm install
```

### 3. Clean Python Cache
```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
```

### 4. Remove Log Files
```bash
# Remove log files (should be in .gitignore)
find . -type f -name "*.log" -delete
```

## Files to Review for Removal

### Legacy/Unused Files
- [ ] `MicrosoftAjax.js` - Old Microsoft Ajax library
- [ ] `MicrosoftAjaxApplicationServices.js`
- [ ] `MicrosoftAjaxWebForms.js`
- [ ] `WebForms.js`
- [ ] `WebUIValidation.js`
- [ ] `GoogleCapchaValidation.js` (if not used)
- [ ] `ManageUser.js` (if legacy)
- [ ] `Gotham_Book_400.font.js` (if not used)

### Duplicate/Backup Files
- [ ] Review `build_unified/` directory - archive if completed
- [ ] Review `archives/` directory - move to external storage
- [ ] Review `backups/` directory - move to external storage
- [ ] Check for `.bak`, `.backup`, `.old` files

### Documentation Cleanup
- [ ] Consolidate multiple audit reports into one
- [ ] Archive old progress reports (PHASE1_PROGRESS.md, etc.)
- [ ] Remove redundant guides

## .gitignore Improvements

### Add These Patterns
```
# Build artifacts
build_unified/
.output/

# Test outputs
test-results/
playwright-report/

# IDE
.vscode/settings.json
.idea/

# OS
.DS_Store
Thumbs.db

# Temporary
*.tmp
*.temp
.tmp/

# Logs
*.log
logs/

# Legacy
MicrosoftAjax*.js
WebForms.js
WebUIValidation.js
```

## Repository Size Optimization

### Current State
- Total Size: 189 MB
- Files: ~4,892

### Optimization Targets
1. **Archive old documentation** - Save 10-20 MB
2. **Remove legacy JavaScript libraries** - Save 5-10 MB  
3. **Clean up build_unified/** - Save 20-50 MB
4. **Compress analysis data** - Save 10-15 MB

### Expected After Cleanup
- Target Size: ~120-140 MB
- File Reduction: ~500-1000 files

## Automation Script

```bash
#!/bin/bash
# cleanup.sh - Automated repository cleanup

echo "🧹 Starting repository cleanup..."

# Remove build artifacts
echo "Removing build artifacts..."
rm -rf dist/ build/ .next/ out/

# Remove test artifacts
echo "Removing test artifacts..."
rm -rf coverage/ htmlcov/ .nyc_output/ test-results/ playwright-report/

# Clean Python cache
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove log files
echo "Removing log files..."
find . -type f -name "*.log" -delete 2>/dev/null

# Remove temporary files
echo "Removing temporary files..."
find . -type f -name "*.tmp" -delete
find . -type f -name "*.temp" -delete
find . -type f -name "*.bak" -delete

echo "✅ Cleanup complete!"
echo "Run 'git status' to review changes."
```

## Safety Notes

⚠️ **Before removing any files:**
1. Verify they are not used in production
2. Check for references in source code
3. Create a backup if unsure
4. Review with team if deleting large sections

✅ **Safe to remove immediately:**
- Build artifacts (dist/, build/)
- Python cache (__pycache__/)
- Log files (*.log)
- Temporary files (*.tmp)

❌ **DO NOT remove:**
- Source code (frontend/src/, etc.)
- Configuration files (.env.example, etc.)
- Documentation (README.md, CLAUDE.md, etc.)
- Active dependencies (node_modules/ - but can reinstall)
