// Testes do NETKIT/WEB: o renderer standalone (com DOM mínimo) e o kit React
// (com um React mínimo), sem browser, sem dependências e sem internet.
import { readFileSync, writeFileSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { fileURLToPath, pathToFileURL } from "node:url"
import test from "node:test"
import assert from "node:assert/strict"

import { makeDom, findAll, findText } from "./dom-shim.mjs"
import { renderTree, treeText, treeFind, createElement as h } from "./react-shim.mjs"
const ROOT = fileURLToPath(new URL("..", import.meta.url))
const read = (relative) => readFileSync(join(ROOT, relative), "utf8")

const SPEC = {
  schema: "netsites-site/1",
  id: "teste",
  title: "Teste",
  domain: "teste.web",
  lang: "pt-BR",
  theme: "corpo",
  home: "index",
  images: {
    foto: { url: "/img/foto.jpg" },
    gato: { atlas: "base\\x.inkatlas", part: "gato" },
  },
  pages: [
    {
      id: "index",
      address: "NETdir://teste.web",
      title: "Início",
      root: {
        type: "page",
        props: { background: "#0a0a0a", padding: [180, 200, 180, 160], gap: 56 },
        children: [
          { type: "text", props: { text: "Olá Night City", size: 110, upper: true, color: "#ffffff" } },
          { type: "image", props: { image: "foto", width: 900, height: 480 } },
          { type: "image", props: { image: "gato", width: 300, height: 300 } },
          {
            type: "row",
            props: { gap: 40, valign: "center" },
            children: [
              { type: "rect", props: { width: 20, height: 20, color: "#e0312b" } },
              { type: "text", props: { text: "Sobre", link: "sobre", hover: "#ffffff" } },
            ],
          },
        ],
      },
    },
    {
      id: "sobre",
      address: "NETdir://teste.web/sobre",
      title: "Sobre",
      root: { type: "page", props: { background: "#0a0a0a" }, children: [{ type: "text", props: { text: "Segunda página" } }] },
    },
  ],
}

const { document } = makeDom()
globalThis.document = document
globalThis.window = {
  location: { hash: "" },
  addEventListener() {},
  removeEventListener() {},
}
globalThis.location = globalThis.window.location
globalThis.addEventListener = (type, fn) => {
  globalThis.__listeners = globalThis.__listeners || {}
  globalThis.__listeners[type] = fn
}
globalThis.removeEventListener = () => {}
globalThis.fetch = async () => ({ ok: true, json: async () => SPEC })

const fireHash = () => {
  const handler = (globalThis.__listeners || {}).hashchange
  if (handler) handler()
}

await import(pathToFileURL(join(ROOT, "assets/standalone/netkit-web.standalone.js")).href)

/* --------------------------------------------------------------------------- standalone */

test("standalone: expõe a API e a versão", () => {
  assert.ok(globalThis.NetKit, "NetKit não foi criado")
  assert.equal(globalThis.NetKit.version, "1.0.0")
  assert.deepEqual(globalThis.NetKit.themes, ["net", "corpo", "street", "tabloid", "neon"])
  assert.match(globalThis.NetKit.css, /--nk-accent/)
})

test("standalone: monta o site, o tema e a página inicial", () => {
  const host = document.createElement("div")
  const api = globalThis.NetKit.render(SPEC, host)
  assert.equal(host.children.length, 1)
  const site = host.children[0]
  assert.equal(site.className, "nk-site nk-theme-corpo")
  assert.equal(site.getAttribute("data-nk-site"), "teste")
  const main = site.children[0]
  assert.equal(main.className, "nk-page")
  assert.equal(main.style.getPropertyValue("--nk-bg-color"), "#0a0a0a")
  const inner = main.children[0]
  assert.equal(inner.className, "nk-page-inner")
  assert.equal(inner.style.padding, "calc(var(--nk-u) * 180) calc(var(--nk-u) * 200) calc(var(--nk-u) * 180) calc(var(--nk-u) * 160)")
  assert.equal(inner.style.gap, "calc(var(--nk-u) * 56)")
  assert.match(findText(host), /Olá Night City/)
  assert.equal(document.title, "Teste")
  assert.equal(api.meta.home, "index")
})

test("standalone: texto, imagem, marcador de atlas, link e hover", () => {
  const host = document.createElement("div")
  globalThis.NetKit.render(SPEC, host)
  const texts = findAll(host, (node) => node.className === "nk-text")
  const titulo = texts[0]
  assert.equal(titulo.textContent, "Olá Night City")
  assert.equal(titulo.style.getPropertyValue("--nk-size"), "110")
  assert.equal(titulo.style.getPropertyValue("--nk-transform"), "uppercase")
  assert.equal(titulo.style.getPropertyValue("--nk-color"), "#ffffff")

  const img = findAll(host, (node) => node.tagName === "IMG")[0]
  assert.equal(img.getAttribute("src"), "/img/foto.jpg")
  assert.equal(img.getAttribute("loading"), "lazy")

  const missing = findAll(host, (node) => node.className === "nk-missing")[0]
  assert.equal(missing.getAttribute("data-part"), "gato")

  const link = findAll(host, (node) => node.tagName === "A")[0]
  assert.equal(link.getAttribute("href"), "#/sobre")
  assert.equal(link.getAttribute("data-hover"), "text")
  assert.equal(link.style.getPropertyValue("--nk-hover-color"), "#ffffff")

  const row = findAll(host, (node) => node.className === "nk-row")[0]
  assert.equal(row.style.getPropertyValue("--nk-gap"), "calc(var(--nk-u) * 40)")
  assert.equal(row.style.alignItems, "center")
  const rect = findAll(host, (node) => node.className === "nk-rect")[0]
  assert.equal(rect.style.getPropertyValue("--nk-bg-color"), "#e0312b")
})

test("standalone: navega por hash sem recarregar", () => {
  const host = document.createElement("div")
  globalThis.NetKit.render(SPEC, host)
  assert.match(findText(host), /Olá Night City/)
  globalThis.location.hash = "#/sobre"
  fireHash()
  assert.match(findText(host), /Segunda página/)
  assert.doesNotMatch(findText(host), /Olá Night City/)
  globalThis.location.hash = ""
  fireHash()
  assert.match(findText(host), /Olá Night City/)
})

test("standalone: injeta o CSS uma única vez", () => {
  globalThis.NetKit.ensureCSS(document)
  globalThis.NetKit.ensureCSS(document)
  const styles = findAll(document.documentElement, (node) => node.getAttribute("id") === "nk-web-css")
  assert.equal(styles.length, 1)
  assert.match(styles[0].textContent, /\.nk-page/)
})

test("standalone: o código fora do bloco de CSS não tem cores literais", () => {
  const source = read("assets/standalone/netkit-web.standalone.js")
  const withoutCss = source.replace(/\/\* NETKIT:CSS:BEGIN \*\/[\s\S]*?\/\* NETKIT:CSS:END \*\//, "")
  assert.equal((withoutCss.match(/#[0-9a-fA-F]{6}/g) || []).length, 0, "as cores vivem só no CSS")
})

test("standalone: mount() vai buscar o JSON", async () => {
  const host = document.createElement("div")
  const api = await globalThis.NetKit.mount("/site.json", host)
  assert.equal(api.meta.id, "teste")
  assert.match(findText(host), /Olá Night City/)
})

/* --------------------------------------------------------------------------- kit React */

const reactShim = pathToFileURL(join(ROOT, "tests/react-shim.mjs")).href
const kitSource = read("assets/netkit-web/netkit-web.js").replace(/from "react"/, `from "${reactShim}"`)
const kitPath = join(tmpdir(), `netkit-web-${process.pid}.mjs`)
writeFileSync(kitPath, kitSource, "utf8")
const kit = await import(pathToFileURL(kitPath).href)

test("react: exporta tudo o que a documentação promete", () => {
  const expected = [
    "Site", "Page", "Column", "Row", "Stack", "Text", "Image", "Rect", "Spacer",
    "NavBar", "Header", "Hero", "Button", "Card", "Grid", "Section", "Article",
    "ProductCard", "Divider", "Badge", "Quote", "BulletList", "Table", "Banner", "Footer",
    "THEME_NAMES", "VERSION", "pagesOf", "siteMeta", "textOf", "u", "pageHref", "useNav",
  ]
  for (const name of expected) assert.ok(kit[name] !== undefined, `falta exportar ${name}`)
  assert.equal(kit.VERSION, "1.0.0")
})

test("react: componentes não têm cores literais (só variáveis do CSS)", () => {
  const hex = kitSource.match(/#[0-9a-fA-F]{6}/g) || []
  assert.deepEqual(hex, [], `o kit não escreve cores: ${hex.join(", ")}`)
})

test("react: Text, Column, Row e ligações", () => {
  const text = renderTree(kit.Text({ size: 46, color: "var(--nk-accent)", children: "Olá" }))
  assert.equal(text.tag, "span")
  assert.match(text.props.className, /nk-text/)
  assert.equal(text.props.style["--nk-size"], 46)
  assert.equal(treeText(text), "Olá")

  const heading = renderTree(kit.Text({ heading: true, children: "Título" }))
  assert.equal(heading.props.style["--nk-font"], "var(--nk-heading-font)")
  assert.equal(heading.props.style["--nk-transform"], "var(--nk-heading-transform)")

  const link = renderTree(kit.Text({ link: "sobre", children: "ir" }))
  assert.equal(link.tag, "a")
  assert.equal(link.props.href, "#/sobre")
  assert.match(link.props.className, /nk-link/)
  assert.equal(link.props["data-hover"], undefined, "sem hover não há cor de destaque: só o véu do CSS")

  const hover = renderTree(kit.Text({ link: "sobre", hover: "var(--nk-link-hover)", children: "ir" }))
  assert.equal(hover.props["data-hover"], "text")
  assert.equal(hover.props.style["--nk-hover-color"], "var(--nk-link-hover)")

  const external = renderTree(kit.Text({ link: "mailto:ola@neon.web", children: "mail" }))
  assert.equal(external.props.href, "mailto:ola@neon.web", "mailto: é endereço, não id de página")

  const col = renderTree(kit.Column({ gap: 40, padding: [0, 0, 0, 24], children: "x" }))
  assert.equal(col.props.style["--nk-gap"], "calc(var(--nk-u) * 40)")
  assert.equal(col.props.style["--nk-pad"], "calc(var(--nk-u) * 0) calc(var(--nk-u) * 0) calc(var(--nk-u) * 0) calc(var(--nk-u) * 24)")

  const row = renderTree(kit.Row({ stack: true, link: "index", hover: "var(--nk-line)", children: "x" }))
  assert.equal(row.tag, "a")
  assert.equal(row.props["data-stack"], "1")
  assert.equal(row.props["data-hover"], "bg")
  assert.equal(row.props.style["--nk-hover-bg"], "var(--nk-line)")
})

test("react: Site escolhe a página, o tema e o idioma", () => {
  const tree = renderTree(
    kit.Site({
      id: "s",
      title: "S",
      domain: "s.web",
      theme: "neon",
      lang: "pt-BR",
      children: [
        h(kit.Page, { id: "index", children: [kit.Text({ children: "primeira" })] }),
        h(kit.Page, { id: "sobre", children: [kit.Text({ children: "segunda" })] }),
      ],
    })
  )
  assert.match(tree.props.className, /nk-theme-neon/)
  assert.match(treeText(tree), /primeira/)
  assert.doesNotMatch(treeText(tree), /segunda/)
})

test("react: blocos desenham o que prometem", () => {
  const header = renderTree(kit.Header({ title: "N", subtitle: "sub", nav: [{ label: "Início", to: "index" }], active: "index" }))
  assert.match(treeText(header), /Nn?sub/)
  const h1 = treeFind(header, (node) => node.tag === "h1")
  assert.equal(h1.length, 1)

  const hero = renderTree(kit.Hero({ title: "Título", text: "linha", cta: { label: "Ir", to: "index" } }))
  assert.equal(treeFind(hero, (node) => node.props.className === "nk-hero").length, 1)
  assert.equal(treeFind(hero, (node) => node.props.className === "nk-hero-veil").length, 1)
  assert.equal(hero.props.style.height, "calc(var(--nk-u) * 820)")

  const button = renderTree(kit.Button({ label: "Comprar", to: "index" }))
  assert.equal(button.tag, "a")
  assert.equal(button.props.href, "#/index")

  const card = renderTree(kit.Card({ title: "C", text: "t", to: "index", meta: "META" }))
  assert.equal(card.tag, "a")
  assert.match(treeText(card), /META/)

  const grid = renderTree(kit.Grid({ columns: 2, children: [kit.Text({ children: "a" }), kit.Text({ children: "b" })] }))
  assert.equal(grid.props.style["--nk-cols"], 2)

  const table = renderTree(kit.Table({ columns: ["A", "B"], rows: [["1", "2"]] }))
  assert.equal(treeFind(table, (node) => node.props.role === "columnheader").length, 2)

  const list = renderTree(kit.BulletList({ items: ["um", "dois"] }))
  assert.equal(treeFind(list, (node) => node.props.className === "nk-bullet").length, 2)

  const footer = renderTree(kit.Footer({ text: "©", links: [{ label: "Sobre", to: "sobre" }] }))
  assert.equal(treeFind(footer, (node) => node.props.href === "#/sobre").length, 1)
})

test("react: todos os componentes renderizam com as props mínimas", () => {
  const props = {
    Site: { id: "s", title: "S", domain: "s.web", children: h(kit.Page, { id: "index", children: "x" }) },
    Page: { id: "p", children: "x" },
    Column: { children: "x" },
    Row: { children: "x" },
    Stack: { children: "x" },
    Text: { children: "x" },
    Image: { image: "foto" },
    Rect: { width: 10, height: 10 },
    Spacer: { grow: 1 },
    NavBar: { items: [{ label: "a", to: "index" }] },
    Header: { title: "T" },
    Hero: { title: "T" },
    Button: { label: "B", to: "index" },
    Card: { title: "C" },
    Grid: { children: "x" },
    Section: { title: "S" },
    Article: { title: "A", body: ["p1"] },
    ProductCard: { name: "P", price: 100 },
    Divider: {},
    Badge: { text: "B" },
    Quote: { text: "Q" },
    BulletList: { items: ["i"] },
    Table: { columns: ["A"], rows: [["1"]] },
    Banner: { text: "B" },
    Footer: { text: "F" },
  }
  for (const [name, values] of Object.entries(props)) {
    const tree = renderTree(kit[name](values))
    assert.ok(tree, `${name} não desenhou nada`)
  }
})

test("react: sem Site, a imagem mostra o marcador e o texto não parte", () => {
  const tree = renderTree(kit.Image({ image: "naoexiste", width: 100, height: 100 }))
  assert.equal(treeFind(tree, (node) => node.props.className === "nk-missing").length, 1)
  assert.equal(kit.textOf([kit.Text({ children: "a" }), "b", 3, null]), "ab3")
})

test.after(() => {
  try {
    rmSync(kitPath)
  } catch {
    /* nada a limpar */
  }
})
