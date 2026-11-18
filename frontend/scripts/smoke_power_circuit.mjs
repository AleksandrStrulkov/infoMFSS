import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const frontendDir = fileURLToPath(new URL('..', import.meta.url))
const sourceDir = path.join(frontendDir, 'src')
const outputDir = path.join(frontendDir, '..', 'static', 'power-circuit')
const appSource = fs.readFileSync(path.join(sourceDir, 'App.jsx'), 'utf8')
const viteSource = fs.readFileSync(path.join(frontendDir, 'vite.config.js'), 'utf8')

for (const forbidden of ['import.meta.glob', '/api/schema-dirs', '/api/upload-schema']) {
  assert.ok(!appSource.includes(forbidden), `Client still references ${forbidden}`)
  assert.ok(!viteSource.includes(forbidden), `Vite still references ${forbidden}`)
}
assert.ok(appSource.includes('fetchJson(schemasBase'), 'Catalog must be fetched from Django')
assert.ok(appSource.includes('fetchJson(schemaUrl('), 'Selected schema must be fetched from Django')
assert.ok(fs.existsSync(path.join(outputDir, 'app.js')))
assert.ok(fs.existsSync(path.join(outputDir, 'app.css')))

function collectFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const filename = path.join(dir, entry.name)
    return entry.isDirectory() ? collectFiles(filename) : [filename]
  })
}

const publicFiles = collectFiles(outputDir)
assert.ok(publicFiles.every((filename) => /\.(js|css)$/.test(filename)))
const publicText = publicFiles.map((filename) => fs.readFileSync(filename, 'utf8')).join('\n')
const schemaDir = path.join(sourceDir, 'data', 'schemas')
for (const filename of collectFiles(schemaDir).filter((name) => name.endsWith('.json'))) {
  const schema = JSON.parse(fs.readFileSync(filename, 'utf8'))
  assert.ok(!publicText.includes(path.basename(filename)), `Public bundle contains filename ${filename}`)
  assert.ok(!publicText.includes(JSON.stringify(schema)), `Public bundle contains JSON ${filename}`)
  if (typeof schema.mine === 'string' && schema.mine.length >= 8) {
    assert.ok(!publicText.includes(schema.mine), `Public bundle contains mine title ${filename}`)
  }
}
console.log(`Frontend smoke passed: ${publicFiles.length} public JS/CSS files, no private schemas`)
