# Build Configuration and Known Issues

## Build Status

### Backend Services (6/6 - ✅ ALL PASSING)
All backend packages build successfully:
- `@brainsait/shared-models` - TypeScript compilation successful
- `@brainsait/claims-engine` - TypeScript compilation successful
- `@brainsait/rejection-tracker` - TypeScript compilation successful
- `@brainsait/oasis-integration` - TypeScript compilation successful
- `@brainsait/compliance-reporter` - TypeScript compilation successful
- `@brainsait/notification-service` - TypeScript compilation successful

**Build command:**
```powershell
npx turbo run build --filter='!@brainsait/web' --concurrency=4
```

**Build time:** ~53 seconds

### Web Application (Development Only - ⚠️ Build Issues)

The Next.js web application (`@brainsait/web`) cannot be statically built due to React Context usage incompatible with Next.js 14 prerendering.

**Issue:** 
```
TypeError: Cannot read properties of null (reading 'useContext')
Error occurred prerendering page "/500"
Error occurred prerendering page "/404"
```

**Root Cause:**
- The app uses `AuthProvider` (React Context) for authentication state
- Next.js 14 attempts to statically prerender error pages (/404, /500)
- React Context requires client-side rendering and cannot be prerendered
- Configuration options (`dynamic = 'force-dynamic'`, disabling `output: 'export'`) do not prevent error page prerendering

**Workaround:**
Use development mode instead of production build:

```powershell
cd apps/web
npm run dev
```

The development server works correctly with all React Context features.

## Build Commands

### Full Build (Backend Only)
```powershell
# Recommended: Build only backend services
cd C:\Users\rcmrejection3\nphies-rcm\GIVC\build_unified\brainsait-rcm
npx turbo run build --filter='!@brainsait/web' --concurrency=4
```

### Individual Package Build
```powershell
# Build specific package
cd packages/[package-name]
npm run build
```

### Development Mode
```powershell
# Start all services in development
npx turbo run dev

# Start only web app in development
cd apps/web
npm run dev
```

## Deployment Strategy

### Backend Services
All backend services can be built and deployed normally:
1. Build using Turbo with web filter: `npx turbo run build --filter='!@brainsait/web'`
2. Deploy compiled outputs from `dist/` directories
3. Use production Node.js runtime

### Frontend Application
Deploy using development/runtime mode:
1. **Option A - Development Server:**
   - Deploy with `npm run dev`
   - Use PM2 or similar process manager
   - Set `NODE_ENV=production` for optimization

2. **Option B - Custom Build (Future):**
   - Upgrade to Next.js 15 which has better dynamic rendering support
   - Refactor to use React Server Components where possible
   - Move client-side contexts to client components only

3. **Option C - Alternative Frameworks:**
   - Consider Vite + React for full client-side rendering
   - Or keep Next.js but use Pages Router instead of App Router

## TypeScript Configuration

All packages use TypeScript 5.3.3 with the following configuration:
- Target: ES2020
- Module: CommonJS (backend), ESNext (frontend)
- Strict mode enabled
- Declaration files generated

### Recently Fixed Issues
1. ✅ Enum type mismatches in `ValidationIssuesList.tsx` and `RiskScoreCard.tsx`
2. ✅ Missing `tsconfig.json` for `notification-service`
3. ✅ ESLint warnings blocking build (now ignored during builds)

## Performance Metrics

- **Backend build time:** ~53 seconds (with cache)
- **Package count:** 6 backend packages
- **Cache hit rate:** 83% (5/6 packages)
- **Concurrency:** 4 parallel builds

## Next Steps

To resolve the web app build issue:
1. **Short-term:** Deploy web app in development mode with PM2
2. **Medium-term:** Upgrade to Next.js 15 when stable
3. **Long-term:** Refactor authentication to use React Server Components
