import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.API_BACKEND_URL || 'http://backend:8000',
        changeOrigin: true,
        headers: {
          'X-API-Token': process.env.API_PROXY_TOKEN || '',
        },
      },
      '/ws': {
        target: process.env.API_BACKEND_URL || 'http://backend:8000',
        ws: true,
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('proxyReqWs', (proxyReq) => {
            proxyReq.setHeader('X-API-Token', process.env.API_PROXY_TOKEN || '');
          });
        },
      },
    },
  },
});
