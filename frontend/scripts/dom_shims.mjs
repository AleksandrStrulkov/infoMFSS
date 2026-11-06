import { JSDOM } from 'jsdom'

const dom = new JSDOM('<!DOCTYPE html><body></body>')
if (!global.window) global.window = dom.window
global.document = dom.window.document
try { global.navigator = dom.window.navigator } catch {}
if (!global.CSSStyleSheet) global.CSSStyleSheet = dom.window.CSSStyleSheet
global.DOMParser = dom.window.DOMParser
global.XMLSerializer = dom.window.XMLSerializer
if (!global.requestAnimationFrame) global.requestAnimationFrame = (cb) => setTimeout(cb, 0)
const safeBtoa = (str) => Buffer.from(unescape(encodeURIComponent(String(str))), 'binary').toString('base64')
global.btoa = safeBtoa
try { dom.window.btoa = safeBtoa } catch {}

const SVGProto = dom.window.SVGElement.prototype
if (!SVGProto.getBBox) {
  SVGProto.getBBox = function () {
    const tag = this.tagName.toLowerCase()
    const num = (v) => parseFloat(v || 0)
    if (tag === 'circle' || tag === 'ellipse') {
      const rx = num(this.getAttribute('rx')) || num(this.getAttribute('r'))
      const ry = num(this.getAttribute('ry')) || num(this.getAttribute('r'))
      const cx = num(this.getAttribute('cx'))
      const cy = num(this.getAttribute('cy'))
      return { x: cx - rx, y: cy - ry, width: rx * 2, height: ry * 2 }
    }
    if (tag === 'rect') {
      return { x: num(this.getAttribute('x')), y: num(this.getAttribute('y')), width: num(this.getAttribute('width')), height: num(this.getAttribute('height')) }
    }
    const d = this.getAttribute('d') || this.getAttribute('points') || ''
    const numbers = (d.match(/-?\d+(?:\.\d+)?/g) || []).map(Number)
    if (numbers.length >= 4) {
      const xs = numbers.filter((_, i) => i % 2 === 0)
      const ys = numbers.filter((_, i) => i % 2 === 1)
      const x0 = Math.min(...xs)
      const y0 = Math.min(...ys)
      return { x: x0, y: y0, width: Math.max(...xs) - x0, height: Math.max(...ys) - y0 }
    }
    const text = (this.textContent || '').trim()
    return { x: 0, y: 0, width: text.length * 7, height: 14 }
  }
}
const textProto = dom.window.SVGTextElement?.prototype || SVGProto
textProto.getComputedTextLength = function () {
  return (this.textContent || '').length * 7
}
textProto.getNumberOfChars = function () {
  return (this.textContent || '').length
}
textProto.getSubStringLength = function (offset, count) {
  return (this.textContent || '').slice(offset, offset + count).length * 7
}
textProto.getExtentOfChar = function () {
  return { x: 0, y: 0, width: 7, height: 12 }
}
textProto.getStartPositionOfChar = function () {
  return { x: 0, y: 0, matrixTransform: () => ({ x: 0, y: 0 }) }
}
textProto.getRotationOfChar = function () {
  return 0
}
textProto.getEndPositionOfChar = textProto.getStartPositionOfChar

export { dom }
