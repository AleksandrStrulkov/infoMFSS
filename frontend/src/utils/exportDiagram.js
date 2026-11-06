import { jsPDF } from 'jspdf'

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export function downloadText(text, filename, mime) {
  downloadBlob(new Blob([text], { type: `${mime};charset=utf-8` }), filename)
}

// SVG от mermaid уже содержит <style> со всеми styles внутри файла
export function exportSvgFile(svgText, name) {
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n${svgText}`
  downloadText(xml, `${name}.svg`, 'image/svg+xml')
}

async function svgToCanvas(svgText, scale) {
  const blob = new Blob([svgText], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  try {
    const img = await new Promise((resolve, reject) => {
      const image = new Image()
      image.onload = () => resolve(image)
      image.onerror = () => reject(new Error('Не удалось отрисовать SVG в bitmap.'))
      image.src = url
    })
    const width = img.width || 800
    const height = img.height || 600
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(width * scale)
    canvas.height = Math.round(height * scale)
    const ctx = canvas.getContext('2d')
    ctx.scale(scale, scale)
    ctx.drawImage(img, 0, 0, width, height)
    return canvas
  } finally {
    URL.revokeObjectURL(url)
  }
}

export async function exportPngFile(svgText, name, scale = 2) {
  const canvas = await svgToCanvas(svgText, scale)
  const blob = await new Promise((resolve, reject) => {
    canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('Не удалось получить PNG.'))), 'image/png')
  })
  downloadBlob(blob, `${name}.png`)
}

// Ориентация PDF — альбомная/книжная — подбирается по пропорциям схемы
export async function exportPdfFile(svgText, name, scale = 2) {
  const canvas = await svgToCanvas(svgText, scale)
  const pngDataUrl = canvas.toDataURL('image/png')
  const width = canvas.width / scale
  const height = canvas.height / scale
  const doc = new jsPDF({
    orientation: width > height ? 'landscape' : 'portrait',
    unit: 'pt',
    format: [width, height],
    compress: true,
  })
  doc.addImage(pngDataUrl, 'PNG', 0, 0, width, height)
  doc.save(`${name}.pdf`)
}
