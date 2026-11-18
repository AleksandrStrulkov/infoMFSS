import { useEffect, useRef, useState, Component } from 'react'
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch'
import mermaid from 'mermaid'
import { jsonToMermaid } from './utils/jsonToMermaid.js'
import { postProcessMermaidSvg } from './utils/postProcessDiagram.js'
import {
  exportSvgFile,
  exportPngFile,
  exportPdfFile,
  downloadText,
} from './utils/exportDiagram.js'

const schemasBase = document.getElementById('root')?.dataset.schemasUrl || '/power-circuit/schemas/'

async function fetchJson(url, signal) {
  const response = await fetch(url, { credentials: 'same-origin', signal, redirect: 'manual' })
  if (response.type === 'opaqueredirect' || response.status === 401 || response.status === 302) {
    throw new Error('Сессия истекла. Войдите снова и обновите страницу.')
  }
  if (!response.ok) throw new Error(`Не удалось загрузить схему (HTTP ${response.status}).`)
  if (!response.headers.get('content-type')?.toLowerCase().includes('application/json')) {
    throw new Error('Сервер вернул не JSON. Возможно, требуется повторный вход.')
  }
  return response.json()
}

function schemaUrl(id) {
  const [dir, filename, ...rest] = id.split('/')
  if (rest.length || !/^mine_[1-9][0-9]*$/.test(dir) || !filename?.endsWith('.json')) {
    throw new Error('Некорректный идентификатор схемы.')
  }
  return `${schemasBase}${encodeURIComponent(dir)}/${encodeURIComponent(filename)}/`
}

function configureMermaid() {
  // theme: 'default' и securityLevel: 'loose' — как в Mermaid Live Editor,
  // цвета берутся из classDef (mufta/lamp/... ) в тексте диаграммы,
  // никакие themeVariables их не перебивают
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',
    // обязательно на верхнем уровне: без этого mermaid рисует подписи
    // foreignObject'ом, и пост-обработка (тексты кругов, надписи и т.п.)
    // не находит <text> и не работает
    htmlLabels: false,
    theme: 'default',
    flowchart: {
      useMaxWidth: false,
      htmlLabels: false,
      // плавная интерполяция без ступенчатых ортогональных изломов;
      // финальные кабели всё равно строго осевые ( rebuilt в postProcess)
      curve: 'basis',
      // расслоение секций: рамки subgraph растягиваются заголовками,
      // поэтому горизонтальный зазор нужен большой, иначе кластеры наложатся
      nodeSpacing: 120,
      rankSpacing: 55,
      padding: 12,
      subGraphTitleMargin: { top: 0, bottom: 2 },
      subGraphTitlePadding: 0,
    },
  })
}

let renderCounter = 0

// цвет фона экспорта = фон канвы страницы в текущей теме
function themeBg() {
  const v = getComputedStyle(document.documentElement).getPropertyValue('--canvas-bg')
  return v ? String(v).trim() : document.documentElement.dataset.theme === 'light' ? '#f8fafc' : '#0b1220'
}

class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div className="error-panel">
          <h2>Непредвиденная ошибка приложения</h2>
          <pre>{String(this.state.error?.message || this.state.error)}</pre>
        </div>
      )
    }
    return this.props.children
  }
}

function groupMines(schemas) {
  const folders = new Map()
  for (const schema of schemas) {
    const dir = schema.id.split('/')[0]
    if (!folders.has(dir)) folders.set(dir, { dir, mine: schema.mine, files: [] })
    folders.get(dir).files.push(schema)
  }
  return [...folders.values()]
}

function SchemaViewer({ schemaFile, direction, lastSvgRef }) {
  const [renderError, setRenderError] = useState(null)
  const [rendered, setRendered] = useState(null)
  const schema = schemaFile?.data
  const schemaName = schemaFile?.name
  const renderKey = `${schemaFile?.id}:${direction}`

  useEffect(() => {
    let cancelled = false
    lastSvgRef.current = null

    const renderChart = async () => {
      if (!schema) return
      try {
        configureMermaid()
        const { code, shapes } = jsonToMermaid(schema, direction)
        const { svg } = await mermaid.render(`schema-render-${++renderCounter}`, code)
        const normalized = postProcessMermaidSvg(svg, { shapes })
        if (!cancelled) {
          setRendered({ key: renderKey, svg: normalized })
          lastSvgRef.current = { key: renderKey, svg: normalized }
          setRenderError(null)
        }
      } catch (err) {
        if (!cancelled) {
          setRendered(null)
          lastSvgRef.current = null
          const detail = err?.message || String(err)
          setRenderError({ key: renderKey, message: `Ошибка в схеме "${schemaName}.json":\n${detail}` })
        }
      }
    }

    renderChart()
    return () => {
      cancelled = true
    }
  }, [schema, schemaName, direction, renderKey, lastSvgRef])

  if (renderError?.key === renderKey && schemaFile) {
    return (
      <div className="error-panel">
        <h2>Схема не построена</h2>
        <pre>{renderError.message}</pre>
      </div>
    )
  }

  if (!schemaFile) {
    return (
      <div className="error-panel">
        <h2>Схема не построена</h2>
        <p>Схема для этой шахты ещё не загружена.</p>
      </div>
    )
  }

  return (
    <div
      className="schema-svg"
      // SVG сгенерирован локальным mermaid из пользовательского JSON
      dangerouslySetInnerHTML={{ __html: rendered?.key === renderKey ? rendered.svg : '' }}
    />
  )
}

export default function App() {
  const [mineList, setMineList] = useState([])
  const [catalogLoading, setCatalogLoading] = useState(true)
  const [loading, setLoading] = useState(false)
  const [loadError, setLoadError] = useState('')
  const [activeDir, setActiveDir] = useState('')
  const [activeFileId, setActiveFileId] = useState('')
  const [loadedSchema, setLoadedSchema] = useState(null)
  const transformRef = useRef(null)
  const lastSvgRef = useRef(null)
  const schemaData = loadedSchema?.id === activeFileId ? loadedSchema.data : null
  const schemaReady = Boolean(schemaData) && !loading && !catalogLoading && !loadError
  const requestIdRef = useRef(0)
  const mineFiles = mineList.find((m) => m.dir === activeDir)?.files ?? []
  const selected = mineFiles.find((file) => file.id === activeFileId) ?? null
  const mineTitle = mineList.find((m) => m.dir === activeDir)?.mine ?? activeDir

  useEffect(() => {
    const controller = new AbortController()
    fetchJson(schemasBase, controller.signal)
      .then((catalog) => {
        if (!Array.isArray(catalog.schemas)) throw new Error('Некорректный каталог схем.')
        const folders = groupMines(catalog.schemas)
        setMineList(folders)
        setActiveDir(folders[0]?.dir ?? '')
        setActiveFileId(folders[0]?.files[0]?.id ?? '')
      })
      .catch((error) => {
        if (error.name !== 'AbortError') setLoadError(error.message)
      })
      .finally(() => {
        if (!controller.signal.aborted) setCatalogLoading(false)
      })
    return () => controller.abort()
  }, [])

  useEffect(() => {
    requestIdRef.current += 1
    lastSvgRef.current = null
    setLoadedSchema(null)
    if (!activeFileId) {
      setLoading(false)
      return
    }
    setLoadError('')
    const controller = new AbortController()
    const requestId = requestIdRef.current
    setLoading(true)
    Promise.resolve()
      .then(() => {
        if (controller.signal.aborted || requestId !== requestIdRef.current) return null
        return fetchJson(schemaUrl(activeFileId), controller.signal)
      })
      .then((data) => {
        if (data && !controller.signal.aborted && requestId === requestIdRef.current) {
          setLoadedSchema({ id: activeFileId, data })
        }
      })
      .catch((error) => {
        if (!controller.signal.aborted && requestId === requestIdRef.current && error.name !== 'AbortError') {
          setLoadError(error.message)
        }
      })
      .finally(() => {
        if (!controller.signal.aborted && requestId === requestIdRef.current) setLoading(false)
      })
    return () => controller.abort()
  }, [activeFileId])
  const [direction, setDirection] = useState('TD')
  const renderKey = `${activeFileId}:${direction}`
  const [theme, setTheme] = useState(() =>
    document.documentElement.dataset.theme === 'light' ? 'light' : 'dark',
  )
  const [exportMenuOpen, setExportMenuOpen] = useState(false)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])

  const handleExport = async (kind) => {
    setExportMenuOpen(false)
    if (!selected || !schemaReady) return
    try {
      if (kind === 'json') {
        const pretty = JSON.stringify(schemaData, null, 2)
        downloadText(pretty, `${mineTitle}-${selected.name}.json`, 'application/json')
        return
      }
      const rendered = lastSvgRef.current
      if (!rendered || rendered.key !== renderKey) {
        window.alert('Схема ещё не отрисована — подождите, пока она построится.')
        return
      }
      const svgText = rendered.svg
      if (kind === 'svg') exportSvgFile(svgText, `${mineTitle}-${selected.name}`)
      else if (kind === 'png') await exportPngFile(svgText, `${mineTitle}-${selected.name}`, 2, themeBg())
      else if (kind === 'pdf') await exportPdfFile(svgText, `${mineTitle}-${selected.name}`, 2, themeBg())
    } catch (err) {
      window.alert(`Ошибка экспорта: ${err.message || err}`)
    }
  }

  return (
    <div className="app">
      <header className="toolbar">
        <div className="toolbar-title">infoMFSS · Инженерные схемы</div>

        <label className="toolbar-field">
          Шахта:
          <select
            value={activeDir}
            onChange={(e) => {
              const dir = e.target.value
              const folder = mineList.find((m) => m.dir === dir) ?? null
              requestIdRef.current += 1
              lastSvgRef.current = null
              setLoadedSchema(null)
              setLoading(true)
              setActiveDir(dir)
              setActiveFileId(folder?.files[0]?.id ?? '')
              transformRef.current?.resetTransform()
            }}
          >
            {mineList.map((m) => (
              <option key={m.dir} value={m.dir}>
                {m.mine}
              </option>
            ))}
          </select>
        </label>

        <label className="toolbar-field">
          Схема:
          <select
            value={activeFileId}
            onChange={(e) => {
              requestIdRef.current += 1
              lastSvgRef.current = null
              setLoadedSchema(null)
              setLoading(true)
              setActiveFileId(e.target.value)
              transformRef.current?.resetTransform()
            }}
          >
            {mineFiles.map((file) => (
              <option key={file.id} value={file.id}>
                {file.name}.json
              </option>
            ))}
          </select>
        </label>

        <button
          type="button"
          className="toolbar-btn"
          onClick={() => {
            lastSvgRef.current = null
            setDirection((d) => (d === 'TD' ? 'LR' : 'TD'))
          }}
          title="Ориентация схемы"
        >
          Ориентация: {direction === 'TD' ? 'сверху вниз' : 'слева направо'}
        </button>

        <button
          type="button"
          className="toolbar-btn"
          onClick={() => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))}
          title="Переключить фон"
        >
          Тема: {theme === 'dark' ? 'тёмная' : 'светлая'}
        </button>

        <div className="dropdown">
          <button
            type="button"
            className="toolbar-btn"
            onClick={() => setExportMenuOpen((open) => !open)}
          >
            Экспорт ▾
          </button>
          {exportMenuOpen && (
            <div className="dropdown-menu">
              <button type="button" onClick={() => handleExport('svg')}>
                SVG (вектор)
              </button>
              <button type="button" onClick={() => handleExport('png')}>
                PNG (2×)
              </button>
              <button type="button" onClick={() => handleExport('pdf')}>
                PDF (альбом/книжный по размеру)
              </button>
              <button type="button" onClick={() => handleExport('json')}>
                JSON (исходник)
              </button>
            </div>
          )}
        </div>

        <div className="toolbar-spacer" />

        <button type="button" className="toolbar-btn" onClick={() => transformRef.current?.zoomIn()}>
          Zoom +
        </button>
        <button type="button" className="toolbar-btn" onClick={() => transformRef.current?.zoomOut()}>
          Zoom −
        </button>
        <button
          type="button"
          className="toolbar-btn"
          onClick={() => transformRef.current?.resetTransform()}
        >
          Reset
        </button>
      </header>

      <main className="workspace">
        <ErrorBoundary>
          <TransformWrapper
            ref={transformRef}
            minScale={0.1}
            maxScale={6}
            centerOnInit
            wheel={{ step: 0.15 }}
            doubleClick={{ disabled: false, step: 1.3 }}
          >
            <TransformComponent wrapperClass="workspace-canvas" contentClass="workspace-content">
              {catalogLoading || loading || (activeFileId && !schemaData && !loadError) ? (
                <p>Загрузка схемы…</p>
              ) : loadError ? (
                <div className="error-panel">
                  <h2>Не удалось загрузить схему</h2>
                  <p>{loadError}</p>
                </div>
              ) : mineList.length === 0 ? (
                <div className="error-panel"><p>Пока нет доступных схем.</p></div>
              ) : (
                <SchemaViewer
                  key={activeFileId}
                  schemaFile={schemaData ? { ...selected, data: schemaData } : null}
                  direction={direction}
                  lastSvgRef={lastSvgRef}
                />
              )}
            </TransformComponent>
          </TransformWrapper>
        </ErrorBoundary>
      </main>
    </div>
  )
}
