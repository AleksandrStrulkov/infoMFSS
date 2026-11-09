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

async function svgToCanvas(svgText, scale, bg) {
  // защита от переполнения canvas: размеры и координаты подъём
  const xml = /xmlns=/.test(svgText)
    ? svgText
    : svgText.replace(/<svg([>\s])/, '<svg xmlns="http://www.w3.org/2000/svg"$1')
  const blob = new Blob([xml], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  try {
    const img = await new Promise((resolve, reject) => {
      const image = new Image()
      image.onload = () => resolve(image)
      image.onerror = () => reject(new Error('Не удалось отрисовать SVG в bitmap.'))
      image.src = url
    })
    const naturalW = img.width || 800
    const naturalH = img.height || 600
    // максимум canvas ~16384×16384 px (ограничение браузеров)
    const fit = Math.min(1, 16384 / naturalW, 16384 / naturalH)
    const effScale = Math.max(1, Math.min(scale, fit * scale, fit))
    const width = naturalW
    const height = naturalH
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(width * effScale)
    canvas.height = Math.round(height * effScale)
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = bg || '#ffffff'
    ctx.fillRect(0, 0, width, height)
    ctx.scale(effScale, effScale)
    ctx.drawImage(img, 0, 0, width, height)
    return canvas
  } finally {
    URL.revokeObjectURL(url)
  }
}

// Фон экспорта всегда в теме, открытой на странице (PNG/PDF не прозрачны)
export async function exportPngFile(svgText, name, scale = 2, bg = '#ffffff') {
  const canvas = await svgToCanvas(svgText, scale, bg)
  const blob = await new Promise((resolve, reject) => {
    canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('Не удалось получить PNG.'))), 'image/png')
  })
  downloadBlob(blob, `${name}.png`)
}

// Ориентация PDF — альбомная/книжная — подбирается по пропорциям схемы
export async function exportPdfFile(svgText, name, scale = 2, bg = '#ffffff') {
  const canvas = await svgToCanvas(svgText, scale, bg)
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
