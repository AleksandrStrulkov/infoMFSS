import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const frontendDir = fileURLToPath(new URL('.', import.meta.url))

export default defineConfig({
  plugins: [react()],
  base: '/static/power-circuit/',
  server: {
    port: 5173,
    open: false,
  },
  build: {
    outDir: path.resolve(frontendDir, '../static/power-circuit'),
    emptyOutDir: true,
    sourcemap: false,
    rollupOptions: {
      input: path.resolve(frontendDir, 'src/main.jsx'),
      output: {
        entryFileNames: 'app.js',
        chunkFileNames: 'chunks/[name].js',
        assetFileNames: (asset) => asset.name?.endsWith('.css') ? 'app.css' : 'assets/[name][extname]',
      },
    },
  },
})
