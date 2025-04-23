import { fileURLToPath, URL } from 'node:url'
import path from 'path'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, path.resolve(__dirname, '..'))

  const isProd = mode === 'production'

  const backendUrl = isProd
    ? env.VITE_APP_PRODUCTION_BACKEND_URL
    : env.VITE_APP_DEVELOPMENT_BACKEND_URL

  const backendPort = isProd
    ? env.VITE_APP_PRODUCTION_BACKEND_PORT
    : env.VITE_APP_DEVELOPMENT_BACKEND_PORT
  if (!backendUrl || !backendPort) {
    throw new Error(
      'Backend URL or port is undefined — check your .env file and restart Vite!',
    )
  }

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
      // host: '0.0.0.0',
      // port: 5173,
      proxy: {
        '/api': {
          target: target,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
