// React mínimo para testar o netkit-web.js sem instalar React: só o que o kit usa.
// As funções são chamadas como componentes normais por `renderTree`.

export const Fragment = Symbol.for("react.fragment")

const PROVIDERS = new Map()

export function createElement(type, props, ...children) {
  const merged = { ...(props || {}) }
  const flat = children.length > 1 ? children : children.length === 1 ? children[0] : undefined
  if (flat !== undefined) merged.children = flat
  return { type, props: merged }
}

export function isValidElement(value) {
  return Boolean(value) && typeof value === "object" && "type" in value && "props" in value
}

export const Children = {
  forEach(children, fn) {
    if (children === null || children === undefined) return
    if (Array.isArray(children)) {
      children.forEach((child) => fn(child))
      return
    }
    fn(children)
  },
}

export function createContext(defaultValue) {
  const ctx = { _value: defaultValue }
  ctx.Provider = function Provider() {}
  PROVIDERS.set(ctx.Provider, ctx)
  return ctx
}

export function useContext(ctx) {
  return ctx._value
}

export function useMemo(fn) {
  return fn()
}

export function useState(initial) {
  return [typeof initial === "function" ? initial() : initial, () => {}]
}

export function useEffect() {}
export function useCallback(fn) {
  return fn
}

function render(node) {
  if (node === null || node === undefined || node === false || node === true) return null
  if (typeof node === "string" || typeof node === "number") return String(node)
  if (Array.isArray(node)) return node.map(render).filter((x) => x !== null)
  if (!isValidElement(node)) return null

  if (PROVIDERS.has(node.type)) {
    const ctx = PROVIDERS.get(node.type)
    const previous = ctx._value
    ctx._value = node.props.value
    const out = render(node.props.children)
    ctx._value = previous
    return out
  }
  if (typeof node.type === "function") return render(node.type(node.props))
  if (node.type === Fragment) return render(node.props.children)

  return {
    tag: node.type,
    props: node.props,
    children: [].concat(render(node.props.children) || []),
  }
}

/** Converte o resultado de um componente em árvore simples (tag/props/children). */
export function renderTree(element) {
  const out = render(element)
  if (out === null) return { tag: null, props: {}, children: [] }
  if (typeof out === "string") return { text: out }
  if (Array.isArray(out)) return out
  return out
}

/** Todo o texto da árvore, na ordem. */
export function treeText(tree) {
  if (tree === null || tree === undefined) return ""
  if (typeof tree === "string") return tree
  if (Array.isArray(tree)) return tree.map(treeText).join("")
  if (tree.text !== undefined) return String(tree.text)
  return (tree.children || []).map(treeText).join("")
}

/** Todos os nós da árvore que satisfazem o predicado. */
export function treeFind(tree, predicate) {
  const out = []
  const walk = (node) => {
    if (!node || typeof node === "string") return
    if (Array.isArray(node)) {
      node.forEach(walk)
      return
    }
    if (predicate(node)) out.push(node)
    ;(node.children || []).forEach(walk)
  }
  walk(tree)
  return out
}
