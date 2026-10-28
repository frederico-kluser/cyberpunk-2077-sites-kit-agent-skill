# Changelog

Todas as alterações relevantes deste projeto ficam neste ficheiro.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto usa
[SemVer](https://semver.org/lang/pt-BR/).

- As versões são publicadas como tags `v<MAJOR>.<MINOR>.<PATCH>` a partir de `main`.
- As entradas são **geradas** dos [Commits Convencionais](https://www.conventionalcommits.org/pt-br/) no
  momento do release (`python3 scripts/oss-changelog.py --write`) — não se escrevem à mão.
- Comparações: <https://github.com/frederico-kluser/cyberpunk-2077-sites-kit-agent-skill/compare/>

## [Unreleased]

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

[Unreleased]: https://github.com/frederico-kluser/cyberpunk-2077-sites-kit-agent-skill/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/frederico-kluser/cyberpunk-2077-sites-kit-agent-skill/releases/tag/v1.0.0
