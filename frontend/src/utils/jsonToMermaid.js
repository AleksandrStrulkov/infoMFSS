const INFO_KEY_PREFIX = 'информационно'

let safeIdCounter = 0

function escapeLabel(value) {
  return String(value)
    .replace(/"/g, '#quot;')
    .replace(/[\r\n]+/g, ' ')
    .trim()
}

function detectClass(name) {
  const lower = String(name).toLowerCase()
  if (lower.includes('муфта')) return 'coupling'
  if (lower.includes('бп') || lower.includes('лампа')) return 'power'
  if (
    lower.includes('ссм') ||
    lower.includes('ссв') ||
    lower.includes('сср') ||
    lower.includes('ссф') ||
    lower.includes('ссп') ||
    lower.includes('вк') ||
    lower.includes('шсу')
  ) {
    return 'equipment'
  }
  return 'neutral'
}

function makeIdRegistry() {
  const idByName = new Map()
  const classNameById = new Map()

  const getNodeId = (name) => {
    if (name === null || name === undefined) {
      throw new Error(`Узел с пустым именем (${name}) — проверьте JSON-схему.`)
    }
    const label = String(name).trim()
    if (!label) {
      throw new Error('В схеме встречается устройство с пустым названием — добавьте имя или удалите пустую запись.')
    }
    if (!idByName.has(label)) {
      const id = `node_${safeIdCounter++}`
      idByName.set(label, id)
      classNameById.set(id, detectClass(label))
    }
    return idByName.get(label)
  }

  return { getNodeId, idByName, classNameById }
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
  const { getNodeId, classNameById } = makeIdRegistry()
  const lines = [flow]

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
    lines.push(`  ${id}["${escapeLabel(name)}"]`)
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
            lines.push(`    ${id}["${escapeLabel(name)}"]`)
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
    }
  }

  // --- раскраска ---
  const byClass = new Map()
  for (const [id, className] of classNameById.entries()) {
    if (!byClass.has(className)) byClass.set(className, [])
    byClass.get(className).push(id)
  }
  if (byClass.size > 0) {
    lines.push('  classDef coupling fill:#64748b,stroke:#cbd5e1,color:#f8fafc,rx:14,ry:14,stroke-width:2px;')
    lines.push('  classDef power fill:#b45309,stroke:#fbbf24,color:#fef3c7,stroke-width:2px;')
    lines.push('  classDef equipment fill:#0f766e,stroke:#5eead4,color:#ecfdf5,stroke-width:2px;')
    lines.push('  classDef neutral fill:#1e293b,stroke:#64748b,color:#e2e8f0,stroke-width:1px;')
    for (const [className, ids] of byClass.entries()) {
      lines.push(`  class ${ids.join(',')} ${className};`)
    }
  }

  return lines.join('\n')
}
