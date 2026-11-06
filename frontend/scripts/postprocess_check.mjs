import './dom_shims.mjs'

const { default: mermaid } = await import('mermaid')
const { jsonToMermaid } = await import('../src/utils/jsonToMermaid.js')
const { postProcessMermaidSvg } = await import('../src/utils/postProcessDiagram.js')

import fs from 'fs'

const NODE_SPACING = Number(process.env.NODE_SPACING || 120)
const RANK_SPACING = Number(process.env.RANK_SPACING || 55)
const PAD = Number(process.env.PAD || 12)

mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'loose',
  htmlLabels: false,
  flowchart: {
    useMaxWidth: false,
    htmlLabels: false,
    curve: 'basis',
    nodeSpacing: NODE_SPACING,
    rankSpacing: RANK_SPACING,
    padding: PAD,
    subGraphTitleMargin: { top: 0, bottom: 2 },
    subGraphTitlePadding: 0,
  },
  theme: 'default',
})

const schemaFiles = fs.readdirSync('src/data/schemas').filter((f) => f.endsWith('.json'))

const findings = []
let lastOut = ''

for (const schemaPath of schemaFiles) {
  for (const dir of ['TB', 'LR']) {
  const schema = JSON.parse(fs.readFileSync(`src/data/schemas/${schemaPath}`, 'utf8'))
  const { code, shapes } = jsonToMermaid(schema, dir)
  console.log(`\n=== schema: ${schemaPath} (${dir}) ===`)
  console.log('пунктирные связи остались?', /-\.->/.test(code))
  const { svg } = await mermaid.render(`pp-${dir}-${schemaPath.replace(/\W+/g, '_')}`, code)
  const out = postProcessMermaidSvg(svg, { shapes })
  lastOut = out

  const doc = new DOMParser().parseFromString(out, 'image/svg+xml')

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
      const dupes = new Set(tspans.map((t) => t.textContent))
      if (tspans.length > dupes.size) findings.push(`дубли строк текста в ${id}`)
      // текст обязан стоять в центре круга по обеим осям
      const textEl = g.querySelector('text')
      const labelG = textEl?.closest('g.label')
      const offsetY = /translate\(\s*-?[\d.]+[,\s]+(-?[\d.]+)/.exec(labelG?.getAttribute('transform') || '')?.[1]
      const linesCount = (textEl && [...textEl.children].length) || 1
      const startY = num(textEl?.getAttribute('y'))
      const blockCenterY = num(offsetY) + startY + ((linesCount - 1) * 11) / 2 - (11 * 0.32)
      if (Math.abs(blockCenterY) > 3) {
        findings.push(`текст круга ${id} не по центру Y: смещение ${blockCenterY.toFixed(1)}px`)
      }
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
    if (pairs.length > 1) {
      for (let i = 1; i < pairs.length; i++) {
        const dx = Math.abs(pairs[i].x - pairs[i - 1].x)
        const dy = Math.abs(pairs[i].y - pairs[i - 1].y)
        if (dx > 0.5 && dy > 0.5) {
          findings.push(`диагональ в ${m[0]} сегмент ${i}: ${JSON.stringify([pairs[i - 1], pairs[i]])}`)
        }
      }
    }
    const byId = (nid) => doc.querySelector(`g.node[id*="-${nid}-"]`)
    const endpoints = [
      [m[1], pairs[0], 'source'],
      [m[2], pairs[pairs.length - 1], 'target'],
    ]
    for (const [nodeId, pt, label] of endpoints) {
      if (!pt) continue
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

  const clusters = [...doc.querySelectorAll('g.cluster')].map((a) => {
    const ra = a.querySelector('rect')
    return { id: a.getAttribute('id'), rect: ra, x: num(ra?.getAttribute('x')), y: num(ra?.getAttribute('y')), w: num(ra?.getAttribute('width')), h: num(ra?.getAttribute('height')) }
  }).filter((c) => c.rect)
  for (let i = 0; i < clusters.length; i++) {
    for (let j = i + 1; j < clusters.length; j++) {
      const a = clusters[i]
      const b = clusters[j]
      const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)
      const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y)
      if (ox > 0 && oy > 0) findings.push(`наложение кластеров ${a.id} и ${b.id}`)
    }
  }
  const fills = clusters
    .map((c) => /fill:([^;"']+)/.exec(c.rect.getAttribute('style') || c.rect.getAttribute('fill') || '')?.[1] ?? '?')
  console.log('фоны зон:', fills.join(' | '))
  if (new Set(fills).size < clusters.length) findings.push('фоны зон не уникальны')
  }
}

console.log('PROBLEMS:', findings.length ? findings.join('\n') : 'none')
fs.writeFileSync('scripts/pp_output_check.svg', lastOut, 'utf8')
console.log('svg saved: scripts/pp_output_check.svg, bytes:', lastOut.length)
