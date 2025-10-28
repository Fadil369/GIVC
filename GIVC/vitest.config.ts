/// <reference types="vitest" />
import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./frontend/src/test/setup.ts'],
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'frontend/src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        'dist/',
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
    include: ['frontend/src/**/*.{test,spec}.{js,ts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', '.git'],
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
});
