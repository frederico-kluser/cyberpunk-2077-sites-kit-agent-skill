# Três sites completos (copiar e adaptar)

Cada exemplo é um ficheiro `src/sites/<Nome>.jsx` que passa no `check` tal como está. Troque os textos, as
imagens e o `domain`; **não** troque a estrutura por HTML nem acrescente estilos.

---

## 1. Notícia — tema `tabloid` (jornal em papel)

![Notícia no tema tabloid](../../docs/prints/02-noticia-tabloid.png)

```jsx
import {
  Site, Page, Header, Article, Section, Grid, Card, Text, Divider, Badge, Quote, Footer,
} from "../netkit/netkit-web.js"
import "../netkit/netkit-web.css"

const imagens = {
  manchete: { url: "/img/manchete.jpg" },
  cidade: { url: "/img/cidade.jpg" },
  logo: { url: "/img/logo.png" },
}

const nav = [
  { label: "Início", to: "index" },
  { label: "Matéria", to: "materia" },
  { label: "Sobre", to: "sobre" },
]

export default function Noticias() {
  return (
    <Site id="noticias" title="Notícias" domain="ncity.web" theme="tabloid" images={imagens}>
      <Page id="index" title="Início">
        <Header logo="logo" title="Notícias" subtitle="A cidade, sem filtro" nav={nav} active="index" />
        <Section title="Última hora">
          <Grid columns={2}>
            <Card image="manchete" meta="Metrópole" title="A noite em que a NET caiu"
                  text="Sete horas sem rede. A cidade lembrou-se do que era o silêncio."
                  to="materia" width={1400} imageHeight={560} />
            <Card image="cidade" meta="Bairro" title="Kabuki acorda mais cedo"
                  text="O mercado abriu antes da polícia. Ninguém sabe porquê." width={1400} imageHeight={560} />
          </Grid>
        </Section>
        <Divider />
        <Section title="Em destaque">
          <Article
            title="A noite em que a NET caiu"
            byline="Por V. · 12/03/2077"
            image="manchete"
            width={2200}
            body={[
              "Às 23h17 a rede piscou. Às 23h18 já não havia rede nenhuma. Os técnicos dizem que foi um erro de configuração; os que estavam na rua dizem outra coisa.",
              "O que se sabe: nenhum banco perdeu dados, nenhum hospital parou, e o preço dos chips subiu 40% antes do amanhecer.",
            ]}
          />
          <Quote text="O silêncio também é um serviço." author="Rogue Amendiares" />
        </Section>
        <Footer text="© 2077 Notícias" links={[{ label: "Sobre", to: "sobre" }]} />
      </Page>

      <Page id="materia" title="A noite em que a NET caiu">
        <Header logo="logo" title="Notícias" nav={nav} active="materia" />
        <Badge text="Metrópole" />
        <Article
          title="A noite em que a NET caiu"
          byline="Por V. · 12/03/2077"
          image="manchete"
          width={2200}
          body={[
            "Às 23h17 a rede piscou. Às 23h18 já não havia rede nenhuma.",
            "Os técnicos dizem que foi um erro de configuração. Quem estava na rua diz que foi alguém com uma ideia melhor.",
          ]}
        />
        <Divider />
        <Section title="Relacionadas">
          <Grid columns={2}>
            <Card title="O mercado abriu antes da polícia" text="Kabuki, 04h40." to="index" width={1400} />
            <Card title="Quem ganha com o silêncio" text="Três empresas, uma janela de sete horas." to="index" width={1400} />
          </Grid>
        </Section>
        <Footer text="© 2077 Notícias" links={[{ label: "Início", to: "index" }]} />
      </Page>

      <Page id="sobre" title="Sobre">
        <Header logo="logo" title="Notícias" nav={nav} active="sobre" />
        <Section title="Sobre">
          <Text size={46} wrap={2200} lineHeight={1.25}>
            Notícias é um jornal independente de Night City. Não temos dono, não temos anúncios de armas e
            não publicamos o que não conseguimos confirmar duas vezes.
          </Text>
          <Text size={38} upper={true} weight="semibold" color="var(--nk-muted)">
            Redação · Night City
          </Text>
        </Section>
        <Footer text="© 2077 Notícias" links={[{ label: "Início", to: "index" }]} />
      </Page>
    </Site>
  )
}
```

---

## 2. Loja — tema `street`

![Loja no tema street](../../docs/prints/03-loja-street.png)

```jsx
import {
  Site, Page, Header, Banner, Section, Grid, ProductCard, Table, Text, Divider, Footer,
} from "../netkit/netkit-web.js"
import "../netkit/netkit-web.css"

const imagens = {
  jaqueta: { url: "/img/jaqueta.jpg" },
  chip: { url: "/img/chip.jpg" },
  oculos: { url: "/img/oculos.jpg" },
  promo: { url: "/img/promo.jpg" },
}

const nav = [
  { label: "Loja", to: "index" },
  { label: "Tabela", to: "precos" },
]

export default function Garagem() {
  return (
    <Site id="garagem" title="Garagem Kabuki" domain="kabuki.web" theme="street" images={imagens}>
      <Page id="index" title="Loja">
        <Header title="Garagem Kabuki" subtitle="Peças originais e o resto" nav={nav} active="index" />
        <Banner image="promo" text="Semana do cromo — 20% em tudo" to="precos" height={300} />
        <Section title="Mais vendidos">
          <Grid columns={3}>
            <ProductCard image="jaqueta" name="Jaqueta Samurai" price={1250} to="precos" />
            <ProductCard image="chip" name="Chip de refrigeração" price={340} to="precos" />
            <ProductCard image="oculos" name="Óculos anti-flash" price={780} to="precos" />
          </Grid>
        </Section>
        <Divider />
        <Section title="Porque comprar aqui">
          <Text size={46} wrap={2000} lineHeight={1.25}>
            Tudo o que está na montra existe. Se não existir, dizemos. Se estiver partido, dizemos antes de
            pagar.
          </Text>
        </Section>
        <Footer text="© 2077 Garagem Kabuki" links={[{ label: "Tabela de preços", to: "precos" }]} />
      </Page>

      <Page id="precos" title="Tabela de preços">
        <Header title="Garagem Kabuki" nav={nav} active="precos" />
        <Section title="Tabela">
          <Table
            columns={["Peça", "Estado", "Preço"]}
            widths={[1100, 700, 600]}
            rows={[
              ["Jaqueta Samurai", "Usada", "1.250 eddies"],
              ["Chip de refrigeração", "Novo", "340 eddies"],
              ["Óculos anti-flash", "Novo", "780 eddies"],
            ]}
          />
        </Section>
        <Footer text="© 2077 Garagem Kabuki" links={[{ label: "Loja", to: "index" }]} />
      </Page>
    </Site>
  )
}
```

---

## 3. Portfólio — tema `neon`

![Portfólio no tema neon](../../docs/prints/04-portfolio-neon.png)

```jsx
import {
  Site, Page, Header, Hero, Section, Grid, Card, Text, Button, Divider, Quote, BulletList, Footer,
} from "../netkit/netkit-web.js"
import "../netkit/netkit-web.css"

const imagens = {
  palco: { url: "/img/palco.jpg" },
  som: { url: "/img/som.jpg" },
  luz: { url: "/img/luz.jpg" },
  cartaz: { url: "/img/cartaz.jpg" },
}

const nav = [
  { label: "Trabalho", to: "index" },
  { label: "Contacto", to: "contacto" },
]

export default function Estudio() {
  return (
    <Site id="estudio" title="Estúdio Neon" domain="neon.web" theme="neon" images={imagens}>
      <Page id="index" title="Trabalho">
        <Header title="Estúdio Neon" subtitle="Som, luz e cartaz" nav={nav} active="index" />
        <Hero
          image="palco"
          title="Fazemos a noite parecer mais alta"
          text="Som ao vivo, desenho de luz e cartazes para clubes em Night City."
          cta={{ label: "Falar connosco", to: "contacto" }}
        />
        <Section title="Trabalho">
          <Grid columns={3}>
            <Card image="som" meta="Som" title="Clube Totentanz" text="Sistema de som e acústica." to="contacto" />
            <Card image="luz" meta="Luz" title="Afterlife" text="Desenho de luz do salão." to="contacto" />
            <Card image="cartaz" meta="Cartaz" title="Série Kabuki" text="Seis cartazes serigrafados." to="contacto" />
          </Grid>
        </Section>
        <Quote text="Fizeram o clube parecer maior por dentro." author="Barman do Totentanz" />
        <Divider />
        <Section title="Como trabalhamos">
          <BulletList
            items={[
              "Primeira conversa: meia hora, sem custo.",
              "Proposta com desenho e orçamento por escrito.",
              "Montagem na véspera, desmontagem no fim da noite.",
            ]}
          />
        </Section>
        <Footer text="© 2077 Estúdio Neon" links={[{ label: "Contacto", to: "contacto" }]} />
      </Page>

      <Page id="contacto" title="Contacto">
        <Header title="Estúdio Neon" nav={nav} active="contacto" />
        <Section title="Contacto">
          <Text size={46} wrap={2000} lineHeight={1.25}>
            Escreva para ola@neon.web com a data do evento e o tipo de sala.
          </Text>
          <Button label="Escrever email" to="mailto:ola@neon.web" />
          <Text size={38} upper={true} weight="semibold" color="var(--nk-muted)">
            Respondemos em dois dias úteis
          </Text>
        </Section>
        <Footer text="© 2077 Estúdio Neon" links={[{ label: "Trabalho", to: "index" }]} />
      </Page>
    </Site>
  )
}
```

> `Text` dentro de `Text` não existe: o texto é uma string, sem markup. Para dar destaque a uma parte da
> frase, parta-a em dois `Text` num `Row` — o `check` recusa aninhamento.

---

## O que estes exemplos mostram

| Decisão | Porquê |
| --- | --- |
| `tabloid` para notícia | é o único tema claro; lê-se como papel |
| `street` para loja | amarelo de rua para preço e promoção |
| `neon` para portfólio | rosa/ciano para trabalho criativo |
| `Card width={1400}` numa `Grid` de 2 | cartões grandes ocupam a coluna inteira |
| `ProductCard` sem `width` | usa o tamanho de fábrica (640 ink) |
| `Table` com `widths` | controla a coluna do preço à direita |
| `Quote` e `BulletList` | variam o ritmo sem inventar componentes |
| `to="mailto:…"` | link externo é permitido; formulário não existe |
