"""Testes do netkit.py e do kit (contrato visual, injeção, verificação, build)."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "scripts" / "netkit.py"

spec = importlib.util.spec_from_file_location("netkit", MODULE)
netkit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(netkit)


def quiet(function, *args, **kwargs):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(io.StringIO()):
        try:
            code = function(*args, **kwargs)
        except netkit.NetkitError as exc:
            print(str(exc), file=buffer)
            code = 2
    return code, buffer.getvalue()


class TokensTest(unittest.TestCase):
    def test_paleta_sai_do_css(self):
        tokens = netkit.css_tokens()
        self.assertGreaterEqual(len(tokens["colors"]), 30)
        for color in ("#5ef6ff", "#0e0e17", "#f2efe8", "#ff2fd0", "#2a3a46", "#ffffff"):
            self.assertIn(color, tokens["colors"])

    def test_cores_legais(self):
        colors = netkit.css_tokens()["colors"]
        self.assertTrue(netkit.legal_color("var(--nk-accent)", colors))
        self.assertTrue(netkit.legal_color("#5ef6ff", colors))
        self.assertTrue(netkit.legal_color("#2a3a4600", colors))
        self.assertTrue(netkit.legal_color("transparent", colors))
        self.assertFalse(netkit.legal_color("#ff0000", colors))
        self.assertFalse(netkit.legal_color("rgb(255,0,0)", colors))
        self.assertFalse(netkit.legal_color("red", colors))

    def test_css_sem_perigo_de_template_literal(self):
        css = (ROOT / "assets/netkit-web/netkit-web.css").read_text(encoding="utf-8")
        self.assertNotIn("`", css)
        self.assertNotIn("${", css)

    def test_css_embutida_igual_a_origem(self):
        css = (ROOT / "assets/netkit-web/netkit-web.css").read_text(encoding="utf-8")
        standalone = (ROOT / "assets/standalone/netkit-web.standalone.js").read_text(encoding="utf-8")
        embedded = netkit.extract_between(standalone, "/* NETKIT:CSS:BEGIN */", "/* NETKIT:CSS:END */")
        self.assertEqual(embedded.strip(), css.strip())


class VersionsTest(unittest.TestCase):
    def test_versoes_coerentes(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        js = (ROOT / "assets/netkit-web/netkit-web.js").read_text(encoding="utf-8")
        standalone = (ROOT / "assets/standalone/netkit-web.standalone.js").read_text(encoding="utf-8")
        self.assertEqual(package["version"], netkit.VERSION)
        self.assertIn(f'VERSION = "{netkit.VERSION}"', js)
        self.assertIn(f'VERSION = "{netkit.VERSION}"', standalone)

    def test_dts_declara_os_exports(self):
        js = (ROOT / "assets/netkit-web/netkit-web.js").read_text(encoding="utf-8")
        dts = (ROOT / "assets/netkit-web/netkit-web.d.ts").read_text(encoding="utf-8")
        exported = set(re.findall(r"^export (?:function|const) ([A-Za-z_]\w*)", js, re.M))
        declared = set(re.findall(r"^  export (?:function|const) ([A-Za-z_]\w*)", dts, re.M))
        self.assertEqual(exported - declared, set())
        self.assertIn("Site", exported)


class CheckJsxTest(unittest.TestCase):
    def run_check(self, text: str) -> netkit.Report:
        report = netkit.Report()
        path = Path("Teste.jsx")
        netkit.check_jsx(path, text, report, netkit.css_tokens())
        return report

    def test_arranque_do_kit_passa(self):
        text = netkit.starter_jsx("Noticias", "../netkit/netkit-web.js", "../netkit/netkit-web.css")
        report = self.run_check(text)
        self.assertEqual([(i["line"], i["message"]) for i in report.errors], [])
        self.assertIn("<Site", text)

    def test_html_e_estilo_proibidos(self):
        text = """import { Site, Page } from "../netkit/netkit-web.js"
export default function X() {
  return (
    <Site id="x" title="X" domain="x.web">
      <Page id="index">
        <div style={{ color: "red" }}>olá</div>
      </Page>
    </Site>
  )
}
"""
        report = self.run_check(text)
        messages = " | ".join(i["message"] for i in report.errors)
        self.assertIn("style=", messages)
        self.assertIn("<div>", messages)

    def test_tamanho_cor_e_ligacao(self):
        text = """import { Site, Page, Text } from "../netkit/netkit-web.js"
export default function X() {
  return (
    <Site id="x" title="X" domain="x.web">
      <Page id="index">
        <Text size={47} color="#ff0000" link="naoexiste">a</Text>
      </Page>
    </Site>
  )
}
"""
        report = self.run_check(text)
        messages = " | ".join(i["message"] for i in report.errors)
        self.assertIn("tamanho 47", messages)
        self.assertIn("#ff0000", messages)
        self.assertIn("naoexiste", messages)

    def test_props_desconhecidas_e_tema(self):
        text = """import { Site, Page, Text } from "../netkit/netkit-web.js"
export default function X() {
  return (
    <Site id="x" title="X" domain="x.web" theme="vaporwave">
      <Page id="index">
        <Text tamanho={46} color="var(--nk-accent)">a</Text>
      </Page>
    </Site>
  )
}
"""
        report = self.run_check(text)
        messages = " | ".join(i["message"] for i in report.errors)
        self.assertIn("tamanho", messages)
        self.assertIn("vaporwave", messages)

    def test_componente_local_e_permitido(self):
        text = """import { Site, Page, Text, Column } from "../netkit/netkit-web.js"
function Aviso({ children }) {
  return <Column gap={20}><Text size={46}>{children}</Text></Column>
}
export default function X() {
  return (
    <Site id="x" title="X" domain="x.web">
      <Page id="index"><Aviso>olá</Aviso></Page>
    </Site>
  )
}
"""
        report = self.run_check(text)
        self.assertEqual([i["message"] for i in report.errors], [])

    def test_esquemas_de_url_sao_enderecos(self):
        for target in ("mailto:ola@neon.web", "tel:+351900000000", "https://exemplo.com", "NETdir://ncity.pub"):
            text = f"""import {{ Site, Page, Button }} from "../netkit/netkit-web.js"
export default function X() {{
  return (
    <Site id="x" title="X" domain="x.web">
      <Page id="index"><Button label="Ir" to="{target}" /></Page>
    </Site>
  )
}}
"""
            report = self.run_check(text)
            self.assertEqual([i["message"] for i in report.errors], [], target)

    def test_texto_dentro_de_texto_e_recusado(self):
        text = """import { Site, Page, Text } from "../netkit/netkit-web.js"
export default function X() {
  return (
    <Site id="x" title="X" domain="x.web">
      <Page id="index">
        <Text size={46}>Olá <Text size={46} color="var(--nk-accent)">mundo</Text></Text>
      </Page>
    </Site>
  )
}
"""
        report = self.run_check(text)
        messages = " | ".join(i["message"] for i in report.errors)
        self.assertIn("dentro de <Text>", messages)


class CheckJsonTest(unittest.TestCase):
    def check(self, spec: dict) -> netkit.Report:
        report = netkit.Report()
        netkit.check_json(Path("site.json"), json.dumps(spec), report, netkit.css_tokens())
        return report

    def test_site_do_template_passa(self):
        spec = json.loads(netkit.site_json("Teste", "teste.web", "net"))
        report = self.check(spec)
        self.assertEqual([i["message"] for i in report.errors], [])

    def test_erros_de_formato(self):
        spec = json.loads(netkit.site_json("Teste", "teste.web", "net"))
        spec["domain"] = "Ncity"
        spec["pages"][0]["address"] = "NETdir://outro.web"
        spec["pages"][0]["root"]["children"][0]["props"]["color"] = "#ff0000"
        spec["pages"][0]["root"]["children"][0]["props"]["size"] = 47
        spec["pages"][1]["root"]["children"][0]["children"] = [{"type": "text", "props": {"text": "x"}}]
        report = self.check(spec)
        messages = " | ".join(i["message"] for i in report.errors)
        for needle in ("domain", "fora do domínio", "#ff0000", "tamanho 47", "não pode ter filhos"):
            self.assertIn(needle, messages)

    def test_link_para_pagina_posterior(self):
        spec = json.loads(netkit.site_json("Teste", "teste.web", "net"))
        spec["pages"][0]["root"]["children"][4]["props"]["link"] = "sobre"
        report = self.check(spec)
        self.assertEqual([i["message"] for i in report.errors], [])

    def test_schema_e_home(self):
        spec = {"schema": "outra/1", "id": "X", "domain": "x.web", "title": "", "home": "nada", "pages": []}
        report = self.check(spec)
        messages = " | ".join(i["message"] for i in report.errors)
        self.assertIn("netsites-site/1", messages)
        self.assertIn("não tem páginas", messages)


class InjectTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="netkit-test-"))
        self.site = self.tmp / "site"
        self.site.mkdir()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def inject(self, site: Path, flavor: str = "react", **extra):
        args = Namespace(
            target=str(site),
            flavor=flavor,
            name="MeuSite",
            fonts=False,
            new_site=True,
            force=False,
            dry_run=False,
        )
        for key, value in extra.items():
            setattr(args, key, value)
        return quiet(netkit.cmd_inject, args)

    def test_react_injeta_e_verifica(self):
        code, out = self.inject(self.site)
        self.assertEqual(code, 0, out)
        self.assertTrue((self.site / "netkit" / "netkit-web.js").exists())
        self.assertTrue((self.site / "netkit" / "netkit-web.css").exists())
        self.assertTrue((self.site / "netkit" / "manifest.json").exists())
        manifest = json.loads((self.site / "netkit" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], netkit.VERSION)
        self.assertEqual(len(manifest["files"]), 3)
        code, out = quiet(netkit.cmd_verify, Namespace(target=str(self.site)))
        self.assertEqual(code, 0, out)

    def test_react_starter_passa_no_check(self):
        self.inject(self.site)
        code, _ = quiet(netkit.cmd_check, Namespace(paths=[str(self.site / "sites")], json=False))
        self.assertEqual(code, 0)

    def test_estatico_patcha_o_index_e_e_idempotente(self):
        (self.site / "index.html").write_text(
            "<!doctype html>\n<html><head><title>x</title></head><body></body></html>\n", encoding="utf-8"
        )
        self.inject(self.site, flavor="static")
        self.inject(self.site, flavor="static")
        html = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count(netkit.BEGIN), 1)
        self.assertIn("netkit-web.standalone.js", html)
        self.assertIn("netsites", html)
        code, out = quiet(netkit.cmd_check, Namespace(paths=[str(self.site)], json=False))
        self.assertEqual(code, 0, out)

    def test_kit_adulterado_falha_a_verificacao(self):
        self.inject(self.site)
        target = self.site / "netkit" / "netkit-web.css"
        target.write_text(target.read_text(encoding="utf-8") + "\n/* hack */\n", encoding="utf-8")
        code, out = quiet(netkit.cmd_verify, Namespace(target=str(self.site)))
        self.assertEqual(code, 1)
        self.assertIn("ALTERADO", out)

    def test_sem_forcar_nao_sobrescreve(self):
        self.inject(self.site)
        target = self.site / "netkit" / "netkit-web.js"
        target.write_text("// mexido\n", encoding="utf-8")
        code, out = self.inject(self.site)
        self.assertEqual(code, 2)
        self.assertIn("já existe", out)

    def test_dry_run_nao_escreve(self):
        code, out = self.inject(self.site, dry_run=True)
        self.assertEqual(code, 0)
        self.assertIn("LIGARIA", out)
        self.assertFalse((self.site / "netkit").exists())


class NewAndBuildTest(unittest.TestCase):
    def test_new_react_passa_no_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = Namespace(
                dir=tmp, name="Afterlife", flavor="react", theme="net",
                kit=str(ROOT / "assets" / "netkit-web"), force=False,
            )
            code, out = quiet(netkit.cmd_new, args)
            self.assertEqual(code, 0, out)
            code, _ = quiet(netkit.cmd_check, Namespace(paths=[tmp], json=False))
            self.assertEqual(code, 0)

    def test_new_estatico_passa_no_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = Namespace(dir=tmp, name="Kabuki", flavor="static", theme="tabloid", kit=None, force=False)
            code, out = quiet(netkit.cmd_new, args)
            self.assertEqual(code, 0, out)
            code, _ = quiet(netkit.cmd_check, Namespace(paths=[tmp], json=False))
            self.assertEqual(code, 0)

    def test_build_e_verificacao_do_kit(self):
        code, out = quiet(netkit.cmd_build, Namespace())
        self.assertEqual(code, 0, out)
        code, out = quiet(netkit.cmd_verify, Namespace(target=None))
        self.assertEqual(code, 0, out)
        self.assertIn("kit OK", out)

    def test_check_json_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "site.json"
            path.write_text(netkit.site_json("Teste", "teste.web", "net"), encoding="utf-8")
            code, out = quiet(netkit.cmd_check, Namespace(paths=[str(path)], json=True))
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertTrue(data["ok"])


class PrintsTest(unittest.TestCase):
    """As capturas são parte da entrega: existem e as páginas de origem também."""

    def setUp(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("prints", ROOT / "scripts" / "prints.py")
        self.prints = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(self.prints)

    def test_paginas_de_origem_existem(self):
        for shot in self.prints.SHOTS:
            self.assertTrue((ROOT / "docs" / "prints" / "src" / shot["page"]).exists(), shot["page"])

    def test_capturas_existem(self):
        missing = [s["name"] for s in self.prints.SHOTS if not (ROOT / "docs" / "prints" / f"{s['name']}.png").exists()]
        self.assertEqual(missing, [], f"capturas em falta: {missing} — corra python3 scripts/prints.py --shots")

    def test_lista(self):
        code, out = quiet(self.prints.main, ["--list"])
        self.assertEqual(code, 0)
        self.assertIn("01-temas", out)
        self.assertIn("og", out)


class CliTest(unittest.TestCase):
    def test_version(self):
        code, out = quiet(netkit.main, ["version"])
        self.assertEqual(code, 0)
        self.assertIn(netkit.VERSION, out)

    def test_lista_de_componentes(self):
        code, out = quiet(netkit.main, ["list", "components"])
        self.assertEqual(code, 0)
        self.assertIn("Site", out)
        self.assertIn("ProductCard", out)

    def test_ficheiro_inexistente(self):
        code, _ = quiet(netkit.main, ["check", "nao_existe_este_ficheiro.jsx"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
