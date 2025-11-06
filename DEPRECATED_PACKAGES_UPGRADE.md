# Deprecated Packages Upgrade Guide

**Date:** October 29, 2025  
**Status:** Informational - Action Required

---

## Overview

During npm audit, several deprecated packages were identified. This guide provides upgrade paths and alternatives.

---

## Deprecated Packages Summary

### 1. fstream@1.0.12
**Status:** Deprecated  
**Reason:** Security vulnerabilities, unmaintained  
**Current Usage:** Likely indirect dependency  

**Recommended Action:**
```powershell
# Find which package depends on fstream
npm ls fstream

# Update parent packages or replace with:
# - 'tar' for tar operations
# - 'archiver' for creating archives
# - Node.js built-in fs/stream for basic operations

# Example replacement:
npm uninstall fstream
npm install tar archiver
```

**Modern Alternatives:**
- **tar** - Pure JavaScript tar implementation
- **archiver** - Multi-format archive creation
- **Node.js fs/promises** - Built-in file operations

---

### 2. eslint@8.57.1
**Status:** Deprecated (ESLint v9 available)  
**Reason:** Major version superseded  
**Current Usage:** Development dependency  

**Recommended Action:**
```powershell
# Check current version
npm ls eslint

# Upgrade to ESLint v9 (requires config migration)
npm install eslint@^9.0.0 --save-dev

# Note: ESLint v9 uses flat config format
# Migration guide: https://eslint.org/docs/latest/use/configure/migration-guide
```

**Migration Steps:**
1. Backup current `.eslintrc.js` or `.eslintrc.json`
2. Install ESLint v9: `npm install eslint@latest --save-dev`
3. Convert config to flat format using migration tool
4. Update `eslint-config-*` and `eslint-plugin-*` packages
5. Test linting: `npm run lint`

**Breaking Changes:**
- Flat config format required (no more `.eslintrc`)
- Some plugins need updates for v9 compatibility
- New rule defaults

---

### 3. react-native-vector-icons@10.3.0
**Status:** Deprecated  
**Reason:** Monolithic package, prefer individual icon libraries  
**Current Usage:** Mobile app (if React Native used)  

**Recommended Action:**
```powershell
# Replace with icon-family-specific packages:
npm uninstall react-native-vector-icons

# Install only needed icon families:
npm install @react-native-vector-icons/fontawesome
npm install @react-native-vector-icons/material-icons
npm install @react-native-vector-icons/ionicons
```

**Modern Alternatives:**
- **@expo/vector-icons** - If using Expo
- **react-native-svg + icon libraries** - SVG-based icons
- Individual icon family packages (lighter bundle)

**Migration Example:**
```javascript
// Before (deprecated):
import Icon from 'react-native-vector-icons/FontAwesome';

// After (recommended):
import Icon from '@react-native-vector-icons/fontawesome';
```

---

## Additional Packages to Monitor

### Not Deprecated Yet, But Worth Updating:

#### glob@7.x
**Current:** v7.x (older version)  
**Latest:** v10.x  
**Reason to Upgrade:** Performance improvements, better pattern matching

```powershell
npm ls glob
npm install glob@latest
```

#### rimraf@2.x
**Current:** v2.x (older version)  
**Latest:** v5.x  
**Reason to Upgrade:** Faster deletion, better error handling

```powershell
npm ls rimraf
npm install rimraf@latest --save-dev
```

---

## Upgrade Priority

### High Priority (Security/Maintenance)
1. **fstream** → tar/archiver
   - Security concerns
   - No longer maintained
   - Direct replacement needed

### Medium Priority (Functionality)
2. **react-native-vector-icons** → Individual packages
   - Bundle size reduction
   - Better tree-shaking
   - Improved performance

### Low Priority (Non-breaking)
3. **eslint@8** → eslint@9
   - Requires config migration
   - Breaking changes in config format
   - Plan migration during major update cycle

---

## Testing After Upgrades

### 1. Run Full Build
```powershell
cd C:\Users\rcmrejection3\nphies-rcm\GIVC\build_unified\brainsait-rcm
npx turbo run build
```

### 2. Run Linting
```powershell
npx turbo run lint
```

### 3. Run Tests
```powershell
npx turbo run test
```

### 4. Check for New Warnings
```powershell
npm install 2>&1 | Select-String -Pattern "deprecated"
```

---

## Automated Dependency Updates

### Using npm-check-updates
```powershell
# Install tool
npm install -g npm-check-updates

# Check for updates
ncu

# Update package.json (interactive)
ncu -u -i

# Install updated dependencies
npm install
```

### Using Dependabot (GitHub)
Enable Dependabot in repository settings for automated PRs:

**.github/dependabot.yml:**
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/build_unified/brainsait-rcm"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

---

## Upgrade Checklist

Before upgrading deprecated packages:

- [ ] Identify all usages: `npm ls <package-name>`
- [ ] Check if direct or indirect dependency
- [ ] Review breaking changes in upgrade guide
- [ ] Backup current package.json and package-lock.json
- [ ] Test in development environment first
- [ ] Update related packages (plugins, configs)
- [ ] Run full test suite
- [ ] Update documentation if APIs changed
- [ ] Commit changes with clear message

---

## Monitoring Future Deprecations

### Regular Audits
```powershell
# Weekly check
npm outdated

# Monthly security audit
npm audit

# Quarterly dependency review
npm ls --depth=0
```

### Subscribe to Updates
- GitHub watch for major dependencies
- npm blog: https://blog.npmjs.org/
- Node.js release schedule: https://nodejs.org/en/about/releases/

---

## Rollback Procedure

If upgrade causes issues:

```powershell
# Restore from Git
git checkout HEAD -- package.json package-lock.json

# Reinstall previous versions
npm install

# Or restore specific package version
npm install <package>@<previous-version>
```

---

## Additional Resources

- **npm deprecate docs:** https://docs.npmjs.com/cli/v10/commands/npm-deprecate
- **Package update strategies:** https://docs.npmjs.com/updating-packages
- **Semantic versioning:** https://semver.org/
- **Breaking change guides:** Check individual package repositories

---

**Next Review Date:** January 29, 2026  
**Maintained By:** GIVC Development Team  
**Questions?** Check package GitHub issues or npm package pages
