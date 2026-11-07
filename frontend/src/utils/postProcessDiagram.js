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

  // --- Полная перестройка кабелей: ортогональные порты (4 стороны блока) ---
  // У каждого блока ровно 4 порта: верх (0°), право (90°), низ (180°),
  // лево (270°). Стрелки выходят и входят строго по нормали к грани.
  // Каждое ответвление занимает свою грань: если желаемая сторона занята,
  // берётся ближайшая свободная по направлению к встречному блоку.
  const fmt = (p) => `${p.x.toFixed(2)},${p.y.toFixed(2)}`
  const SIDE_TOP = 0
  const SIDE_RIGHT = 1
  const SIDE_BOTTOM = 2
  const SIDE_LEFT = 3

  const sideTowards = (node, other) => {
    const dx = other.center.x - node.center.x
    const dy = other.center.y - node.center.y
    if (Math.abs(dy) >= Math.abs(dx)) return dy >= 0 ? SIDE_BOTTOM : SIDE_TOP
    return dx >= 0 ? SIDE_RIGHT : SIDE_LEFT
  }

  const sideAnchor = (node, side) => {
    const margin = node.info.shape === 'circle' ? CIRCLE_MARGIN : RECT_MARGIN
    if (side === SIDE_TOP) return { x: node.center.x, y: node.center.y - (node.half.hh + margin) }
    if (side === SIDE_RIGHT) return { x: node.center.x + (node.half.hw + margin), y: node.center.y }
    if (side === SIDE_BOTTOM) return { x: node.center.x, y: node.center.y + (node.half.hh + margin) }
    return { x: node.center.x - (node.half.hw + margin), y: node.center.y }
  }

  // предпочесть при выборе свободной грани ту, куда «смотрит» встречный узел
  const candidatesFor = (side, node, other) => {
    const dx = other.center.x - node.center.x
    const dy = other.center.y - node.center.y
    if (side === SIDE_TOP || side === SIDE_BOTTOM) {
      const near = dx >= 0 ? SIDE_RIGHT : SIDE_LEFT
      const far = dx >= 0 ? SIDE_LEFT : SIDE_RIGHT
      return [side, near, far, (side + 2) % 4]
    }
    const near = dy >= 0 ? SIDE_BOTTOM : SIDE_TOP
    const far = dy >= 0 ? SIDE_TOP : SIDE_BOTTOM
    return [side, near, far, (side + 2) % 4]
  }

  // концы связей: отдельный конец на выход (s) и на вход (t)
  const ends = []
  const routable = new Set() // edges, у которых есть оба конца
  for (const edge of edges) {
    const s = nodes.get(edge.from)
    const t = nodes.get(edge.to)
    if (!s?.half || !t?.half) {
      edge.pathEl.setAttribute('d', sanitizePath(edge.pathEl.getAttribute('d') || ''))
      continue
    }
    routable.add(edge)
    ends.push({ edge, role: 's', nodeId: edge.from, node: s, other: t })
    ends.push({ edge, role: 't', nodeId: edge.to, node: t, other: s })
  }

  // Распределение по граням: чем однозначнее направление к встречному
  // блоку (доминирующая ось), тем раньше конец связи встаёт на свою
  // грань; занятые грани пропускаются, берётся ближайшая свободная
  const taken = new Map() // nodeId -> Set(side)
  for (const nodeId of nodes.keys()) {
    if (nodes.get(nodeId).half) taken.set(nodeId, new Set())
  }
  const ambiguous = (e) => {
    const dx = Math.abs(e.other.center.x - e.node.center.x)
    const dy = Math.abs(e.other.center.y - e.node.center.y)
    return Math.min(dx, dy) / (dx + dy + 1e-9)
  }
  const sideOf = new Map()
  ;[...ends]
    .sort((a, b) => ambiguous(a) - ambiguous(b))
    .forEach((e) => {
      const used = taken.get(e.nodeId)
      const desired = sideTowards(e.node, e.other)
      let side = null
      for (const cand of candidatesFor(desired, e.node, e.other)) {
        if (!used.has(cand)) {
          side = cand
          break
        }
      }
      // все 4 порта заняты — порт всё равно нужен (сгруппируются ниже)
      if (side === null) side = desired
      used.add(side)
      sideOf.set(e, side)
    })

  // Якорь — центр грани (строго по нормали). Если несколько концов
  // делят одну грань (портов не хватило) — разнос вдоль грани
  const ANCHOR_GAP = 16
  const faceGroups = new Map()
  for (const e of ends) {
    const key = `${e.nodeId}:${sideOf.get(e)}`
    faceGroups.set(key, (faceGroups.get(key) ?? []).concat(e))
  }
  for (const [key, list] of faceGroups.entries()) {
    const entityId = key.slice(0, key.lastIndexOf(':'))
    const side = Number(key.slice(key.lastIndexOf(':') + 1))
    const node = nodes.get(entityId)
    const verticalFace = side === SIDE_TOP || side === SIDE_BOTTOM
    const maxHalf = node.info.shape === 'circle'
      ? 12
      : Math.max((verticalFace ? node.half.hw : node.half.hh) - 6, 0)
    // сортировка по позиции встречного узла — линии не перекрещиваются
    list.sort((a, b) => (verticalFace ? a.other.center.x - b.other.center.x : a.other.center.y - b.other.center.y))
    const n = list.length
    const span = Math.min((n - 1) * ANCHOR_GAP, maxHalf * 2)
    list.forEach((e, i) => {
      e.offset = n === 1 ? 0 : -span / 2 + (span * i) / (n - 1)
      e.anchor = sideAnchor(node, side)
      if (verticalFace) e.anchor.x += e.offset
      else e.anchor.y += e.offset
    })
  }

  // Сборка пути: строго ортогональные сегменты (0° / 90° / 180° / 270°)
  for (const edge of routable) {
    const sEnd = ends.find((e) => e.edge === edge && e.role === 's')
    const tEnd = ends.find((e) => e.edge === edge && e.role === 't')
    const S = sEnd.anchor
    const T = tEnd.anchor
    const sSide = sideOf.get(sEnd)
    const tSide = sideOf.get(tEnd)
    const aVert = sSide === SIDE_TOP || sSide === SIDE_BOTTOM
    const bVert = tSide === SIDE_TOP || tSide === SIDE_BOTTOM
    let pts
    if (aVert && bVert) {
      pts = S.x === T.x
        ? [S, T]
        : [S, { x: S.x, y: (S.y + T.y) / 2 }, { x: T.x, y: (S.y + T.y) / 2 }, T]
    } else if (!aVert && !bVert) {
      pts = S.y === T.y
        ? [S, T]
        : [S, { x: (S.x + T.x) / 2, y: S.y }, { x: (S.x + T.x) / 2, y: T.y }, T]
    } else if (aVert) {
      pts = [S, { x: S.x, y: T.y }, T]
    } else {
      pts = [S, { x: T.x, y: S.y }, T]
    }
    // срез нулевых сегментов
    const clean = []
    for (const p of pts) {
      const last = clean[clean.length - 1]
      if (!last || Math.abs(last.x - p.x) > 0.01 || Math.abs(last.y - p.y) > 0.01) clean.push(p)
    }
    edge.pathEl.setAttribute('d', clean.map((p, i) => `${i === 0 ? 'M' : 'L'}${fmt(p)}`).join(''))
  }

  return new XMLSerializer().serializeToString(svg)
}
