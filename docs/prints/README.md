# Prints do kit

Capturas reais do **netkit-web** num browser headless (Chrome/Edge), geradas por código — nenhuma foi
desenhada à mão, e nenhuma imagem da CDPR entra aqui.

| Ficheiro | O que mostra | Origem |
| --- | --- | --- |
| [`01-temas.png`](01-temas.png) | os cinco temas lado a lado, com a mesma estrutura | `src/temas.html` |
| [`02-noticia-tabloid.png`](02-noticia-tabloid.png) | notícia completa no tema `tabloid` (Header, Hero, Section, Card, Footer) | `src/noticia.html` |
| [`03-loja-street.png`](03-loja-street.png) | loja no tema `street` (Banner, Grid de ProductCard) | `src/loja.html` |
| [`04-portfolio-neon.png`](04-portfolio-neon.png) | portfólio no tema `neon` (Hero, Grid de Card, Quote) | `src/portfolio.html` |
| [`05-componentes.png`](05-componentes.png) | catálogo: paleta, rampa de texto, botões, etiquetas, cartões, tabela, lista, faixa, rodapé | `src/componentes.html` |
| [`06-noticia-mobile.png`](06-noticia-mobile.png) | a notícia a 390 px: tudo empilhado, sem CSS extra | `src/noticia.html` |
| [`07-standalone-json.png`](07-standalone-json.png) | o caminho **sem React**: `netkit-web.standalone.js` a desenhar um `netsites-site/1` inline | `src/json.html` |
| [`og.png`](og.png) | capa do repositório (1280×640) | `src/og.html` |

## Regenerar

```bash
python3 scripts/prints.py            # fontes + arte + capturas
python3 scripts/prints.py --shots    # só as capturas (a arte já está no repo)
python3 scripts/prints.py --art      # só fontes (OFL) + arte abstrata
python3 scripts/prints.py --check    # confere que todas existem
python3 scripts/prints.py --list     # nomes, páginas e medidas
```

Requisitos: Node/Python do projeto, um Chrome/Chromium/Edge (ou `NETKIT_BROWSER=/caminho/do/browser`) e
`pillow` **só** para `--art` (a arte já está commitada). O script serve o repositório em `127.0.0.1` e
fotografa cada página com `--headless=new --screenshot`, com `--virtual-time-budget` para as fontes e as
imagens carregarem.

## Como as páginas são feitas

`src/*.html` são páginas de documentação: carregam o `assets/netkit-web/netkit-web.css` e usam **as mesmas
classes que os componentes React emitem** (`nk-header`, `nk-hero`, `nk-card`, `nk-product`, `nk-table`…).
Só a moldura de documentação (`_print.css`: grelhas, etiquetas, `@font-face`) é que não é do kit. É por isso
que os prints mostram o produto real — e foi assim que apareceram dois bugs de CSS (o texto do `Hero` ficava
atrás da imagem e a navegação não tinha `gap`).

## Arte e fontes

- `src/art/*.jpg` — arte abstrata **gerada** por `scripts/prints.py` (Pillow, semente fixa): cidade na rua,
  skyline, palco, produtos, retrato e um gráfico de barras. Nada de conteúdo da CDPR.
- `src/fonts/*.woff2` — **Rajdhani** e **Orbitron**, licença SIL OFL (ver `OFL-*.txt` na mesma pasta),
  vendorizadas **só** para os prints. O kit não distribui fontes: um site que as queira carrega-as por
  `<link>` (o `inject --flavor static --fonts` escreve esse link).
