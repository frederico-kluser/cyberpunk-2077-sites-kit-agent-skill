# Checklist de entrega

Antes de dizer «está pronto». Os seis primeiros pontos são automáticos (`check` + `verify`); os restantes
são revisão humana.

## Automático

- [ ] `python3 scripts/netkit.py check <pasta do site>` → **0 erros**
- [ ] `python3 scripts/netkit.py verify --target <site>` → **kit OK** (nenhum ficheiro alterado)
- [ ] `python3 scripts/netkit.py verify` → **kit OK** (a skill está íntegra)
- [ ] `python3 scripts/netkit.py preview <site.json>` (estático) **ou** o dev server (React) abre sem erro
- [ ] nenhum `console` de erro no browser ao navegar entre todas as páginas
- [ ] todos os `link`/`to` abrem a página certa (nenhum 404, nenhum `#` vazio)

## Revisão

- [ ] **Só elementos do kit:** nenhum `<div>`, `style=`, `className=`, CSS, ícone, emoji, sombra, raio,
      gradiente, animação ou fonte nova (ver [`proibido.md`](proibido.md))
- [ ] **Cores e tamanhos da rampa:** tema escolhido com intenção; nenhum hex inventado; títulos com
      `heading` (nunca cor à mão)
- [ ] **Hierarquia:** um `Header`, um `Footer`, `Hero` só na principal; `Section` separa blocos; títulos
      `h1`→`h2`→`h3` coerentes
- [ ] **Conteúdo real:** sem Lorem ipsum, sem `TODO`, sem `[inserir]`; textos escritos na língua do pedido
- [ ] **Imagens com licença:** cada imagem tem proveniência registada; nenhum asset/captura da CDPR
- [ ] **Acessibilidade:** imagens de conteúdo com `alt`; links com texto que se entende fora de contexto;
      contraste do tema mantido
- [ ] **Responsivo:** a 390 px de largura nada transborda (as `Row stack` empilham; a `Grid` colapsa)
- [ ] **Estado do site no git:** `netkit/` commitado com `manifest.json`; sem segredos; sem ficheiros de
      build (`dist/`) no git

## Relatório de entrega (o que dizer ao dono)

```
Site: <nome> · tema <tema> · kit netkit-web 1.1.0 (<react|estático>)
Páginas: <ids>
Contrato visual: check 0 erros · verify OK
Imagens: <n> (proveniência: <…>)
Pré-visualização: <URL/comando>
O que falta no kit (se algo): <…>
```

## Quando `check` falha

1. Ler a mensagem: ela diz o ficheiro, a linha, **o que está errado** e **a solução**.
2. Corrigir o site — **nunca** o kit.
3. Repetir até 0 erros. Não se entrega com avisos por resolver sem os mencionar no relatório.

## Definição de pronto

- O site abre, navega e lê-se bem em desktop e telemóvel.
- `check` verde e `verify` verde.
- Nenhum elemento visual fora do sistema — e se faltou algo, o relatório diz o quê e o que se usou no lugar.
- Conteúdo e imagens com direitos tratados.
