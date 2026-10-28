---
name: cyberpunk-2077-sites-kit-agent-skill
description: >-
  Entrega e usa o KIT DE FRONTEND dos sites no padrão do mod NetSites do Cyberpunk 2077: um sistema visual
  FECHADO (5 temas, 8 nós de layout, 25 componentes React, rampas de tamanho/espaço/cor) mais um renderer
  standalone que desenha `netsites-site/1` sem React nem build. Injeta o kit num site em um comando
  (inject + manifesto sha256), cria páginas só com os componentes do kit, valida o contrato visual
  (check: proíbe HTML/CSS/inline styles, cores fora da paleta, tamanhos fora da rampa, props inventadas),
  pré-visualiza localmente (preview) e verifica se o kit foi adulterado (verify). Use SEMPRE que o pedido
  for criar, entregar ou revisar um site (landing, notícia, loja, portfólio, página de campanha) no visual
  do Cyberpunk 2077/NET, injetar o netkit-web num projeto React/Next/Vite/HTML, ou responder "faz um site
  no padrão do nosso mod de sites".
version: 1.1.0
license: MIT
author: Frederico Guilherme Klüser de Oliveira
homepage: https://github.com/frederico-kluser/cyberpunk-2077-sites-kit-agent-skill
tags:
  - cyberpunk-2077
  - netsites
  - frontend
  - react
  - design-system
  - kit
  - sites
---

# NETKIT/WEB — o kit dos sites no padrão do mod NetSites

Esta skill **entrega o kit** (código, pronto a injetar) e **explica como usá-lo** para construir sites no
padrão visual dos sites NET do Cyberpunk 2077 — o mesmo sistema do kit do estúdio (`@cp77/netkit`) e do mod
**NetSites**, agora para a web.

> **REGRA ZERO — o sistema é FECHADO.**
> Um site feito com esta skill usa **exclusivamente** os elementos visuais que existem aqui: os 5 temas, os
> 8 tipos de nó, os 25 componentes, as rampas de tamanho/espaço e a paleta. **Nada além disso.**
> Não se escreve CSS, não se usa HTML solto, não se inventa cor, sombra, raio, gradiente, ícone, animação,
> textura ou tipografia. Se o pedido exigir algo que o kit não tem, **diz-se o que falta e apresenta-se a
> alternativa mais próxima com os elementos existentes** — nunca se improvisa. Detalhe e lista completa em
> [`references/proibido.md`](references/proibido.md).

## O que a skill entrega

| Peça | Onde | Para quê |
| --- | --- | --- |
| **Kit React** `netkit-web` | [`assets/netkit-web/`](assets/netkit-web/) | componentes (`Site`, `Page`, `Header`, `Hero`, `Card`…) + a CSS com todos os tokens + tipos `.d.ts`; entra em Vite, Next, CRA e Astro **sem build do kit** |
| **Renderer standalone** | [`assets/standalone/netkit-web.standalone.js`](assets/standalone/netkit-web.standalone.js) | desenha um `netsites-site/1` (JSON) no browser: uma tag `<script>` e o site aparece — sem React, sem npm, sem bundler |
| **CLI** | [`scripts/netkit.py`](scripts/netkit.py) | `inject` · `check` · `verify` · `preview` · `new` · `list` · `build` |
| **Prints** | [`docs/prints/`](docs/prints/) + [`scripts/prints.py`](scripts/prints.py) | capturas reais do kit (5 temas, 3 sites, catálogo, mobile, caminho JSON) e o gerador headless |
| **Contrato visual** | [`references/`](references/) | o sistema (tokens, componentes, formato), o que é proibido, como injetar, exemplos e checklist |
| **Registo global** | [`scripts/link-skill-global.sh`](scripts/link-skill-global.sh) | liga a skill a todos os roots de skills da máquina (`~/.dsh`, `~/.claude`, `~/.agents`, `~/.codex`, …) |

A versão do kit é uma só: `1.1.0` no `package.json`, no `netkit-web.js`, no standalone e no manifesto.
`verify` falha se divergirem.

## Regra zero em prática

**Existe** (e é tudo o que existe):

- **8 nós de layout:** `page`, `column`, `row`, `stack`, `text`, `image`, `rect`, `spacer`.
- **25 componentes:** `Site` `Page` `Column` `Row` `Stack` `Text` `Image` `Rect` `Spacer` e os blocos
  `NavBar` `Header` `Hero` `Button` `Card` `Grid` `Section` `Article` `ProductCard` `Divider` `Badge`
  `Quote` `BulletList` `Table` `Banner` `Footer`.
- **5 temas:** `net` (ciano), `corpo` (vermelho/preto), `street` (amarelo), `tabloid` (papel claro),
  `neon` (rosa/ciano) — as cores vivem **só** em `netkit-web.css`.
- **Rampas:** 20 tamanhos de texto, 36 espaços, bordas de 3 ou 4, 5 famílias de letras, 6 pesos.

**Não existe** (e não se cria): HTML, CSS, `style=`, `className`, Tailwind, styled-components, `<div>`,
`<img>`, `<a>`, `<button>`, `<svg>`, `<video>`, `<canvas>`, `<iframe>`, formulários, ícones, emoji, sombras,
raios, gradientes, filtros, transformações, animações, transições (fora do hover do kit), fontes novas,
cores novas, tamanhos novos, props novas.

Quando falta: **diga o que falta, porquê, e qual a combinação mais próxima com o que existe** — e siga com
essa. Exemplo: «não há ícones no kit; uso `Badge` com a sigla ou `Rect` de acento como marcador».

## Antes de começar (sempre, 2 comandos)

```bash
python3 scripts/netkit.py version        # 1.1.0
python3 scripts/netkit.py verify         # kit OK: CSS sincronizada, versões, exports
```

`verify` sem `--target` confere o kit do repositório. Se falhar, **não** se corrige à mão: `python3
scripts/netkit.py build` (sincroniza a CSS embutida) e repete-se.

## Fluxo A — injetar o kit num site React (o caminho normal)

```bash
# 1. injeta (idempotente; nunca sobrescreve sem --force)
python3 scripts/netkit.py inject --target ~/projetos/meu-site --flavor react --name Noticias --new-site

# 2. escreve as páginas em src/sites/Noticias.jsx (só componentes do kit)
#    o starter gerado já passa no check — copie o estilo dele

# 3. valida o contrato visual
python3 scripts/netkit.py check src/sites

# 4. confirma que ninguém mexeu no kit
python3 scripts/netkit.py verify --target .
```

O que o `inject` faz:

- copia `netkit-web.js`, `netkit-web.css` e `netkit-web.d.ts` para `src/netkit/` (ou `netkit/` se não houver
  `src/`) e escreve `manifest.json` com o **sha256** de cada ficheiro (a prova de que o kit não foi editado);
- com `--new-site`, cria `src/sites/<Nome>.jsx` com um site de arranque (duas páginas, header, hero, grelha
  de cartões, rodapé) e os imports já certos;
- imprime os passos seguintes com os caminhos reais.

No código, a forma é sempre esta:

```jsx
import { Site, Page, Header, Hero, Section, Grid, Card, Text, Button, Footer } from "../netkit/netkit-web.js"
import "../netkit/netkit-web.css"

const imagens = { foto: { url: "/img/fachada.jpg" } }

export default function Noticias() {
  return (
    <Site id="noticias" title="Notícias" domain="ncity.web" theme="net" images={imagens}>
      <Page id="index" title="Início">
        <Header title="Notícias" subtitle="Night City · 2077" nav={[{ label: "Início", to: "index" }]} active="index" />
        <Hero image="foto" title="A cidade não espera" cta={{ label: "Ler", to: "materia" }} />
        <Section title="Destaques">
          <Grid columns={3}>
            <Card title="Primeiro" text="Um cartão do kit." meta="NET" to="materia" />
          </Grid>
        </Section>
        <Footer text="© 2077" links={[{ label: "Sobre", to: "sobre" }]} />
      </Page>
      <Page id="materia" title="Matéria">…</Page>
    </Site>
  )
}
```

- **Ligações:** `to`/`link` recebem o **id de uma página** do próprio site (`#/id`, funciona em qualquer
  alojamento) ou um endereço completo (`https://…`). Nunca um caminho inventado.
- **Imagens:** `images={{ nome: { url } }}` (web) ou `{ file: "images/x.png" }` (relativo). Uma entrada
  `{ atlas, part }` (jogo) desenha um **marcador** no browser — conteúdo da CDPR não vai para a web.
- **Unidades:** tudo em unidades ink do jogo; 1 ink = `--nk-u` (0,5 px no desktop). Não se converte nada à
  mão: passa-se o número que está na rampa.

## Fluxo B — site estático a partir de `netsites-site/1` (sem React)

```bash
python3 scripts/netkit.py inject --target ~/projetos/site-estatico --flavor static --name Estatico
python3 scripts/netkit.py preview ~/projetos/site-estatico/netkit/site.json
```

O `inject` estático copia `netkit-web.standalone.js` + `netkit-web.css`, gera `netkit/site.json` e injeta
no `index.html` (bloco marcado `<!-- netkit:begin -->…<!-- netkit:end -->`, substituído em vez de
duplicado):

```html
<link rel="stylesheet" href="netkit/netkit-web.css" />
<netsites src="netkit/site.json"></netsites>
<script src="netkit/netkit-web.standalone.js" defer></script>
```

O JSON é o **mesmo formato do mod** (`netsites-site/1`): páginas com `root` e nós `page`/`column`/`row`/
`stack`/`text`/`image`/`rect`/`spacer`. Extensões só da web: `theme` (nome do tema), `images.<nome>.url` e
`image.props.fit`/`alt`. Formato completo em [`references/formato-site.md`](references/formato-site.md);
o validador aplica as mesmas regras do jogo **mais** o contrato visual.

## Fluxo C — trazer um site do jogo/estúdio para a web

O `site.json` exportado pelo estúdio (ou escrito à mão) já é `netsites-site/1`: `inject --flavor static`,
substituir `netkit/site.json`, `check`, `preview`. As imagens do jogo (`atlas`+`part`) **não** são extraídas
nem copiadas — ficam como marcador; para publicar, troque por imagens suas com licença (`{ "url": … }`).
Conteúdo da CDPR nunca entra no git nem num site público.

## Comandos

| Comando | O que faz | Exemplo |
| --- | --- | --- |
| `inject` | copia o kit + manifesto sha256 + starter | `--target . --flavor react --name Noticias --new-site` |
| `check` | valida o contrato visual (JSX/HTML/JSON) | `check src/sites` · `check site.json --json` |
| `verify` | confere o kit ou uma cópia instalada | `verify` · `verify --target .` |
| `preview` | serve um `site.json` local, sem internet | `preview netkit/site.json` |
| `new` | cria uma página React ou um `site.json` | `new --dir src/sites --name Afterlife` |
| `list` | imprime o inventário fechado | `list components` · `list tokens` |
| `build` | sincroniza a CSS embutida no standalone | `build` |
| `version` | versão do kit | `version` |

Códigos de saída: `0` ok · `1` problemas encontrados · `2` uso inválido · `3` kit incompleto.

## O sistema em uma página

- **Temas** (cores e voz de título): `net` #0e0e17/#5ef6ff · `corpo` #0a0a0a/#e0312b · `street`
  #121212/#f3e600 · `tabloid` #f2efe8/#c8102e · `neon` #0d0614/#ff2fd0.
- **Texto:** 32–46 para corpo/legendas, 50–72 para subtítulos, 96–150 para títulos. `heading` veste a voz do
  tema (família, peso, cor, caixa) sem escrever cores.
- **Layout:** `Column` (vertical), `Row` (horizontal; `stack` empilha no telemóvel), `Stack` (camadas),
  `Grid` (2 colunas em tablet e 1 no telemóvel, sozinha). `gap`/`padding` só da rampa.
- **Pintura:** `background`, `border` (3 ou 4), `Rect` para faixas, `Divider` para linhas, `Badge` para
  etiquetas. Zero sombras, raios ou gradientes — a CSS do kit fixa `border-radius: 0`.
- **Interação:** só `link`/`to` (navega) e `hover` (cor). Não há botões com estado, formulários, menus
  dropdown ou modais.
- **Responsivo:** o kit trata de tudo (`--nk-u` desce em ecrãs estreitos; `Row stack`; `Grid` colapsa).
  O site não escreve media queries.

## Conteúdo, imagens e licenças

- Texto do site: uma `string` por nó `Text` — **sem markup** (negrito, itálico, links dentro do texto não
  existem no sistema). Palavra a destacar = outro `Text` com `color`/`size` da rampa.
- Imagens: próprias e com licença (registe a proveniência no `README` do site). **Nunca** extrair, copiar ou
  publicar assets da CDPR (atlas, ícones, fundos do jogo), nem capturas do jogo sem permissão.
- Língua: a do pedido. `Site lang` ajusta `<html lang>`; números e preços com o formato da língua
  (`price` em número usa `pt-PT` por omissão).
- Acessibilidade (parte do kit, não opcional): `Header` usa `h1`, `Section`/`Hero` `h2`, cartões `h3`;
  imagens de conteúdo levam `alt`; links são `<a>` reais com foco visível; contraste das cinco paletas é
  verificado pelo tema (não troque cores «para ficar bonito»).

## Validar e entregar

1. `check` sem erros (**só então** se entrega).
2. `preview` (JSON) ou o dev server do projeto (React) para ver o resultado.
3. `verify --target .` sem alterações ao kit.
4. Checklist de entrega: [`references/checklist.md`](references/checklist.md) (10 pontos, incluindo
   «nenhum elemento fora do kit», «nenhuma cor/tamanho fora da rampa», «nenhum asset da CDPR»).

O `check` é o contrato executável: se ele passa, o site **não** fugiu do sistema visual. Um site que precise
de algo fora do kit é um pedido de evolução do kit (issue no repositório), não uma exceção no site.

## Erros frequentes

| Sintoma | Causa | Solução |
| --- | --- | --- |
| `check`: `<div>` não existe no kit | HTML no JSX | `Column`/`Row`/`Stack`; texto em `Text` |
| `check`: `style=` não entra | estilo à mão | use `background`, `border`, `padding`, `gap`, `color` |
| `check`: tamanho fora da rampa | número inventado | escolha da rampa (`list tokens`) |
| `check`: cor fora da paleta | hex/CSS novo | `var(--nk-accent)`, `var(--nk-muted)`, … |
| `check`: ligação não é página | `to` errado | id de uma `<Page>` ou `https://…` |
| `verify --target`: ALTERADO | kit editado no site | `inject --force` e refaça a alteração no site (não no kit) |
| CSS embutida ≠ CSS de origem | standalone desatualizado | `python3 scripts/netkit.py build` |
| Site em branco no estático | falta o `netsites`/script | copie o bloco `netkit:begin` do `index.html` |
| Imagem do jogo em branco | `atlas`+`part` no browser | esperado: marcador. Use `{ url }`/`{ file }` |

## Ficheiros desta skill

```
SKILL.md                     este contrato
README.md                    visão humana, instalação e badges
assets/netkit-web/           o kit React (js + css + d.ts)
assets/standalone/           renderer JSON sem React (script único)
scripts/netkit.py            inject · check · verify · preview · new · list · build
scripts/link-skill-global.sh liga a skill a todos os roots de skills
references/design-system.md  tokens, temas, rampas, tipografia, espaçamento
references/componentes.md    catálogo completo (props, exemplos, quando usar)
references/formato-site.md   netsites-site/1 aplicado à web
references/proibido.md       a lista do que NUNCA entra (e o que dizer quando falta)
references/injecao.md        injeção por stack (Vite, Next, Astro, HTML, WordPress)
references/exemplos.md       três páginas completas (notícia, loja, portfólio)
references/checklist.md      o que confirmar antes de entregar
tests/                       48 testes (node: 15 · python: 33) — `npm test`
docs/prints/                 capturas reais do kit + `scripts/prints.py` (browser headless)
```

## Registo global (fora do projeto)

```bash
bash scripts/link-skill-global.sh            # liga em todos os roots que existem
bash scripts/link-skill-global.sh --check    # sai 1 se algum estiver fora
```

Liga por symlink nos mesmos locais das outras skills da máquina (`~/.dsh/skills`, `~/.claude/skills`,
`~/.agents/skills`, `~/.codex/skills`, contas `~/.claude-*`, `~/.jcode`, `~/.pi`, `~/.config/opencode`).
Nunca substitui um diretório real: move-o para `~/Agent-Skills/.link-backups/<data>/` antes.

## Regras finais

1. **O kit não se edita.** Corrigir o kit é tarefa do repositório (`assets/`, `references/`, testes), com
   versão nova — nunca um `if` no site.
2. **`check` verde é condição de entrega.** Sem exceções, nem «é só um detalhe».
3. **Nada de conteúdo da CDPR** em sites, no git ou em pré-visualizações públicas.
4. **Não inventar elementos.** Falta algo → dizer o que falta e seguir com a combinação mais próxima.
5. **Erros sempre no formato** `Erro: <o quê> — Solução: <o que fazer>`.
