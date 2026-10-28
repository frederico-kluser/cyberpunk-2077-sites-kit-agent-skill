# Formato do site (`netsites-site/1`) — na web

O mesmo contrato de dados do mod **NetSites** (o stúdio exporta-o, o jogo lê-o). Na web é o que o
`netkit-web.standalone.js` desenha — sem React, sem build, uma tag `<script>`.

```json
{
  "schema": "netsites-site/1",
  "id": "noticias",
  "title": "Notícias",
  "domain": "ncity.web",
  "lang": "pt-BR",
  "theme": "net",
  "home": "index",
  "icon": "logo",
  "images": { "logo": { "url": "/img/logo.png" } },
  "pages": [
    {
      "id": "index",
      "address": "NETdir://ncity.web",
      "title": "Início",
      "root": { "type": "page", "props": { "gap": 56 }, "children": [] }
    }
  ]
}
```

## Campos do topo

| Campo | Regra |
| --- | --- |
| `schema` | sempre `netsites-site/1` |
| `id` | `[a-z0-9_]+`; nome do site |
| `title` | nome curto (barra de endereço, `<title>`) |
| `domain` | `[a-z0-9.-]+` (ex.: `ncity.web`, `afterlife.corp`) |
| `lang` | opcional: língua do documento (vai para `<html lang>`) |
| `theme` | **extensão web**: `net` · `corpo` · `street` · `tabloid` · `neon` (o jogo ignora) |
| `home` | id da página principal (omissão: a primeira) |
| `icon` | opcional: nome de uma imagem de `images` |
| `images` | mapa `nome → imagem` (ver abaixo) |
| `pages` | lista de páginas, pelo menos uma |

## Imagens

```json
{
  "foto":   { "url": "/img/fachada.jpg" },
  "logo":   { "file": "images/logo.png" },
  "gato":   { "atlas": "base\\gameplay\\…\\x.inkatlas", "part": "gato" }
}
```

| Forma | Onde serve | No browser |
| --- | --- | --- |
| `{ "url": "https://…" }` | **web**: caminho absoluto ou externo | `<img src>` |
| `{ "file": "images/x.png" }` | **web**: relativo à pasta do site | `<img src>` |
| `{ "atlas": "…", "part": "…" }` | jogo (o mod) | marcador com o nome da parte |

Regras: o nome é `[a-z0-9_]+`; uma imagem tem `atlas`+`part` **ou** `file`/`url` (nunca `url` e `file`
juntos); os nós `image` referenciam um nome de `images`. Nunca se copia conteúdo da CDPR para a web.

## Páginas

| Campo | Regra |
| --- | --- |
| `id` | `[a-z0-9_]+`, único; é o destino de `link` |
| `address` | começa por `NETdir://` e pertence ao `domain` do site (`NETdir://ncity.web`, `NETdir://ncity.web/sobre`) |
| `title` | título da página |
| `root` | um nó `page` (obrigatório) |

## Nós

`{ "type": "text", "props": { … }, "children": [ … ] }`. Só `page`, `column`, `row` e `stack` têm filhos.

| Tipo | Props próprias | Equivalente React |
| --- | --- | --- |
| `page` | `background`, `padding`, `gap`, `align` | `<Page>` |
| `column` | `gap`, `padding`, `align`, `background`, `border` | `<Column>` |
| `row` | `gap`, `padding`, `valign`, `background`, `border` | `<Row>` |
| `stack` | `padding`, `align`, `valign`, `background`, `border` | `<Stack>` |
| `text` | `text`, `size`, `color`, `font`, `weight`, `upper`, `align`, `wrap`, `lineHeight` | `<Text>` |
| `image` | `image`, `tint`, `fit`, `alt` (**web**) | `<Image>` |
| `rect` | `color` | `<Rect>` |
| `spacer` | — | `<Spacer>` |

Props comuns: `width`, `height`, `grow`, `selfAlign`, `margin`, `opacity`, `link`, `hover`, `name`.

Valores:
- números em **ink** (1 ink = 0,5 px no desktop);
- `padding`/`margin`: número ou `[topo, direita, baixo, esquerda]`;
- cores: `#rrggbb` ou `#rrggbbaa`, **da paleta** (o `check` recusa fora dela);
- `border`: `{ "color": "#2a3a46", "width": 3 }` (largura 3 ou 4);
- `link`: id de página do site ou endereço completo (`https://…`, `mailto:…`, `NETdir://…`);
- `upper`: `true`/`false`; `wrap`: largura de quebra em ink (0 = sem quebra);
- `font`: `raj` `orbitron` `blender` `industry` `arial`; `weight`: `light` `regular` `medium` `semibold`
  `bold` `black`; `align`: `left` `center` `right` (texto) ou `start` `center` `end` `stretch` (contentor).

## Exemplo completo (duas páginas)

```json
{
  "schema": "netsites-site/1",
  "id": "afterlife",
  "title": "The Afterlife",
  "domain": "afterlife.web",
  "lang": "pt-BR",
  "theme": "street",
  "home": "index",
  "images": { "foto": { "url": "/img/bar.jpg" } },
  "pages": [
    {
      "id": "index",
      "address": "NETdir://afterlife.web",
      "title": "Início",
      "root": {
        "type": "page",
        "props": { "background": "#121212", "padding": [180, 200, 180, 160], "gap": 56 },
        "children": [
          { "type": "text", "props": { "text": "THE AFTERLIFE", "size": 110, "upper": true, "color": "#f3e600", "weight": "bold" } },
          { "type": "rect", "props": { "height": 4, "color": "#3b3820" } },
          { "type": "image", "props": { "image": "foto", "width": 3138, "height": 820, "alt": "Balcão do bar" } },
          { "type": "text", "props": { "text": "O bar onde os lendas não morrem.", "size": 46, "wrap": 2000, "lineHeight": 1.25 } },
          {
            "type": "row",
            "props": { "gap": 40, "padding": [0, 0, 0, 24] },
            "children": [
              { "type": "rect", "props": { "width": 14, "height": 64, "color": "#f3e600" } },
              { "type": "text", "props": { "text": "A CASA", "size": 72, "upper": true, "weight": "bold", "color": "#f3e600" } }
            ]
          },
          { "type": "text", "props": { "text": "HISTÓRIA", "size": 44, "upper": true, "weight": "semibold", "link": "sobre", "hover": "#ffffff" } }
        ]
      }
    },
    {
      "id": "sobre",
      "address": "NETdir://afterlife.web/sobre",
      "title": "História",
      "root": {
        "type": "page",
        "props": { "background": "#121212", "padding": [180, 200, 180, 160], "gap": 56 },
        "children": [
          { "type": "text", "props": { "text": "HISTÓRIA", "size": 110, "upper": true, "color": "#f3e600", "weight": "bold" } },
          { "type": "text", "props": { "text": "Duas páginas, um formato, zero invenções.", "size": 46, "wrap": 2000 } },
          { "type": "text", "props": { "text": "VOLTAR", "size": 44, "upper": true, "weight": "semibold", "link": "index", "hover": "#ffffff" } }
        ]
      }
    }
  ]
}
```

## O que o validador exige

`python3 scripts/netkit.py check site.json` aplica:

- `schema`, `id`, `domain` (`[a-z0-9.-]+`, não pode ser de um site do jogo nem do mod), `title`;
- páginas com `id` válido e único, `address` `NETdir://` **do domínio do site**, `home` existente;
- nós de tipo conhecido, filhos só em contentores, profundidade ≤ 40, props conhecidas (desconhecidas =
  aviso), números finitos;
- **contrato visual web:** cores da paleta, tamanhos da rampa, espaços da rampa, bordas 3/4, `link` para
  página existente ou endereço, imagem referenciada existente;
- avisos: texto longo sem `wrap`, página vazia, mais de 600 nós, imagem não usada.

## Como o renderer resolve as coisas

| Situação | Comportamento |
| --- | --- |
| `link` sem `://` | navega para `#/<id>` (hash, funciona em qualquer alojamento) |
| `link` com `://` | `<a href>` normal |
| página inexistente no hash | mostra a página `home` |
| tema desconhecido | cai em `net` |
| imagem `atlas`+`part` | marcador com `data-part` (sem asset) |
| `title` do site | vai para `document.title` |
| `lang` | vai para `<html lang>` |
| `fit` | `cover` (omissão) ou `contain` |

Para publicar num site já existente: copie os três ficheiros (`netkit-web.standalone.js`,
`netkit-web.css`, `site.json`), acrescente `<netsites src="…"></netsites>` e o `<script defer>` — é tudo.
