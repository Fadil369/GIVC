import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: './frontend',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
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
  },
})