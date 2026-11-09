import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const SCHEMAS_DIR = fileURLToPath(new URL('./src/data/schemas', import.meta.url))
const MAX_UPLOAD_SIZE = 2 * 1024 * 1024

function sendJson(res, status, payload) {
  res.statusCode = status
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  res.end(JSON.stringify(payload, null, 2))
}

// шахты хранятся в папках mine_N; из поля "mine" («Шахта 2») выбираем её,
// без поля или со странным значением файл идёт в mine_1
function mineDirFor(parsed) {
  if (!parsed || typeof parsed !== 'object') return 'mine_1'
  const raw = typeof parsed.mine === 'string' ? parsed.mine.trim() : ''
  const num = /(?:^|\b)(?:Шахта\s*)?((?:mine_)?\d+)(?:\b|$)/i.exec(raw)
  if (!num) return 'mine_1'
  const n = num[1].replace(/^mine_/i, '')
  return Number.isFinite(Number(n)) && Number(n) >= 1 ? `mine_${n}` : 'mine_1'
}

// Плагин для dev-сервера: принимает JSON-схему и сохраняет её в проект
function schemaUploadServer() {
  return {
    name: 'infomfss-upload-schema',
    apply: 'serve',
    configureServer(server) {
      // список папок шахт: import.meta.glob не видит пустые папки,
      // поэтому фронту отдаём реальное содержимое src/data/schemas
      server.middlewares.use('/api/schema-dirs', (req, res) => {
        let dirs = []
        try {
          dirs = fs
            .readdirSync(SCHEMAS_DIR, { withFileTypes: true })
            .filter((entry) => entry.isDirectory())
            .map((entry) => entry.name)
        } catch {
          dirs = []
        }
        sendJson(res, 200, { ok: true, dirs })
      })

      server.middlewares.use('/api/upload-schema', (req, res) => {
        if (req.method !== 'POST') {
          sendJson(res, 405, { ok: false, error: 'Используйте метод POST.' })
          return
        }

        const chunks = []
        req.on('data', (chunk) => {
          chunks.push(chunk)
          if (Buffer.concat(chunks).length > MAX_UPLOAD_SIZE) {
            req.destroy()
            sendJson(res, 413, { ok: false, error: 'Файл больше 2 МБ.' })
          }
        })

        req.on('end', () => {
          try {
            const body = Buffer.concat(chunks)
            const rawName = req.headers['x-schema-filename']
              ? decodeURIComponent(String(req.headers['x-schema-filename']))
              : ''
            const base = path.basename(rawName)
            if (!base || !base.toLowerCase().endsWith('.json')) {
              throw new Error('Имя файла должно оканчиваться на .json (заголовок x-schema-filename).')
            }
            const text = body.toString('utf8')
            let parsed
            try {
              parsed = JSON.parse(text)
            } catch {
              throw new Error('Файл не является корректным JSON.')
            }
            const mineDir = mineDirFor(parsed)
            fs.mkdirSync(path.join(SCHEMAS_DIR, mineDir), { recursive: true })
            fs.writeFileSync(path.join(SCHEMAS_DIR, mineDir, base), text, 'utf8')
            sendJson(res, 200, { ok: true, file: `${mineDir}/${base}` })
          } catch (err) {
            sendJson(res, 400, { ok: false, error: err.message })
          }
        })
      })
    },
  }
}

export default defineConfig({
  plugins: [react(), schemaUploadServer()],
  server: {
    port: 5173,
    open: false,
  },
})
