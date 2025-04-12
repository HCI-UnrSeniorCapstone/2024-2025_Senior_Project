import { fileURLToPath, URL } from 'node:url'
import fs from 'fs'
import path from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// Read the config.json file
// NOTE: config.json is used by each developer for connecting to their own flask port on the server
// config.json SHOULD NOT be pushed to GITHUB
const config = JSON.parse(
  fs.readFileSync(path.resolve(__dirname, 'src/config.json'), 'utf-8'),
)

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  define: {
    'import.meta.env.VITE_BACKEND_URL': JSON.stringify(config.backendUrl),
    'import.meta.env.VITE_BACKEND_PORT': JSON.stringify(config.backendPort),
  },
  server: {
    proxy: {
      '/api': {
        target: `${config.backendUrl}:${config.backendPort}`,
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
