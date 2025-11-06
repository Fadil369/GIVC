// This file prevents Next.js from attempting to statically generate error pages
// which would fail due to React Context usage in the app

export const runtime = 'experimental-edge';
export const dynamic = 'force-dynamic';

function Error() {
  return null; // This will never be rendered in App Router
}

export default Error;
