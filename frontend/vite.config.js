import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  const isProd = mode === 'production'

  const backendUrl = isProd
    ? env.VITE_APP_PRODUCTION_BACKEND_URL || 'http://localhost'
    : env.VITE_APP_DEVELOPMENT_BACKEND_URL || 'http://localhost'

  const backendPort = isProd
    ? env.VITE_APP_PRODUCTION_BACKEND_PORT || '8000'
    : env.VITE_APP_DEVELOPMENT_BACKEND_PORT || '5002'

  const target = `${backendUrl}:${backendPort}`
  console.log(`[VITE] Proxying /api → ${target}`)

  return {
    plugins: [vue(), vueDevTools()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: '0.0.0.0', // allows VS Code SSH port forwarding
      port: 5173,
      proxy: {
        '/api': {
          target,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
