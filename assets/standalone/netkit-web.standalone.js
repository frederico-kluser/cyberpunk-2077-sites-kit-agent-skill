/* ============================================================================
   NETKIT/WEB — netkit-web.standalone.js  (v1.0.0)
   Desenha um site `netsites-site/1` no browser SEM React, SEM build e SEM
   dependências: uma tag <script> e o site aparece.

   Injeção mínima (site estático, WordPress, qualquer HTML):

     <link rel="stylesheet" href="/netkit/netkit-web.css">   (opcional: o script
                                                              injeta o CSS sozinho)
     <netsites src="/netkit/site.json"></netsites>
     <script src="/netkit/netkit-web.standalone.js" defer></script>

   Ou por código:

     NetKit.render(spec, "#alvo")      // spec já em memória
     NetKit.mount("/netkit/site.json", "#alvo")   // vai buscar o JSON

   O CSS vai EMBUTIDO neste ficheiro (gerado por `python scripts/netkit.py
   build` a partir de netkit-web.css). Não editar o bloco NETKIT:CSS à mão:
   `verify` compara-o com o CSS de origem.
   ========================================================================== */
(function (global) {
  "use strict"

  var VERSION = "1.0.0"
  var THEME_NAMES = ["net", "corpo", "street", "tabloid", "neon"]

  /* ---- CSS de origem (sincronizado por scripts/netkit.py build) --------- */
  var CSS = `/* NETKIT:CSS:BEGIN */
/* ============================================================================
   NETKIT/WEB — netkit-web.css
   O SISTEMA VISUAL FECHADO dos sites no padrão do mod NetSites (Cyberpunk 2077).

   REGRA ABSOLUTA: este ficheiro é a única fonte de cor, tipo, espaço e forma.
   Ninguém (agente ou humano) escreve CSS num site feito com o kit: o site usa
   só componentes do netkit-web e as props documentadas. Mexer aqui muda o
   sistema todo — por isso o comando verify (scripts/netkit.py) compara o
   sha256 do ficheiro com o manifesto do kit.

   Unidades: «ink» do jogo. 1 unidade ink = --nk-u px (0,5 px por omissão).
   A área de página do jogo é 3138 x 1293 ink; no browser vira o max-width de
   .nk-page-inner. Tudo escala por --nk-u, inclusive o tipo.

   Estrutura: 1) tokens  2) base  3) nós  4) blocos  5) responsivo  6) a11y
   ========================================================================== */

/* ------------------------------------------------------------------ 1) TOKENS
   Tudo o que é cor/letra/peso/espaçamento nasce aqui. O checker do kit lê
   este bloco para saber quais são as cores legais (NETKIT:TOKENS).
   ------------------------------------------------------------------------ */
/* NETKIT:TOKENS:BEGIN */
:root,
.nk-theme-net {
  /* paleta NET — ciano do navegador */
  --nk-bg: #0e0e17;
  --nk-text-color: #c0c8cf;
  --nk-text-size: 46;
  --nk-heading-color: #5ef6ff;
  --nk-heading-font: var(--nk-font-raj);
  --nk-heading-weight: var(--nk-w-bold);
  --nk-heading-transform: uppercase;
  --nk-muted: #7b8a96;
  --nk-accent: #5ef6ff;
  --nk-accent2: #ff6159;
  --nk-surface: #141b24;
  --nk-line: #2a3a46;
  --nk-link: #5ef6ff;
  --nk-link-hover: #28ffff;
  --nk-on-accent: #0e0e17;
  --nk-on-surface: #ffffff;
  --nk-veil: #00000088;
  --nk-veil-hover: #ffffff14;
}
.nk-theme-corpo {
  /* corpo — vermelho e preto */
  --nk-bg: #0a0a0a;
  --nk-text-color: #e9e9e9;
  --nk-text-size: 46;
  --nk-heading-color: #ffffff;
  --nk-heading-font: var(--nk-font-orbitron);
  --nk-heading-weight: var(--nk-w-black);
  --nk-heading-transform: uppercase;
  --nk-muted: #8c8c8c;
  --nk-accent: #e0312b;
  --nk-accent2: #ffffff;
  --nk-surface: #161616;
  --nk-line: #3a1412;
  --nk-link: #ff6159;
  --nk-link-hover: #ffffff;
  --nk-on-accent: #0e0e17;
  --nk-on-surface: #ffffff;
  --nk-veil: #00000088;
  --nk-veil-hover: #ffffff14;
}
.nk-theme-street {
  /* rua — amarelo Night City */
  --nk-bg: #121212;
  --nk-text-color: #efe9d2;
  --nk-text-size: 46;
  --nk-heading-color: #f3e600;
  --nk-heading-font: var(--nk-font-raj);
  --nk-heading-weight: var(--nk-w-bold);
  --nk-heading-transform: uppercase;
  --nk-muted: #9b9580;
  --nk-accent: #f3e600;
  --nk-accent2: #ff2a6d;
  --nk-surface: #1d1c18;
  --nk-line: #3b3820;
  --nk-link: #f3e600;
  --nk-link-hover: #ffffff;
  --nk-on-accent: #0e0e17;
  --nk-on-surface: #ffffff;
  --nk-veil: #00000088;
  --nk-veil-hover: #ffffff14;
}
.nk-theme-tabloid {
  /* notícias — papel claro (o único tema claro) */
  --nk-bg: #f2efe8;
  --nk-text-color: #1a1a1a;
  --nk-text-size: 46;
  --nk-heading-color: #111111;
  --nk-heading-font: var(--nk-font-raj);
  --nk-heading-weight: var(--nk-w-bold);
  --nk-heading-transform: none;
  --nk-muted: #5b5b5b;
  --nk-accent: #c8102e;
  --nk-accent2: #1d3c78;
  --nk-surface: #ffffff;
  --nk-line: #d6d0c4;
  --nk-link: #c8102e;
  --nk-link-hover: #1d3c78;
  --nk-on-accent: #0e0e17;
  --nk-on-surface: #111111;
  --nk-veil: #00000066;
  --nk-veil-hover: #00000010;
}
.nk-theme-neon {
  /* clube — rosa e ciano */
  --nk-bg: #0d0614;
  --nk-text-color: #f5d7ef;
  --nk-text-size: 46;
  --nk-heading-color: #ff2fd0;
  --nk-heading-font: var(--nk-font-orbitron);
  --nk-heading-weight: var(--nk-w-bold);
  --nk-heading-transform: uppercase;
  --nk-muted: #9d7fa0;
  --nk-accent: #ff2fd0;
  --nk-accent2: #5ef6ff;
  --nk-surface: #1a0d24;
  --nk-line: #3d1a46;
  --nk-link: #5ef6ff;
  --nk-link-hover: #ff2fd0;
  --nk-on-accent: #0e0e17;
  --nk-on-surface: #ffffff;
  --nk-veil: #00000088;
  --nk-veil-hover: #ffffff14;
}
:root,
.nk-theme-net,
.nk-theme-corpo,
.nk-theme-street,
.nk-theme-tabloid,
.nk-theme-neon {
  /* tinta neutra permitida (o kit e os sites usam só estas) */
  --nk-ink-white: #ffffff;
  --nk-ink-soft: #e6e6e6;
  --nk-ink-dark: #111111;
  --nk-ink-veil: #00000088;
  --nk-ink-clear: #00000000;

  /* famílias: as cinco do jogo, com queda para o que existe no browser */
  --nk-font-raj: "Rajdhani", "Segoe UI", Roboto, Arial, sans-serif;
  --nk-font-orbitron: "Orbitron", "Rajdhani", "Segoe UI", Arial, sans-serif;
  --nk-font-blender: "Blender Pro", "Rajdhani", "Segoe UI", Arial, sans-serif;
  --nk-font-industry: "Industry", "Rajdhani", "Segoe UI", Arial, sans-serif;
  --nk-font-arial: Arial, Helvetica, sans-serif;
  --nk-font-text: var(--nk-font-raj);

  /* pesos do jogo */
  --nk-w-light: 300;
  --nk-w-regular: 400;
  --nk-w-medium: 500;
  --nk-w-semibold: 600;
  --nk-w-bold: 700;
  --nk-w-black: 900;

  /* página: padding e gap do tema (página 21:9 do jogo) */
  --nk-page-pad: calc(var(--nk-u) * 180) calc(var(--nk-u) * 200) calc(var(--nk-u) * 180) calc(var(--nk-u) * 160);
  --nk-page-gap: calc(var(--nk-u) * 56);
  --nk-page-w: calc(var(--nk-u) * 3138);
}
/* NETKIT:TOKENS:END */

/* ------------------------------------------------------------------ 2) BASE */
.nk-site {
  /* 1 unidade ink = 0,5 px (desktop); desce nos ecrãs estreitos */
  --nk-u: 0.5px;
  width: 100%;
  color: var(--nk-text-color);
  font-family: var(--nk-font-text);
  font-weight: var(--nk-w-medium);
  line-height: 1.15;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
.nk-site *,
.nk-site *::before,
.nk-site *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 0;
  font: inherit;
  color: inherit;
  letter-spacing: 0;
  text-decoration: none;
  list-style: none;
  background: none;
}

/* ------------------------------------------------------------------ 3) NÓS */
/* página */
.nk-page {
  position: relative;
  display: flex;
  justify-content: center;
  width: 100%;
  min-height: 100vh;
  min-height: 100svh;
  overflow-x: clip;
  background-color: var(--nk-bg-color, var(--nk-bg));
}
.nk-page-inner {
  display: flex;
  flex-direction: column;
  gap: var(--nk-page-gap, calc(var(--nk-u) * 56));
  width: 100%;
  max-width: var(--nk-page-w);
  padding: var(--nk-page-pad);
}

/* contentores */
.nk-col,
.nk-row,
.nk-stack {
  background-color: var(--nk-bg-color, transparent);
  border: var(--nk-border, 0 solid transparent);
}
.nk-col {
  display: flex;
  flex-direction: column;
  align-items: var(--nk-align, stretch);
  justify-content: var(--nk-justify, flex-start);
  gap: var(--nk-gap, 0px);
  padding: var(--nk-pad, 0px);
}
.nk-row {
  display: flex;
  flex-direction: row;
  align-items: var(--nk-valign, flex-start);
  justify-content: var(--nk-justify, flex-start);
  gap: var(--nk-gap, 0px);
  padding: var(--nk-pad, 0px);
}
.nk-stack {
  display: grid;
  grid-template-areas: "nk-stack-cell";
  align-items: var(--nk-valign, start);
  justify-items: var(--nk-align, stretch);
  gap: var(--nk-gap, 0px);
  padding: var(--nk-pad, 0px);
}
.nk-stack > * {
  grid-area: nk-stack-cell;
}

/* texto */
.nk-text {
  display: block;
  min-width: 0;
  color: var(--nk-color, var(--nk-text-color));
  font-family: var(--nk-font, var(--nk-font-text));
  font-size: calc(var(--nk-u) * var(--nk-size, var(--nk-text-size)));
  font-weight: var(--nk-weight, var(--nk-w-medium));
  line-height: var(--nk-lh, 1.15);
  text-transform: var(--nk-transform, none);
  text-align: var(--nk-align-text, left);
  white-space: var(--nk-wrap-mode, nowrap);
  overflow-wrap: break-word;
  max-width: 100%;
}

/* imagem */
.nk-imgbox {
  position: relative;
  display: block;
  overflow: hidden;
  background-color: var(--nk-surface);
  border: var(--nk-border, 0 solid transparent);
}
.nk-imgbox > img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: var(--nk-fit, cover);
}
.nk-tint {
  position: absolute;
  inset: 0;
  background-color: var(--nk-tint, transparent);
  mix-blend-mode: multiply;
  pointer-events: none;
}
.nk-missing {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: calc(var(--nk-u) * 24);
  border: calc(var(--nk-u) * 3) solid var(--nk-line);
  color: var(--nk-muted);
  font-size: calc(var(--nk-u) * 30);
  text-transform: uppercase;
  text-align: center;
}

/* retângulo e espaço */
.nk-rect {
  display: block;
  background-color: var(--nk-bg-color, transparent);
  border: var(--nk-border, 0 solid transparent);
  flex: none;
}
.nk-sp {
  display: block;
  flex: none;
}

/* ligações — a única interação do sistema */
.nk-link {
  position: relative;
  cursor: pointer;
  text-decoration: none;
}
.nk-link:not([data-hover])::after {
  content: "";
  position: absolute;
  inset: 0;
  background-color: var(--nk-veil-hover);
  opacity: 0;
  pointer-events: none;
}
.nk-link:not([data-hover]):hover::after {
  opacity: 1;
}
.nk-link[data-hover="bg"]:hover {
  background-color: var(--nk-hover-bg);
}
.nk-link[data-hover="text"]:hover {
  color: var(--nk-hover-color);
}
.nk-link[data-hover="tint"]:hover .nk-tint {
  background-color: var(--nk-hover-color);
}

/* ------------------------------------------------------------------ 4) BLOCOS */
/* cabeçalho e navegação */
.nk-nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
.nk-nav-item {
  display: flex;
  flex-direction: column;
  gap: calc(var(--nk-u) * 10);
  align-items: stretch;
}
.nk-nav-mark {
  display: block;
  height: calc(var(--nk-u) * 6);
  background-color: var(--nk-mark, transparent);
}
.nk-header {
  display: flex;
  flex-direction: column;
  gap: calc(var(--nk-u) * 40);
  padding: 0 0 0 calc(var(--nk-u) * 24);
  background-color: var(--nk-bg-color, transparent);
}
.nk-header-row {
  display: flex;
  align-items: center;
  gap: calc(var(--nk-u) * 48);
}
.nk-header-titles {
  display: flex;
  flex-direction: column;
  gap: calc(var(--nk-u) * 6);
  min-width: 0;
}

/* destaque */
.nk-hero {
  position: relative;
  display: grid;
  grid-template-areas: "nk-stack-cell";
  align-items: end;
  overflow: hidden;
}
.nk-hero > * {
  grid-area: nk-stack-cell;
}
.nk-hero-veil {
  background-color: var(--nk-veil);
}
.nk-hero-body {
  display: flex;
  flex-direction: column;
  gap: calc(var(--nk-u) * 36);
  padding: calc(var(--nk-u) * 96) 0 calc(var(--nk-u) * 96) calc(var(--nk-u) * 96);
  min-width: 0;
}

/* botão (é uma linha com fundo/borda e um texto) */
.nk-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: calc(var(--nk-u) * 26) calc(var(--nk-u) * 64);
  background-color: var(--nk-bg-color, transparent);
  border: var(--nk-border, 0 solid transparent);
  flex: none;
}

/* cartão, produto, secção, artigo */
.nk-card,
.nk-product {
  display: flex;
  flex-direction: column;
  background-color: var(--nk-bg-color, var(--nk-surface));
  border: var(--nk-border, 0 solid transparent);
  overflow: hidden;
  flex: none;
}
.nk-card-body,
.nk-product-body {
  display: flex;
  flex-direction: column;
  gap: calc(var(--nk-u) * 18);
  padding: calc(var(--nk-u) * 44) calc(var(--nk-u) * 40) calc(var(--nk-u) * 44) calc(var(--nk-u) * 48);
  min-width: 0;
}
.nk-section {
  display: flex;
  flex-direction: column;
  gap: calc(var(--nk-u) * 40);
  min-width: 0;
}
.nk-section-head {
  display: flex;
  align-items: center;
  gap: calc(var(--nk-u) * 24);
}
.nk-section-bar {
  display: block;
  width: calc(var(--nk-u) * 14);
  height: calc(var(--nk-u) * 64);
  background-color: var(--nk-accent);
  flex: none;
}
.nk-article {
  display: flex;
  flex-direction: column;
  gap: calc(var(--nk-u) * 36);
  min-width: 0;
}

/* grelha */
.nk-grid {
  display: grid;
  grid-template-columns: repeat(var(--nk-cols, 3), minmax(0, 1fr));
  gap: var(--nk-gap, calc(var(--nk-u) * 48));
  width: 100%;
}

/* divisória, etiqueta, citação, lista */
.nk-divider {
  display: block;
  height: var(--nk-thickness, calc(var(--nk-u) * 4));
  background-color: var(--nk-line);
  flex: none;
}
.nk-badge {
  display: inline-flex;
  align-items: center;
  padding: calc(var(--nk-u) * 8) calc(var(--nk-u) * 24);
  background-color: var(--nk-bg-color, var(--nk-accent));
  flex: none;
  align-self: flex-start;
}
.nk-quote {
  display: flex;
  gap: calc(var(--nk-u) * 40);
  align-items: stretch;
  min-width: 0;
}
.nk-quote-bar {
  display: block;
  width: calc(var(--nk-u) * 10);
  background-color: var(--nk-accent);
  flex: none;
}
.nk-quote-body {
  display: flex;
  flex-direction: column;
  gap: calc(var(--nk-u) * 20);
  min-width: 0;
}
.nk-list {
  display: flex;
  flex-direction: column;
  gap: calc(var(--nk-u) * 22);
  min-width: 0;
}
.nk-list-item {
  display: flex;
  align-items: flex-start;
  gap: calc(var(--nk-u) * 28);
  min-width: 0;
}
.nk-bullet {
  display: block;
  width: calc(var(--nk-u) * 18);
  height: calc(var(--nk-u) * 18);
  margin-top: calc(var(--nk-u) * 20);
  background-color: var(--nk-accent);
  flex: none;
}

/* tabela */
.nk-table-wrap {
  width: 100%;
  overflow-x: auto;
}
.nk-table {
  display: flex;
  flex-direction: column;
  border: var(--nk-border, 0 solid transparent);
  min-width: 100%;
}
.nk-tr {
  display: flex;
  align-items: stretch;
  background-color: var(--nk-bg-color, transparent);
}
.nk-td {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: calc(var(--nk-u) * 22) calc(var(--nk-u) * 22);
  min-width: 0;
}

/* faixa (banner) */
.nk-banner {
  position: relative;
  display: grid;
  grid-template-areas: "nk-stack-cell";
  align-items: center;
  overflow: hidden;
}
.nk-banner > * {
  grid-area: nk-stack-cell;
}
.nk-banner-body {
  display: flex;
  align-items: center;
  gap: calc(var(--nk-u) * 40);
  padding: 0 calc(var(--nk-u) * 80);
  min-width: 0;
}

/* rodapé */
.nk-footer {
  display: flex;
  flex-direction: column;
  gap: calc(var(--nk-u) * 30);
  padding: 0 0 0 calc(var(--nk-u) * 60);
}
.nk-footer-row {
  display: flex;
  align-items: center;
  gap: calc(var(--nk-u) * 56);
  flex-wrap: wrap;
}

/* ------------------------------------------------------------------ 5) RESPONSIVO
   O kit é que sabe o que fazer no telemóvel; o site não escreve media queries.
   ------------------------------------------------------------------------ */
@media (max-width: 1439px) {
  .nk-site {
    --nk-u: 0.46px;
  }
}
@media (max-width: 1100px) {
  .nk-site {
    --nk-u: 0.42px;
  }
  .nk-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 860px) {
  .nk-site {
    --nk-u: 0.38px;
  }
  .nk-row[data-stack="1"],
  .nk-header-row,
  .nk-hero-body,
  .nk-banner-body,
  .nk-footer-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .nk-hero-body,
  .nk-banner-body {
    padding: calc(var(--nk-u) * 48);
  }
  .nk-header {
    padding-left: 0;
  }
}
@media (max-width: 620px) {
  .nk-site {
    --nk-u: 0.34px;
  }
  .nk-grid {
    grid-template-columns: 1fr;
  }
  .nk-card,
  .nk-product,
  .nk-article,
  .nk-imgbox {
    width: 100% !important;
    max-width: 100%;
  }
  .nk-btn {
    align-self: stretch;
  }
}
@media (prefers-reduced-motion: reduce) {
  .nk-site * {
    transition: none !important;
    animation: none !important;
  }
}

/* ------------------------------------------------------------------ 6) A11Y */
.nk-link:focus-visible,
.nk-site [tabindex]:focus-visible {
  outline: calc(var(--nk-u) * 4) solid var(--nk-accent);
  outline-offset: calc(var(--nk-u) * 4);
}
.nk-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  clip-path: inset(50%);
  white-space: nowrap;
}
@media print {
  .nk-page {
    background: #ffffff;
  }
}
/* NETKIT:CSS:END */`

  var ALIGN = { start: "flex-start", center: "center", end: "flex-end", stretch: "stretch" }
  var TEXT_ALIGN = { left: "left", center: "center", right: "right" }
  var WEIGHT = {
    light: "var(--nk-w-light)",
    regular: "var(--nk-w-regular)",
    medium: "var(--nk-w-medium)",
    semibold: "var(--nk-w-semibold)",
    bold: "var(--nk-w-bold)",
    black: "var(--nk-w-black)",
  }
  var FONT = {
    raj: "var(--nk-font-raj)",
    orbitron: "var(--nk-font-orbitron)",
    blender: "var(--nk-font-blender)",
    industry: "var(--nk-font-industry)",
    arial: "var(--nk-font-arial)",
  }

  /* ------------------------------------------------------------ utilidades */

  function u(n) {
    return "calc(var(--nk-u) * " + n + ")"
  }

  function space(v) {
    if (v === undefined || v === null) return null
    var b = typeof v === "number" ? [v, v, v, v] : v
    return b.map(u).join(" ")
  }

  function setVars(el, style) {
    for (var k in style) {
      if (!Object.prototype.hasOwnProperty.call(style, k)) continue
      var v = style[k]
      if (v === undefined || v === null) continue
      if (k.indexOf("--") === 0) el.style.setProperty(k, String(v))
      else el.style[k] = v
    }
  }

  function ensureCSS(doc) {
    doc = doc || global.document
    if (!doc || !doc.createElement) return
    if (doc.getElementById && doc.getElementById("nk-web-css")) return
    var style = doc.createElement("style")
    style.setAttribute("id", "nk-web-css")
    style.textContent = CSS
    ;(doc.head || doc.documentElement).appendChild(style)
  }

  function clear(el) {
    while (el.lastChild) el.removeChild(el.lastChild)
  }

  function hrefFor(link) {
    if (link === undefined || link === null || link === "") return null
    var s = String(link)
    // um esquema (https:, mailto:, tel:, NETdir:) é um endereço; o resto é id de página
    return /^[a-z][a-z0-9+.-]*:/i.test(s) ? s : "#/" + s
  }

  function findPage(pages, id) {
    for (var i = 0; i < pages.length; i++) if (pages[i].id === id) return pages[i]
    return null
  }

  function metaOf(spec) {
    var pages = spec.pages || []
    var home = spec.home || (pages[0] && pages[0].id) || "index"
    return {
      id: spec.id || "site",
      title: spec.title || spec.id || "",
      domain: spec.domain || "",
      lang: spec.lang,
      home: home,
      theme: spec.theme || "net",
      icon: spec.icon,
      images: spec.images || {},
      pages: pages.map(function (p) {
        return {
          id: p.id,
          title: p.title || p.id,
          address: p.address || "NETdir://" + (spec.domain || "") + "/" + p.id,
          root: p.root,
        }
      }),
    }
  }

  /* ------------------------------------------------------------ pintura */

  function applyCommon(el, p, kind) {
    var st = {}
    if (p.width !== undefined) st.width = u(p.width)
    if (p.height !== undefined) st.height = u(p.height)
    if (p.grow !== undefined) st.flexGrow = p.grow
    if (p.selfAlign) {
      st.alignSelf = ALIGN[p.selfAlign] || p.selfAlign
      st.justifySelf = ALIGN[p.selfAlign] || p.selfAlign
    }
    if (p.margin !== undefined) st.margin = space(p.margin)
    if (p.opacity !== undefined) st.opacity = p.opacity
    if (p.background) st["--nk-bg-color"] = p.background
    if (p.tint) st["--nk-tint"] = p.tint
    if (p.border && p.border.color) st["--nk-border"] = u(p.border.width || 3) + " solid " + p.border.color
    if (p.hover) {
      if (kind === "text" || kind === "tint") st["--nk-hover-color"] = p.hover
      else st["--nk-hover-bg"] = p.hover
    }
    setVars(el, st)
    if (p.link) el.setAttribute("data-hover", kind)
    if (p.name) el.setAttribute("data-name", p.name)
  }

  function applyText(el, p) {
    var st = {}
    if (p.size !== undefined) st["--nk-size"] = p.size
    if (p.color) st["--nk-color"] = p.color
    if (p.font) st["--nk-font"] = FONT[p.font] || p.font
    if (p.weight) st["--nk-weight"] = WEIGHT[p.weight] || p.weight
    if (p.upper) st["--nk-transform"] = "uppercase"
    if (p.align) st["--nk-align-text"] = TEXT_ALIGN[p.align] || p.align
    if (p.lineHeight !== undefined) st["--nk-lh"] = p.lineHeight
    if (p.wrap !== undefined && p.wrap !== 0) {
      st["--nk-wrap-mode"] = "normal"
      st.maxWidth = u(p.wrap)
    }
    setVars(el, st)
  }

  function makeEl(tag, cls, p, kind) {
    var el = global.document.createElement(p.link ? "a" : tag)
    el.className = cls + (p.link ? " nk-link" : "")
    if (p.link) {
      el.setAttribute("href", hrefFor(p.link))
      el.setAttribute("data-hover", kind)
    }
    applyCommon(el, p, kind)
    return el
  }

  function appendAll(el, children, ctx) {
    if (!children) return
    for (var i = 0; i < children.length; i++) {
      var child = buildNode(children[i], ctx)
      if (child) el.appendChild(child)
    }
  }

  /* ------------------------------------------------------------ nós */

  function buildNode(node, ctx) {
    if (!node || !node.type) return null
    var p = node.props || {}
    var el

    switch (node.type) {
      case "column":
      case "row":
      case "stack":
        el = makeEl("div", "nk-" + (node.type === "column" ? "col" : node.type), p, "bg")
        if (p.padding !== undefined) setVars(el, { "--nk-pad": space(p.padding) })
        if (p.gap !== undefined) setVars(el, { "--nk-gap": u(p.gap) })
        if (node.type === "row" && p.valign) el.style.alignItems = ALIGN[p.valign] || p.valign
        else if (node.type !== "row" && p.align) el.style.alignItems = ALIGN[p.align] || p.align
        if (node.type === "stack") {
          if (p.align) el.style.justifyItems = ALIGN[p.align] || p.align
          if (p.valign) el.style.alignItems = ALIGN[p.valign] || p.valign
        }
        appendAll(el, node.children, ctx)
        return el

      case "text":
        el = makeEl("span", "nk-text", p, "text")
        applyText(el, p)
        el.textContent = p.text === undefined || p.text === null ? "" : String(p.text)
        return el

      case "rect":
        el = makeEl("div", "nk-rect", p, "bg")
        if (p.color) setVars(el, { "--nk-bg-color": p.color })
        return el

      case "image":
        el = makeEl("div", "nk-imgbox", p, "tint")
        setVars(el, { "--nk-fit": p.fit === "contain" ? "contain" : "cover" })
        var entry = ctx.images[p.image]
        var src = entry && (entry.url || entry.file)
        if (src) {
          var img = global.document.createElement("img")
          img.setAttribute("src", src)
          img.setAttribute("alt", p.alt || "")
          img.setAttribute("loading", "lazy")
          img.setAttribute("decoding", "async")
          el.appendChild(img)
        } else {
          var miss = global.document.createElement("div")
          miss.className = "nk-missing"
          miss.setAttribute("data-atlas", (entry && entry.atlas) || "")
          miss.setAttribute("data-part", (entry && entry.part) || p.image || "")
          miss.textContent = (entry && entry.part) || p.image || ""
          el.appendChild(miss)
        }
        if (p.tint) {
          var tint = global.document.createElement("span")
          tint.className = "nk-tint"
          el.appendChild(tint)
        }
        return el

      case "spacer":
        el = makeEl("span", "nk-sp", p, "bg")
        return el

      default:
        if (global.console) global.console.warn("netkit-web: nó desconhecido «" + node.type + "»")
        return null
    }
  }

  function buildPage(page, ctx) {
    var root = page.root || { type: "page", props: {}, children: [] }
    var p = root.props || {}
    var main = global.document.createElement("main")
    main.className = "nk-page"
    if (p.background) setVars(main, { "--nk-bg-color": p.background })
    var inner = global.document.createElement("div")
    inner.className = "nk-page-inner"
    var st = {}
    if (p.padding !== undefined) st.padding = space(p.padding)
    if (p.gap !== undefined) st.gap = u(p.gap)
    if (p.align) st.alignItems = ALIGN[p.align] || p.align
    setVars(inner, st)
    appendAll(inner, root.children, ctx)
    main.appendChild(inner)
    return main
  }

  /* ------------------------------------------------------------ montagem */

  function routeId(meta) {
    var hash = (global.location && global.location.hash) || ""
    var id = hash.replace(/^#\/?/, "")
    return findPage(meta.pages, id) ? id : meta.home
  }

  function render(spec, host, opts) {
    opts = opts || {}
    var doc = global.document
    if (!doc) throw new Error("netkit-web: sem document — isto corre no browser")
    ensureCSS(doc)
    if (typeof host === "string") host = doc.querySelector(host)
    if (!host) throw new Error("netkit-web: alvo do site não encontrado")
    if (!spec || !spec.pages || !spec.pages.length) throw new Error("netkit-web: o site não tem páginas")

    var meta = metaOf(spec)

    if (spec.lang && doc.documentElement) doc.documentElement.setAttribute("lang", spec.lang)
    var theme = THEME_NAMES.indexOf(meta.theme) >= 0 ? meta.theme : "net"
    var site = doc.createElement("div")
    site.className = "nk-site nk-theme-" + theme
    site.setAttribute("data-nk-site", meta.id)
    host.appendChild(site)

    var ctx = { images: meta.images, meta: meta }

    function draw() {
      clear(site)
      var id = routeId(meta)
      var page = findPage(meta.pages, id) || meta.pages[0]
      site.appendChild(buildPage(page, ctx))
      if (opts.title !== false && meta.title && doc) doc.title = meta.title
    }

    function onHash() {
      draw()
    }
    if (global.addEventListener) global.addEventListener("hashchange", onHash)
    draw()

    return {
      meta: meta,
      go: function (id) {
        if (global.location) global.location.hash = "#/" + id
      },
      refresh: draw,
      destroy: function () {
        if (global.removeEventListener) global.removeEventListener("hashchange", onHash)
        clear(site)
        if (site.parentNode) site.parentNode.removeChild(site)
      },
    }
  }

  function mount(specOrUrl, host, opts) {
    if (typeof specOrUrl === "string") {
      if (typeof global.fetch !== "function") {
        throw new Error("netkit-web: fetch indisponível para ler " + specOrUrl)
      }
      return global
        .fetch(specOrUrl, { cache: "no-cache" })
        .then(function (r) {
          if (!r.ok) throw new Error("netkit-web: " + specOrUrl + " respondeu " + r.status)
          return r.json()
        })
        .then(function (spec) {
          return render(spec, host, opts)
        })
    }
    return render(specOrUrl, host, opts)
  }

  /* ------------------------------------------------------------ auto-montagem */

  function autoMount() {
    if (!global.document || !global.document.querySelectorAll) return
    var list = global.document.querySelectorAll("netsites[src], [data-netsite]")
    for (var i = 0; i < list.length; i++) {
      var el = list[i]
      if (el.getAttribute("data-nk-mounted")) continue
      el.setAttribute("data-nk-mounted", "1")
      var src = el.getAttribute("src") || el.getAttribute("data-netsite")
      var inline = el.textContent ? el.textContent.trim() : ""
      if (src) {
        mount(src, el)
      } else if (inline) {
        try {
          render(JSON.parse(inline), el)
        } catch (err) {
          if (global.console) global.console.error("netkit-web: JSON inválido no elemento", err)
        }
      }
    }
  }

  if (global.document) {
    if (global.document.readyState === "loading") {
      global.document.addEventListener("DOMContentLoaded", autoMount)
    } else {
      autoMount()
    }
  }

  global.NetKit = {
    version: VERSION,
    themes: THEME_NAMES.slice(),
    css: CSS,
    render: render,
    mount: mount,
    autoMount: autoMount,
    ensureCSS: ensureCSS,
  }
})(typeof globalThis !== "undefined" ? globalThis : typeof window !== "undefined" ? window : this)
