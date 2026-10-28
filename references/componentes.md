# Catálogo de componentes

Tudo o que se pode desenhar. Um site usa **só** isto. Cada componente aceita as *props comuns* e as suas.

## Props comuns (todos os nós)

| Prop | Tipo | O quê |
| --- | --- | --- |
| `width`, `height` | ink | tamanho fixo; sem elas o nó ajusta-se ao conteúdo |
| `grow` | número | estica no eixo do pai, na proporção |
| `selfAlign` | `start` `center` `end` `stretch` | alinhamento no eixo cruzado do pai |
| `margin` | ink ou `[topo, dir, baixo, esq]` | margem exterior |
| `opacity` | 0–1 | transparência |
| `link` | texto | id de página do site ou endereço; o nó passa a `<a>` |
| `hover` | cor | cor ao passar o rato (fundo, texto ou tinta) |
| `name` | texto | nome do widget (testes/depuração) |

`padding` aceita ink ou `[topo, direita, baixo, esquerda]` — como no CSS, **topo primeiro**.

## 1. Estrutura

### `Site` — o site inteiro (obrigatório, um por site)

| Prop | Obrig. | O quê |
| --- | --- | --- |
| `id` | sim | `[a-z0-9_]+`; nome do site |
| `title` | sim | nome curto (lista de sites / `<title>`) |
| `domain` | sim | `[a-z0-9.-]+`, ex. `ncity.web` |
| `theme` | não | `net` (omissão) · `corpo` · `street` · `tabloid` · `neon` |
| `images` | não | mapa de imagens: `{ nome: { url } \| { file } \| { atlas, part } }` |
| `home` | não | id da página principal (omissão: a primeira) |
| `lang` | não | língua do documento (`pt-BR`, `en`) |
| `icon` | não | nome de imagem em `images` |
| `children` | — | as `<Page>` |

### `Page` — uma página

| Prop | Obrig. | O quê |
| --- | --- | --- |
| `id` | sim | `[a-z0-9_]+`; é o destino de `to`/`link` |
| `title` | não | título da página (metadados) |
| `path` | não | caminho alternativo no endereço |
| `background` | não | cor de fundo (omissão: a do tema) |
| `padding` | não | margem interior (omissão: 180/200/180/160) |
| `gap` | não | espaço entre blocos (omissão: 56) |
| `align` | não | alinhamento dos filhos (omissão `stretch`) |

```jsx
<Page id="index" title="Início">
  <Header title="Notícias" />
  <Section title="Destaques">…</Section>
  <Footer text="© 2077" />
</Page>
```

### `Column` / `Row` / `Stack` — layout

| Prop | `Column` | `Row` | `Stack` |
| --- | --- | --- | --- |
| `gap` | sim | sim | não |
| `padding` | sim | sim | sim |
| `align` | sim (horizontal) | — | sim (horizontal) |
| `valign` | — | sim (vertical) | sim (vertical) |
| `stack` | — | sim (empilha ≤860px) | — |
| `background`, `border` | sim | sim | sim |

```jsx
<Column gap={40} padding={[44, 40, 44, 48]} background="var(--nk-surface)">
  <Text size={58} weight="bold" heading>Título</Text>
  <Text size={42}>Texto.</Text>
</Column>

<Row gap={24} valign="center" stack>
  <Rect width={14} height={64} color="var(--nk-accent)" />
  <Text size={72} heading>Secção</Text>
</Row>

<Stack height={820}>
  <Image image="foto" height={820} selfAlign="stretch" />
  <Rect height={820} color="var(--nk-ink-veil)" selfAlign="stretch" />
  <Text size={150} heading>Por cima</Text>
</Stack>
```

### `Text` — todo o texto

| Prop | O quê |
| --- | --- |
| `children` | o texto (uma string; números viram texto) |
| `size` | tamanho da rampa (omissão 46) |
| `color` | cor da paleta ou `var(--nk-…)` |
| `font` | `raj` (omissão) `orbitron` `blender` `industry` `arial` |
| `weight` | `light` `regular` `medium` `semibold` `bold` `black` |
| `upper` | maiúsculas |
| `align` | `left` `center` `right` |
| `wrap` | largura de quebra (ink); sem ela o texto não quebra |
| `lineHeight` | 1 (omissão 1.15) — parágrafos longos: 1.25 |
| `heading` | veste a voz de título do tema (família/peso/cor/caixa) |
| `as` | etiqueta semântica: `p` `h1` `h2` `h3` `span` |

```jsx
<Text size={110} as="h1" heading>Notícias</Text>
<Text size={44} color="var(--nk-muted)">Night City · 2077</Text>
<Text size={46} wrap={2000} lineHeight={1.25}>Parágrafo longo…</Text>
<Text size={38} upper weight="semibold" color="var(--nk-muted)">Por V. · 12/03</Text>
```

**Sem markup:** `<Text>Olá <b>mundo</b></Text>` não existe. Destaque = outro `Text`.

### `Image` — imagem

| Prop | O quê |
| --- | --- |
| `image` | nome da imagem em `<Site images>` (obrigatório) |
| `width`, `height` | caixa (ink). Sem `height`, a imagem usa a altura natural |
| `fit` | `cover` (omissão) ou `contain` |
| `tint` | cor que multiplica a imagem |
| `alt` | texto alternativo (obrigatório para imagem de conteúdo) |

```jsx
<Site images={{ foto: { url: "/img/fachada.jpg" } }}>
  <Image image="foto" width={900} height={480} alt="Fachada da loja" />
</Site>
```

Uma imagem `{ atlas, part }` (do jogo) aparece como marcador com o nome da parte: é intencional, o conteúdo
da CDPR não vai para a web.

### `Rect` e `Spacer`

```jsx
<Rect width={14} height={64} color="var(--nk-accent)" />
<Rect height={4} color="var(--nk-line)" />
<Spacer height={40} />
<Spacer grow={1} />          {/* empurra o resto da linha */}
```

## 2. Blocos

### `NavBar` — links em linha

```jsx
<NavBar items={[{ label: "Início", to: "index" }, { label: "Sobre", to: "sobre" }]} active="index" />
```

`items` (obrigatório), `active` (id ativo), `gap` (64), `size` (44), `color`, `activeColor`. O ativo leva a
barra de acento por baixo.

### `Header` — cabeçalho do site

```jsx
<Header logo="logo" title="Notícias" subtitle="Night City · 2077"
        nav={[{ label: "Início", to: "index" }, { label: "Sobre", to: "sobre" }]} active="index" />
```

`logo` (nome em `images`), `logoSize` (160), `title` (obrigatório, `<h1>`), `subtitle`, `nav`, `active`.
Já inclui a linha divisória de 4 ink.

### `Hero` — destaque (uma vez por site)

```jsx
<Hero image="foto" title="A cidade não espera" text="Uma frase de apoio."
      cta={{ label: "Ler a matéria", to: "materia" }} height={820} />
```

`image`, `title` (obrigatório), `text`, `cta` (`{label,to}`), `height` (820), `align`.
Véu preto de 53% automático; sem imagem, fundo `--nk-surface`.

### `Button` — ação

```jsx
<Button label="Comprar" to="loja" />
<Button label="Voltar" to="index" variant="outline" size={40} />
```

`label` e `to` obrigatórios; `variant` `solid` (omissão) ou `outline`; `size` (46); `color`, `textColor`.
É um link com caixa. Não há botão com estado, nem evento de clique.

### `Card` — cartão de conteúdo

```jsx
<Card image="foto" title="Primeiro" text="Resumo curto." meta="NET" to="materia" width={900} imageHeight={480} />
```

`title` obrigatório; `image`, `text`, `meta` (etiqueta pequena em acento), `to`, `width` (900),
`imageHeight` (480). Com `to`, o cartão inteiro é clicável.

### `Grid` — grelha

```jsx
<Grid columns={3} gap={48}>
  <Card title="A" text="…" />
  <Card title="B" text="…" />
  <Card title="C" text="…" />
</Grid>
```

`columns` (3), `gap` (48). Colapsa para 2 e 1 coluna sozinho. Os filhos devem ter largura compatível
(omissão de cartão: 900 — em grelha de 3, use `width` menor ou deixe crescer).

### `Section` — bloco com título

```jsx
<Section title="Destaques" gap={40}>
  <Grid columns={3}>…</Grid>
</Section>
```

`title` (obrigatório, `<h2>` com barra de acento) e `children`. É o divisor natural da página.

### `Article` — leitura longa

```jsx
<Article title="A noite em que a NET caiu" byline="Por V. · 12/03/2077"
         body={["Primeiro parágrafo.", "Segundo parágrafo."]} width={2200} image="foto" />
```

`title` e `body` obrigatórios; `byline`, `width` (2200), `image`. Cada string é um parágrafo com `wrap`
automático e `lineHeight` 1.25.

### `ProductCard` — produto

```jsx
<ProductCard image="produto" name="Jaqueta Samurai" price={1250} to="loja" width={640} />
```

`name` e `price` obrigatórios; `image`, `to`, `width` (640). Preço numérico sai formatado em `pt-PT`;
`"1.250"` também é aceite. Mostra sempre a unidade `eddies`.

### `Divider`, `Badge`, `Quote`, `BulletList`

```jsx
<Divider thickness={4} />
<Badge text="Exclusivo" />
<Quote text="A cidade não espera." author="Rogue" />
<BulletList items={["Primeiro ponto", "Segundo ponto"]} width={2200} />
```

- `Divider`: `color`, `thickness` (4; no rodapé 3), `margin`.
- `Badge`: `text`, `color`, `textColor` — etiqueta pequena, alinhada à esquerda.
- `Quote`: `text`, `author`, `width` (2000) — acrescenta as aspas « ».
- `BulletList`: `items`, `width` (2200) — marcadores quadrados de acento.

### `Table` — dados

```jsx
<Table columns={["Produto", "Preço"]} rows={[["Jaqueta", "1.250 eddies"], ["Chip", "300 eddies"]]} widths={[1400, 1000]} />
```

`columns` e `rows` obrigatórios; `widths` (ink, opcional). Cabeçalho em acento e maiúsculas, linhas
alternadas com `--nk-surface`, scroll horizontal no telemóvel.

### `Banner` — faixa de anúncio

```jsx
<Banner image="promo" text="Promoção até sexta" to="loja" height={300} />
```

`text` obrigatório; `image` (sem imagem usa `--nk-accent2`), `to` (faixa clicável), `height` (300), `color`.

### `Footer` — rodapé

```jsx
<Footer text="© 2077 Notícias" links={[{ label: "Sobre", to: "sobre" }, { label: "Contacto", to: "contacto" }]} />
```

`text` obrigatório; `links`. Inclui a linha de 3 ink e empurra os links para a direita.

## 3. Composições que o sistema aprova

| Quero… | Combinação |
| --- | --- |
| página inicial | `Header` + `Hero` + `Section`/`Grid` + `Section`/`BulletList` + `Footer` |
| notícia | `Header` + `Article` + `Divider` + `Section`(3 `Card` relacionados) + `Footer` |
| loja | `Header` + `Banner` + `Section` + `Grid` de `ProductCard` + `Footer` |
| portfólio | `Header` + `Hero` + `Section`/`Grid` de `Card` + `Quote` + `Footer` |
| dados | `Header` + `Section` + `Table` + `Footer` |
| campanha | `Header` + `Hero` + `Banner` + `Section`/`Column` + `Footer` |

O que **não** é composição válida: dois `Hero`, `Header` no meio da página, `Card` dentro de `Card`,
`Stack` dentro de `Stack` sem sobreposição, `Grid` com um só filho (use `Column`).
