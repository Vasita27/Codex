import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const isDev = mode === 'development';

  return {
    plugins: [react()],
    server: isDev
      ? {
          host: '0.0.0.0',
          port: 3000,
          proxy: {
            '/api/auth': {
              target: 'http://localhost:5000',
              changeOrigin: true,
            },
            '/api': {
              target: 'http://localhost:5001',
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
