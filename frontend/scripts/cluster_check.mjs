import './dom_shims.mjs'

const { default: mermaid } = await import('mermaid')
const { jsonToMermaid } = await import('../src/utils/jsonToMermaid.js')
import fs from 'fs'

const schema = JSON.parse(fs.readFileSync('src/data/schemas/1-3Д север ВПП уклона.json', 'utf8'))

function num(v) {
  return parseFloat(v || 0)
}

for (const spacing of [
  { nodeSpacing: 24, rankSpacing: 34, padding: 6 },
  { nodeSpacing: 34, rankSpacing: 55, padding: 12 },
]) {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',
    htmlLabels: false,
    flowchart: {
      useMaxWidth: false,
      htmlLabels: false,
      curve: 'stepAfter',
      nodeSpacing: spacing.nodeSpacing,
      rankSpacing: spacing.rankSpacing,
      padding: spacing.padding,
      subGraphTitleMargin: { top: 0, bottom: 2 },
      subGraphTitlePadding: 0,
    },
    theme: 'dark',
  })
  const { code: chartCode, shapes } = jsonToMermaid(schema, 'TD')
  const { svg } = await mermaid.render(`cl-${spacing.nodeSpacing}`, chartCode)
  const doc = new DOMParser().parseFromString(svg, 'image/svg+xml')
  const clusters = []
  for (const g of doc.querySelectorAll('g.cluster')) {
    const rect = g.querySelector('rect')
    console.log(`  cluster ${g.getAttribute('id')} transform=${g.getAttribute('transform')} rect=${!!rect}`)
    if (!rect) continue
    clusters.push({
      label: g.getAttribute('id'),
      x: num(rect.getAttribute('x')),
      y: num(rect.getAttribute('y')),
      w: num(rect.getAttribute('width')),
      h: num(rect.getAttribute('height')),
    })
  }
  console.log(`--- spacing node=${spacing.nodeSpacing} rank=${spacing.rankSpacing} padding=${spacing.padding} ---`)
  for (let i = 0; i < clusters.length; i++) {
    const a = clusters[i]
    console.log(`  ${a.label}: (${a.x.toFixed(0)}, ${a.y.toFixed(0)}) ${a.w.toFixed(0)}x${a.h.toFixed(0)}`)
    for (let j = i + 1; j < clusters.length; j++) {
      const b = clusters[j]
      const overlapX = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)
      const overlapY = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y)
      if (overlapX > 0 && overlapY > 0) {
        console.log(`  !! НАЛОЖЕНИЕ ${a.label} и ${b.label}: X=${overlapX.toFixed(1)} Y=${overlapY.toFixed(1)}`)
      }
    }
  }
  void shapes
}
