# Node.js Upgrade Guide - v18 to v20+

**Current Version:** Node.js v18.17.0, npm 9.6.7  
**Target Version:** Node.js v20.19.0+ (LTS)  
**Date:** October 29, 2025

---

## Why Upgrade?

Several packages in the GIVC monorepo recommend or require Node.js v20+:

### Packages Requiring Node v20+
- **react-router-dom** v7.9.4 - Requires >=20.0.0
- **react-router** v7.9.4 - Requires >=20.0.0
- **vitest** v4.0.4 - Requires ^20.0.0 || ^22.0.0 || >=24.0.0
- **vite** v7.1.12 - Requires ^20.19.0 || >=22.12.0
- **undici** v7.14.0 - Requires >=20.18.1
- **expo-server** v1.0.3 - Requires >=20.16.0

### React Native Metro Bundler
- All **metro** packages v0.83.2 - Require >=20.19.4
- **@react-native/** packages v0.81.5 - Require >= 20.19.4

### TypeScript ESLint
- **@typescript-eslint/** packages v8.46.2 - Require ^18.18.0 || ^20.9.0 || >=21.1.0

---

## Current Status

✅ **Node v18.17.0 is functional** - All core packages work with engine warnings  
⚠️ **Some features limited** - React Native and modern Vite features need v20+  
📋 **Recommended upgrade** - For full compatibility and future-proofing

---

## Installation Options

### Option 1: Using Node Version Manager (NVM) - **RECOMMENDED**

**Windows (nvm-windows):**
```powershell
# Install nvm-windows if not already installed
# Download from: https://github.com/coreybutler/nvm-windows/releases

# List available Node versions
nvm list available

# Install Node v20 LTS
nvm install 20.19.0

# Use Node v20
nvm use 20.19.0

# Verify installation
node --version
npm --version
```

**Benefits:**
- Switch between Node versions easily
- Maintain v18 for other projects
- Safe rollback if issues occur

### Option 2: Direct Installation

**Download Node.js v20.19.0 LTS:**
- Visit: https://nodejs.org/
- Download Windows Installer (.msi)
- Run installer with default settings
- Restart PowerShell/terminal

**Verify installation:**
```powershell
node --version  # Should show v20.19.0
npm --version   # Should show v10.9.x or higher
```

---

## Post-Upgrade Steps

### 1. Reinstall Dependencies
```powershell
cd C:\Users\rcmrejection3\nphies-rcm\GIVC\build_unified\brainsait-rcm

# Clean existing installation
Remove-Item node_modules -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item package-lock.json -Force -ErrorAction SilentlyContinue

# Clear npm cache
npm cache clean --force

# Fresh install with Node v20
npm install --legacy-peer-deps
```

### 2. Verify No Engine Warnings
```powershell
# Should complete without EBADENGINE warnings
npm install --legacy-peer-deps 2>&1 | Select-String -Pattern "EBADENGINE"
```

### 3. Run Full Build
```powershell
# Build all packages
npx turbo run build

# Should build successfully:
# - @brainsait/web (Next.js)
# - @brainsait/mobile (React Native)
# - All other packages
```

### 4. Run Tests
```powershell
# Execute test suites
npx turbo run test
```

---

## Compatibility Matrix

| Package/Feature | Node v18.17.0 | Node v20.19.0+ |
|----------------|---------------|----------------|
| TypeScript compilation | ✅ Works | ✅ Works |
| Turbo monorepo | ✅ Works | ✅ Works |
| Basic builds | ✅ Works | ✅ Works |
| React Router v7 | ⚠️ Warning | ✅ Full support |
| Vitest v4 | ⚠️ Warning | ✅ Full support |
| Vite v7 | ⚠️ Warning | ✅ Full support |
| Metro bundler | ⚠️ Warning | ✅ Full support |
| React Native | ⚠️ Limited | ✅ Full support |
| TypeScript ESLint v8 | ⚠️ Warning | ✅ Full support |

---

## Rollback Procedure

If you encounter issues after upgrading:

### Using NVM (Recommended)
```powershell
# Switch back to Node v18
nvm use 18.17.0

# Reinstall dependencies
cd C:\Users\rcmrejection3\nphies-rcm\GIVC\build_unified\brainsait-rcm
Remove-Item node_modules -Recurse -Force
npm install --legacy-peer-deps
```

### Direct Installation
1. Uninstall Node v20 from Windows Settings > Apps
2. Reinstall Node v18.17.0 from nodejs.org/download/release/
3. Reinstall project dependencies

---

## Expected Improvements After Upgrade

### Performance
- ⚡ Faster module loading with updated V8 engine
- ⚡ Improved TypeScript compilation speed
- ⚡ Better Vite development server performance

### Compatibility
- ✅ No engine warnings during npm install
- ✅ Full React Native Metro bundler support
- ✅ Modern Vite features available
- ✅ Latest React Router capabilities

### Developer Experience
- 🔧 Access to newer npm features (v10.x)
- 🔧 Better error messages and diagnostics
- 🔧 Improved watch mode reliability

---

## Known Issues & Solutions

### Issue 1: Global npm packages need reinstall
**Solution:** Reinstall global packages after upgrade
```powershell
npm install -g turbo typescript eslint
```

### Issue 2: package-lock.json conflicts
**Solution:** Delete and regenerate
```powershell
Remove-Item package-lock.json -Force
npm install --legacy-peer-deps
```

### Issue 3: Cached binaries
**Solution:** Clear caches
```powershell
npm cache clean --force
npx clear-npx-cache
```

---

## Verification Checklist

After upgrading, verify:

- [ ] `node --version` shows v20.19.0 or higher
- [ ] `npm --version` shows v10.x or higher
- [ ] npm install completes without EBADENGINE warnings
- [ ] All packages build successfully (`npx turbo run build`)
- [ ] Tests execute without errors (`npx turbo run test`)
- [ ] Development servers start (`npm run dev`)
- [ ] No regression in existing functionality

---

## Timeline Recommendation

**Immediate (Optional):**
- Current v18.17.0 is functional for core development
- Upgrade when convenient or needed for specific features

**Short-term (Recommended within 1 month):**
- Upgrade to v20+ for full feature compatibility
- Resolve all engine warnings
- Enable React Native development

**Long-term (Node v18 EOL: April 2025):**
- Must upgrade before Node v18 reaches end-of-life
- v20 LTS supported until April 2026

---

## Additional Resources

- **Node.js Downloads:** https://nodejs.org/
- **Node.js Release Schedule:** https://github.com/nodejs/release
- **NVM Windows:** https://github.com/coreybutler/nvm-windows
- **Migration Guide:** https://nodejs.org/en/download/releases

---

**Document Version:** 1.0  
**Last Updated:** October 29, 2025  
**Maintained By:** GIVC Development Team
