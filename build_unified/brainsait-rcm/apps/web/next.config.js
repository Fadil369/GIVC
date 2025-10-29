/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Don't fail build on ESLint warnings
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Fail on TypeScript errors but not warnings
    ignoreBuildErrors: false,
  },
  transpilePackages: [
    '@brainsait/rejection-tracker',
    '@brainsait/notification-service',
    '@brainsait/compliance-reporter'
  ],
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Disable SWC minifier (use Babel instead)
  swcMinify: false,
  // Note: 'output: export' disabled due to React Context usage
  // Use standard Next.js build for server-side rendering
  // output: 'export',
  images: {
    unoptimized: true, // Cloudflare will handle image optimization
  },
  trailingSlash: true,
}

module.exports = nextConfig