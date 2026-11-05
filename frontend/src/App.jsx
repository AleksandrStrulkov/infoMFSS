import { useEffect, useMemo, useRef, useState, Component } from 'react'
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch'
import mermaid from 'mermaid'
import { jsonToMermaid } from './utils/jsonToMermaid.js'

const rawSchemas = import.meta.glob('./data/schemas/*.json', {
  eager: true,
  query: '?raw',
  import: 'default',
})

function configureMermaid(theme) {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',
    flowchart: { useMaxWidth: false, htmlLabels: false },
    theme: theme === 'light' ? 'default' : 'dark',
    themeVariables: {
      fontFamily: 'Segoe UI, Arial, sans-serif',
      fontSize: '14px',
      background: theme === 'light' ? '#f8fafc' : '#0b1220',
      primaryColor: theme === 'light' ? '#e2e8f0' : '#1e293b',
      primaryTextColor: theme === 'light' ? '#1e293b' : '#e2e8f0',
      primaryBorderColor: theme === 'light' ? '#64748b' : '#64748b',
      lineColor: theme === 'light' ? '#475569' : '#94a3b8',
    },
  })
}

let renderCounter = 0

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

function parseSchemas() {
  const list = []
  for (const [path, text] of Object.entries(rawSchemas)) {
    const name = path.split('/').pop().replace(/\.json$/i, '')
    list.push({ name, path, text })
  }
  list.sort((a, b) => a.name.localeCompare(b.name))
  return list
}

function SchemaViewer({ schemaFile, direction, theme }) {
  const [error, setError] = useState(null)
  const [svg, setSvg] = useState('')

  useEffect(() => {
    let cancelled = false

    const renderChart = async () => {
      if (!schemaFile) return
      try {
        configureMermaid(theme)
        const schema = JSON.parse(schemaFile.text)
        const chartCode = jsonToMermaid(schema, direction)
        const { svg: rendered } = await mermaid.render(`schema-render-${++renderCounter}`, chartCode)
        if (!cancelled) {
          setSvg(rendered)
          setError(null)
        }
      } catch (err) {
        if (!cancelled) {
          setSvg('')
          const detail = err?.message || String(err)
          setError(`Ошибка в схеме "${schemaFile.name}.json":\n${detail}`)
        }
      }
    }

    renderChart()
    return () => {
      cancelled = true
    }
  }, [schemaFile, direction, theme])

  if (error) {
    return (
      <div className="error-panel">
        <h2>Схема не построена</h2>
        <pre>{error}</pre>
      </div>
    )
  }

  if (!schemaFile) {
    return (
      <div className="error-panel">
        <h2>Схемы не найдены</h2>
        <p>Положите JSON-файлы в frontend/src/data/schemas/ — они подхватятся автоматически.</p>
      </div>
    )
  }

  return (
    <div
      className="schema-svg"
      // SVG сгенерирован локальным mermaid из пользовательского JSON
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  )
}

export default function App() {
  const schemaFiles = useMemo(parseSchemas, [])
  const [selectedName, setSelectedName] = useState(() => schemaFiles[0]?.name ?? '')
  const [direction, setDirection] = useState('TD')
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme === 'light' ? 'light' : 'dark')
  const transformRef = useRef(null)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])

  const selected = schemaFiles.find((f) => f.name === selectedName) ?? null
  const activeName = selected ? selected.name : (schemaFiles[0]?.name ?? '')

  return (
    <div className="app">
      <header className="toolbar">
        <div className="toolbar-title">infoMFSS · Инженерные схемы</div>

        <label className="toolbar-field">
          Схема:
          <select
            value={activeName}
            onChange={(e) => {
              setSelectedName(e.target.value)
              transformRef.current?.resetTransform()
            }}
          >
            {schemaFiles.map((file) => (
              <option key={file.path} value={file.name}>
                {file.name}.json
              </option>
            ))}
          </select>
        </label>

        <button
          type="button"
          className="toolbar-btn"
          onClick={() => setDirection((d) => (d === 'TD' ? 'LR' : 'TD'))}
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
              <SchemaViewer schemaFile={selected} direction={direction} theme={theme} />
            </TransformComponent>
          </TransformWrapper>
        </ErrorBoundary>
      </main>
    </div>
  )
}
