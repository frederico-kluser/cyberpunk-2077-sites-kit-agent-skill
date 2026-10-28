"use client"
/* ============================================================================
   NETKIT/WEB — netkit-web.js  (v1.0.0)
   Componentes React dos sites NET — o mesmo sistema visual do kit do estúdio
   (@cp77/netkit) e do mod NetSites, agora para a web.

   REGRAS DO FICHEIRO (não negociáveis):
   - Não há JSX: usa-se createElement, por isso o ficheiro entra em qualquer
     projeto (Vite, Next, CRA, Astro) sem transformação nenhuma.
   - Cor, tipo, peso e espaço vêm TODOS de netkit-web.css (variáveis --nk-*).
     Aqui não se escreve um hex novo, uma família de letras nem um tamanho novo.
   - Um site só usa o que este módulo exporta. Nada de HTML, CSS ou props soltas.

   Uso:
     import { Site, Page, Header, Hero, Text } from "./netkit/netkit-web.js"
     import "./netkit/netkit-web.css"
   ========================================================================== */
import {
  Children,
  Fragment,
  createContext,
  createElement as h,
  isValidElement,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react"

export const VERSION = "1.0.0"

/** Temas fechados (as cores vivem no CSS; aqui só os nomes). */
export const THEME_NAMES = ["net", "corpo", "street", "tabloid", "neon"]

const ALIGN = { start: "flex-start", center: "center", end: "flex-end", stretch: "stretch" }
const TEXT_ALIGN = { left: "left", center: "center", right: "right" }
const WEIGHT = {
  light: "var(--nk-w-light)",
  regular: "var(--nk-w-regular)",
  medium: "var(--nk-w-medium)",
  semibold: "var(--nk-w-semibold)",
  bold: "var(--nk-w-bold)",
  black: "var(--nk-w-black)",
}
const FONT = {
  raj: "var(--nk-font-raj)",
  orbitron: "var(--nk-font-orbitron)",
  blender: "var(--nk-font-blender)",
  industry: "var(--nk-font-industry)",
  arial: "var(--nk-font-arial)",
}

/* ------------------------------------------------------------------ helpers */

/** Unidades ink -> CSS. */
export const u = (n) => `calc(var(--nk-u) * ${n})`

const cx = (...names) => names.filter(Boolean).join(" ")

function box4(v) {
  if (v === undefined || v === null) return null
  return typeof v === "number" ? [v, v, v, v] : v
}

const space = (v) => {
  const b = box4(v)
  return b ? b.map(u).join(" ") : undefined
}

/** Props comuns a todos os nós (width/height/grow/margin/opacity/link/hover/name). */
function frame(p, hoverKind) {
  const s = {}
  if (p.width !== undefined) s.width = u(p.width)
  if (p.height !== undefined) s.height = u(p.height)
  if (p.grow !== undefined) s.flexGrow = p.grow
  if (p.selfAlign) {
    s.alignSelf = ALIGN[p.selfAlign] ?? p.selfAlign
    s.justifySelf = ALIGN[p.selfAlign] ?? p.selfAlign
  }
  if (p.margin !== undefined) s.margin = space(p.margin)
  if (p.opacity !== undefined) s.opacity = p.opacity
  if (p.background) s["--nk-bg-color"] = p.background
  if (p.border) s["--nk-border"] = `${u(p.border.width)} solid ${p.border.color}`
  if (p.hover) {
    if (hoverKind === "text" || hoverKind === "tint") s["--nk-hover-color"] = p.hover
    else s["--nk-hover-bg"] = p.hover
  }
  return s
}

/** Props de texto (incluindo a voz de título do tema). */
function type(p) {
  const s = {}
  if (p.heading) {
    s["--nk-font"] = "var(--nk-heading-font)"
    s["--nk-weight"] = "var(--nk-heading-weight)"
    s["--nk-color"] = "var(--nk-heading-color)"
    s["--nk-transform"] = "var(--nk-heading-transform)"
  }
  if (p.size !== undefined) s["--nk-size"] = p.size
  if (p.color) s["--nk-color"] = p.color
  if (p.font) s["--nk-font"] = FONT[p.font] ?? p.font
  if (p.weight) s["--nk-weight"] = WEIGHT[p.weight] ?? p.weight
  if (p.upper !== undefined) s["--nk-transform"] = p.upper ? "uppercase" : "none"
  if (p.align) s["--nk-align-text"] = TEXT_ALIGN[p.align] ?? p.align
  if (p.lineHeight !== undefined) s["--nk-lh"] = p.lineHeight
  if (p.wrap !== undefined) {
    s["--nk-wrap-mode"] = p.wrap ? "normal" : "nowrap"
    s.maxWidth = u(p.wrap)
  }
  return s
}

/** Constrói a etiqueta e as props de um nó (liga a <a> quando tem link). */
function attrs(p, cls, style, tag, hoverKind) {
  const isLink = Boolean(p.link)
  const props = {
    className: cx(cls, isLink && "nk-link"),
    style,
    "data-hover": isLink && p.hover ? hoverKind : undefined,
  }
  if (isLink) props.href = resolve(p.link)
  if (p.name) props["data-name"] = p.name
  return isLink ? ["a", props] : [tag, props]
}

/* ------------------------------------------------------------------ contexto */

const SiteCtx = createContext(null)

/** Acesso ao site (páginas, imagens, navegação). */
export function useNav() {
  const ctx = useContext(SiteCtx)
  if (!ctx) throw new Error("netkit-web: useNav() só funciona dentro de <Site>")
  return ctx
}

/** Endereço de uma página do site (hash — funciona em qualquer alojamento). */
export const pageHref = (id) => `#/${id}`

function resolve(to) {
  if (!to) return undefined
  const value = String(to)
  // um esquema (https:, mailto:, tel:, NETdir:) é um endereço; o resto é id de página
  return /^[a-z][a-z0-9+.-]*:/i.test(value) ? value : pageHref(value)
}

/* ------------------------------------------------------------------ site */

/** As <Page> do site, mesmo dentro de Fragmentos e listas. */
export function pagesOf(children) {
  const out = []
  const walk = (c) => {
    Children.forEach(c, (el) => {
      if (!isValidElement(el)) return
      if (el.type === Page) out.push(el)
      else if (el.type === Fragment) walk(el.props.children)
    })
  }
  walk(children)
  return out
}

/** Metadados do site (o que a NET mostra na lista e na barra de endereço). */
export function siteMeta(p) {
  const pages = pagesOf(p.children)
  const home = p.home ?? pages[0]?.props.id ?? "index"
  return {
    id: p.id,
    title: p.title,
    domain: p.domain,
    lang: p.lang,
    home,
    icon: p.icon,
    images: p.images ?? {},
    pages: pages.map((el) => {
      const path = el.props.path ?? (el.props.id === home ? "" : `/${el.props.id}`)
      return {
        id: el.props.id,
        title: el.props.title ?? el.props.id,
        path,
        address: `NETdir://${p.domain}${path}`,
      }
    }),
  }
}

function useHashRoute(meta) {
  const read = () => {
    if (typeof window === "undefined") return meta.home
    const id = window.location.hash.replace(/^#\/?/, "")
    return meta.pages.some((pg) => pg.id === id) ? id : meta.home
  }
  const [route, setRoute] = useState(read)
  useEffect(() => {
    const onHash = () => setRoute(read())
    window.addEventListener("hashchange", onHash)
    onHash()
    return () => window.removeEventListener("hashchange", onHash)
  }, [meta.home, meta.pages.length])
  return route
}

function MissingPage({ id }) {
  return h(
    "main",
    { className: "nk-page" },
    h(
      "div",
      { className: "nk-page-inner" },
      h(Text, { size: 64, color: "var(--nk-accent2)" }, `A página «${id}» não existe neste site`)
    )
  )
}

/**
 * O site: tema, imagens, páginas e navegação por hash.
 * `theme` é um dos cinco nomes fechados (net, corpo, street, tabloid, neon).
 */
export function Site(props) {
  const meta = useMemo(() => siteMeta(props), [props])
  const pages = pagesOf(props.children)
  const route = useHashRoute(meta)
  const theme = THEME_NAMES.includes(props.theme) ? props.theme : "net"
  const page = pages.find((el) => el.props.id === route) ?? pages[0]

  useEffect(() => {
    if (props.lang && typeof document !== "undefined") document.documentElement.lang = props.lang
  }, [props.lang])

  const ctx = useMemo(() => ({ meta, images: meta.images, href: resolve, page: route }), [meta, route])

  return h(
    SiteCtx.Provider,
    { value: ctx },
    h(
      "div",
      { className: `nk-site nk-theme-${theme}`, "data-nk-site": props.id },
      page ? h(Page, { ...page.props, __fromSite: true }) : h(MissingPage, { id: route })
    )
  )
}

/** Uma página do site (a raiz: fundo, margens interiores e scroll). */
export function Page(props) {
  const { children, background, padding, gap, align, name } = props
  const outer = {}
  if (background) outer["--nk-bg-color"] = background
  const inner = {}
  if (gap !== undefined) inner.gap = u(gap)
  if (padding !== undefined) inner.padding = space(padding)
  if (align) inner.alignItems = ALIGN[align] ?? align
  return h(
    "main",
    { className: "nk-page", style: outer, "data-name": name || "page" },
    h("div", { className: "nk-page-inner", style: inner }, children)
  )
}

/* ------------------------------------------------------------------ contentores */

/** Coluna: filhos de cima para baixo. */
export function Column(props) {
  const { children, padding, gap, align, background, border, ...rest } = props
  const style = frame({ background, border, ...rest }, "bg")
  if (padding !== undefined) style["--nk-pad"] = space(padding)
  if (gap !== undefined) style["--nk-gap"] = u(gap)
  if (align) style["--nk-align"] = ALIGN[align] ?? align
  const [el, p] = attrs(props, "nk-col", style, "div", "bg")
  return h(el, p, children)
}

/** Linha: filhos da esquerda para a direita. `stack` empilha no telemóvel. */
export function Row(props) {
  const { children, padding, gap, valign, background, border, stack, ...rest } = props
  const style = frame({ background, border, ...rest }, "bg")
  if (padding !== undefined) style["--nk-pad"] = space(padding)
  if (gap !== undefined) style["--nk-gap"] = u(gap)
  if (valign) style["--nk-valign"] = ALIGN[valign] ?? valign
  const [el, p] = attrs(props, "nk-row", style, "div", "bg")
  if (stack) p["data-stack"] = "1"
  return h(el, p, children)
}

/** Camadas: os filhos sobrepõem-se (imagem de fundo e texto por cima). */
export function Stack(props) {
  const { children, padding, align, valign, background, border, ...rest } = props
  const style = frame({ background, border, ...rest }, "bg")
  if (padding !== undefined) style["--nk-pad"] = space(padding)
  if (align) style["--nk-align"] = ALIGN[align] ?? align
  if (valign) style["--nk-valign"] = ALIGN[valign] ?? valign
  const [el, p] = attrs(props, "nk-stack", style, "div", "bg")
  return h(el, p, children)
}

/* ------------------------------------------------------------------ folhas */

/** O texto dos filhos, sem markup (o jogo não tem rich text). */
export function textOf(children) {
  if (children === null || children === undefined || typeof children === "boolean") return ""
  if (typeof children === "string" || typeof children === "number") return String(children)
  if (Array.isArray(children)) return children.map(textOf).join("")
  if (isValidElement(children)) return textOf(children.props.children)
  return ""
}

/**
 * Texto. `heading` veste a voz de título do tema (família, peso, cor, caixa).
 * `as` escolhe a etiqueta semântica: p, h1, h2, h3 ou span.
 */
export function Text(props) {
  const { children, as = "span", link, ...rest } = props
  const style = { ...frame({ ...rest, link }, "text"), ...type(rest) }
  const [el, p] = attrs({ ...rest, link }, "nk-text", style, as, "text")
  return h(el, p, textOf(children))
}

/** Imagem: ficheiro/URL do site (uma parte de atlas do jogo vira marcador no browser). */
export function Image(props) {
  const { image, tint, fit, alt = "", ...rest } = props
  const ctx = useContext(SiteCtx)
  const entry = ctx?.images?.[image]
  const style = frame({ ...rest, tint }, "tint")
  style["--nk-fit"] = fit === "contain" ? "contain" : "cover"
  const [el, p] = attrs(rest, "nk-imgbox", style, "div", "tint")
  const src = entry && (entry.url || entry.file)
  const inner = src
    ? h("img", { src, alt, loading: "lazy", decoding: "async", height: props.height ? "100%" : undefined })
    : h(
        "div",
        { className: "nk-missing", "data-atlas": entry?.atlas || "", "data-part": entry?.part || image },
        entry?.part || image
      )
  return h(el, p, inner, tint ? h("span", { className: "nk-tint", "aria-hidden": "true" }) : null)
}

/** Retângulo de cor (faixas, fundos, divisórias). */
export function Rect(props) {
  const style = frame(props, "bg")
  if (props.color) style["--nk-bg-color"] = props.color
  const [el, p] = attrs(props, "nk-rect", style, "div", "bg")
  return h(el, p)
}

/** Espaço vazio (fixo com width/height, elástico com grow). */
export function Spacer(props) {
  if (props.name) {
    return h("span", { className: "nk-sp", style: frame(props), "data-name": props.name, "aria-hidden": "true" })
  }
  return h("span", { className: "nk-sp", style: frame(props), "aria-hidden": "true" })
}

/* ------------------------------------------------------------------ blocos */

/** Navegação: links em linha; o ativo leva a barra de acento por baixo. */
export function NavBar({ items = [], active, gap = 64, size = 44, color, activeColor }) {
  return h(
    "nav",
    { className: "nk-nav", style: { "--nk-gap": u(gap) }, "aria-label": "Navegação do site" },
    items.map((it) => {
      const on = it.to === active
      return h(
        Column,
        { key: it.to, gap: 10, link: it.to, name: `nav_${it.to}` },
        h(Text, { size, weight: "semibold", upper: true, color: on ? activeColor || "var(--nk-accent)" : color || "var(--nk-text-color)" }, it.label),
        h("span", {
          className: "nk-nav-mark",
          style: { "--nk-mark": on ? activeColor || "var(--nk-accent)" : "transparent" },
          "aria-hidden": "true",
        })
      )
    })
  )
}

/** Cabeçalho: logótipo, nome, subtítulo, navegação e a linha de baixo. */
export function Header({ logo, logoSize = 160, title, subtitle, nav, active }) {
  return h(
    "header",
    { className: "nk-header", "data-name": "header" },
    h(
      "div",
      { className: "nk-header-row" },
      logo ? h(Image, { image: logo, width: logoSize, height: logoSize }) : null,
      h(
        "div",
        { className: "nk-header-titles" },
        h(Text, { size: 110, as: "h1", heading: true }, title),
        subtitle ? h(Text, { size: 44, color: "var(--nk-muted)" }, subtitle) : null
      )
    ),
    nav ? h(NavBar, { items: nav, active }) : null,
    h(Divider, { thickness: 4 })
  )
}

/** Destaque: imagem grande, título por cima e um botão. */
export function Hero({ image, title, text, cta, height = 820, align = "start" }) {
  return h(
    "section",
    { className: "nk-hero", style: { height: u(height), justifyItems: ALIGN[align] ?? align }, "data-name": "hero" },
    image
      ? h(Image, { image, height, selfAlign: "stretch" })
      : h(Rect, { height, selfAlign: "stretch", color: "var(--nk-surface)" }),
    h("span", { className: "nk-hero-veil", "aria-hidden": "true" }),
    h(
      "div",
      { className: "nk-hero-body" },
      h(Text, { size: 150, as: "h2", heading: true, color: "var(--nk-ink-white)", wrap: 2200 }, title),
      text ? h(Text, { size: 52, color: "var(--nk-ink-soft)", wrap: 1900 }, text) : null,
      cta ? h(Button, { label: cta.label, to: cta.to }) : null
    )
  )
}

/** Botão: caixa com fundo (solid) ou borda (outline) e texto. */
export function Button({ label, to, variant = "solid", size = 46, color, textColor }) {
  const solid = variant !== "outline"
  const style = { "--nk-bg-color": solid ? color || "var(--nk-accent)" : "transparent" }
  if (!solid) style["--nk-border"] = `${u(4)} solid ${color || "var(--nk-accent)"}`
  return h(
    "a",
    { className: "nk-btn nk-link", href: resolve(to), style, "data-hover": solid ? "bg" : undefined, "data-name": `button_${to}` },
    h(Text, { size, weight: "bold", upper: true, color: textColor || (solid ? "var(--nk-on-accent)" : color || "var(--nk-accent)") }, label)
  )
}

/** Cartão: imagem, etiqueta, título e texto; clicável quando tem `to`. */
export function Card({ image, title, text, to, width = 900, imageHeight = 480, meta }) {
  return h(
    Column,
    { width, background: "var(--nk-surface)", link: to, hover: to ? "var(--nk-line)" : undefined, name: "card" },
    image ? h(Image, { image, width, height: imageHeight }) : null,
    h(
      "div",
      { className: "nk-card-body" },
      meta ? h(Text, { size: 34, upper: true, weight: "semibold", color: "var(--nk-accent)" }, meta) : null,
      h(Text, { size: 58, as: "h3", weight: "bold", color: "var(--nk-on-surface)", wrap: width - 88 }, title),
      text ? h(Text, { size: 42, color: "var(--nk-text-color)", wrap: width - 88 }, text) : null
    )
  )
}

/** Grelha: divide os filhos em colunas (2 em tablet, 1 em telemóvel). */
export function Grid({ columns = 3, gap = 48, children }) {
  return h("div", { className: "nk-grid", style: { "--nk-cols": columns, "--nk-gap": u(gap) }, "data-name": "grid" }, children)
}

/** Secção com título e barra de acento. */
export function Section({ title, children, gap = 40 }) {
  return h(
    "section",
    { className: "nk-section", style: { "--nk-gap": u(gap) }, "data-name": "section" },
    h(
      "div",
      { className: "nk-section-head" },
      h("span", { className: "nk-section-bar", "aria-hidden": "true" }),
      h(Text, { size: 72, as: "h2", heading: true }, title)
    ),
    children
  )
}

/** Artigo: título, linha de autor/data, imagem e parágrafos (uma string por parágrafo). */
export function Article({ title, byline, body = [], width = 2200, image }) {
  return h(
    "article",
    { className: "nk-article", style: { maxWidth: u(width) }, "data-name": "article" },
    h(Text, { size: 96, as: "h2", weight: "bold", color: "var(--nk-on-surface)", wrap: width }, title),
    byline ? h(Text, { size: 38, upper: true, weight: "semibold", color: "var(--nk-muted)" }, byline) : null,
    image ? h(Image, { image, width, height: Math.round(width * 0.42) }) : null,
    body.map((p, i) => h(Text, { key: i, size: 46, color: "var(--nk-text-color)", wrap: width, lineHeight: 1.25 }, p))
  )
}

/** Produto: imagem, nome, preço em eurodólares e botão de comprar. */
export function ProductCard({ image, name, price, to, width = 640 }) {
  const shown = typeof price === "number" ? price.toLocaleString("pt-PT") : price
  return h(
    Column,
    { width, border: { color: "var(--nk-line)", width: 3 }, name: "product" },
    image ? h(Image, { image, width, height: width }) : h(Rect, { width, height: width, color: "var(--nk-line)" }),
    h(
      "div",
      { className: "nk-product-body" },
      h(Text, { size: 50, weight: "bold", color: "var(--nk-on-surface)", wrap: width - 80 }, name),
      h(
        Row,
        { gap: 18, valign: "center" },
        h(Text, { size: 58, weight: "bold", color: "var(--nk-accent)" }, shown),
        h(Text, { size: 36, upper: true, color: "var(--nk-muted)" }, "eddies")
      ),
      to ? h(Button, { label: "Comprar", to, size: 40 }) : null
    )
  )
}

/** Divisória. */
export function Divider({ color, thickness = 4, margin }) {
  const style = { "--nk-thickness": u(thickness) }
  if (color) style["--nk-bg-color"] = color
  if (margin !== undefined) style.margin = space(margin)
  return h("span", { className: "nk-divider", style, "aria-hidden": "true" })
}

/** Etiqueta pequena (estado, categoria). */
export function Badge({ text, color, textColor }) {
  return h(
    "span",
    { className: "nk-badge", style: { "--nk-bg-color": color || "var(--nk-accent)" } },
    h(Text, { size: 32, weight: "bold", upper: true, color: textColor || "var(--nk-on-accent)" }, text)
  )
}

/** Citação. */
export function Quote({ text, author, width = 2000 }) {
  return h(
    "blockquote",
    { className: "nk-quote", style: { maxWidth: u(width) }, "data-name": "quote" },
    h("span", { className: "nk-quote-bar", "aria-hidden": "true" }),
    h(
      "div",
      { className: "nk-quote-body" },
      h(Text, { size: 60, weight: "semibold", color: "var(--nk-text-color)", wrap: width }, `«${text}»`),
      author ? h(Text, { size: 38, upper: true, color: "var(--nk-muted)" }, `— ${author}`) : null
    )
  )
}

/** Lista com marcadores. */
export function BulletList({ items = [], width = 2200 }) {
  return h(
    "ul",
    { className: "nk-list", "data-name": "list" },
    items.map((it, i) =>
      h(
        "li",
        { className: "nk-list-item", key: i },
        h("span", { className: "nk-bullet", "aria-hidden": "true" }),
        h(Text, { size: 46, color: "var(--nk-text-color)", wrap: width }, it)
      )
    )
  )
}

/** Tabela (cabeçalho + linhas). `widths` em unidades ink. */
export function Table({ columns = [], rows = [], widths }) {
  const w = widths ?? columns.map(() => Math.floor(2400 / columns.length))
  return h(
    "div",
    { className: "nk-table-wrap" },
    h(
      "div",
      { className: "nk-table", style: { "--nk-border": `${u(3)} solid var(--nk-line)` }, role: "table" },
      h(
        "div",
        { className: "nk-tr", role: "row", style: { "--nk-bg-color": "var(--nk-surface)" } },
        columns.map((c, i) =>
          h(
            "div",
            { className: "nk-td", role: "columnheader", key: i, style: { width: u(w[i]), padding: `${u(22)} ${u(22)}` } },
            h(Text, { size: 38, upper: true, weight: "bold", color: "var(--nk-accent)" }, c)
          )
        )
      ),
      rows.map((r, ri) =>
        h(
          "div",
          { className: "nk-tr", role: "row", key: ri, style: { "--nk-bg-color": ri % 2 ? "var(--nk-surface)" : "transparent" } },
          r.map((c, i) =>
            h(
              "div",
              { className: "nk-td", role: "cell", key: i, style: { width: u(w[i]), padding: `${u(20)} ${u(22)}` } },
              h(Text, { size: 42, color: "var(--nk-text-color)", wrap: w[i] - 64 }, String(c))
            )
          )
        )
      )
    )
  )
}

/** Faixa de anúncio: imagem (ou cor) e texto grande; clicável quando tem `to`. */
export function Banner({ image, text, to, height = 300, color }) {
  const style = { height: u(height) }
  const inner = [
    image
      ? h(Image, { key: "img", image, height, selfAlign: "stretch" })
      : h(Rect, { key: "bg", height, selfAlign: "stretch", color: color || "var(--nk-accent2)" }),
    h(
      "div",
      { className: "nk-banner-body", key: "body" },
      h(Text, { size: 80, as: "h2", weight: "bold", upper: true, color: "var(--nk-ink-white)" }, text)
    ),
  ]
  const cls = cx("nk-banner", to && "nk-link")
  if (to) {
    return h("a", { href: resolve(to), className: cls, style, "data-hover": "bg", "data-name": "banner" }, inner)
  }
  return h("aside", { className: cls, style, "data-name": "banner" }, inner)
}

/** Rodapé com texto e links. */
export function Footer({ text, links = [] }) {
  return h(
    "footer",
    { className: "nk-footer", "data-name": "footer" },
    h(Divider, { thickness: 3 }),
    h(
      "div",
      { className: "nk-footer-row" },
      h(Text, { size: 36, color: "var(--nk-muted)" }, text),
      h(Spacer, { grow: 1 }),
      links.map((l) =>
        h(
          Text,
          { key: l.to, size: 36, upper: true, weight: "semibold", color: "var(--nk-link)", hover: "var(--nk-link-hover)", link: l.to },
          l.label
        )
      )
    )
  )
}
