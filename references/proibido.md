# O que NUNCA entra (e o que dizer quando falta)

> Esta é a lista que faz o sistema ser um sistema. Um site do kit não tem exceções: tem **elementos**.
> O `check` verifica automaticamente quase tudo aqui; o resto é disciplina de quem escreve.

## 1. Código proibido no site

| Proibido | Porquê | Em vez disso |
| --- | --- | --- |
| `<div>`, `<span>`, `<section>`, `<a>`, `<p>`… | o jogo não desenha HTML; o estilo tem de sair do kit | `Column` `Row` `Stack` `Text` `Section` `link` |
| `<h1>`…`<h6>`, `<b>`, `<i>`, `<strong>`, `<small>`, `<br>` | tipografia é do `Text` | `Text as="h2"`, `weight`, `upper` |
| `<img>`, `<picture>`, `<video>`, `<canvas>`, `<svg>` | imagem é do `Image`; não há ícones nem media além de imagem | `Image` (imagem estática) |
| `<a href>` solto | o link é prop, não tag | `link`/`to` no componente |
| `<button>`, `<form>`, `<input>`, `<select>`, `<textarea>` | o sistema não tem interação além de navegar | `Button` (link) e `Text` |
| `style=`, `className=`, `class=` | a aparência é do kit; é isto que impede o site de divergir | `background`, `border`, `padding`, `gap`, `color`, `size` |
| `<style>`, ficheiro CSS do site, Tailwind, CSS-in-JS, `@apply` | idem | a CSS é `netkit-web.css`, nunca tocada |
| `dangerouslySetInnerHTML`, `innerHTML` | texto é texto | `Text` |
| `<Text>` dentro de `<Text>` (ou um componente dentro de `Text`) | o texto é uma **string**; o jogo não tem rich text | dois `Text` lado a lado num `Row`, ou outra frase |
| SVG/ícone/emoji como «ícone» | não existe ícone no sistema | `Badge` com sigla, `Rect` de acento, `Text` |
| `<iframe>`, embed, mapa, player | fora do sistema | ligação externa (`to="https://…"`) |
| `<script>` próprio no site | comportamento não faz parte do kit | peça evolução do kit |

## 2. Visual proibido (mesmo «escondido» numa prop)

| Proibido | Nota |
| --- | --- |
| `border-radius` / cantos redondos | o sistema é quadrado: raio 0 |
| `box-shadow`, `text-shadow`, brilho, `filter: drop-shadow` | profundidade só com `--nk-veil` e `--nk-surface` |
| gradientes (lineares, radiais, cónicos) | fundo é cor sólida ou imagem |
| `backdrop-filter`, blur, vidro | não existe |
| `transform`, `rotate`, `skew`, `scale` | não existe |
| animações, `keyframes`, transições (fora do hover do kit) | não existe movimento |
| hex fora da paleta, `rgb()`, `hsl()`, `red`, `currentColor` inventado | só tokens e os neutros |
| tamanho de texto fora da rampa (47, 48, 55, 100…) | a rampa tem 20 valores |
| `gap`/`padding`/`margin` fora da rampa (13, 17, 35…) | a rampa tem 36 valores |
| borda de 1, 2, 5, 6… | só 3 ou 4 |
| fonte nova (`Inter`, `Poppins`, `Montserrat`, `monospace`…) | só as 5 do sistema |
| peso 100/200/800 ou `font-weight: bold` cru | só os 6 pesos por nome |
| opacidade fora de 0–1, `mix-blend-mode` próprio | o único blend é o `tint` do kit |
| duas colunas de texto lado a lado numa página | leitura do sistema é uma coluna (`Article`) |
| imagem de fundo com texto sem véu | legibilidade: `Hero` já põe véu; em `Stack` use `Rect color="var(--nk-ink-veil)"` |

## 3. Conteúdo proibido

- **Assets da CDPR**: atlas, ícones, fontes do jogo, captures, áudio, modelos, texto extraído do jogo. Nem no
  git, nem no build, nem numa pré-visualização pública. Uma referência `atlas`+`part` é um caminho, não um
  asset — e no browser aparece como marcador.
- **Texto de marca** sem autorização (Cyberpunk 2077, CD Projekt, Night City como marca registada) em
  material comercial. Em projeto pessoal/open-source, siga a política do projeto.
- **Lorem ipsum** ou texto de enchimento num site entregue. Escreva conteúdo real, curto e verificável.
- **Placeholders** (`TODO`, `[inserir]`, `xxx`) — se falta conteúdo, entregue a página sem essa secção e
  diga o que falta.
- **Dados pessoais de terceiros**, números de telefone/IBAN inventados que pareçam reais, promessas médicas
  ou financeiras — bom senso vale mais do que estética.

## 4. O protocolo «falta algo»

O pedido pede um elemento que o kit não tem (um ícone, um formulário, um carrossel, um menu dropdown, um
vídeo, um botão com estado). **Não se improvisa.** Resposta e ação:

1. **Diga o que falta**, em uma frase: «O kit não tem ícones nem carrossel.»
2. **Diga o que o sistema tem de mais próximo** e **faça** com isso:
   - ícone → `Badge` com sigla, ou `Rect` de acento como marcador;
   - carrossel → `Grid` com os 3–6 cartões visíveis (sem paginação);
   - menu dropdown → `NavBar` com todas as opções à vista;
   - formulário → endereço de email/telefone em `Text` + `Button` para `mailto:` (link externo);
   - vídeo → `Image` de capa com `to` para o vídeo alojado;
   - botão com estado → `Button` (navega) e uma `Section` de confirmação;
   - gráfico → `Table` com os números (o sistema não tem gráficos).
3. **Registe o pedido** como melhoria do kit (issue no repositório), com o componente que faria falta.
4. **Nunca** entregue o site com a invenção «só desta vez». Uma exceção estraga o sistema inteiro e o
   `check` seguinte falha.

## 5. Como rever à mão (quando o `check` não chega)

```bash
# HTML, estilos e CSS
grep -nE '<(div|span|a|p|img|button|svg|video|form|input|h[1-6])\b|style=|className=|class=' src/sites/*.jsx
# cores e tamanhos fora do sistema
grep -nE '#[0-9a-fA-F]{3,8}|rgb\(|hsl\(' src/sites/*.jsx
grep -nE 'size=\{[0-9]+\}' src/sites/*.jsx
# animações, sombras, raios
grep -nEi 'shadow|radius|gradient|animate|transition|transform|filter' src/sites/*.jsx
```

O `grep` serve para apanhar o que o `check` não vê (por exemplo um texto que diz «clique no ícone»). O
`check` continua a ser a barreira obrigatória — o grep é revisão, não substituto.

## 6. Regra de ouro

Se a frase começa por «só precisamos de…» e o resto não está em
[`componentes.md`](componentes.md) nem em [`design-system.md`](design-system.md), a resposta é **não** —
diga o que falta, proponha a alternativa e siga. O site é do kit; o kit não é do site.
