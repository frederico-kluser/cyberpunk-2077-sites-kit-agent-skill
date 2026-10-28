# Changelog

Todas as alterações relevantes deste projeto ficam neste ficheiro.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto usa
[SemVer](https://semver.org/lang/pt-BR/).

- As versões são publicadas como tags `v<MAJOR>.<MINOR>.<PATCH>` a partir de `main`.
- As entradas são **geradas** dos [Commits Convencionais](https://www.conventionalcommits.org/pt-br/) no
  momento do release (`python3 scripts/oss-changelog.py --write`) — não se escrevem à mão.
- Comparações: <https://github.com/frederico-kluser/cyberpunk-2077-sites-kit-agent-skill/compare/>

## [Unreleased]

## [1.1.0] — 2026-10-28

### Added

- **Prints reais do kit** em `docs/prints/` (cinco temas, notícia, loja, portfólio, catálogo, telemóvel e o
  caminho JSON sem React) e a capa `og.png`.
- **Gerador das capturas** `scripts/prints.py`: serve o repositório, fotografa com Chrome/Edge headless,
  gera a arte abstrata (Pillow, semente fixa) e descarrega as fontes OFL; `--check` valida a entrega.
- Testes das capturas (origem e ficheiros) e passos `npm run prints` / `prints:check`.

### Fixed

- **Hero**: o texto ficava atrás da imagem (a imagem é `position: relative` e o corpo era estático) e o véu
  tinha altura 0. Agora o corpo tem `z-index` e o véu cobre a área toda.
- **Navegação**: `NavBar` não tinha `gap` — os links apareciam colados (`--nk-gap` era definida mas ignorada).
- **Bordas**: `--nk-border` herdava para os descendentes e desenhava caixas fantasma dentro de cartões e
  botões; a borda passou a ser inline (`style.border`) e a variável desapareceu da CSS.
- **Button**: esticava na largura toda dentro de colunas (Hero); agora alinha a `flex-start`.

## [1.0.0] — 2026-10-28

### Added

- **Kit React `netkit-web`** com 25 componentes e 8 nós de layout no padrão visual dos sites NET do
  Cyberpunk 2077 (temas `net`, `corpo`, `street`, `tabloid`, `neon`).
- **Sistema visual fechado** em `assets/netkit-web/netkit-web.css`: paleta, tipografia, rampas de tamanho
  (20 valores), espaço (36 valores) e forma (raio 0, bordas 3/4, sem sombras/gradientes).
- **Renderer standalone** `netkit-web.standalone.js`: desenha `netsites-site/1` no browser sem React nem
  build, com CSS embutida sincronizada (`build`).
- **CLI `scripts/netkit.py`**: `inject` (com manifesto sha256), `check` (contrato visual de JSX/HTML/JSON),
  `verify`, `preview`, `new`, `list`, `build`.
- **Skill global** (`SKILL.md` + `scripts/link-skill-global.sh`) e documentação em `references/`
  (design system, componentes, formato, proibido, injeção, exemplos, checklist).
- **44 testes** sem dependências (14 node + 30 python) e CI com `build` agregador, CodeQL-ready e
  OpenSSF Scorecard.

[Unreleased]: https://github.com/frederico-kluser/cyberpunk-2077-sites-kit-agent-skill/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/frederico-kluser/cyberpunk-2077-sites-kit-agent-skill/releases/tag/v1.1.0
[1.0.0]: https://github.com/frederico-kluser/cyberpunk-2077-sites-kit-agent-skill/releases/tag/v1.0.0
