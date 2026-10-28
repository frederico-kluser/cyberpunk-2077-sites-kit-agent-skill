#!/usr/bin/env python3
"""netkit.py — CLI oficial do NETKIT/WEB (sites no padrão visual do mod NetSites).

Comandos:
  inject    copia o kit para um site (React ou estático) com manifesto sha256
  verify    confere o kit (CSS embutida, versões, exports) ou a cópia num site
  check     valida o contrato visual de um site (JSX, HTML ou netsites-site/1)
  new       cria uma página de arranque (React) ou um site.json (estático)
  preview   serve um site.json localmente, sem internet nem build
  list      imprime o inventário fechado (componentes, temas, rampas, tokens)
  build     sincroniza a CSS de origem com a cópia embutida no standalone
  version   imprime a versão do kit

Saída e erros: `Erro: <o quê> — Solução: <o que fazer>` em stderr.
Exit codes: 0 ok · 1 problemas encontrados · 2 uso inválido · 3 kit incompleto.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.1.0"

ROOT = Path(__file__).resolve().parent.parent
KIT_DIR = ROOT / "assets" / "netkit-web"
STANDALONE_DIR = ROOT / "assets" / "standalone"
TEMPLATES = ROOT / "assets" / "templates"

REACT_FILES = ["netkit-web.js", "netkit-web.css", "netkit-web.d.ts"]
STANDALONE_FILES = ["netkit-web.standalone.js", "netkit-web.css"]

THEMES = ["net", "corpo", "street", "tabloid", "neon"]

#: Tamanhos de texto permitidos (unidades ink). São os que o kit usa.
SIZES = [32, 34, 36, 38, 40, 42, 44, 46, 50, 52, 58, 60, 64, 72, 80, 96, 110, 120, 140, 150]
#: Espaços permitidos (gap/padding/margin/thickness), unidades ink.
SPACES = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 36, 40, 44, 48, 52, 56, 60, 64, 72, 80, 88, 96, 110, 120, 140, 160, 180, 200, 240]
#: Larguras de borda permitidas.
BORDERS = [3, 4]

#: Nós do formato netsites-site/1 e as props de cada um.
PROPS_BY_TYPE = {
    "page": ["width", "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name",
             "background", "padding", "gap", "align"],
    "column": ["width", "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name",
               "gap", "padding", "align", "background", "border"],
    "row": ["width", "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name",
            "gap", "padding", "valign", "background", "border"],
    "stack": ["width", "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name",
              "padding", "background", "border", "align", "valign"],
    "text": ["width", "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name",
             "text", "size", "color", "font", "weight", "upper", "align", "wrap", "lineHeight"],
    "image": ["width", "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name",
              "image", "tint", "fit", "alt"],
    "rect": ["width", "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name", "color"],
    "spacer": ["width", "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name"],
}
CONTAINERS = {"page", "column", "row", "stack"}

#: Componentes do kit React: props aceites e obrigatórias.
COMPONENTS = {
    "Site": {"props": ["id", "title", "domain", "home", "lang", "icon", "images", "theme", "children"],
             "required": ["id", "title", "domain"]},
    "Page": {"props": ["id", "path", "title", "children", "background", "padding", "gap", "align",
                       "width", "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name"],
             "required": ["id"]},
    "Column": {"props": ["children", "padding", "gap", "align", "background", "border", "width", "height",
                         "grow", "selfAlign", "margin", "opacity", "link", "hover", "name"], "required": []},
    "Row": {"props": ["children", "padding", "gap", "valign", "background", "border", "stack", "width",
                      "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name"], "required": []},
    "Stack": {"props": ["children", "padding", "align", "valign", "background", "border", "width", "height",
                        "grow", "selfAlign", "margin", "opacity", "link", "hover", "name"], "required": []},
    "Text": {"props": ["children", "as", "size", "color", "font", "weight", "upper", "align", "wrap",
                       "lineHeight", "heading", "width", "height", "grow", "selfAlign", "margin", "opacity",
                       "link", "hover", "name"], "required": ["children"]},
    "Image": {"props": ["image", "tint", "fit", "alt", "width", "height", "grow", "selfAlign", "margin",
                        "opacity", "link", "hover", "name"], "required": ["image"]},
    "Rect": {"props": ["color", "width", "height", "grow", "selfAlign", "margin", "opacity", "link",
                       "hover", "name"], "required": []},
    "Spacer": {"props": ["width", "height", "grow", "selfAlign", "margin", "opacity", "link", "hover", "name"],
               "required": []},
    "NavBar": {"props": ["items", "active", "gap", "size", "color", "activeColor"], "required": ["items"]},
    "Header": {"props": ["logo", "logoSize", "title", "subtitle", "nav", "active"], "required": ["title"]},
    "Hero": {"props": ["image", "title", "text", "cta", "height", "align"], "required": ["title"]},
    "Button": {"props": ["label", "to", "variant", "size", "color", "textColor"], "required": ["label", "to"]},
    "Card": {"props": ["image", "title", "text", "to", "width", "imageHeight", "meta"], "required": ["title"]},
    "Grid": {"props": ["columns", "gap", "children"], "required": []},
    "Section": {"props": ["title", "children", "gap"], "required": ["title"]},
    "Article": {"props": ["title", "byline", "body", "width", "image"], "required": ["title", "body"]},
    "ProductCard": {"props": ["image", "name", "price", "to", "width"], "required": ["name", "price"]},
    "Divider": {"props": ["color", "thickness", "margin"], "required": []},
    "Badge": {"props": ["text", "color", "textColor"], "required": ["text"]},
    "Quote": {"props": ["text", "author", "width"], "required": ["text"]},
    "BulletList": {"props": ["items", "width"], "required": ["items"]},
    "Table": {"props": ["columns", "rows", "widths"], "required": ["columns", "rows"]},
    "Banner": {"props": ["image", "text", "to", "height", "color"], "required": ["text"]},
    "Footer": {"props": ["text", "links"], "required": ["text"]},
}

COLOR_PROPS = {"color", "background", "hover", "tint", "textColor", "activeColor"}
SPACE_PROPS = {"gap", "thickness"}
BOX_PROPS = {"padding", "margin"}
SIZE_PROPS = {"size"}
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
VAR_RE = re.compile(r"^var\(\s*--nk-[a-z0-9-]+\s*\)$")
NETDIR_RE = re.compile(r"^(?:[A-Za-z][\w+.-]*://|[A-Za-z][\w+.-]*:)[^\s]*$")
ID_RE = re.compile(r"^[a-z0-9_]+$")
DOMAIN_RE = re.compile(r"^[a-z0-9.-]+$")
FONTS = ["raj", "orbitron", "blender", "industry", "arial"]
WEIGHTS = ["light", "regular", "medium", "semibold", "bold", "black"]
ALIGNS = ["start", "center", "end", "stretch"]
TEXT_ALIGNS = ["left", "center", "right"]
VARIANTS = ["solid", "outline"]
TEXT_TAGS = ["p", "h1", "h2", "h3", "span"]

#: Domínios que um site do kit não pode usar (sites do jogo e do mod).
RESERVED_DOMAINS = {
    "arasaka.corp", "ncity.pub", "netsites.pub", "afterlife", "kangtao.corp",
    "atelier.pub", "cyber.car", "cyber.clicker", "militech.corp", "biotechnica.corp",
}

#: Tags HTML que nunca entram num site do kit (a alternativa é sempre um componente).
HTML_TAGS = {
    "div": "Column / Row / Stack", "span": "Text", "p": "Text", "a": "link={…} no componente",
    "img": "Image", "picture": "Image", "button": "Button", "h1": "Text as=\"h1\"",
    "h2": "Text as=\"h2\"", "h3": "Text as=\"h3\"", "section": "Section", "article": "Article",
    "header": "Header", "footer": "Footer", "nav": "NavBar", "ul": "BulletList", "ol": "BulletList",
    "li": "BulletList", "table": "Table", "tr": "Table", "td": "Table", "th": "Table",
    "figure": "Image", "figcaption": "Text", "svg": "(não existe no kit)", "canvas": "(não existe no kit)",
    "video": "(não existe no kit)", "audio": "(não existe no kit)", "iframe": "(não existe no kit)",
    "form": "(não existe no kit)", "input": "(não existe no kit)", "select": "(não existe no kit)",
    "textarea": "(não existe no kit)", "em": "Text", "strong": "Text", "b": "Text", "i": "Text",
    "small": "Text", "hr": "Divider", "br": "(quebra é automática: use wrap)", "style": "(CSS não entra)",
}


# --------------------------------------------------------------------------- utilidades

class NetkitError(Exception):
    """Erro operacional: imprime `Erro: … — Solução: …` e sai com 2."""


class Report:
    """Problemas encontrados, com ficheiro, linha e severidade."""

    def __init__(self) -> None:
        self.items: list[dict] = []

    def error(self, where: str, line: int, message: str) -> None:
        self.items.append({"where": where, "line": line, "severity": "error", "message": message})

    def warn(self, where: str, line: int, message: str) -> None:
        self.items.append({"where": where, "line": line, "severity": "warning", "message": message})

    @property
    def errors(self) -> list[dict]:
        return [i for i in self.items if i["severity"] == "error"]

    @property
    def warnings(self) -> list[dict]:
        return [i for i in self.items if i["severity"] == "warning"]

    def extend(self, other: "Report", prefix: str = "") -> None:
        for item in other.items:
            self.items.append(
                {**item, "where": f"{prefix}{item['where']}" if prefix else item["where"]}
            )

    def text(self) -> str:
        lines = []
        for item in self.items:
            marker = "ERRO" if item["severity"] == "error" else "AVISO"
            place = item["where"] + (f":{item['line']}" if item.get("line") else "")
            lines.append(f"{marker} {place}: {item['message']}")
        return "\n".join(lines)

    def summary(self) -> str:
        return f"{len(self.errors)} erro(s), {len(self.warnings)} aviso(s)"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def kit_file(name: str) -> Path:
    for base in (KIT_DIR, STANDALONE_DIR):
        candidate = base / name
        if candidate.exists():
            return candidate
    raise SystemExit(f"Erro: {name} não existe no kit — Solução: reinstale a skill")


def css_tokens() -> dict:
    """Cores e variáveis legais, lidas do bloco NETKIT:TOKENS da CSS (fonte única)."""
    css = (KIT_DIR / "netkit-web.css").read_text(encoding="utf-8")
    block = extract_between(css, "NETKIT:TOKENS:BEGIN", "NETKIT:TOKENS:END")
    colors = sorted({m.group(0).lower() for m in re.finditer(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?", block)})
    return {"colors": colors, "css": css, "block": block}


def legal_color(value: str, colors: list[str]) -> bool:
    value = value.strip()
    if VAR_RE.match(value):
        return True
    if value in ("transparent", "currentColor", "inherit"):
        return True
    low = value.lower()
    if HEX_RE.match(low):
        if low in colors:
            return True
        # alfa 00 é sempre transparente
        return low.endswith("00") and low[:7] in colors
    return False


def extract_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"Erro: marcador {start_marker} não existe — Solução: use o ficheiro do kit sem alterações")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"Erro: marcador {end_marker} não existe — Solução: use o ficheiro do kit sem alterações")
    return text[start + len(start_marker):end]


def rel(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


# --------------------------------------------------------------------------- JSX

def match_brace(text: str, start: int) -> int:
    """Índice do `}` que fecha o `{` em `start` (respeita strings e aninhamento)."""
    depth = 0
    i = start
    quote = None
    while i < len(text):
        c = text[i]
        if quote:
            if c == quote and text[i - 1] != "\\":
                quote = None
        elif c in "\"'`":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(text) - 1


def scan_tags(text: str) -> list[dict]:
    """Etiquetas JSX/HTML do ficheiro, com linha e atributos em bruto."""
    tags: list[dict] = []
    i, line = 0, 1
    while i < len(text):
        if text[i] == "\n":
            line += 1
            i += 1
            continue
        if text[i] != "<":
            i += 1
            continue
        if text.startswith("<!--", i):
            end = text.find("-->", i)
            if end < 0:
                break
            line += text.count("\n", i, end)
            i = end + 3
            continue
        j = i + 1
        closing = False
        if j < len(text) and text[j] == "/":
            closing = True
            j += 1
        if j < len(text) and text[j] == ">":
            tags.append({"name": "", "closing": closing, "self": True, "attrs": "", "line": line})
            i = j + 1
            continue
        m = re.match(r"[A-Za-z][\w.:-]*", text[j:])
        if not m:
            i += 1
            continue
        name = m.group(0)
        start_line = line
        j += len(name)
        depth, quote, k = 0, None, j
        while k < len(text):
            c = text[k]
            if quote:
                if c == quote and text[k - 1] != "\\":
                    quote = None
            elif c in "\"'`":
                quote = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth = max(0, depth - 1)
            elif c == ">" and depth == 0:
                break
            if c == "\n":
                line += 1
            k += 1
        self_closing = text[k - 1] == "/"
        tags.append({"name": name, "closing": closing, "self": self_closing, "attrs": text[j:k], "line": start_line})
        i = k + 1
    return tags


def parse_attrs(raw: str) -> list[dict]:
    out: list[dict] = []
    i = 0
    while i < len(raw):
        c = raw[i]
        if c.isspace() or c == ",":
            i += 1
            continue
        if c == "{":
            end = match_brace(raw, i)
            out.append({"name": None, "value": raw[i + 1:end], "expr": True})
            i = end + 1
            continue
        m = re.match(r"[A-Za-z_][\w:-]*", raw[i:])
        if not m:
            i += 1
            continue
        name = m.group(0)
        i += len(name)
        while i < len(raw) and raw[i].isspace():
            i += 1
        if i < len(raw) and raw[i] == "=":
            i += 1
            while i < len(raw) and raw[i].isspace():
                i += 1
            if i < len(raw) and raw[i] in "\"'":
                quote = raw[i]
                end = raw.find(quote, i + 1)
                if end < 0:
                    end = len(raw)
                out.append({"name": name, "value": raw[i + 1:end], "expr": False})
                i = end + 1
            elif i < len(raw) and raw[i] == "{":
                end = match_brace(raw, i)
                out.append({"name": name, "value": raw[i + 1:end], "expr": True})
                i = end + 1
            else:
                m2 = re.match(r"[^\s>]+", raw[i:])
                value = m2.group(0) if m2 else ""
                out.append({"name": name, "value": value, "expr": True})
                i += len(value)
        else:
            out.append({"name": name, "value": None, "expr": False})
    return out


def literal_value(attr: dict) -> str | None:
    """Valor textual de uma prop: string literal, número literal ou null."""
    if attr.get("expr"):
        raw = (attr.get("value") or "").strip()
        if re.fullmatch(r"-?\d+(?:\.\d+)?", raw):
            return raw
        if raw in ("true", "false"):
            return raw
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'`":
            return raw[1:-1]
        return None
    return attr.get("value")


def numbers_in(value: str | None) -> list[int] | None:
    """Números de um valor (número solto ou lista [a, b, c, d])."""
    if value is None:
        return None
    if re.fullmatch(r"-?\d+(?:\.\d+)?", value.strip()):
        return [int(float(value))]
    nums = re.findall(r"-?\d+(?:\.\d+)?", value)
    return [int(float(n)) for n in nums] if nums else None


def local_components(text: str) -> set[str]:
    names = set(re.findall(r"(?:function|const|let)\s+([A-Z]\w*)\s*[=(]", text))
    return names


def page_ids(text: str) -> set[str]:
    ids = set()
    for tag in scan_tags(text):
        if tag["closing"] or tag["name"] != "Page":
            continue
        for attr in parse_attrs(tag["attrs"]):
            if attr["name"] == "id":
                value = literal_value(attr)
                if value:
                    ids.add(value)
    return ids


# --------------------------------------------------------------------------- validadores

def check_jsx(path: Path, text: str, report: Report, tokens: dict) -> None:
    where = path.name
    colors = tokens["colors"]
    for pattern, message in [
        (r"\bstyle\s*=", "style= não entra: a aparência é do kit, não do site"),
        (r"\bclassName\s*=", "className= não entra: use as props do componente"),
        (r"\bclass\s*=", "class= não entra: use as props do componente"),
        (r"dangerouslySetInnerHTML", "HTML cru não entra: o jogo não desenha HTML"),
        (r"<style\b", "tag <style> não entra: a CSS é do kit"),
    ]:
        for match in re.finditer(pattern, text):
            line = text.count("\n", 0, match.start()) + 1
            report.error(where, line, message)

    local = local_components(text)
    allowed = set(COMPONENTS) | local
    pages = page_ids(text)

    for tag in scan_tags(text):
        name = tag["name"]
        if not name or tag["closing"]:
            continue
        if name in HTML_TAGS:
            hint = HTML_TAGS[name]
            report.error(
                where, tag["line"],
                f"<{name}> não existe no kit — Solução: use {hint}; nada fora dos componentes do netkit-web",
            )
            continue
        if name not in allowed:
            report.error(
                where, tag["line"],
                f"<{name}> não é um componente do kit — Solução: use só {', '.join(sorted(COMPONENTS))}",
            )
            continue
        if name in local:
            continue
        spec = COMPONENTS[name]
        attrs = parse_attrs(tag["attrs"])
        seen = set()
        for attr in attrs:
            prop = attr["name"]
            if prop is None:
                report.error(where, tag["line"], f"{{…}} espalhado dentro de <{name}> — Solução: escreva as props uma a uma")
                continue
            if prop in ("key", "ref"):
                continue
            seen.add(prop)
            if prop not in spec["props"]:
                report.error(
                    where, tag["line"],
                    f"<{name}> não tem a prop «{prop}» — Solução: use {', '.join(spec['props'])}",
                )
                continue
            value = literal_value(attr)
            if prop in COLOR_PROPS and value is not None and not legal_color(value, colors):
                report.error(
                    where, tag["line"],
                    f"cor «{value}» fora da paleta — Solução: use var(--nk-accent), var(--nk-line)… "
                    f"ou um hex da paleta ({', '.join(colors[:6])}…)",
                )
            if prop == "border" and value is None:
                inner = attr.get("value") or ""
                for color in re.findall(r"(?:color)\s*:\s*[\"']([^\"']+)[\"']", inner):
                    if not legal_color(color, colors):
                        report.error(where, tag["line"], f"cor de borda «{color}» fora da paleta — Solução: var(--nk-line)")
                widths = numbers_in(inner.split("width:")[-1]) if "width:" in inner else []
                if widths and widths[0] not in BORDERS:
                    report.error(where, tag["line"], f"largura de borda {widths[0]} — Solução: use 3 ou 4")
            if prop == "theme" and value and value not in THEMES:
                report.error(where, tag["line"], f"tema «{value}» — Solução: {', '.join(THEMES)}")
            if prop == "variant" and value and value not in VARIANTS:
                report.error(where, tag["line"], f"variante «{value}» — Solução: solid ou outline")
            if prop == "as" and value and value not in TEXT_TAGS:
                report.error(where, tag["line"], f"as=\"{value}\" — Solução: {', '.join(TEXT_TAGS)}")
            if prop == "font" and value and value not in FONTS:
                report.error(where, tag["line"], f"fonte «{value}» — Solução: {', '.join(FONTS)}")
            if prop == "weight" and value and value not in WEIGHTS:
                report.error(where, tag["line"], f"peso «{value}» — Solução: {', '.join(WEIGHTS)}")
            if prop in ("align", "valign", "selfAlign") and value and value not in ALIGNS:
                report.error(where, tag["line"], f"alinhamento «{value}» — Solução: {', '.join(ALIGNS)}")
            if prop in SIZE_PROPS and value is not None:
                nums = numbers_in(value)
                if nums and nums[0] not in SIZES:
                    report.error(
                        where, tag["line"],
                        f"tamanho {nums[0]} fora da rampa — Solução: {', '.join(str(s) for s in SIZES)}",
                    )
            if prop in SPACE_PROPS and value is not None:
                nums = numbers_in(value)
                if nums and nums[0] not in SPACES:
                    report.error(where, tag["line"], f"espaço {nums[0]} fora da rampa — Solução: múltiplos de 2 até 240, ver list")
            if prop in BOX_PROPS and value is not None:
                nums = numbers_in(value)
                for num in nums or []:
                    if num not in SPACES:
                        report.error(where, tag["line"], f"espaço {num} fora da rampa — Solução: ver netkit.py list")
            if prop in ("link", "to") and value and not NETDIR_RE.match(value) and value not in pages:
                report.error(
                    where, tag["line"],
                    f"ligação «{value}» não é uma página deste site nem um endereço — Solução: use o id de uma <Page> ou https://…",
                )
        for required in spec["required"]:
            if required not in seen and required != "children":
                report.warn(where, tag["line"], f"<{name}> sem «{required}» — confirme se é intencional")

    stack: list[str] = []
    for tag in scan_tags(text):
        name = tag["name"]
        if not name:
            continue
        if tag["closing"]:
            if name in stack:
                while stack and stack.pop() != name:
                    pass
            continue
        if stack and stack[-1] == "Text":
            report.error(
                where, tag["line"],
                f"<{name}> dentro de <Text> — Solução: o texto é uma string; ponha outro <Text> ao lado num Row/Column",
            )
        if not tag.get("self"):
            stack.append(name)

    if "<Page" not in text:
        report.error(where, 1, "o ficheiro não tem <Page> — Solução: um site é um <Site> com pelo menos uma <Page>")
    if not re.search(r"<Text\b", text) and not re.search(r"<(Hero|Header|Card|Article|Section|Button)\b", text):
        report.warn(where, 1, "sem texto visível: um site precisa de <Text> ou de um bloco que o traga")
    if len(scan_tags(text)) > 600:
        report.warn(where, 1, "mais de 600 nós — Solução: divida em páginas (o jogo também tem esse limite)")


def check_html(path: Path, text: str, report: Report) -> None:
    where = path.name
    allowed = {"html", "head", "body", "meta", "title", "link", "script", "noscript", "main", "netsites"}
    for tag in scan_tags(text):
        name = tag["name"].lower()
        if not name:
            continue
        if name == "style":
            report.error(where, tag["line"], "tag <style> não entra — Solução: a CSS é a do kit")
            continue
        if name == "div":
            continue  # só o #alvo da montagem
        if name not in allowed:
            hint = HTML_TAGS.get(name, "os componentes do kit")
            report.error(where, tag["line"], f"<{name}> não entra na página — Solução: {hint}")
    for match in re.finditer(r"\bstyle\s*=\s*[\"']", text):
        line = text.count("\n", 0, match.start()) + 1
        report.error(where, line, "style= inline não entra — Solução: o CSS é o netkit-web.css")
    for match in re.finditer(r"\bclass\s*=\s*[\"']([^\"']+)[\"']", text):
        if not all(part.startswith("nk-") for part in match.group(1).split()):
            line = text.count("\n", 0, match.start()) + 1
            report.error(where, line, f"classe «{match.group(1)}» não é do kit — Solução: use os componentes")
    for tag in scan_tags(text):
        if tag["closing"]:
            continue
        if tag["name"].lower() == "link":
            href = next((a.get("value") or "" for a in parse_attrs(tag["attrs"]) if a["name"] == "href"), "")
            if not ("netkit-web.css" in href or "fonts.googleapis.com" in href or "fonts.gstatic.com" in href):
                report.warn(where, tag["line"], f"<link> para «{href}» — só o CSS do kit e as fontes são esperados")
        if tag["name"].lower() == "script":
            src = next((a.get("value") or "" for a in parse_attrs(tag["attrs"]) if a["name"] == "src"), "")
            if src and "netkit-web" not in src:
                report.warn(where, tag["line"], f"<script> «{src}» fora do kit — o site não deve trazer JS próprio")


def check_json(path: Path, text: str, report: Report, tokens: dict) -> None:
    where = path.name
    colors = tokens["colors"]
    try:
        spec = json.loads(text)
    except json.JSONDecodeError as exc:
        report.error(where, exc.lineno, f"JSON inválido: {exc.msg}")
        return
    if not isinstance(spec, dict):
        report.error(where, 1, "o site tem de ser um objeto JSON")
        return

    schema = spec.get("schema")
    if schema != "netsites-site/1":
        report.error(where, 1, f"schema «{schema}» — Solução: netsites-site/1")
    if not ID_RE.match(str(spec.get("id", ""))):
        report.error(where, 1, f"id «{spec.get('id')}» — Solução: [a-z0-9_]+")
    domain = str(spec.get("domain", ""))
    if not DOMAIN_RE.match(domain):
        report.error(where, 1, f"domain «{domain}» — Solução: [a-z0-9.-]+ (ex.: ncity.web)")
    if domain in RESERVED_DOMAINS:
        report.error(where, 1, f"domain «{domain}» é de um site do jogo ou do mod — Solução: escolha outro")
    if not spec.get("title"):
        report.error(where, 1, "falta o title do site")
    theme = spec.get("theme")
    if theme is not None and theme not in THEMES:
        report.error(where, 1, f"tema «{theme}» — Solução: {', '.join(THEMES)}")

    images = spec.get("images") or {}
    if not isinstance(images, dict):
        report.error(where, 1, "images tem de ser um objeto")
        images = {}
    for name, entry in images.items():
        if not ID_RE.match(str(name)):
            report.error(where, 1, f"imagem «{name}» — Solução: [a-z0-9_]+")
        if not isinstance(entry, dict):
            report.error(where, 1, f"imagem «{name}» tem de ser um objeto")
            continue
        has_atlas = bool(entry.get("atlas") and entry.get("part"))
        has_file = bool(entry.get("file") or entry.get("url"))
        if not (has_atlas or has_file):
            report.error(where, 1, f"imagem «{name}» — Solução: {{atlas,part}} (jogo) ou {{file}}/{{url}} (web)")
        if "url" in entry and "file" in entry:
            report.error(where, 1, f"imagem «{name}» tem url e file — Solução: escolha um")

    pages = spec.get("pages") or []
    if not isinstance(pages, list) or not pages:
        report.error(where, 1, "o site não tem páginas")
        return
    ids = {str(page.get("id", "")) for page in pages}
    if spec.get("home") and spec["home"] not in ids:
        report.error(where, 1, f"home «{spec['home']}» não é uma página do site")
    addresses, node_count, seen_pages = set(), 0, set()
    for page in pages:
        pid = str(page.get("id", ""))
        if not ID_RE.match(pid):
            report.error(where, 1, f"página «{pid}» — Solução: [a-z0-9_]+")
        if pid in seen_pages:
            report.error(where, 1, f"página «{pid}» repetida")
        seen_pages.add(pid)
        address = str(page.get("address", ""))
        if not address.startswith("NETdir://"):
            report.error(where, 1, f"página «{pid}»: endereço tem de começar por NETdir://")
        elif domain and not (address == f"NETdir://{domain}" or address.startswith(f"NETdir://{domain}/")):
            report.error(where, 1, f"página «{pid}»: endereço fora do domínio «{domain}»")
        if address in addresses:
            report.error(where, 1, f"endereço repetido: {address}")
        addresses.add(address)
        root = page.get("root")
        if not isinstance(root, dict) or root.get("type") != "page":
            report.error(where, 1, f"página «{pid}»: a raiz tem de ser um nó page")
            continue
        stack = [(root, pid, 0)]
        while stack:
            node, trail, depth = stack.pop()
            node_count += 1
            ntype = node.get("type")
            props = node.get("props") or {}
            if ntype not in PROPS_BY_TYPE:
                report.error(where, 1, f"{trail}: tipo «{ntype}» desconhecido — Solução: {', '.join(PROPS_BY_TYPE)}")
                continue
            if depth > 40:
                report.error(where, 1, f"{trail}: árvore funda demais (máx. 40)")
                continue
            for key, value in props.items():
                if key not in PROPS_BY_TYPE[ntype]:
                    report.warn(where, 1, f"{trail}: prop «{key}» não existe em {ntype} (o jogo ignora-a)")
                    continue
                if key in COLOR_PROPS and isinstance(value, str) and not legal_color(value, colors):
                    report.error(where, 1, f"{trail}: cor «{value}» fora da paleta — Solução: var(--nk-*) das 5 paletas")
                if key == "size" and isinstance(value, (int, float)) and int(value) not in SIZES:
                    report.error(where, 1, f"{trail}: tamanho {value} fora da rampa — Solução: ver netkit.py list")
                if key in ("gap",) and isinstance(value, (int, float)) and int(value) not in SPACES:
                    report.error(where, 1, f"{trail}: espaço {value} fora da rampa — Solução: ver netkit.py list")
                if key in ("padding", "margin"):
                    values = value if isinstance(value, list) else [value]
                    for num in values:
                        if isinstance(num, (int, float)) and int(num) not in SPACES:
                            report.error(where, 1, f"{trail}: espaço {num} fora da rampa — Solução: ver netkit.py list")
                if key == "border" and isinstance(value, dict):
                    if value.get("width") not in BORDERS:
                        report.error(where, 1, f"{trail}: borda de {value.get('width')} — Solução: 3 ou 4")
                    if not legal_color(str(value.get("color")), colors):
                        report.error(where, 1, f"{trail}: cor de borda «{value.get('color')}» fora da paleta")
                if key == "link" and isinstance(value, str) and value:
                    if not NETDIR_RE.match(value) and value not in ids:
                        report.error(where, 1, f"{trail}: link «{value}» não é página do site nem endereço")
                if key == "theme" and value not in THEMES:
                    report.error(where, 1, f"{trail}: tema «{value}» — Solução: {', '.join(THEMES)}")
            if ntype == "image":
                ref = props.get("image")
                if ref not in images:
                    report.error(where, 1, f"{trail}: imagem «{ref}» não está em images")
            children = node.get("children") or []
            if children and ntype not in CONTAINERS:
                report.error(where, 1, f"{trail}: {ntype} não pode ter filhos")
            for index, child in enumerate(children):
                if isinstance(child, dict):
                    stack.append((child, f"{trail} › {child.get('type')}[{index}]", depth + 1))
        if node_count > 600:
            report.warn(where, 1, f"página «{pid}» com {node_count} nós — divida em páginas")
        node_count = 0
    if spec.get("home") and spec["home"] not in ids:
        report.error(where, 1, f"home «{spec['home']}» não é uma página do site")
    used: set[str] = set()
    for page in pages:
        stack = [page.get("root") or {}]
        while stack:
            node = stack.pop()
            props = node.get("props") or {}
            if node.get("type") == "image" and props.get("image"):
                used.add(str(props["image"]))
            stack.extend([c for c in (node.get("children") or []) if isinstance(c, dict)])
    for name in images:
        if name not in used:
            report.warn(where, 1, f"imagem «{name}» não é usada")


# --------------------------------------------------------------------------- comandos

def cmd_check(args: argparse.Namespace) -> int:
    tokens = css_tokens()
    targets: list[Path] = []
    for item in args.paths:
        path = Path(item)
        if path.is_dir():
            skip = {"netkit-web.js", "netkit-web.css", "netkit-web.d.ts", "netkit-web.standalone.js",
                    "manifest.json", "package-lock.json"}
            for pattern in ("**/*.jsx", "**/*.tsx", "**/*.html", "**/*.json"):
                targets.extend(
                    sorted(p for p in path.glob(pattern) if "node_modules" not in p.parts and p.name not in skip)
                )
        elif path.exists():
            targets.append(path)
        else:
            print(f"Erro: {path} não existe — Solução: indique um ficheiro ou pasta do site", file=sys.stderr)
            return 2
    if not targets:
        print("Erro: nada para validar — Solução: aponte a pasta do site (com .jsx, .html ou .json)", file=sys.stderr)
        return 2

    report = Report()
    for path in targets:
        text = path.read_text(encoding="utf-8", errors="replace")
        suffix = path.suffix.lower()
        if suffix in (".jsx", ".tsx"):
            check_jsx(path, text, report, tokens)
        elif suffix == ".html":
            check_html(path, text, report)
        elif suffix == ".json":
            if '"netsites-site/1"' in text or path.name.endswith("site.json"):
                check_json(path, text, report, tokens)

    result = {
        "ok": not report.errors,
        "files": [str(p) for p in targets],
        "errors": report.errors,
        "warnings": report.warnings,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if report.items:
            print(report.text())
        print(f"\n{report.summary()} em {len(targets)} ficheiro(s)")
        if not report.errors:
            print("CONTRATO VISUAL OK")
    return 0 if not report.errors else 1


def load_json_module(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_build(args: argparse.Namespace) -> int:
    css = (KIT_DIR / "netkit-web.css").read_text(encoding="utf-8")
    if "`" in css or "${" in css:
        print("Erro: a CSS tem ` ou ${ — Solução: remova-os antes de embutir no standalone", file=sys.stderr)
        return 1
    target = STANDALONE_DIR / "netkit-web.standalone.js"
    text = target.read_text(encoding="utf-8")
    pattern = re.compile(r"/\* NETKIT:CSS:BEGIN \*/.*?/\* NETKIT:CSS:END \*/", re.S)
    if not pattern.search(text):
        print("Erro: marcadores NETKIT:CSS ausentes — Solução: restaure o standalone do kit", file=sys.stderr)
        return 1
    replacement = "/* NETKIT:CSS:BEGIN */\n" + css.rstrip() + "\n/* NETKIT:CSS:END */"
    updated = pattern.sub(lambda _m: replacement, text, count=1)
    if updated != text:
        target.write_text(updated, encoding="utf-8", newline="\n")
        print(f"build: CSS embutida no standalone ({len(css)} bytes)")
    else:
        print("build: standalone já estava sincronizado")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    problems: list[str] = []
    if args.target:
        root = Path(args.target).resolve()
        manifest_path = None
        for candidate in (root / "netkit" / "manifest.json", root / "src" / "netkit" / "manifest.json"):
            if candidate.exists():
                manifest_path = candidate
                break
        if not manifest_path:
            print(f"Erro: manifesto do kit não encontrado em {root} — Solução: corra `netkit.py inject` primeiro", file=sys.stderr)
            return 2
        manifest = load_json_module(manifest_path)
        base = manifest_path.parent
        for name, digest in (manifest.get("files") or {}).items():
            path = base / name
            if not path.exists():
                problems.append(f"FALTA {path}")
            elif sha256(path) != digest:
                problems.append(f"ALTERADO {path} (o kit não se edita; volte a fazer inject --force)")
        version = manifest.get("version")
        if version != VERSION:
            problems.append(f"versão instalada {version} ≠ versão do kit {VERSION} — Solução: inject --force")
        if problems:
            print("\n".join(problems))
            print(f"\nkit: {len(problems)} problema(s) — o kit foi alterado ou está incompleto")
            return 1
        print(f"kit OK em {base} (v{version}, {len(manifest.get('files') or {})} ficheiros, sha256 confere)")
        return 0

    css = (KIT_DIR / "netkit-web.css").read_text(encoding="utf-8")
    standalone = (STANDALONE_DIR / "netkit-web.standalone.js").read_text(encoding="utf-8")
    embedded = extract_between(standalone, "/* NETKIT:CSS:BEGIN */", "/* NETKIT:CSS:END */").strip()
    if embedded != css.strip():
        problems.append("CSS embutida no standalone diferente de netkit-web.css — Solução: `netkit.py build`")
    for marker in ("NETKIT:TOKENS:BEGIN", "NETKIT:TOKENS:END"):
        if marker not in css:
            problems.append(f"marcador {marker} ausente na CSS")
    js = (KIT_DIR / "netkit-web.js").read_text(encoding="utf-8")
    dts = (KIT_DIR / "netkit-web.d.ts").read_text(encoding="utf-8")
    exported = set(re.findall(r"^export (?:function|const) ([A-Za-z_]\w*)", js, re.M))
    declared = set(re.findall(r"^  export (?:function|const) ([A-Za-z_]\w*)", dts, re.M))
    missing = sorted(exported - declared)
    if missing:
        problems.append(f"exports sem declaração no .d.ts: {', '.join(missing)}")
    versions = set(re.findall(r'VERSION = "([0-9.]+)"', js + standalone))
    package = load_json_module(ROOT / "package.json") if (ROOT / "package.json").exists() else {}
    if package.get("version"):
        versions.add(str(package["version"]))
    if len(versions) != 1 or VERSION not in versions:
        problems.append(f"versões divergentes: {', '.join(sorted(versions))} (skill diz {VERSION})")
    if problems:
        print("\n".join(f"ERRO {p}" for p in problems))
        return 1
    print(f"kit OK: v{VERSION} · {len(exported)} exports · CSS sincronizada · {len(css)} bytes de CSS")
    return 0


def starter_jsx(name: str, import_path: str, css_path: str) -> str:
    return f'''import {{
  Site, Page, Header, Hero, Section, Grid, Card, Text, Button, Footer,
}} from "{import_path}"
import "{css_path}"

const imagens = {{
  // foto: {{ url: "/img/fachada.jpg" }},
  // logo: {{ file: "images/logo.png" }},
}}

export default function {name}() {{
  return (
    <Site id="{name.lower()}" title="{name}" domain="{name.lower()}.web" theme="net" images={{imagens}}>
      <Page id="index" title="Início">
        <Header
          title="{name}"
          subtitle="Night City · 2077"
          nav={{[
            {{ label: "Início", to: "index" }},
            {{ label: "Sobre", to: "sobre" }},
          ]}}
          active="index"
        />
        <Hero
          title="A cidade não espera"
          text="Um site de exemplo com o kit NET: nada aqui foge do sistema visual."
          cta={{{{ label: "Saber mais", to: "sobre" }}}}
        />
        <Section title="Destaques">
          <Grid columns={{3}}>
            <Card title="Primeiro" text="Um cartão do kit." meta="NET" />
            <Card title="Segundo" text="Outro cartão do kit." meta="NET" />
            <Card title="Terceiro" text="Sem invenções." meta="NET" />
          </Grid>
        </Section>
        <Footer text="© 2077 {name}" links={{[{{ label: "Sobre", to: "sobre" }}]}} />
      </Page>
      <Page id="sobre" title="Sobre">
        <Header title="{name}" nav={{[{{ label: "Início", to: "index" }}, {{ label: "Sobre", to: "sobre" }}]}} active="sobre" />
        <Section title="Sobre">
          <Text size={{46}} wrap={{2000}}>
            Esta página só usa componentes do netkit-web. Para voltar, use o botão abaixo.
          </Text>
          <Button label="Voltar" to="index" />
        </Section>
      </Page>
    </Site>
  )
}}
'''


def site_json(name: str, domain: str, theme: str) -> str:
    spec = {
        "schema": "netsites-site/1",
        "id": name.lower(),
        "title": name,
        "domain": domain,
        "lang": "pt-BR",
        "theme": theme,
        "home": "index",
        "images": {},
        "pages": [
            {
                "id": "index",
                "address": f"NETdir://{domain}",
                "title": "Início",
                "root": {
                    "type": "page",
                    "props": {"padding": [180, 200, 180, 160], "gap": 56},
                    "children": [
                        {"type": "text", "props": {"text": name, "size": 110, "upper": True,
                                                   "color": "#5ef6ff", "weight": "bold"}},
                        {"type": "rect", "props": {"height": 4, "color": "#2a3a46"}},
                        {"type": "text", "props": {"text": "Um site do kit NET, montado com os nós do jogo.",
                                                   "size": 46, "wrap": 2000}},
                        {"type": "spacer", "props": {"height": 40}},
                        {"type": "text", "props": {"text": "SOBRE", "size": 44, "upper": True,
                                                   "weight": "semibold", "link": "sobre", "hover": "#28ffff"}},
                    ],
                },
            },
            {
                "id": "sobre",
                "address": f"NETdir://{domain}/sobre",
                "title": "Sobre",
                "root": {
                    "type": "page",
                    "props": {"padding": [180, 200, 180, 160], "gap": 56},
                    "children": [
                        {"type": "text", "props": {"text": "Sobre", "size": 110, "upper": True,
                                                   "color": "#5ef6ff", "weight": "bold"}},
                        {"type": "text", "props": {"text": "Segunda página. Volte pelo link.", "size": 46, "wrap": 2000}},
                        {"type": "text", "props": {"text": "VOLTAR", "size": 44, "upper": True,
                                                   "weight": "semibold", "link": "index", "hover": "#28ffff"}},
                    ],
                },
            },
        ],
    }
    return json.dumps(spec, ensure_ascii=False, indent=2) + "\n"


def static_index(name: str, kitdir: str, jsonfile: str) -> str:
    return f'''<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{name}</title>
    <link rel="stylesheet" href="{kitdir}/netkit-web.css" />
    <!-- fontes do jogo (opcional): Rajdhani + Orbitron -->
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap" />
  </head>
  <body>
    <netsites src="{jsonfile}"></netsites>
    <script src="{kitdir}/netkit-web.standalone.js" defer></script>
  </body>
</html>
'''


BEGIN = "<!-- netkit:begin -->"
END = "<!-- netkit:end -->"


def write_if_changed(path: Path, content: str, force: bool) -> str:
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if current == content:
            return "igual"
        if not force:
            raise NetkitError(f"o ficheiro {path} já existe e é diferente — use --force para substituir")
        path.write_text(content, encoding="utf-8", newline="\n")
        return "substituído"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return "criado"


def cmd_inject(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"Erro: {target} não existe — Solução: crie a pasta do site primeiro", file=sys.stderr)
        return 2
    flavor = args.flavor
    name = args.name or "MeuSite"
    fonts = args.fonts
    dry = args.dry_run

    if flavor == "react":
        base = target / "src" if (target / "src").is_dir() else target
        kit = base / "netkit"
        sites = base / "sites"
        files = REACT_FILES
    else:
        base = target
        kit = target / "netkit"
        sites = target
        files = STANDALONE_FILES

    plan = []
    for name_file in files:
        source = kit_file(name_file)
        plan.append((source, kit / name_file))
    manifest = {
        "kit": "netkit-web",
        "version": VERSION,
        "flavor": flavor,
        "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": {name_file: sha256(kit_file(name_file)) for name_file in files},
    }
    plan.append((None, kit / "manifest.json"))

    if dry:
        for _source, dest in plan:
            print(f"LIGARIA {dest}")
        return 0

    changed = 0
    kit.mkdir(parents=True, exist_ok=True)
    for source, dest in plan:
        if source is None:
            state = write_if_changed(dest, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", force=True)
        else:
            content = source.read_text(encoding="utf-8")
            state = write_if_changed(dest, content, force=args.force)
        if state != "igual":
            changed += 1
            print(f"{state:>12}  {dest}")

    if flavor == "react":
        import_path = os.path.relpath(kit / "netkit-web.js", sites).replace(os.sep, "/")
        css_path = os.path.relpath(kit / "netkit-web.css", sites).replace(os.sep, "/")
        if not import_path.startswith("."):
            import_path = "./" + import_path
        if not css_path.startswith("."):
            css_path = "./" + css_path
        starter = sites / f"{name}.jsx"
        if args.new_site and not starter.exists():
            write_if_changed(starter, starter_jsx(name, import_path, css_path), force=False)
            print(f"     criado  {starter}")
        print("\nPróximos passos (React):")
        print(f"  1. importe o CSS uma vez no arranque:  import \"{css_path}\"")
        print(f"  2. escreva a página:                   {import_path}")
        print(f"  3. valide:                             python scripts/netkit.py check {sites}")
    else:
        json_file = kit / "site.json"
        write_if_changed(json_file, site_json(name, f"{name.lower()}.web", "net"), force=args.force)
        index = target / "index.html"
        if index.exists():
            text = index.read_text(encoding="utf-8")
            snippet = (
                f"{BEGIN}\n"
                f'<link rel="stylesheet" href="netkit/netkit-web.css" />\n'
                f'<netsites src="netkit/site.json"></netsites>\n'
                f'<script src="netkit/netkit-web.standalone.js" defer></script>\n'
                f"{END}\n"
            )
            if BEGIN in text and END in text:
                text = re.sub(
                    re.escape(BEGIN) + r".*?" + re.escape(END),
                    lambda _m: snippet.rstrip("\n"),
                    text,
                    flags=re.S,
                )
            elif "</body>" in text:
                text = text.replace("</body>", snippet + "  </body>")
            else:
                text += "\n" + snippet
            index.write_text(text, encoding="utf-8", newline="\n")
            print(f"  atualizado  {index} (bloco netkit)")
        else:
            write_if_changed(index, static_index(name, "netkit", "netkit/site.json"), force=False)
            print(f"     criado  {index}")
        print("\nPróximos passos (estático):")
        print(f"  1. abra {index} num servidor local (não file://) ou use `netkit.py preview {json_file}`")
        print(f"  2. edite {json_file} (formato netsites-site/1) e recarregue")
        print(f"  3. valide: python scripts/netkit.py check {json_file}")

    print(f"\nkit {VERSION} · {flavor} · {changed} ficheiro(s) escrito(s) em {kit}")
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    target = Path(args.dir).resolve()
    name = args.name
    if not re.match(r"^[A-Z][A-Za-z0-9]*$", name):
        print("Erro: o nome tem de começar por maiúscula e não ter espaços — Solução: Noticias, Afterlife", file=sys.stderr)
        return 2
    target.mkdir(parents=True, exist_ok=True)
    if args.flavor == "react":
        kit = Path(args.kit or (target.parent / "netkit")).resolve()
        import_path = os.path.relpath(kit / "netkit-web.js", target).replace(os.sep, "/")
        css_path = os.path.relpath(kit / "netkit-web.css", target).replace(os.sep, "/")
        if not import_path.startswith("."):
            import_path = "./" + import_path
        if not css_path.startswith("."):
            css_path = "./" + css_path
        dest = target / f"{name}.jsx"
        state = write_if_changed(dest, starter_jsx(name, import_path, css_path), args.force)
        print(f"{state:>12}  {dest}")
    else:
        dest = target / f"{name}.json"
        theme = args.theme or "net"
        state = write_if_changed(dest, site_json(name, f"{name.lower()}.web", theme), args.force)
        print(f"{state:>12}  {dest}")
        print(f"Abra com: python scripts/netkit.py preview {dest}")
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    path = Path(args.site).resolve()
    if not path.exists():
        print(f"Erro: {path} não existe — Solução: indique um site.json", file=sys.stderr)
        return 2
    base = path if path.is_dir() else path.parent
    site_file = path.name if path.is_file() else None
    if site_file is None:
        candidates = sorted(base.glob("*.json"))
        if not candidates:
            print(f"Erro: sem .json em {base} — Solução: crie um com `netkit.py new`", file=sys.stderr)
            return 2
        site_file = candidates[0].name
    js = (STANDALONE_DIR / "netkit-web.standalone.js").read_text(encoding="utf-8")
    css = (KIT_DIR / "netkit-web.css").read_text(encoding="utf-8")
    page_html = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>pré-visualização · {site_file}</title>
<link rel="stylesheet" href="/__netkit_css__" />
</head>
<body>
<netsites src="/{site_file}"></netsites>
<script src="/__netkit_js__"></script>
</body>
</html>
'''

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (API do http.server)
            if self.path.startswith("/__netkit_preview__"):
                body = page_html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if self.path.startswith("/__netkit_js__"):
                body = js.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/javascript; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if self.path.startswith("/__netkit_css__"):
                body = css.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/css; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            super().do_GET()

        def log_message(self, *args):  # silencia o log por pedido
            return

    handler = functools.partial(Handler, directory=str(base))
    port = args.port
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/__netkit_preview__"
    print(f"pré-visualização em {url}  (Ctrl+C termina)")
    if args.open:
        import webbrowser
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nfim")
    finally:
        server.server_close()
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    tokens = css_tokens()
    if args.what == "components":
        for name, spec in COMPONENTS.items():
            req = ", ".join(spec["required"]) or "—"
            print(f"{name:<12} props: {', '.join(spec['props'])}")
            print(f"{'':<12} obrigatórias: {req}")
        return 0
    if args.what == "tokens":
        print("cores permitidas (fonte: netkit-web.css, bloco NETKIT:TOKENS):")
        for color in tokens["colors"]:
            print(f"  {color}")
        print("\ntemas: " + ", ".join(THEMES))
        print("tamanhos: " + ", ".join(str(s) for s in SIZES))
        print("espaços: " + ", ".join(str(s) for s in SPACES))
        print("bordas: " + ", ".join(str(s) for s in BORDERS))
        print("fontes: " + ", ".join(FONTS))
        print("pesos: " + ", ".join(WEIGHTS))
        return 0
    print(f"NETKIT/WEB v{VERSION}")
    print(f"  temas: {', '.join(THEMES)}")
    print(f"  nós do formato: {', '.join(PROPS_BY_TYPE)}")
    print(f"  componentes: {len(COMPONENTS)} (netkit.py list components)")
    print(f"  tamanhos de texto: {len(SIZES)} · espaços: {len(SPACES)} · cores: {len(tokens['colors'])}")
    print("\n  inject · verify · check · new · preview · build · version")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="netkit.py",
        description="NETKIT/WEB — kit de sites no padrão visual do mod NetSites.",
        epilog="Exemplos: netkit.py inject --target ~/site --name Noticias · netkit.py check src/sites · netkit.py preview site.json",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="valida o contrato visual de um site")
    p_check.add_argument("paths", nargs="+", help="ficheiros ou pastas (.jsx, .tsx, .html, .json)")
    p_check.add_argument("--json", action="store_true", help="saída JSON")
    p_check.set_defaults(func=cmd_check)

    p_inject = sub.add_parser("inject", help="injeta o kit num site")
    p_inject.add_argument("--target", required=True, help="pasta do site")
    p_inject.add_argument("--flavor", choices=["react", "static"], default="react")
    p_inject.add_argument("--name", default="MeuSite", help="nome do site/página de arranque")
    p_inject.add_argument("--fonts", action="store_true", help="(estático) acrescenta as fontes Rajdhani/Orbitron do Google")
    p_inject.add_argument("--new-site", action="store_true", help="(react) cria também src/sites/<Nome>.jsx")
    p_inject.add_argument("--force", action="store_true", help="substitui ficheiros do kit existentes")
    p_inject.add_argument("--dry-run", action="store_true")
    p_inject.set_defaults(func=cmd_inject)

    p_verify = sub.add_parser("verify", help="confere o kit ou uma cópia instalada")
    p_verify.add_argument("--target", help="pasta do site com manifesto do kit")
    p_verify.set_defaults(func=cmd_verify)

    p_new = sub.add_parser("new", help="cria uma página de arranque ou um site.json")
    p_new.add_argument("--dir", required=True)
    p_new.add_argument("--name", required=True)
    p_new.add_argument("--flavor", choices=["react", "static"], default="react")
    p_new.add_argument("--theme", choices=THEMES, default="net")
    p_new.add_argument("--kit", help="(react) pasta do kit para calcular o import")
    p_new.add_argument("--force", action="store_true")
    p_new.set_defaults(func=cmd_new)

    p_preview = sub.add_parser("preview", help="serve um site.json localmente")
    p_preview.add_argument("site")
    p_preview.add_argument("--port", type=int, default=8787)
    p_preview.add_argument("--no-open", dest="open", action="store_false")
    p_preview.set_defaults(func=cmd_preview, open=True)

    p_list = sub.add_parser("list", help="inventário fechado do kit")
    p_list.add_argument("what", nargs="?", choices=["all", "components", "tokens"], default="all")
    p_list.set_defaults(func=cmd_list)

    p_build = sub.add_parser("build", help="sincroniza a CSS embutida no standalone")
    p_build.set_defaults(func=cmd_build)

    p_version = sub.add_parser("version")
    p_version.set_defaults(func=lambda _a: (print(f"netkit-web {VERSION}"), 0)[1])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except NetkitError as exc:
        print(f"Erro: {exc} — Solução: siga a indicação do erro", file=sys.stderr)
        return 2
    except SystemExit as exc:
        return int(exc.code or 0)


if __name__ == "__main__":
    sys.exit(main())
