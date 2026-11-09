import { useEffect, useMemo, useRef, useState, Component } from 'react'
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

const rawSchemas = import.meta.glob('./data/schemas/*/*.json', {
  eager: true,
  query: '?raw',
  import: 'default',
})

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

// Данные шахт лежат по папкам: src/data/schemas/mine_1/*.json, mine_2/...
// Название шахты берём из поля "mine" верхнего уровня каждого JSON
function parseMines() {
  const folders = new Map() // mine_N -> { dir, files: [...] }
  for (const [path, text] of Object.entries(rawSchemas)) {
    const parts = path.split('/')
    const dir = parts[parts.length - 2]
    const fileName = parts[parts.length - 1].replace(/\.json$/i, '')
    if (!folders.has(dir)) folders.set(dir, { dir, files: [] })
    folders.get(dir).files.push({ name: fileName, path, text })
  }
  const list = [...folders.values()]
  for (const folder of list) {
    folder.files.sort((a, b) => a.name.localeCompare(b.name))
    const mineNames = folder.files
      .map((f) => {
        try {
          const parsed = JSON.parse(f.text)
          const mine = parsed?.mine
          return typeof mine === 'string' && mine.trim() ? mine.trim() : null
        } catch {
          return null // битый/пустой файл — шахта именуется по папке
        }
      })
      .filter(Boolean)
    folder.mine = mineNames[0] ?? folder.dir
  }
  list.sort((a, b) => a.dir.localeCompare(b.dir, undefined, { numeric: true }))
  return list
}

function SchemaViewer({ schemaFile, direction, lastSvgRef }) {
  const [error, setError] = useState(null)
  const [svg, setSvg] = useState('')

  useEffect(() => {
    let cancelled = false

    const renderChart = async () => {
      if (!schemaFile) return
      try {
        configureMermaid()
        const schema = JSON.parse(schemaFile.text)
        const { code, shapes } = jsonToMermaid(schema, direction)
        const { svg: rendered } = await mermaid.render(`schema-render-${++renderCounter}`, code)
        const normalized = postProcessMermaidSvg(rendered, { shapes })
        if (!cancelled) {
          setSvg(normalized)
          if (lastSvgRef) lastSvgRef.current = normalized
          setError(null)
        }
      } catch (err) {
        if (!cancelled) {
          setSvg('')
          if (lastSvgRef) lastSvgRef.current = null
          const detail = err?.message || String(err)
          setError(`Ошибка в схеме "${schemaFile.name}.json":\n${detail}`)
        }
      }
    }

    renderChart()
    return () => {
      cancelled = true
    }
  }, [schemaFile, direction, lastSvgRef])

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
        <h2>Схема не построена</h2>
        <p>Схема для этой шахты ещё не загружена.</p>
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
  const mines = useMemo(parseMines, [])
  const [pendingDirs, setPendingDirs] = useState(() => {
    // шахты без файлов (пустые папки) glob не видит — список берём у dev-сервера
    const stored = sessionStorage.getItem('pendingMineDir')
    return stored ? [stored] : []
  })
  useEffect(() => {
    let cancelled = false
    fetch('/api/schema-dirs')
      .then((r) => r.json())
      .then((res) => {
        if (!cancelled && Array.isArray(res?.dirs)) setPendingDirs(res.dirs)
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [])
  // объединяем: папки с файлами + папки, которые dev-сервер знает на диске
  const mineList = useMemo(() => {
    const seen = new Map(mines.map((m) => [m.dir, m]))
    const list = [...mines]
    for (const dir of pendingDirs) {
      if (!seen.has(dir)) list.push({ dir, mine: dir, files: [] })
    }
    list.sort((a, b) => a.dir.localeCompare(b.dir, undefined, { numeric: true }))
    return list
  }, [mines, pendingDirs])
  // по умолчанию — mine_1 и первый файл в нём (если там есть файлы)
  const [activeDir, setActiveDir] = useState(
    () => sessionStorage.getItem('pendingMineDir') || (mines[0]?.dir ?? ''),
  )
  const [activeFileName, setActiveFileName] = useState(
    () => sessionStorage.getItem('pendingMineFile') || (mines[0]?.files[0]?.name ?? ''),
  )
  const mineFiles = mineList.find((m) => m.dir === activeDir)?.files ?? []
  const selected = mineFiles.find((f) => f.name === activeFileName) ?? mineFiles[0] ?? null
  const mineTitle = mineList.find((m) => m.dir === activeDir)?.mine ?? activeDir
  const [direction, setDirection] = useState('TD')
  const [theme, setTheme] = useState(() =>
    document.documentElement.dataset.theme === 'light' ? 'light' : 'dark',
  )
  const [exportMenuOpen, setExportMenuOpen] = useState(false)
  const transformRef = useRef(null)
  const lastSvgRef = useRef(null)
  const uploadInputRef = useRef(null)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])

  // Разовый выбор только что загруженной схемы: после перезагрузки страницы
  // (файл добавился в import.meta.glob) sessionStorage уже не нужен
  useEffect(() => {
    sessionStorage.removeItem('pendingSchema')
    sessionStorage.removeItem('pendingMineDir')
    sessionStorage.removeItem('pendingMineFile')
  }, [])

  const handleExport = async (kind) => {
    setExportMenuOpen(false)
    if (!selected) return
    try {
      if (kind === 'json') {
        const pretty = JSON.stringify(JSON.parse(selected.text), null, 2)
        downloadText(pretty, `${mineTitle}-${selected.name}.json`, 'application/json')
        return
      }
      const svgText = lastSvgRef.current
      if (!svgText) {
        window.alert('Схема ещё не отрисована — подождите, пока она построится.')
        return
      }
      if (kind === 'svg') exportSvgFile(svgText, `${mineTitle}-${selected.name}`)
      else if (kind === 'png') await exportPngFile(svgText, `${mineTitle}-${selected.name}`, 2, themeBg())
      else if (kind === 'pdf') await exportPdfFile(svgText, `${mineTitle}-${selected.name}`, 2, themeBg())
    } catch (err) {
      window.alert(`Ошибка экспорта: ${err.message || err}`)
    }
  }

  const handleUpload = async (event) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    try {
      const text = await file.text()
      JSON.parse(text) // проверяем до отправки, чтобы не плодить битые файлы
      const response = await fetch('/api/upload-schema', {
        method: 'POST',
        headers: {
          'content-type': 'application/json; charset=utf-8',
          'x-schema-filename': encodeURIComponent(file.name),
        },
        body: text,
      })
      const result = await response.json()
      if (!result.ok) throw new Error(result.error || `HTTP ${response.status}`)
      // После записи файла dev-сервер перезагрузит страницу
      // (import.meta.glob подхватит новый файл) — спрашиваем ту самую схему
      const [dir, base] = String(result.file).split('/')
      sessionStorage.setItem('pendingMineDir', dir)
      sessionStorage.setItem('pendingMineFile', (base ?? '').replace(/\.json$/i, ''))
      window.location.reload()
    } catch (err) {
      window.alert(`Не удалось загрузить схему: ${err.message || err}`)
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
              setActiveDir(dir)
              // при смене шахты — её первый файл, схема пересобирается
              setActiveFileName(folder?.files[0]?.name ?? '')
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
            value={selected?.name ?? ''}
            onChange={(e) => {
              setActiveFileName(e.target.value)
              transformRef.current?.resetTransform()
            }}
          >
            {mineFiles.map((file) => (
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

        <button
          type="button"
          className="toolbar-btn"
          onClick={() => uploadInputRef.current?.click()}
          title="Загрузить JSON-схему в проект"
        >
          Загрузить JSON…
        </button>
        <input
          ref={uploadInputRef}
          type="file"
          accept=".json,application/json"
          className="hidden-input"
          onChange={handleUpload}
        />

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
              <SchemaViewer
                schemaFile={selected}
                direction={direction}
                lastSvgRef={lastSvgRef}
              />
            </TransformComponent>
          </TransformWrapper>
        </ErrorBoundary>
      </main>
    </div>
  )
}
