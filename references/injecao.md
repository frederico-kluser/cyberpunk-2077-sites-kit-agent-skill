# Injeção por stack

O kit é **vendorizado** no site (não é uma dependência npm): copia-se para o repositório do site e o
`manifest.json` com os sha256 garante que ninguém o altera. É isso que permite `verify --target .` em CI.

## Regra comum a todas as stacks

1. `python3 scripts/netkit.py inject --target <site> --flavor react|static --name <Nome>`
2. O CSS do kit importa-se **uma vez** (nunca duas).
3. O site importa os componentes de `netkit/netkit-web.js` — nunca reimplementa nenhum.
4. `python3 scripts/netkit.py check <pasta>` e `verify --target <site>` antes de entregar.
5. `netkit/` entra no git do site (o site tem de continuar a funcionar sem acesso à skill).

---

## Vite + React

```bash
python3 scripts/netkit.py inject --target . --flavor react --name Noticias --new-site
```

`inject` põe o kit em `src/netkit/` (porque `src/` existe) e o starter em `src/sites/Noticias.jsx`.

```jsx
// src/main.jsx — o CSS uma única vez
import "./netkit/netkit-web.css"

// src/App.jsx
import Noticias from "./sites/Noticias.jsx"
export default function App() {
  return <Noticias />
}
```

O `Site` navega por hash (`#/sobre`): não é preciso configurar rotas. Se o projeto usar `react-router`,
o hash continua a funcionar — o `Site` não interfere com o router.

## Next.js (App Router)

O kit começa por `"use client"`, por isso funciona em Server Components sem mudanças.

```bash
python3 scripts/netkit.py inject --target . --flavor react --name Noticias --new-site
```

`inject` deteta `src/` (ou cria `netkit/` na raiz, se não houver). O CSS entra no `app/layout.jsx`:

```jsx
import "../netkit/netkit-web.css"
```

A página:

```jsx
// app/page.jsx
import Noticias from "../sites/Noticias"
export default function Page() {
  return <Noticias />
}
```

Notas: nada de `next/dynamic` (o kit não depende de `window` no render); imagens continuam a ser
`<Image>` do kit com `url` — **não** se mistura com `next/image`, que geraria `<img>` fora do contrato.

## Astro (React island)

```bash
python3 scripts/netkit.py inject --target . --flavor react --name Noticias --new-site
```

```astro
---
// src/pages/index.astro
import Noticias from "../sites/Noticias.jsx"
import "../netkit/netkit-web.css"
---
<html lang="pt-BR">
  <body><Noticias client:only="react" /></body>
</html>
```

`client:only="react"` porque o `Site` lê `location.hash` no browser.

## Create React App

Igual ao Vite, com o CSS em `src/index.js`:

```js
import "./netkit/netkit-web.css"
```

## HTML estático (o mais simples)

```bash
python3 scripts/netkit.py inject --target . --flavor static --name Estatico
```

Ficam três ficheiros e um bloco no `index.html`:

```
netkit/netkit-web.standalone.js
netkit/netkit-web.css
netkit/site.json
index.html   ← <!-- netkit:begin --> … <!-- netkit:end -->
```

```html
<link rel="stylesheet" href="netkit/netkit-web.css" />
<netsites src="netkit/site.json"></netsites>
<script src="netkit/netkit-web.standalone.js" defer></script>
```

- O script injeta o CSS sozinho; o `<link>` evita o flash de conteúdo sem estilo.
- Tem de ser servido por HTTP (`python3 scripts/netkit.py preview netkit/site.json` ou qualquer servidor
  estático); `file://` bloqueia o `fetch` do JSON.
- Para embutir o JSON na página: `<netsites>{…json…}</netsites>` (sem `src`).

## WordPress / CMS com bloco de HTML

1. Suba `netkit-web.standalone.js`, `netkit-web.css` e `site.json` para
   `wp-content/uploads/netkit/` (ou tema-filho).
2. Num bloco **HTML personalizado** (página em branco, sem cabeçalho do tema):

```html
<link rel="stylesheet" href="/wp-content/uploads/netkit/netkit-web.css" />
<netsites src="/wp-content/uploads/netkit/site.json"></netsites>
<script src="/wp-content/uploads/netkit/netkit-web.standalone.js" defer></script>
```

3. Se o tema injetar CSS a mais (tipografia, links), isole: o kit já usa `.nk-site` como raiz, mas
   `body` do tema continua a mandar no fundo. Nesse caso use uma página com template em branco.

## Site já existente (qualquer stack)

O mínimo absoluto:

```html
<script src="/netkit/netkit-web.standalone.js" defer></script>
<div data-netsite="/netkit/site.json"></div>
```

`data-netsite` aceita um caminho (fetch do JSON) ou nada (JSON inline no elemento). O script procura
`<netsites src>` e `[data-netsite]` sozinho no `DOMContentLoaded`. Para montar à mão:

```js
NetKit.render(spec, "#alvo")   // spec em memória
await NetKit.mount("/site.json", "#alvo")
```

## CI do site (recomendado)

```yaml
- name: Contrato visual do kit
  run: |
    python3 scripts/netkit.py verify --target .
    python3 scripts/netkit.py check src/sites
```

O primeiro comando falha se alguém editou o kit; o segundo, se o site fugiu do sistema. Com os dois verdes,
o estilo não regride em nenhum PR.

## Problemas comuns

| Sintoma | Causa | Solução |
| --- | --- | --- |
| site em branco (estático) | falta `<netsites>` ou o script | copie o bloco `netkit:begin` |
| `<img>` não aparece | `url` relativa à página errada | caminho a partir da raiz servida (`/img/…`) |
| CSS duplicado / estilos estranhos | CSS importado duas vezes | importe só no arranque |
| `fetch` falha com `file://` | protocolo sem HTTP | `netkit.py preview` ou servidor local |
| texto enorme no telemóvel | `--nk-u` foi sobreposto | não defina `--nk-u` no site; o kit gere |
| tema não muda | `theme` fora dos 5 nomes | `net` `corpo` `street` `tabloid` `neon` |
