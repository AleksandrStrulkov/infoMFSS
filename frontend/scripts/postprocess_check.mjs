import './dom_shims.mjs'

const { default: mermaid } = await import('mermaid')
const { jsonToMermaid } = await import('../src/utils/jsonToMermaid.js')
const { postProcessMermaidSvg } = await import('../src/utils/postProcessDiagram.js')

import fs from 'fs'

mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'loose',
  htmlLabels: false,
  flowchart: {
    useMaxWidth: false,
    htmlLabels: false,
    curve: 'stepAfter',
    nodeSpacing: 34,
    rankSpacing: 55,
    padding: 12,
    subGraphTitleMargin: { top: 0, bottom: 2 },
    subGraphTitlePadding: 0,
  },
  theme: 'dark',
})

const schema = JSON.parse(fs.readFileSync('src/data/schemas/1-3Д север ВПП уклона.json', 'utf8'))
const { code, shapes } = jsonToMermaid(schema, 'TD')
const { svg } = await mermaid.render('pp-test-1', code)
const out = postProcessMermaidSvg(svg, { shapes })

const doc = new DOMParser().parseFromString(out, 'image/svg+xml')

const findings = []

// Круги: радиус и многострочный текст
for (const g of doc.querySelectorAll('g.node')) {
  const id = (/(node_\d+)-\d+$/.exec(g.getAttribute('id')) || [])[1]
  const shape = shapes[id]?.shape
  if (!g.getAttribute('transform') || g.getAttribute('transform').includes('NaN')) {
    findings.push(`BAD transform на ${id}`)
  }
  if (g.querySelector('g.outer-path')) findings.push(`tri shape остался у ${id}`)
  if (shape === 'circle') {
    const r = g.querySelector('circle')?.getAttribute('r')
    if (r !== '28') findings.push(`circle ${id} r=${r}`)
    const tspans = [...g.querySelectorAll('g.label text tspan')]
    console.log(`circle ${id}: r=${r}, tspans=${tspans.map((t) => t.textContent).join(' / ')}`)
  }
}

function num(v) {
  return parseFloat(v || 0)
}

// Все ребра: строго осевые линии (нет диагоналей), концы на полюсах торцов
for (const pathEl of doc.querySelectorAll('g.edgePaths path')) {
  const m = /L_(node_\d+)_(node_\d+)_(\d+)$/.exec(pathEl.getAttribute('id') || '')
  if (!m) continue
  const d = pathEl.getAttribute('d') || ''
  if (/NaN/.test(d) || /LL/.test(d)) findings.push(`мусор в пути ${m[0]}`)
  const pairRe = /(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)/g
  const pairs = []
  let pm
  while ((pm = pairRe.exec(d)) !== null) pairs.push({ x: num(pm[1]), y: num(pm[2]) })
  if (pairs.length < 2) continue
  for (let i = 1; i < pairs.length; i++) {
    const dx = Math.abs(pairs[i].x - pairs[i - 1].x)
    const dy = Math.abs(pairs[i].y - pairs[i - 1].y)
    if (dx > 0.5 && dy > 0.5) {
      findings.push(`диагональ в ${m[0]} сегмент ${i}: ${JSON.stringify([pairs[i - 1], pairs[i]])}`)
    }
  }
  const byId = (nid) => doc.querySelector(`g.node[id*="-${nid}-"]`)
  const endpoints = [
    [m[1], pairs[0], 'source'],
    [m[2], pairs[pairs.length - 1], 'target'],
  ]
  for (const [nodeId, pt, label] of endpoints) {
    const shapeEl = byId(nodeId)
    if (!shapeEl) continue
    const transform = shapeEl.getAttribute('transform')
    const center = {
      x: num(/translate\(\s*(-?[\d.]+)/.exec(transform)?.[1]),
      y: num(/translate\(\s*-?[\d.]+[,\s]+(-?[\d.]+)/.exec(transform)?.[1]),
    }
    const shapeMeta = shapes[nodeId]
    if (shapeMeta?.shape === 'circle') {
      const dist = Math.hypot(pt.x - center.x, pt.y - center.y)
      if (Math.abs(dist - 33) > 2) findings.push(`circle edge ${nodeId} (${label}) dist=${dist.toFixed(1)}`)
    } else {
      const rect = shapeEl.querySelector('rect.basic.label-container')
      if (!rect) continue
      const half = { hw: num(rect.getAttribute('width')) / 2, hh: num(rect.getAttribute('height')) / 2 }
      const rel = { x: pt.x - center.x, y: pt.y - center.y }
      const onFace =
        (Math.abs(Math.abs(rel.x) - (half.hw + 2)) < 0.6 && Math.abs(rel.y) < 0.6) ||
        (Math.abs(Math.abs(rel.y) - (half.hh + 2)) < 0.6 && Math.abs(rel.x) < 0.6)
      if (!onFace) {
        findings.push(`rect edge ${nodeId} (${label}) точка не на полюсе торца: rel=${rel.x.toFixed(1)},${rel.y.toFixed(1)}`)
      }
    }
  }
}

// Наложения сабграфов
for (const a of doc.querySelectorAll('g.cluster')) {
  const ra = a.querySelector('rect')
  if (!ra) continue
  const ba = { x: num(ra.getAttribute('x')), y: num(ra.getAttribute('y')), w: num(ra.getAttribute('width')), h: num(ra.getAttribute('height')) }
  for (const b of doc.querySelectorAll('g.cluster')) {
    if (b === a) continue
    const rb = b.querySelector('rect')
    if (!rb) continue
    const bb = { x: num(rb.getAttribute('x')), y: num(rb.getAttribute('y')), w: num(rb.getAttribute('width')), h: num(rb.getAttribute('height')) }
    const ox = Math.min(ba.x + ba.w, bb.x + bb.w) - Math.max(ba.x, bb.x)
    const oy = Math.min(ba.y + ba.h, bb.y + bb.h) - Math.max(ba.y, bb.y)
    if (ox > 0 && oy > 0) findings.push(`наложение кластеров ${a.getAttribute('id')} и ${b.getAttribute('id')}`)
  }
}

console.log('PROBLEMS:', findings.length ? findings.join('\n') : 'none')
fs.writeFileSync('scripts/pp_output_check.svg', out, 'utf8')
console.log('svg saved: scripts/pp_output_check.svg, bytes:', out.length)
