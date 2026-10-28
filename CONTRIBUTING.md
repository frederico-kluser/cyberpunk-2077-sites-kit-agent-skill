# Contribuir

Obrigado por quereres melhorar o NETKIT/WEB. Este repositório é o **kit** e o **contrato visual** dos sites
no padrão do mod NetSites: uma alteração aqui muda todos os sites que usam o kit, por isso o processo é
deliberadamente conservador.

## O que precisas

| Ferramenta | Versão | Para quê |
| --- | --- | --- |
| Node.js | ≥ 20 | testes do renderer e do kit React (`node --test`) |
| Python | ≥ 3.10 | a CLI (`scripts/netkit.py`) e os testes do contrato |

Não há dependências npm: `npm install` não é necessário (e o CI não o corre).

```bash
git clone https://github.com/frederico-kluser/cyberpunk-2077-sites-kit-agent-skill.git
cd cyberpunk-2077-sites-kit-agent-skill
npm test                      # 14 testes node + 30 testes python
python3 scripts/netkit.py verify
```

## Onde mexer

| Quero… | Ficheiro | Cuidados |
| --- | --- | --- |
| mudar uma cor, um tamanho, um espaço | `assets/netkit-web/netkit-web.css` | é a **fonte única**; atualizar `references/design-system.md` |
| acrescentar/mudar um componente | `assets/netkit-web/netkit-web.js` | atualizar `.d.ts`, `COMPONENTS` em `scripts/netkit.py` e `references/componentes.md` |
| mudar o renderer JSON | `assets/standalone/netkit-web.standalone.js` | correr `python3 scripts/netkit.py build` e `verify` |
| mudar regras do contrato | `scripts/netkit.py` | acrescentar caso em `tests/test_netkit.py` |
| documentação | `references/`, `README.md`, `SKILL.md` | os exemplos de `references/exemplos.md` têm de passar no `check` |

O CSS e o standalone andam juntos: a CSS é **embutida** no standalone entre os marcadores
`/* NETKIT:CSS:BEGIN */ … /* NETKIT:CSS:END */`. Nunca se edita o bloco à mão — `python3 scripts/netkit.py
build` sincroniza e `verify` falha se estiverem diferentes (é também o que o CI confirma).

## Versão

A versão é **calculada** a partir dos commits (SemVer): `feat` → MINOR, `fix`/`docs`/`refactor` → PATCH,
`feat!`/`BREAKING CHANGE` → MAJOR. A versão vive em `package.json`, em `VERSION` do `netkit-web.js` e do
standalone; o `verify` falha se divergirem. Não se sobe a versão num PR de funcionalidade — isso é feito no
release.

## Commits e ramos

- Ramo: `<tipo>/<slug>` — `feat/hero-video`, `fix/tabela-telemovel`. Fora da convenção o push é recusado.
- Commit: Conventional Commits, imperativo, ≤ 72 caracteres — `feat(hero): aceitar imagem de capa`.
- PR para `main`, título convencional, **squash merge** (o histórico é linear e o título do PR vira a
  mensagem do commit).
- O CI (`build`) valida as mensagens e corre os testes; sem ele verde não há merge.

## Regras do kit

1. **Nada de exceções no site.** Uma funcionalidade nova é um componente novo no kit (com testes, tipos e
   documentação), nunca um `style` no site.
2. **Sem assets da CDPR.** Nenhum ficheiro extraído do jogo (atlas, ícones, fontes, capturas) entra no git,
   nem em testes, nem em exemplos.
3. **Sem dependências novas** sem uma razão forte: o kit é JS puro + CSS, o renderer é um ficheiro e a CLI é
   Python stdlib.
4. **Exemplos válidos.** Se mudares o sistema, os três exemplos de `references/exemplos.md` e os starters
   gerados pelo `netkit.py new` têm de continuar a passar no `check`.

## Checklist do PR

- [ ] `npm test` verde
- [ ] `python3 scripts/netkit.py verify` verde
- [ ] `python3 scripts/netkit.py build` sem diferenças (`git diff --exit-code`)
- [ ] documentação atualizada (design-system / componentes / formato / proibido, conforme o caso)
- [ ] versão **não** alterada (só no release)
- [ ] descrição do PR explica o efeito nos sites existentes

## Código de conduta e segurança

- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) — respeito é o mínimo.
- [`SECURITY.md`](SECURITY.md) — vulnerabilidades por canal privado, nunca em issue pública.
