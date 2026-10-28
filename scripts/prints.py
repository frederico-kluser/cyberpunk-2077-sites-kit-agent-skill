#!/usr/bin/env python3
"""prints.py — gera as capturas do kit (docs/prints/*.png) com um browser headless.

O que faz (nesta ordem):

  1. fonts — descarrega as fontes OFL (Rajdhani + Orbitron) para docs/prints/src/fonts,
     se ainda não estiverem lá, para os prints serem iguais em qualquer máquina;
  2. art   — desenha a arte abstrata de apoio (docs/prints/src/art/*.jpg) com Pillow,
     determinística (seed fixa): nada de imagens de terceiros no repositório;
  3. shots — serve o repositório em 127.0.0.1 e fotografa cada página de
     docs/prints/src/*.html nas medidas de SHOTS, escrevendo docs/prints/<nome>.png.

Uso:
  python3 scripts/prints.py              # tudo
  python3 scripts/prints.py --shots      # só as capturas (usa a arte já gerada)
  python3 scripts/prints.py --art        # só arte + fontes
  python3 scripts/prints.py --check      # confere que as capturas existem (não escreve)
  python3 scripts/prints.py --list       # lista as capturas e as medidas

Browser: variável NETKIT_BROWSER, ou o primeiro Chrome/Edge/Chromium encontrado.
Erros: `Erro: <o quê> — Solução: <o que fazer>` em stderr.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import os
import random
import shutil
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRINTS = ROOT / "docs" / "prints"
SRC = PRINTS / "src"
ART = SRC / "art"
FONTS = SRC / "fonts"

#: nome do ficheiro (sem .png), página de origem e tamanho da janela em px
SHOTS = [
    {"name": "01-temas", "page": "temas.html", "size": (1440, 640)},
    {"name": "02-noticia-tabloid", "page": "noticia.html", "size": (1440, 1250)},
    {"name": "03-loja-street", "page": "loja.html", "size": (1440, 1210)},
    {"name": "04-portfolio-neon", "page": "portfolio.html", "size": (1440, 1210)},
    {"name": "05-componentes", "page": "componentes.html", "size": (1440, 2260)},
    {"name": "06-noticia-mobile", "page": "noticia.html", "size": (390, 1250)},
    {"name": "07-standalone-json", "page": "json.html", "size": (1440, 900)},
    {"name": "og", "page": "og.html", "size": (1280, 640)},
]

FONT_CSS = "https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@700;900&display=swap"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


# --------------------------------------------------------------------------- browser

def find_browser() -> str:
    env = os.environ.get("NETKIT_BROWSER")
    if env and Path(env).exists():
        return env
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit(
        "Erro: browser headless não encontrado — Solução: instale Chrome/Chromium ou defina NETKIT_BROWSER"
    )


# --------------------------------------------------------------------------- fonts

def download_fonts() -> None:
    FONTS.mkdir(parents=True, exist_ok=True)
    if any(FONTS.glob("*.woff2")):
        print("fonts: já existem (não descarrego de novo)")
        return
    request = urllib.request.Request(FONT_CSS, headers={"User-Agent": UA})
    try:
        css = urllib.request.urlopen(request, timeout=30).read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001 — rede é externa
        raise SystemExit(f"Erro: não consegui ler o CSS das fontes ({exc}) — Solução: corra com rede ou copie fonts/ de outro checkout") from exc

    blocks = css.split("@font-face")
    seen: dict[tuple[str, str], str] = {}
    for block in blocks[1:]:
        if "/* latin */" not in block.split("@font-face")[0] and "U+0000-00FF" not in block:
            continue
        family = block.split("font-family:", 1)[1].split(";", 1)[0].strip().strip("'\"")
        weight = block.split("font-weight:", 1)[1].split(";", 1)[0].strip()
        url = block.split("url(", 1)[1].split(")", 1)[0].strip().strip("'\"")
        seen.setdefault((family, weight), url)

    for (family, _weight), url in seen.items():
        target = FONTS / f"{family.lower()}-{_weight}.woff2"
        if target.exists():
            continue
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()
        target.write_bytes(data)
        print(f"fonts: {target.name} ({len(data)} bytes)")

    for family, licence in (("rajdhani", "rajdhani"), ("orbitron", "orbitron")):
        target = FONTS / f"OFL-{family}.txt"
        if target.exists():
            continue
        url = f"https://raw.githubusercontent.com/google/fonts/main/ofl/{licence}/OFL.txt"
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()
        except Exception:  # noqa: BLE001 — licença é obrigatória; falha alto
            raise SystemExit(f"Erro: não consegui descarregar a OFL de {family} — Solução: copie o OFL do checkout das fontes")
        target.write_bytes(data)
        print(f"fonts: {target.name}")


# --------------------------------------------------------------------------- arte

def _hex(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _canvas(width: int, height: int, color: str):
    from PIL import Image

    return Image.new("RGB", (width, height), _hex(color))


def _glow(img, box, color: str, blur: int, alpha: int):
    """Luz aditiva (screen): a zona do ellipse clareia, o resto fica igual."""
    from PIL import Image, ImageChops, ImageDraw, ImageFilter

    layer = Image.new("RGB", img.size, (0, 0, 0))
    ImageDraw.Draw(layer).ellipse(box, fill=_hex(color))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    layer = layer.point(lambda v: int(v * alpha / 255))
    return ImageChops.screen(img, layer)


def _grain(img, amount: int, seed: int):
    from PIL import Image

    rng = random.Random(seed)
    noise = Image.new("L", img.size)
    noise.putdata([rng.randint(0, amount) for _ in range(img.size[0] * img.size[1])])
    return Image.blend(img, Image.merge("RGB", (noise, noise, noise)), 0.06)


def _vignette(img, strength: float = 0.35):
    from PIL import Image, ImageDraw, ImageFilter

    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (-img.size[0] * 0.15, -img.size[1] * 0.25, img.size[0] * 1.15, img.size[1] * 1.25),
        fill=int(255 * (1 - strength)),
    )
    mask = mask.filter(ImageFilter.GaussianBlur(120))
    black = Image.new("RGB", img.size, (0, 0, 0))
    return Image.composite(img, black, mask)


def art_city_paper() -> None:
    from PIL import ImageDraw

    img = _canvas(1600, 900, "#c9c4b8")
    grad = ImageDraw.Draw(img)
    for y in range(520):
        tone = int(201 - (y / 520) * 46)
        grad.line([(0, y), (1600, y)], fill=(tone, tone - 4, tone - 12))
    draw = ImageDraw.Draw(img)
    rng = random.Random(2077)
    for depth, (color, base) in enumerate((("#b3ada0", 620), ("#6f6a61", 700), ("#1a1a1a", 790))):
        x = -60
        while x < 1660:
            w = rng.randint(40, 130) + depth * 10
            top = base - rng.randint(60, 320) - depth * 40
            draw.rectangle([x, top, x + w, 900], fill=_hex(color))
            for wy in range(top + 30, 880, 42):
                for wx in range(x + 14, x + w - 16, 34):
                    if rng.random() < 0.28:
                        draw.rectangle([wx, wy, wx + 12, wy + 18], fill=_hex("#d6d0c4"))
            x += w + rng.randint(6, 26)
    draw.rectangle([900, 250, 1400, 290], fill=_hex("#c8102e"))
    draw.rectangle([1180, 150, 1204, 420], fill=_hex("#1a1a1a"))
    img = _vignette(img, 0.5)
    _grain(img, 90, 3).save(ART / "cidade_papel.jpg", quality=86, optimize=True)


def art_city_net() -> None:
    from PIL import ImageDraw

    img = _canvas(1600, 900, "#0e0e17")
    draw = ImageDraw.Draw(img)
    rng = random.Random(77)
    img = _glow(img, (80, 240, 1050, 860), "#24515f", 140, 240)
    for depth, (color, base) in enumerate((("#141b24", 640), ("#18222c", 720), ("#0a0d13", 830))):
        x = -40
        while x < 1640:
            w = rng.randint(50, 150)
            top = base - rng.randint(90, 380)
            draw.rectangle([x, top, x + w, 900], fill=_hex(color))
            for wy in range(top + 26, 890, 36):
                for wx in range(x + 12, x + w - 14, 28):
                    if rng.random() < 0.42:
                        draw.rectangle([wx, wy, wx + 10, wy + 14], fill=_hex("#5ef6ff"))
            x += w + rng.randint(8, 30)
    draw.rectangle([240, 300, 660, 330], fill=_hex("#ff6159"))
    draw.rectangle([980, 210, 1010, 520], fill=_hex("#5ef6ff"))
    img = _glow(img, (-200, 500, 1800, 1100), "#16212c", 200, 90)
    img = _vignette(img, 0.45)
    _grain(img, 70, 11).save(ART / "cidade_net.jpg", quality=86, optimize=True)


def art_bar() -> None:
    from PIL import ImageDraw

    img = _canvas(1600, 900, "#121212")
    draw = ImageDraw.Draw(img)
    img = _glow(img, (680, 60, 1560, 780), "#8a7714", 150, 250)
    img = _glow(img, (250, 380, 850, 900), "#3a3208", 170, 150)
    for x in range(60, 1600, 190):
        draw.rectangle([x, 0, x + 8, 900], fill=_hex("#1d1c18"))
    draw.rectangle([980, 200, 1420, 226], fill=_hex("#f3e600"))
    draw.rectangle([1080, 260, 1320, 286], fill=_hex("#ff2a6d"))
    draw.rounded_rectangle([300, 470, 760, 900], radius=18, fill=_hex("#1d1c18"))
    for i, x in enumerate(range(380, 740, 70)):
        height = 120 + (i % 3) * 40
        draw.rectangle([x, 470 - height, x + 34, 470], fill=_hex("#3b3820"))
        draw.rectangle([x + 6, 470 - height + 10, x + 28, 470 - height + 34], fill=_hex("#f3e600"))
    img = _vignette(img, 0.55)
    _grain(img, 80, 5).save(ART / "bar.jpg", quality=86, optimize=True)


def art_stage() -> None:
    from PIL import ImageDraw

    img = _canvas(1600, 900, "#0d0614")
    draw = ImageDraw.Draw(img)
    for i in range(7):
        x = 120 + i * 210
        draw.polygon([(x, 0), (x + 90, 0), (x + 260, 900), (x + 140, 900)], fill=_hex("#1a0d24"))
    img = _glow(img, (240, -160, 760, 620), "#ff2fd0", 150, 220)
    img = _glow(img, (860, -180, 1460, 560), "#5ef6ff", 170, 170)
    img = _glow(img, (420, 420, 1200, 980), "#7a1f7a", 220, 110)
    draw = ImageDraw.Draw(img)
    rng = random.Random(9)
    for i in range(90):
        x = rng.randint(0, 1600)
        h = rng.randint(60, 150)
        draw.ellipse([x, 900 - h, x + 46, 900 + h // 2], fill=_hex("#0a0410"))
    draw.rectangle([0, 760, 1600, 766], fill=_hex("#ff2fd0"))
    img = _vignette(img, 0.5)
    _grain(img, 60, 21).save(ART / "palco.jpg", quality=86, optimize=True)


def art_product(name: str, bg: str, body: str, accent: str, shape: str) -> None:
    from PIL import ImageDraw

    img = _canvas(800, 800, bg)
    img = _glow(img, (80, 60, 720, 700), accent, 150, 70)
    draw = ImageDraw.Draw(img)
    if shape == "jacket":
        draw.polygon([(250, 180), (550, 180), (640, 660), (160, 660)], fill=_hex(body))
        draw.polygon([(250, 180), (400, 330), (550, 180), (470, 660), (330, 660)], fill=_hex("#0d0d0d"))
        draw.rectangle([160, 600, 640, 626], fill=_hex(accent))
    elif shape == "chip":
        draw.rectangle([210, 210, 590, 590], fill=_hex(body))
        for i in range(6):
            draw.rectangle([180, 260 + i * 52, 210, 292 + i * 52], fill=_hex(accent))
            draw.rectangle([590, 260 + i * 52, 620, 292 + i * 52], fill=_hex(accent))
            draw.rectangle([260 + i * 52, 180, 292 + i * 52, 210], fill=_hex(accent))
            draw.rectangle([260 + i * 52, 590, 292 + i * 52, 620], fill=_hex(accent))
        draw.rectangle([330, 330, 470, 470], fill=_hex("#0d0d0d"))
    else:
        draw.ellipse([180, 300, 400, 500], outline=_hex(accent), width=18)
        draw.ellipse([400, 300, 620, 500], outline=_hex(accent), width=18)
        draw.rectangle([390, 380, 410, 420], fill=_hex(accent))
        draw.rectangle([120, 340, 190, 370], fill=_hex(body))
        draw.rectangle([610, 340, 680, 370], fill=_hex(body))
    img = _vignette(img, 0.4)
    _grain(img, 70, 31).save(ART / f"{name}.jpg", quality=86, optimize=True)


def art_portrait() -> None:
    from PIL import ImageDraw

    img = _canvas(800, 800, "#141b24")
    img = _glow(img, (80, 60, 740, 740), "#2a6b7c", 140, 170)
    draw = ImageDraw.Draw(img)
    draw.ellipse([280, 150, 520, 400], fill=_hex("#0a0d13"))
    draw.polygon([(150, 800), (240, 430), (560, 430), (650, 800)], fill=_hex("#0a0d13"))
    draw.rectangle([250, 430, 550, 452], fill=_hex("#5ef6ff"))
    img = _vignette(img, 0.45)
    _grain(img, 60, 41).save(ART / "retrato.jpg", quality=86, optimize=True)



def art_report() -> None:
    """Gráfico abstrato de barras: a imagem do print do caminho JSON (sem React)."""
    from PIL import ImageDraw

    img = _canvas(1600, 900, "#0a0a0a")
    draw = ImageDraw.Draw(img)
    for y in range(0, 900, 90):
        draw.line([(0, y), (1600, y)], fill=_hex("#1b0a09"), width=1)
    bars = [180, 300, 240, 420, 360, 540, 470, 660]
    for index, height in enumerate(bars):
        x = 120 + index * 180
        draw.rectangle([x, 820 - height, x + 120, 820], fill=_hex("#e0312b"))
        draw.rectangle([x, 820 - height, x + 120, 820 - height + 10], fill=_hex("#ff6159"))
    draw.line([(60, 850), (1540, 850)], fill=_hex("#3a1412"), width=6)
    img = _glow(img, (900, 0, 1700, 600), "#3a1412", 200, 120)
    img = _vignette(img, 0.35)
    _grain(img, 50, 51).save(ART / "relatorio.jpg", quality=86, optimize=True)


def build_art() -> None:
    try:
        import PIL  # noqa: F401
    except ImportError:
        raise SystemExit(
            "Erro: Pillow não está instalado — Solução: `pip install pillow` ou use a arte já commitada em docs/prints/src/art"
        ) from None
    ART.mkdir(parents=True, exist_ok=True)
    art_city_paper()
    art_city_net()
    art_bar()
    art_stage()
    art_product("jaqueta", "#1d1c18", "#2b2a22", "#f3e600", "jacket")
    art_product("chip", "#1d1c18", "#232323", "#ff2a6d", "chip")
    art_product("oculos", "#1a0d24", "#241030", "#5ef6ff", "glasses")
    art_portrait()
    art_report()
    total = sum(p.stat().st_size for p in ART.glob("*.jpg"))
    print(f"art: {len(list(ART.glob('*.jpg')))} imagens · {total // 1024} KB")


# --------------------------------------------------------------------------- capturas

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # silencia o log por pedido
        return


def capture(browser: str, url: str, target: Path, size: tuple[int, int]) -> None:
    width, height = size
    profile = Path(os.environ.get("TEMP", "/tmp")) / "netkit-prints-profile"
    command = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--force-device-scale-factor=1",
        f"--user-data-dir={profile}",
        f"--window-size={width},{height}",
        "--virtual-time-budget=6000",
        f"--screenshot={target}",
        url,
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if not target.exists():
        raise SystemExit(
            f"Erro: o browser não escreveu {target.name} — Solução: verifique {browser} (stderr: {result.stderr[-400:]})"
        )


def build_shots(only: str | None = None) -> None:
    browser = find_browser()
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"servidor: http://127.0.0.1:{port}/ · browser: {Path(browser).name}")
    try:
        PRINTS.mkdir(parents=True, exist_ok=True)
        for shot in SHOTS:
            if only and only != shot["name"]:
                continue
            page = SRC / shot["page"]
            if not page.exists():
                raise SystemExit(f"Erro: {page} não existe — Solução: restaure docs/prints/src")
            target = PRINTS / f"{shot['name']}.png"
            url = f"http://127.0.0.1:{port}/docs/prints/src/{shot['page']}"
            capture(browser, url, target, shot["size"])
            print(f"  {shot['name']}.png  {shot['size'][0]}x{shot['size'][1]}  {target.stat().st_size // 1024} KB")
    finally:
        server.shutdown()
        server.server_close()


def check() -> int:
    missing = [s["name"] for s in SHOTS if not (PRINTS / f"{s['name']}.png").exists()]
    if missing:
        print("Erro: capturas em falta: " + ", ".join(missing) + " — Solução: python3 scripts/prints.py --shots")
        return 1
    total = 0
    for shot in SHOTS:
        path = PRINTS / f"{shot['name']}.png"
        size = path.stat().st_size
        total += size
        if size < 4096:
            print(f"Erro: {path.name} tem {size} bytes — Solução: gere de novo (página vazia?)")
            return 1
    try:
        browser = Path(find_browser()).name
    except SystemExit:
        browser = "não encontrado (só --shots precisa de browser)"
    print(f"prints OK: {len(SHOTS)} capturas · {total // 1024} KB · browser: {browser}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prints.py", description="Capturas do kit (browser headless).")
    parser.add_argument("--art", action="store_true", help="só fontes + arte")
    parser.add_argument("--shots", action="store_true", help="só capturas")
    parser.add_argument("--fonts", action="store_true", help="só fontes")
    parser.add_argument("--only", help="gera só uma captura (pelo nome, ex.: 01-temas)")
    parser.add_argument("--check", action="store_true", help="confere as capturas (não escreve)")
    parser.add_argument("--list", action="store_true", help="lista capturas e medidas")
    args = parser.parse_args(argv)

    if args.list:
        for shot in SHOTS:
            print(f"{shot['name']:<22} {shot['page']:<20} {shot['size'][0]}x{shot['size'][1]}")
        return 0
    if args.check:
        return check()
    if args.fonts:
        download_fonts()
        return 0
    if args.art:
        download_fonts()
        build_art()
        return 0
    if args.shots:
        build_shots(args.only)
        return 0
    download_fonts()
    build_art()
    build_shots(args.only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
