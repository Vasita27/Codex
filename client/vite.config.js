import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api/auth': {
        target: 'http://server:5000',  // Express server in Docker
        changeOrigin: true,
      },
      '/api': {
        target: 'http://flask-ai:5001', // Flask server in Docker
        changeOrigin: true,
      }
    }
  }
})
