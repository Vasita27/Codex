import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const isDev = mode === 'development';

  return {
    plugins: [react()],
    server: isDev
      ? {
          host: true,
          port: 3000,
          proxy: {
            '/api/auth': {
              target: 'http://server:5000',
              changeOrigin: true,
            },
            '/api': {
              target: 'http://flask-ai:5001',
              changeOrigin: true,
            },
          },
        }
      : undefined,
    build: {
      outDir: 'dist',
    },
  };
});
