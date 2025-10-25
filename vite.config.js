import react from '@vitejs/plugin-react-swc'
import path from 'path'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'
import { visualizer } from 'rollup-plugin-visualizer'
import compression from 'vite-plugin-compression'

/**
 * OPTIMIZED VITE CONFIG
 * Target: < 2s build time, < 400 kB bundle
 */
export default defineConfig({
  plugins: [
    // SWC is 20x faster than Babel
    react({
      jsxImportSource: 'react',
    }),
    
    // Brotli compression
    compression({
      verbose: true,
      disable: false,
      threshold: 10240,
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
    
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\./,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 10,
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 300,
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
        ],
      },
      manifest: {
        name: 'GIVC Healthcare Platform',
        short_name: 'GIVC',
        description: 'Global Integrated Virtual Care Healthcare Platform',
        theme_color: '#1f2937',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/assets/brainsait-logo.svg',
            sizes: '192x192',
            type: 'image/svg+xml',
          },
        ],
      },
    }),
    
    // Bundle visualization
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  root: './frontend',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    sourcemap: false, // Disabled in production for performance
    target: 'ES2022',
    rollupOptions: {
      output: {
        // Optimized code splitting
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@headlessui/react', '@heroicons/react', 'framer-motion'],
          'utils-vendor': ['axios', 'date-fns', 'uuid', 'crypto-js'],
        },
        // Optimize chunk filenames
        chunkFileNames: 'assets/[name].[hash:8].js',
        entryFileNames: 'assets/[name].[hash:8].js',
        assetFileNames: 'assets/[name].[hash:8][extname]',
      },
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info'],
      },
      mangle: true,
      output: {
        comments: false,
      },
    },
    cssCodeSplit: true,
    chunkSizeWarningLimit: 500,
    reportCompressedSize: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(process.cwd(), './frontend/src'),
      '@/components': path.resolve(process.cwd(), './frontend/src/components'),
      '@/config': path.resolve(process.cwd(), './frontend/src/config'),
      '@/utils': path.resolve(process.cwd(), './frontend/src/utils'),
      '@/types': path.resolve(process.cwd(), './frontend/src/types'),
      '@/hooks': path.resolve(process.cwd(), './frontend/src/hooks'),
      '@/services': path.resolve(process.cwd(), './frontend/src/services'),
    },
  },
  server: {
    host: true,
    port: 3000,
    open: true,
    cors: true,
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 3000,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8787',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  preview: {
    port: 3001,
    host: true,
  },
  define: {
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development'),
    __PROD__: JSON.stringify(process.env.NODE_ENV === 'production'),
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', 'axios', 'date-fns'],
    exclude: ['@vite/client', '@vite/env'],
  },
  esbuild: {
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
    legalComments: 'none',
  },
})