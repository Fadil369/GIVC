import react from '@vitejs/plugin-react'
import path from 'path'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
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
  ],
  root: './frontend',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    sourcemap: process.env.NODE_ENV === 'development',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['@headlessui/react', '@heroicons/react', 'framer-motion'],
          utils: ['axios', 'date-fns', 'uuid', 'crypto-js'],
        },
      },
    },
    target: 'esnext',
    minify: 'terser',
    cssCodeSplit: true,
    reportCompressedSize: false,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
      '@/components': path.resolve(__dirname, './frontend/src/components'),
      '@/config': path.resolve(__dirname, './frontend/src/config'),
      '@/utils': path.resolve(__dirname, './frontend/src/utils'),
      '@/types': path.resolve(__dirname, './frontend/src/types'),
      '@/hooks': path.resolve(__dirname, './frontend/src/hooks'),
      '@/services': path.resolve(__dirname, './frontend/src/services'),
    },
  },
  server: {
    host: true,
    port: 3000,
    open: true,
    cors: true,
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
    __DEV__: process.env.NODE_ENV === 'development',
    __PROD__: process.env.NODE_ENV === 'production',
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
  },
  esbuild: {
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
  },
})