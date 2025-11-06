/**
 * GIVC Healthcare Platform - Advanced Vite Configuration
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Optimized build configuration with bundle analysis, compression,
 * and performance optimizations for healthcare platform
 */

import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const isProduction = mode === 'production';

  return {
    plugins: [
      react({
        // Enable Fast Refresh
        fastRefresh: true,
        // Babel optimizations
        babel: {
          plugins: [
            // Remove console.log in production
            isProduction && ['transform-remove-console', { exclude: ['error', 'warn'] }],
          ].filter(Boolean),
        },
      }),

      // Bundle analyzer - visualize bundle size
      visualizer({
        filename: './dist/stats.html',
        open: false,
        gzipSize: true,
        brotliSize: true,
        template: 'treemap', // or 'sunburst', 'network'
      }),

      // Progressive Web App support
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'robots.txt', 'givc-logo.svg'],
        manifest: {
          name: 'GIVC Healthcare Platform',
          short_name: 'GIVC',
          description: 'Global Integrated Virtual Care - HIPAA-compliant healthcare platform',
          theme_color: '#3b82f6',
          background_color: '#ffffff',
          display: 'standalone',
          icons: [
            {
              src: '/pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png',
            },
            {
              src: '/pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png',
            },
          ],
        },
        workbox: {
          // Cache strategies for different resource types
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'google-fonts-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
                },
                cacheableResponse: {
                  statuses: [0, 200],
                },
              },
            },
            {
              urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
              handler: 'CacheFirst',
              options: {
                cacheName: 'images-cache',
                expiration: {
                  maxEntries: 50,
                  maxAgeSeconds: 60 * 60 * 24 * 30, // 30 days
                },
              },
            },
          ],
        },
      }),
    ],

    resolve: {
      alias: {
        '@': path.resolve(__dirname, './frontend/src'),
        '@components': path.resolve(__dirname, './frontend/src/components'),
        '@hooks': path.resolve(__dirname, './frontend/src/hooks'),
        '@services': path.resolve(__dirname, './frontend/src/services'),
        '@config': path.resolve(__dirname, './frontend/src/config'),
        '@utils': path.resolve(__dirname, './frontend/src/utils'),
        '@contexts': path.resolve(__dirname, './frontend/src/contexts'),
        '@assets': path.resolve(__dirname, './frontend/src/assets'),
      },
    },

    // Build optimizations
    build: {
      // Target modern browsers for smaller bundle
      target: 'es2015',

      // Output directory
      outDir: 'dist',

      // Generate sourcemaps for debugging
      sourcemap: !isProduction,

      // Minification
      minify: isProduction ? 'terser' : false,
      terserOptions: isProduction
        ? {
            compress: {
              drop_console: true, // Remove console.log in production
              drop_debugger: true,
              pure_funcs: ['console.log', 'console.info'], // Remove specific functions
            },
            format: {
              comments: false, // Remove comments
            },
          }
        : undefined,

      // Rollup options
      rollupOptions: {
        output: {
          // Manual chunks for better code splitting
          manualChunks: {
            // Vendor chunks
            'vendor-react': ['react', 'react-dom', 'react-router-dom'],
            'vendor-ui': ['@headlessui/react', '@heroicons/react', 'lucide-react', 'framer-motion'],
            'vendor-forms': ['react-hook-form', 'react-dropzone'],
            'vendor-utils': ['axios', 'date-fns', 'clsx', 'uuid'],
            
            // Feature chunks (lazy-loaded components will auto-split)
            'auth': [
              './frontend/src/components/Auth/Login.jsx',
              './frontend/src/components/Auth/ProtectedRoute.jsx',
            ],
          },
          
          // Asset file naming
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.');
            let extType = info[info.length - 1];
            
            if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
              extType = 'images';
            } else if (/woff|woff2|eot|ttf|otf/.test(extType)) {
              extType = 'fonts';
            }
            
            return `assets/${extType}/[name]-[hash][extname]`;
          },
          
          // Chunk file naming
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
        },
      },

      // Chunk size warnings
      chunkSizeWarningLimit: 500, // 500 KB warning threshold
      
      // Asset inline limit
      assetsInlineLimit: 4096, // 4KB - inline smaller assets as base64
      
      // CSS code splitting
      cssCodeSplit: true,
      
      // Report compressed size
      reportCompressedSize: true,
    },

    // Server configuration
    server: {
      port: 5173,
      host: true,
      strictPort: false,
      open: false,
      cors: true,
      
      // Proxy API requests to Cloudflare Workers
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8787',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path,
        },
      },
    },

    // Preview configuration
    preview: {
      port: 4173,
      host: true,
      strictPort: false,
      open: false,
      cors: true,
    },

    // Optimizations
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        '@headlessui/react',
        '@heroicons/react',
      ],
      // Exclude packages that cause issues
      exclude: ['@vite/client', '@vite/env'],
    },

    // CSS optimization
    css: {
      devSourcemap: !isProduction,
      modules: {
        localsConvention: 'camelCase',
      },
    },

    // Environment variables
    define: {
      // Make env variables available
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },

    // Performance optimizations
    esbuild: {
      logOverride: { 'this-is-undefined-in-esm': 'silent' },
      drop: isProduction ? ['console', 'debugger'] : [],
    },

    // JSON handling
    json: {
      stringify: true, // Inline JSON as strings for better tree-shaking
    },

    // Worker handling
    worker: {
      format: 'es',
    },
  };
});
