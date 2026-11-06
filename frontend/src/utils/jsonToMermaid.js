const INFO_KEY_PREFIX = 'информационно'

// Пастельные полупрозрачные фоны локаций (8-значный hex: последние 2 — альфа)
const ZONE_FILLS = [
  '#ffcdd259',
  '#c8e6c95c',
  '#bbdefb52',
  '#ffe0b252',
  '#b2dfdb5c',
  '#e1bee752',
  '#fff9c45c',
  '#e0e0e059',
  '#d1c4e952',
  '#b3e5fc52',
  '#ffccbc5c',
  '#c5cae952',
]

let safeIdCounter = 0

function escapeLabel(value) {
  return String(value)
    .replace(/"/g, '#quot;')
    .replace(/[\r\n]+/g, ' ')
    .trim()
}

// Класс узла определяется строго по префиксам/именам элементов
// (никаких названий подсистем в коде). Порядок проверок важен:
// суффикс "-БП" у "1ССМ11-БП" не должен сделать блок оранжевым.
function detectNodeMeta(name) {
  const lower = String(name).toLowerCase()
  if (lower.startsWith(INFO_KEY_PREFIX)) return { shape: 'rect', className: 'info' }
  if (lower.includes('тшм') || lower.includes('муфта')) return { shape: 'circle', className: 'mufta' }
  if (lower.includes('лампа')) return { shape: 'circle', className: 'lamp' }
  if (lower.includes('аош')) return { shape: 'rect', className: 'aosh' }
  if (lower.includes('шсу')) return { shape: 'rect', className: 'orange' }
  if (
    lower.includes('ссп') || lower.includes('ссм') || lower.includes('ссв') ||
    lower.includes('сср') || lower.includes('ссф')
  ) {
    return { shape: 'rect', className: 'blue' }
  }
  if (lower.includes('вк') || lower.includes('сзв')) return { shape: 'rect', className: 'green' }
  if (/^ft|\bft/i.test(String(name))) return { shape: 'rect', className: 'magenta' }
  if (lower.includes('бп')) return { shape: 'rect', className: 'orange' }
  return { shape: 'rect', className: 'other' }
}

// Название муфты переносим на вторую строку, чтобы круги были компактными
// и одинаковыми: "ТШМ №87" -> "ТШМ<br/>№87"
function muftaLabel(label) {
  const m = /^(тшм|муфта)\s*(.+)$/i.exec(label)
  if (!m) return label
  let rest = m[2]
  if (!rest.startsWith('№')) rest = `№${rest}`
  return `${m[1]}<br/>${rest}`
}

function nodeDefinition(id, name, meta) {
  let label = escapeLabel(name)
  if (meta.className === 'mufta') label = muftaLabel(label)
  if (meta.shape === 'circle') return `${id}(("${label}")):::${meta.className}`
  return `${id}["${label}"]:::${meta.className}`
}

function makeIdRegistry() {
  const idByName = new Map()
  const metaById = new Map()

  const getNodeId = (name) => {
    if (name === null || name === undefined) {
      throw new Error(`Узел с пустым именем (${name}) — проверьте JSON-схему.`)
    }
    const label = String(name).trim()
    if (!label) {
      throw new Error('В схеме встречается устройство с пустым названием — добавьте имя или удалите пустую запись.')
    }
    if (!idByName.has(label)) {
      const meta = detectNodeMeta(label)
      const id = `node_${safeIdCounter++}`
      idByName.set(label, id)
      metaById.set(id, meta)
    }
    return idByName.get(label)
  }

  return { getNodeId, idByName, metaById }
}

function normalizeConnections(schema) {
  const groups = []
  for (const key of Object.keys(schema)) {
    if (!key.toLowerCase().startsWith('connections')) continue
    const rawItems = schema[key]
    if (rawItems === undefined || rawItems === null) continue
    if (!Array.isArray(rawItems)) {
      throw new Error(`Поле "${key}" должно быть массивом связей, сейчас: ${typeof rawItems}.`)
    }
    const edges = []
    rawItems.forEach((item, index) => {
      if (!item || typeof item !== 'object' || Array.isArray(item)) {
        throw new Error(`"${key}[${index}]": связь должна быть объектом вида { from, to, cable }.`)
      }
      if (typeof item.from !== 'string' || !item.from.trim()) {
        throw new Error(`"${key}[${index}]": отсутствует или пустое поле "from".`)
      }
      const targets = Array.isArray(item.to) ? item.to : [item.to]
      if (targets.length === 0) {
        throw new Error(`"${key}[${index}]": поле "to" пустое (может быть строкой или массивом строк).`)
      }
      for (const target of targets) {
        if (typeof target !== 'string' || !target.trim()) {
          throw new Error(
            `"${key}[${index}]": элемент поля "to" должен быть непустой строкой, получено: ${JSON.stringify(target)}.`,
          )
        }
        edges.push({ from: item.from.trim(), to: target.trim(), cable: item.cable })
      }
    })
    groups.push({ key, edges })
  }
  return groups
}

export function jsonToMermaid(schema, direction = 'TD') {
  if (!schema || typeof schema !== 'object' || Array.isArray(schema)) {
    throw new Error('Схема должна быть JSON-объектом с ключами locations и connections_*.')
  }

  const flow = direction === 'LR' ? 'flowchart LR' : 'flowchart TD'
  const { getNodeId, idByName, metaById } = makeIdRegistry()
  const lines = [flow]

  // Шапка стилей: classDef сразу после заголовка диаграммы
  lines.push('  classDef mufta fill:#e0e0e0b8,stroke:#666,stroke-width:2px,color:#000')
  lines.push('  classDef lamp fill:#ffeb3bb3,stroke:#f9a825,stroke-width:2px,color:#000')
  lines.push('  classDef aosh fill:#fff59db3,stroke:#f9a825,stroke-width:1.5px,color:#000')
  lines.push('  classDef orange fill:#ffb74db3,stroke:#ef6c00,stroke-width:1.5px,color:#000')
  lines.push('  classDef blue fill:#bbdefbb3,stroke:#1565c0,stroke-width:1.5px,color:#000')
  lines.push('  classDef green fill:#a5d6a7b3,stroke:#2e7d32,stroke-width:1.5px,color:#000')
  lines.push('  classDef magenta fill:#f48fb1b3,stroke:#ad1457,stroke-width:1.5px,color:#000')
  lines.push('  classDef info fill:#f5f5f5b3,stroke:#9e9e9e,stroke-dasharray: 5 5,color:#333')
  lines.push('  classDef other fill:#eceff1b3,stroke:#78909c,stroke-width:1px,color:#000')

  const edgesInfo = []

  // --- locations ---
  const locations = schema.locations
  if (locations !== undefined && locations !== null && (typeof locations !== 'object' || Array.isArray(locations))) {
    throw new Error('Поле "locations", если оно задано, должно быть объектом вида { "Название выработки": ["Устройство", ...] }.')
  }
  const hasLocations = !!locations && typeof locations === 'object' && Object.keys(locations).length > 0

  const emittedAtRoot = new Set()
  const emitRootNode = (name) => {
    const id = getNodeId(name)
    if (emittedAtRoot.has(id)) return
    emittedAtRoot.add(id)
    lines.push(`  ${nodeDefinition(id, name, metaById.get(id))}`)
  }

  const subgraphNodeIds = new Set()

  if (hasLocations) {
    let subgraphIndex = 0
    for (const [locName, devices] of Object.entries(locations)) {
      if (!String(locName).trim()) {
        throw new Error('В "locations" встречается локация с пустым названием.')
      }
      if (!Array.isArray(devices)) {
        throw new Error(`locations["${locName}"]: значение должно быть массивом названий устройств.`)
      }

      const isInfoBlock = String(locName).toLowerCase().startsWith(INFO_KEY_PREFIX)

      if (isInfoBlock) {
        // Информационный блок — узлы рисуются без рамки subgraph
        devices.forEach((device) => emitRootNode(device))
      } else {
        const seen = new Set()
        const uniqueDevices = []
        devices.forEach((device) => {
          const name = String(device).trim()
          const id = getNodeId(name)
          if (!seen.has(id)) {
            seen.add(id)
            uniqueDevices.push({ id, name })
          }
        })
        if (uniqueDevices.length > 0) {
          const zoneIdx = subgraphIndex++
          const locId = `loc_${zoneIdx}`
          uniqueDevices.forEach(({ id }) => subgraphNodeIds.add(id))
          lines.push(`  subgraph ${locId}["${escapeLabel(locName)}"]`)
          for (const { id, name } of uniqueDevices) {
            lines.push(`    ${nodeDefinition(id, name, metaById.get(id))}`)
          }
          lines.push('  end')
          // Пастельный полупрозрачный фон группы — свой цвет у каждой локации
          lines.push(`  style ${locId} fill:${ZONE_FILLS[zoneIdx % ZONE_FILLS.length]},stroke:#9fb3c8`)
        }
      }
    }
  }

  // --- связи (заодно регистрируем узлы, которых нет ни в одной локации) ---
  const connectionGroups = normalizeConnections(schema)
  for (const group of connectionGroups) {
    for (const edge of group.edges) {
      getNodeId(edge.from)
      getNodeId(edge.to)
    }
  }

  if (hasLocations) {
    // Узлы, встречающиеся только в связях, ставим на верхний уровень
    for (const group of connectionGroups) {
      for (const edge of group.edges) {
        if (!subgraphNodeIds.has(getNodeId(edge.from))) emitRootNode(edge.from)
        if (!subgraphNodeIds.has(getNodeId(edge.to))) emitRootNode(edge.to)
      }
    }
  } else {
    // Схема без локаций: все узлы на верхнем уровне
    const roots = new Set()
    for (const group of connectionGroups) {
      for (const edge of group.edges) {
        roots.add(edge.from)
        roots.add(edge.to)
      }
    }
    roots.forEach(emitRootNode)
  }

  // --- связи: жирные стрелки ===> без дефолтных подписей;
  // текст на стрелке — только если в JSON явно задан cable ---
  for (const group of connectionGroups) {
    for (const edge of group.edges) {
      const fromId = getNodeId(edge.from)
      const toId = getNodeId(edge.to)
      const hasCable = edge.cable !== undefined && edge.cable !== null && String(edge.cable).trim() !== ''
      lines.push(
        hasCable
          ? `  ${fromId} ==>|"${escapeLabel(edge.cable)}"| ${toId}`
          : `  ${fromId} ==> ${toId}`,
      )
      edgesInfo.push({ from: fromId, to: toId })
    }
  }

  const shapes = {}
  for (const [id, meta] of metaById.entries()) {
    shapes[id] = { shape: meta.shape, className: meta.className }
  }

  return { code: lines.join('\n'), shapes, edges: edgesInfo }
}
