const INFO_KEY_PREFIX = 'информационно'

let safeIdCounter = 0

function escapeLabel(value) {
  return String(value)
    .replace(/"/g, '#quot;')
    .replace(/[\r\n]+/g, ' ')
    .trim()
}

// Класс узла определяется по тексту названия (регистронезависимо).
// Порядок проверок важен: "1ВК#16-БП" — это ВК (зелёный), а не БП;
// "ШСУ#3.2-БП" — ШСУ (синий).
function detectNodeMeta(name) {
  const lower = String(name).toLowerCase()
  if (lower.includes('тшм') || lower.includes('муфта')) return { shape: 'rect', className: 'coupling' }
  if (lower.includes('лампа')) return { shape: 'circle', className: 'lamp' }
  if (lower.includes('сзв')) return { shape: 'circle', className: 'ssv' }
  if (lower.includes('вк')) return { shape: 'rect', className: 'vk' }
  if (lower.includes('шсу')) return { shape: 'rect', className: 'shsu' }
  if (lower.includes('бп')) return { shape: 'rect', className: 'power' }
  if (
    lower.includes('ссм') ||
    lower.includes('ссв') ||
    lower.includes('сср') ||
    lower.includes('ссф') ||
    lower.includes('ссп')
  ) {
    return { shape: 'rect', className: 'equipment' }
  }
  return { shape: 'rect', className: 'neutral' }
}

function nodeDefinition(id, name, meta) {
  const label = escapeLabel(name)
  if (meta.shape === 'circle') return `${id}(("${label}"))`
  return `${id}["${label}"]`
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
    const isHighVoltage = /127/.test(key)
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
    groups.push({ key, isHighVoltage, edges })
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
          const locId = `loc_${subgraphIndex++}`
          uniqueDevices.forEach(({ id }) => subgraphNodeIds.add(id))
          lines.push(`  subgraph ${locId}["${escapeLabel(locName)}"]`)
          for (const { id, name } of uniqueDevices) {
            lines.push(`    ${nodeDefinition(id, name, metaById.get(id))}`)
          }
          lines.push('  end')
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

  // --- связи ---
  for (const group of connectionGroups) {
    for (const edge of group.edges) {
      const fromId = getNodeId(edge.from)
      const toId = getNodeId(edge.to)
      const hasCable = edge.cable !== undefined && edge.cable !== null && String(edge.cable).trim() !== ''
      if (group.isHighVoltage) {
        lines.push(
          hasCable
            ? `  ${fromId} ==>|"${escapeLabel(edge.cable)}"| ${toId}`
            : `  ${fromId} ==> ${toId}`,
        )
      } else {
        lines.push(
          hasCable
            ? `  ${fromId} -.->|"${escapeLabel(edge.cable)}"| ${toId}`
            : `  ${fromId} -.-> ${toId}`,
        )
      }
      edgesInfo.push({ from: fromId, to: toId })
    }
  }

  // --- раскраска ---
  const byClass = new Map()
  for (const id of metaById.keys()) {
    const className = metaById.get(id).className
    if (!byClass.has(className)) byClass.set(className, [])
    byClass.get(className).push(id)
  }
  if (byClass.size > 0) {
    lines.push('  classDef coupling fill:#475569,stroke:#94a3b8,color:#f1f5f9,stroke-width:2px;')
    lines.push('  classDef lamp fill:#dc2626,stroke:#fca5a5,color:#ffffff,stroke-width:2px;')
    lines.push('  classDef ssv fill:#16a34a,stroke:#86efac,color:#ffffff,stroke-width:2px;')
    lines.push('  classDef vk fill:#15803d,stroke:#4ade80,color:#ffffff,stroke-width:2px;')
    lines.push('  classDef shsu fill:#1d4ed8,stroke:#93c5fd,color:#ffffff,stroke-width:2px;')
    lines.push('  classDef power fill:#b45309,stroke:#fbbf24,color:#fef3c7,stroke-width:2px;')
    lines.push('  classDef equipment fill:#0f766e,stroke:#5eead4,color:#ecfdf5,stroke-width:2px;')
    lines.push('  classDef neutral fill:#1e293b,stroke:#64748b,color:#e2e8f0,stroke-width:1px;')
    for (const [className, ids] of byClass.entries()) {
      lines.push(`  class ${ids.join(',')} ${className};`)
    }
  }

  const shapes = {}
  for (const [id, meta] of metaById.entries()) {
    shapes[id] = { shape: meta.shape, className: meta.className }
  }

  return { code: lines.join('\n'), shapes, edges: edgesInfo }
}
