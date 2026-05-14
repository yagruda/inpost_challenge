import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file from ../.env (root)
  const env = loadEnv(mode, process.cwd() + '/..', '');
  
  return {
    plugins: [react()],
    base: env.VITE_BASE_PATH || '/',
    server: {
      host: '0.0.0.0',
      allowedHosts: true
    }
  }
})
