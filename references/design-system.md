# O sistema visual (fechado)

Tudo o que se pode ver num site do kit sai deste documento e de `assets/netkit-web/netkit-web.css`.
O CSS é a **fonte única**: o `check` lê a paleta de lá (`NETKIT:TOKENS`) e o `verify` confere o sha256.
Nenhum site escreve cor, tamanho, letra, sombra ou espaço próprio.

## Unidades e geometria

| Conceito | Valor | Na web |
| --- | --- | --- |
| Unidade | 1 **ink** (unidade do jogo) | `--nk-u` = `0.5px` no desktop |
| Área da página | 3138 × 1293 ink (21:9) | largura máxima `--nk-page-w` = 1569 px, centrada |
| Margem da página | 180 / 200 / 180 / 160 ink | 90 / 100 / 90 / 80 px |
| Espaço entre blocos da página | 56 ink | 28 px |
| Escala | desce com o ecrã | `0.5` → `0.46` (1439) → `0.42` (1100) → `0.38` (860) → `0.34` (620) |

Um número de prop é **sempre** em ink. Não se converte nada à mão: `<Text size={46}>` é 23 px no desktop e
15,6 px no telemóvel, porque o kit multiplica por `--nk-u`.

## As cinco paletas

Cada tema muda **cor e voz de título**. A estrutura, as rampas e os componentes são os mesmos.

| Tema | Quando usar | Fundo | Texto | Título | Acento | Acento 2 | Superfície | Linha |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `net` | portal/NET, notícias gerais, institucional | `#0e0e17` | `#c0c8cf` | `#5ef6ff` | `#5ef6ff` | `#ff6159` | `#141b24` | `#2a3a46` |
| `corpo` | corporação, banca, contrato, thriller | `#0a0a0a` | `#e9e9e9` | `#ffffff` | `#e0312b` | `#ffffff` | `#161616` | `#3a1412` |
| `street` | rua, loja, gangue, evento, comida | `#121212` | `#efe9d2` | `#f3e600` | `#f3e600` | `#ff2a6d` | `#1d1c18` | `#3b3820` |
| `tabloid` | jornal/revista em papel (único tema claro) | `#f2efe8` | `#1a1a1a` | `#111111` | `#c8102e` | `#1d3c78` | `#ffffff` | `#d6d0c4` |
| `neon` | clube, música, moda, portfólio ousado | `#0d0614` | `#f5d7ef` | `#ff2fd0` | `#ff2fd0` | `#5ef6ff` | `#1a0d24` | `#3d1a46` |

Cada tema define ainda: `--nk-muted` (texto secundário), `--nk-link`, `--nk-link-hover`, `--nk-veil`
(veil sobre imagens: preto 53% ou 40% no tabloid), `--nk-on-accent` (texto sobre acento), `--nk-on-surface`
(texto sobre superfície), `--nk-heading-transform` (`uppercase` excepto no tabloid).

**Tinta neutra permitida** (para casos que o tema não cobre): `#ffffff`, `#e6e6e6`, `#111111`,
`#00000088` (veil), `#00000000` (transparente). Em código usa-se `var(--nk-ink-white)`, `var(--nk-ink-soft)`,
`var(--nk-ink-dark)`, `var(--nk-ink-veil)`, `var(--nk-ink-clear)`.

**Cores em código:**
- nos componentes do kit, **sempre** `var(--nk-…)` — nunca um hex;
- num site, `var(--nk-…)` é a regra; um hex da tabela acima é aceite pelo `check`, mas o tema é preferível
  porque troca sozinho com `<Site theme="…">`.

## Rampa de tamanhos de texto

São os 20 tamanhos que o sistema usa. Qualquer outro valor é erro do `check`.

| Ink | px (desktop) | Uso |
| --- | --- | --- |
| 32 | 16 | etiqueta mínima, legenda de badge |
| 34 | 17 | meta de cartão |
| 36 | 18 | rodapé, nota |
| 38 | 19 | byline, autor/data |
| 40 | 20 | rótulo de interface |
| 42 | 21 | texto de cartão |
| 44 | 22 | subtítulo de header, navegação |
| 46 | 23 | **corpo de texto** (o tamanho do jogo) |
| 50 | 25 | nome de produto |
| 52 | 26 | texto de destaque (hero) |
| 58 | 29 | título de cartão |
| 60 | 30 | citação |
| 64 | 32 | texto grande de exceção |
| 72 | 36 | título de secção |
| 80 | 40 | texto de faixa/banner |
| 96 | 48 | título de artigo |
| 110 | 55 | título do site (header) |
| 120 | 60 | título de página editorial |
| 140 | 70 | título de campanha |
| 150 | 75 | título de destaque (hero) |

Regra prática: **corpo 46**, **secção 72**, **artigo 96**, **header 110**, **hero 150**. Para texto curto,
`wrap` é obrigatório (o `check` avisa acima de 140 caracteres sem `wrap`).

## Rampa de espaços

`gap`, `padding`, `margin` e `thickness` usam só estes valores (ink):

```
0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 36 40 44 48 52 56 60 64 72 80 88 96 110 120 140 160 180 200 240
```

Atalhos do sistema: `6` (título/subtítulo), `10` (navegação + barra), `18` (dentro do cartão), `20` (linha
de lista), `22` (célula de tabela), `26` (padding vertical de botão), `36` (hero), `40` (secção),
`44/48` (padding de cartão), `56` (entre blocos de página), `64` (entre links), `96` (padding de hero),
`160/200` (margem de página).

## Tipografia

| Prop `font` | Família | No browser |
| --- | --- | --- |
| `raj` (omissão) | Rajdhani | `"Rajdhani", "Segoe UI", Roboto, Arial` |
| `orbitron` | Orbitron | `"Orbitron", "Rajdhani", …` |
| `blender` | Blender Pro | `"Blender Pro", "Rajdhani", …` (a fonte é comercial: cai na Rajdhani) |
| `industry` | Industry | `"Industry", "Rajdhani", …` (idem) |
| `arial` | Arial | `Arial, Helvetica` |

| Prop `weight` | Valor | Quando |
| --- | --- | --- |
| `light` | 300 | texto muito grande e secundário |
| `regular` | 400 | corpo alternativo |
| `medium` | 500 | **omissão** |
| `semibold` | 600 | navegação, byline |
| `bold` | 700 | títulos, botões, preços |
| `black` | 900 | títulos do tema `corpo`/`neon` (voz do tema) |

A voz de título do tema (`<Text heading>`, `Header`, `Section`, `Hero`) já traz família, peso, cor e caixa.
Para títulos **não** se escolhe fonte nem cor: usa-se `heading`.

Carregar as fontes reais é opcional (`inject --fonts` escreve o link do Google Fonts para Rajdhani e
Orbitron). Sem esse link o site funciona e mantém as proporções — só não fica com o desenho exato das letras.

## Forma, linha e pintura

- **Raio:** 0. Sempre. `border-radius` não existe no sistema (o CSS fixa `0`).
- **Sombra:** nenhuma. Profundidade faz-se com `--nk-veil` sobre imagem e com `--nk-surface` atrás do texto.
- **Gradiente:** nenhum. Fundo é cor sólida (`background`, `Rect`) ou imagem.
- **Bordas:** só `3` ou `4` ink (`border={{ color: "var(--nk-line)", width: 3 }}`).
- **Divisórias:** `Divider` (4 ink) ou `Rect height={4}`; no rodapé, 3.
- **Véu sobre imagem:** automático no `Hero` (preto 53%); o `Banner` usa a imagem crua.

## Layout — a semântica que o kit garante

| Nó | Eixo principal | Eixo cruzado | Notas |
| --- | --- | --- | --- |
| `Column` | vertical | `align` (omissão `stretch`) | filhos esticam na largura |
| `Row` | horizontal | `valign` (omissão `start`) | `stack` empilha no telemóvel |
| `Stack` | sobreposição | `align` + `valign` | todos os filhos na mesma célula |
| `Grid` | grelha | — | 3 colunas → 2 (1100px) → 1 (620px) |
| `Page` | vertical, com scroll | `align` | fundo full-bleed, conteúdo com largura máxima |

- `width`/`height` fixam; `grow` estica no eixo do pai; `selfAlign` alinha no eixo cruzado.
- `gap` é o espaço **entre** filhos; `padding` é a margem **interior**; `margin` é a **exterior**.
- `background` pinta a caixa inteira (por trás do padding); `border` é uma moldura na aresta.
- Ordem de leitura: um `Column` por bloco, `Row` para o que é lado a lado, `Stack` só quando há sobreposição.
- Nunca se aninha `Stack` dentro de `Stack` sem necessidade: o jogo também desenha pior.

## Ligações, hover e foco

- `link`/`to` transformam o nó em `<a>`: um nó, um link. Não se envolve um cartão em `<a>`.
- Sem `hover`, o kit acende o véu branco de 8% por cima (`--nk-veil-hover`). Com `hover`, a cor dada
  substitui o fundo (contentor), a cor do texto (`Text`) ou a tinta da imagem (`Image`).
- Foco de teclado: contorno de acento de 4 ink, definido pelo kit. Não se remove.
- Links externos (`https://…`) ficam como estão; `NETdir://…` também (é o endereço do jogo e não resolve no
  browser — útil para mostrar o endereço, não para navegar).

## Responsivo (o kit trata, o site não escreve media queries)

| Ecrã | `--nk-u` | Grelha | `Row stack` | Cartões/imagens |
| --- | --- | --- | --- | --- |
| ≥ 1440 | 0.5px | 3 colunas | lado a lado | largura fixa |
| ≤ 1439 | 0.46px | 3 | lado a lado | largura fixa |
| ≤ 1100 | 0.42px | 2 | lado a lado | largura fixa |
| ≤ 860 | 0.38px | 2 | empilhado | header/hero/banner empilham |
| ≤ 620 | 0.34px | 1 | empilhado | tudo a 100% |

Se um bloco precisar de outro comportamento, usa-se `Row stack` (empilha em 860px) — não CSS.

## Receita de página (a que funciona sempre)

```
Page
  Header            (título, subtítulo, navegação, linha)
  Hero              (imagem, título, texto, botão)     ← só na página principal
  Section title     (barra de acento + título)
    Grid / Column   (cartões, artigo, tabela, lista)
  Divider
  Footer            (texto + links)
```

Uma página tem **um** `Header` e **um** `Footer`; `Hero` aparece no máximo uma vez e nunca abaixo da dobra.
No conteúdo, alterna-se `Section` com `Grid` (3 cartões), `Article` (leitura longa) ou `Table` (dados) — não
se empilham três `Grid` seguidos sem uma `Section` entre eles.
