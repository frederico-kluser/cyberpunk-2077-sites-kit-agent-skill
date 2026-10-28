// DOM mínimo para testar o renderer standalone sem browser.
// Só implementa o que o netkit-web.standalone.js usa — de propósito.

class Style {
  constructor() {
    this._p = {}
  }
  setProperty(name, value) {
    this._p[name] = String(value)
  }
  getPropertyValue(name) {
    return this._p[name] || ""
  }
}

export class El {
  constructor(tag) {
    this.tagName = String(tag).toUpperCase()
    this.children = []
    this.style = new Style()
    this.attrs = {}
    this.className = ""
    this.parentNode = null
    this._text = ""
  }
  setAttribute(name, value) {
    this.attrs[name] = String(value)
  }
  getAttribute(name) {
    return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null
  }
  appendChild(child) {
    child.parentNode = this
    this.children.push(child)
    return child
  }
  removeChild(child) {
    const index = this.children.indexOf(child)
    if (index >= 0) this.children.splice(index, 1)
    child.parentNode = null
    return child
  }
  get firstChild() {
    return this.children[0] || null
  }
  get lastChild() {
    return this.children[this.children.length - 1] || null
  }
  addEventListener() {}
  removeEventListener() {}
  set textContent(value) {
    this._text = String(value)
    this.children = []
  }
  get textContent() {
    if (this.children.length) return this.children.map((child) => child.textContent).join("")
    return this._text
  }
  set innerHTML(value) {
    this._text = String(value)
    this.children = []
  }
  get innerHTML() {
    return serialize(this)
  }
  querySelector() {
    return null
  }
}

function walk(el, fn) {
  fn(el)
  for (const child of el.children || []) walk(child, fn)
}

export function serialize(el) {
  if (!(el instanceof El)) return String(el)
  const tag = el.tagName.toLowerCase()
  const cls = el.className ? ` class="${el.className}"` : ""
  const style = Object.entries(el.style._p)
    .map(([key, value]) => `${key}:${value}`)
    .join(";")
  const st = style ? ` style="${style}"` : ""
  const attrs = Object.entries(el.attrs)
    .map(([key, value]) => ` ${key}="${value}"`)
    .join("")
  const inner = el.children.map(serialize).join("") || el._text
  return `<${tag}${cls}${st}${attrs}>${inner}</${tag}>`
}

export function findText(el) {
  let out = ""
  walk(el, (node) => {
    if (!node.children.length && node._text) out += node._text + "\n"
  })
  return out
}

export function findAll(el, predicate) {
  const out = []
  walk(el, (node) => {
    if (predicate(node)) out.push(node)
  })
  return out
}

export function makeDom() {
  const head = new El("head")
  const body = new El("body")
  const documentElement = new El("html")
  documentElement.appendChild(head)
  documentElement.appendChild(body)
  const listeners = new Map()
  const document = {
    head,
    body,
    documentElement,
    readyState: "complete",
    title: "",
    createElement: (tag) => new El(tag),
    getElementById(id) {
      let found = null
      walk(documentElement, (node) => {
        if (!found && node.getAttribute && node.getAttribute("id") === id) found = node
      })
      return found
    },
    querySelectorAll(selector) {
      if (selector !== "netsites[src], [data-netsite]") return []
      return findAll(documentElement, (node) => node.tagName === "NETSITES" && node.getAttribute("src"))
    },
    addEventListener(type, fn) {
      listeners.set(type, fn)
    },
    removeEventListener(type) {
      listeners.delete(type)
    },
  }
  return {
    document,
    fire(type) {
      const fn = listeners.get(type)
      if (fn) fn()
    },
  }
}
