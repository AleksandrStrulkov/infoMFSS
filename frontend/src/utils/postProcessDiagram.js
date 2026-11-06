const SVG_NS = 'http://www.w3.org/2000/svg'

const CIRCLE_RADIUS = 28
const CIRCLE_FONT_SIZE = 11
const CIRCLE_LINE_HEIGHT = 11
const RECT_MARGIN = 2
const CIRCLE_MARGIN = 5

function parseTranslate(el) {
  const m = /translate\(\s*(-?[\d.]+)[,\s]+(-?[\d.]+)/.exec(el.getAttribute('transform') || '')
  return m ? { x: parseFloat(m[1]), y: parseFloat(m[2]) } : { x: 0, y: 0 }
}

function stripNodeId(fullId) {
  // полный id вида "<renderId>-flowchart-node_3-7"
  const m = /-(node_\d+)-\d+$/.exec(fullId)
  return m ? m[1] : null
}

function splitNodeLines(text, maxChars) {
  const words = String(text).split(/\s+/).filter(Boolean)
  const lines = []
  let current = ''
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word
    if (candidate.length <= maxChars || !current) {
      current = candidate
    } else {
      lines.push(current)
      current = word
    }
  }
  if (current) lines.push(current)
  return lines
}

// Замена NaN-координат на последнюю валидную пару (mermaid иногда выдаёт NaN
// на концевых сегментах, если геометрия пересечения с фигурой не решается)
function sanitizePath(d) {
  const pairRe = /([-\dNaN.]+),([-\dNaN.]+)/g
  let lastX = 0
  let lastY = 0
  return d.replace(pairRe, (_, rawX, rawY) => {
    let x = Number(rawX)
    let y = Number(rawY)
    if (!Number.isFinite(x)) x = lastX
    if (!Number.isFinite(y)) y = lastY
    lastX = x
    lastY = y
    return `${x},${y}`
  })
}

export function postProcessMermaidSvg(svgText, meta) {
  const doc = new DOMParser().parseFromString(svgText, 'image/svg+xml')
  const svg = doc.documentElement

  const nodes = new Map()
  for (const g of doc.querySelectorAll('g.node')) {
    const id = stripNodeId(g.getAttribute('id') || '')
    if (!id) continue
    const info = meta.shapes?.[id] ?? { shape: 'rect', className: 'neutral' }
    const half = info.shape === 'circle'
      ? { hw: CIRCLE_RADIUS, hh: CIRCLE_RADIUS }
      : (() => {
          const rect = g.querySelector('rect.basic.label-container')
          if (!rect) return null
          return { hw: parseFloat(rect.getAttribute('width') || '0') / 2, hh: parseFloat(rect.getAttribute('height') || '0') / 2 }
        })()
    nodes.set(id, { g, info, half, center: parseTranslate(g) })
  }

  const edges = []
  for (const pathEl of doc.querySelectorAll('g.edgePaths path')) {
    const m = /L_(node_\d+)_(node_\d+)_(\d+)$/.exec(pathEl.getAttribute('id') || '')
    if (!m) continue
    edges.push({ pathEl, from: m[1], to: m[2] })
  }

  // --- Круги (Лампа / СЗВ): единый радиус, компактный многострочный текст ---
  for (const [, node] of nodes.entries()) {
    if (node.info.shape !== 'circle') continue
    const circle = node.g.querySelector('circle.basic.label-container')
    if (circle) circle.setAttribute('r', String(CIRCLE_RADIUS))
    const text = node.g.querySelector('g.label text')
    if (!text) continue
    // У mermaid текст иерархический: tspan.row > tspan.word. Берём только
    // строки верхнего уровня, иначе подписи задваиваются ("ТШМ ТШМ №87 №87")
    const lines = [...text.children]
      .filter((t) => t.tagName === 'tspan')
      .map((t) => String(t.textContent || '').trim())
      .filter(Boolean)
    // Если у круга уже есть многострочная метка (муфта "ТШМ<br/>№87") —
    // строки сохраняем как есть; однострочник (Лампа/СЗВ) переносим сами
    const wrapped = lines.length > 1 ? lines : splitNodeLines(text.textContent, 9)
    // mermaid сдвигает g.label на translate(0,-7) под свой шрифт —
    // сбрасываем, иначе весь текст уезжает вверх от центра круга
    for (const lg of node.g.querySelectorAll('g.label')) {
      if (lg.contains(text)) {
        lg.setAttribute('transform', 'translate(0, 0)')
        break
      }
    }
    const startY = -(wrapped.length - 1) * (CIRCLE_LINE_HEIGHT / 2) + CIRCLE_LINE_HEIGHT * 0.32
    while (text.firstChild) text.removeChild(text.firstChild)
    text.setAttribute('font-size', String(CIRCLE_FONT_SIZE))
    text.setAttribute('text-anchor', 'middle')
    text.setAttribute('x', '0')
    text.setAttribute('y', startY.toFixed(2))
    wrapped.forEach((line, i) => {
      const tspan = doc.createElementNS(SVG_NS, 'tspan')
      tspan.setAttribute('x', '0')
      if (i > 0) tspan.setAttribute('dy', String(CIRCLE_LINE_HEIGHT))
      tspan.textContent = line
      text.appendChild(tspan)
    })
  }

  // --- Полная перестройка кабелей: выход из полюса торца источника,
  // тройниковая развилка на свободной полосе между строками, вход
  // строго ортогонально в центр торца приёмника ---
  const fmt = (p) => `${p.x.toFixed(2)},${p.y.toFixed(2)}`
  for (const edge of edges) {
    const s = nodes.get(edge.from)
    const t = nodes.get(edge.to)
    if (!s?.half || !t?.half) {
      edge.pathEl.setAttribute('d', sanitizePath(edge.pathEl.getAttribute('d') || ''))
      continue
    }

    const marginS = s.info.shape === 'circle' ? CIRCLE_MARGIN : RECT_MARGIN
    const marginT = t.info.shape === 'circle' ? CIRCLE_MARGIN : RECT_MARGIN
    const dx = t.center.x - s.center.x
    const dy = t.center.y - s.center.y
    const vertical = Math.abs(dy) >= Math.abs(dx)

    // Полюс источника — грань, обращённая к приёмнику
    let source
    let target
    if (vertical) {
      const sideS = dy >= 0 ? 1 : -1
      const sideT = dy >= 0 ? -1 : 1
      source = {
        x: s.center.x,
        y: s.center.y + sideS * (s.half.hh + marginS),
      }
      target = {
        x: t.center.x,
        y: t.center.y + sideT * (t.half.hh + marginT),
      }
    } else {
      const sideS = dx >= 0 ? 1 : -1
      const sideT = dx >= 0 ? -1 : 1
      source = {
        x: s.center.x + sideS * (s.half.hw + marginS),
        y: s.center.y,
      }
      target = {
        x: t.center.x + sideT * (t.half.hw + marginT),
        y: t.center.y,
      }
    }

    // Тройниковая развилка на полосе между строками блоков
    let d
    if (vertical) {
      const yJoin = (source.y + target.y) / 2
      d = source.x === target.x
        ? `M${fmt(source)}L${fmt(target)}`
        : `M${fmt(source)}L${source.x.toFixed(2)},${yJoin.toFixed(2)}L${target.x.toFixed(2)},${yJoin.toFixed(2)}L${fmt(target)}`
    } else {
      const xJoin = (source.x + target.x) / 2
      d = source.y === target.y
        ? `M${fmt(source)}L${fmt(target)}`
        : `M${fmt(source)}L${xJoin.toFixed(2)},${source.y.toFixed(2)}L${xJoin.toFixed(2)},${target.y.toFixed(2)}L${fmt(target)}`
    }
    edge.pathEl.setAttribute('d', d)
  }

  return new XMLSerializer().serializeToString(svg)
}
