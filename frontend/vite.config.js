import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Carga las variables de entorno (.env) desde la raíz del proyecto (un nivel arriba)
  const env = loadEnv(mode, path.resolve(__dirname, '..'), 'VITE_');
  
  return {
    plugins: [react()],
    server: {
      port: parseInt(env.VITE_FRONTEND_PORT || 3000),
      proxy: {
        '/api': {
          target: `${env.VITE_BASE_URL || 'http://localhost'}:${env.VITE_BACKEND_PORT || 8000}`,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  }
})
