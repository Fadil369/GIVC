# Next.js 15 Preparation Guide

## Current Status

The GIVC platform uses Next.js in the following location:
- `build_unified/brainsait-rcm/apps/web` - Currently on Next.js 14.1.0

The main GIVC application uses Vite + React (not Next.js).

## Next.js 15 Key Changes

Next.js 15 is now stable (latest: 15.5.6) and includes several important changes:

### 1. React 19 Support
- Next.js 15 supports React 19 (currently we're on React 18.2.0)
- Includes React Server Components improvements
- Enhanced async/await support in components

### 2. Turbopack Improvements
- Faster development builds
- Improved hot module replacement (HMR)
- Better error messages

### 3. Server Components by Default
- All components are server components by default
- Need to explicitly mark client components with `'use client'`
- Better performance and smaller bundle sizes

### 4. Breaking Changes
- `next.config.js` → `next.config.ts` (TypeScript config supported)
- Some middleware APIs have changed
- Dynamic routes behavior updated
- Image optimization improvements

## Migration Plan for build_unified/brainsait-rcm/apps/web

### Phase 1: Preparation (Before Upgrade)
1. ✅ Ensure TypeScript configuration is complete (tsconfig.json exists)
2. ✅ Run current build successfully: `cd build_unified/brainsait-rcm/apps/web && npm run build`
3. Review current dependencies for compatibility with Next.js 15
4. Audit usage of deprecated APIs

### Phase 2: Update Dependencies
```json
{
  "dependencies": {
    "next": "^15.5.6",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "eslint-config-next": "^15.5.6"
  }
}
```

### Phase 3: Code Updates

#### 3.1 Mark Client Components
Add `'use client'` directive to components that:
- Use React hooks (useState, useEffect, etc.)
- Use browser APIs (window, document)
- Have event handlers (onClick, onChange, etc.)
- Use context providers

Example:
```tsx
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

#### 3.2 Update Configuration Files
Rename `next.config.js` to `next.config.ts` (optional but recommended):
```typescript
import type { NextConfig } from 'next'

const config: NextConfig = {
  // your existing config
}

export default config
```

#### 3.3 Update Middleware (if any)
Review middleware for API changes and update as needed.

#### 3.4 Update API Routes
Next.js 15 has improved API route handlers:
```typescript
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  return NextResponse.json({ message: 'Hello' })
}
```

### Phase 4: Testing
1. Run development server: `npm run dev`
2. Test all pages and routes
3. Run build: `npm run build`
4. Test production build: `npm run start`
5. Run linting: `npm run lint`
6. Test all interactive features

### Phase 5: Production Deployment
1. Update environment variables if needed
2. Deploy to staging environment first
3. Run smoke tests
4. Monitor for errors
5. Deploy to production

## Rollback Plan

If issues occur:
1. Revert package.json to previous versions
2. Run `npm install`
3. Clear `.next` directory: `npm run clean`
4. Rebuild: `npm run build`

## Benefits of Upgrading to Next.js 15

1. **Performance**: Faster builds and better runtime performance
2. **Developer Experience**: Improved error messages and debugging
3. **Server Components**: Better SEO and initial page load
4. **Modern React**: Access to latest React 19 features
5. **Security**: Latest security patches and updates

## Resources

- [Next.js 15 Announcement](https://nextjs.org/blog/next-15)
- [Next.js 15 Upgrade Guide](https://nextjs.org/docs/app/building-your-application/upgrading/version-15)
- [React 19 Release Notes](https://react.dev/blog/2024/12/05/react-19)
- [Server Components Documentation](https://nextjs.org/docs/app/building-your-application/rendering/server-components)

## Timeline Recommendation

- **Now**: Document current state (✅ Complete)
- **Next Sprint**: Update dependencies and test in development
- **Following Sprint**: Deploy to staging and test thoroughly
- **Production**: Deploy when staging tests pass successfully

## Notes

The main GIVC application (`/home/runner/work/GIVC/GIVC`) uses Vite + React, not Next.js. No migration is needed for the main app unless there's a decision to migrate from Vite to Next.js, which would be a much larger undertaking.
