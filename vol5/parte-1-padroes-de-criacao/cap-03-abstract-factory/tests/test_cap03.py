import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
HEADER, ROWS = ["item", "qtd"], [["lápis", 3], ["a<b", 5]]


# ---------- ex01 ----------
def test_html_family(load_exercise):
    m = load_exercise("ex01_renderers")
    assert m.html_heading("A & B", 2) == "<h2>A &amp; B</h2>"
    assert m.html_table(HEADER, ROWS) == "<table><tr><th>item</th><th>qtd</th></tr><tr><td>lápis</td><td>3</td></tr><tr><td>a&lt;b</td><td>5</td></tr></table>"
    assert m.html_link('x"y', "http://a?b=1&c=2") == '<a href="http://a?b=1&amp;c=2">x&quot;y</a>'


def test_markdown_family(load_exercise):
    m = load_exercise("ex01_renderers")
    assert m.md_heading("Vendas", 3) == "### Vendas"
    assert m.md_table(HEADER, [["lápis", 3]]) == "| item | qtd |\n| --- | --- |\n| lápis | 3 |"
    assert m.md_link("detalhes", "http://x") == "[detalhes](http://x)"


@pytest.mark.parametrize("bad", [0, 7, -1])
def test_invalid_level(load_exercise, bad):
    m = load_exercise("ex01_renderers")
    for fn in (m.html_heading, m.md_heading):
        with pytest.raises(ValueError, match=f"nível inválido: {bad}"):
            fn("x", bad)


def test_ragged_rows(load_exercise):
    m = load_exercise("ex01_renderers")
    for fn in (m.html_table, m.md_table):
        with pytest.raises(ValueError, match="linha 2 tem 1 colunas, esperado 2"):
            fn(HEADER, [["a", 1], ["b"]])


def test_renderer_and_report(load_exercise):
    m = load_exercise("ex01_renderers")
    assert set(m.RENDERERS) == {"html", "markdown"}
    r = m.make_renderer(" Markdown ")
    assert (r.heading, r.table, r.link) == (m.md_heading, m.md_table, m.md_link)
    with pytest.raises(ValueError) as info:
        m.make_renderer("latex")
    assert str(info.value) == "família desconhecida: 'latex'; disponíveis: html, markdown"
    report = m.render_report(r, "Vendas", HEADER, [["lápis", 3]], "http://x")
    assert report == "# Vendas\n\n| item | qtd |\n| --- | --- |\n| lápis | 3 |\n\n[detalhes](http://x)"
    assert m.render_report(m.make_renderer("html"), "T", HEADER, [], "u").startswith("<h1>T</h1>\n\n<table>")
    with pytest.raises(TypeError):
        m.Renderer(m.html_heading, m.html_table)


# ---------- ex02 ----------
def f2(a, b):
    ...


def g2(x, y):
    ...


def h1(a):
    ...


def test_check_families_ok(load_exercise):
    m = load_exercise("ex02_family_check")
    assert m.check_families({}) == []
    assert m.check_families({"a": {"p": f2}}) == []
    assert m.check_families({"a": {"p": f2, "q": h1}, "b": {"p": f2, "q": h1}}) == []


def test_check_families_problems(load_exercise):
    m = load_exercise("ex02_family_check")
    families = {
        "html": {"heading": f2, "table": f2, "link": f2},
        "md": {"heading": g2, "link": f2, "code": h1},
        "tex": {"heading": f2, "table": "nao", "link": f2, "zeta": f2},
    }
    assert m.check_families(families) == [
        "md: falta 'table'",
        "md: produto extra 'code'",
        "md: 'heading' tem parâmetros (x, y), esperado (a, b)",
        "tex: produto extra 'zeta'",
        "tex: 'table' não é chamável",
    ]


# ---------- ex03 ----------
def test_family_for_and_join(load_exercise):
    import ntpath
    import posixpath
    m = load_exercise("ex03_stdlib_family")
    assert m.family_for("POSIX") is posixpath and m.family_for("nt") is ntpath
    with pytest.raises(ValueError, match="sistema desconhecido: 'mac'"):
        m.family_for("mac")
    assert m.portable_join("posix", "a", "b", "c") == "a/b/c"
    assert m.portable_join("nt", "a", "b") == "a\\b"
    with pytest.raises(ValueError, match="sem partes"):
        m.portable_join("nt")


def test_describe_and_same_file(load_exercise):
    m = load_exercise("ex03_stdlib_family")
    assert m.describe("posix") == {"sep": "/", "case_sensitive": True, "has_drive": False}
    assert m.describe("nt") == {"sep": "\\", "case_sensitive": False, "has_drive": True}
    assert m.same_file("nt", "C:/A/../B", "c:\\b") is True
    assert m.same_file("posix", "/a/../b", "/b") is True
    assert m.same_file("posix", "/B", "/b") is False
    assert m.same_file("nt", "/B", "/b") is True


# ---------- ex04 ----------
FAMILIES = {"html": {"heading": 1, "link": 2}, "md": {"heading": 3, "link": 4}}


def test_extend_families(load_exercise):
    m = load_exercise("ex04_extend_family")
    new = m.extend_families(FAMILIES, "code", {"html": "H", "md": "M"})
    assert new == {"html": {"heading": 1, "link": 2, "code": "H"}, "md": {"heading": 3, "link": 4, "code": "M"}}
    assert list(new) == ["html", "md"]
    assert FAMILIES == {"html": {"heading": 1, "link": 2}, "md": {"heading": 3, "link": 4}}


def test_extend_families_errors(load_exercise):
    m = load_exercise("ex04_extend_family")
    with pytest.raises(ValueError, match="produto já existe: 'link'"):
        m.extend_families(FAMILIES, "link", {"html": 1, "md": 1})
    with pytest.raises(ValueError, match="faltam construtores para: md"):
        m.extend_families(FAMILIES, "code", {"html": 1})
    with pytest.raises(ValueError, match="faltam construtores para: html, md"):
        m.extend_families(FAMILIES, "code", {})
    with pytest.raises(ValueError, match="famílias desconhecidas: tex, xml"):
        m.extend_families(FAMILIES, "code", {"html": 1, "md": 1, "xml": 1, "tex": 1})
    assert "code" not in FAMILIES["html"]


def test_add_family(load_exercise):
    m = load_exercise("ex04_extend_family")
    new = m.add_family(FAMILIES, "tex", {"heading": 5, "link": 6})
    assert list(new) == ["html", "md", "tex"] and new["tex"] == {"heading": 5, "link": 6}
    assert "tex" not in FAMILIES
    new["html"]["heading"] = 99
    assert FAMILIES["html"]["heading"] == 1
    assert m.add_family({}, "a", {"x": 1}) == {"a": {"x": 1}}
    with pytest.raises(ValueError, match="família já existe: 'md'"):
        m.add_family(FAMILIES, "md", {})
    with pytest.raises(ValueError, match="produtos incompatíveis: faltam link; sobram code, extra"):
        m.add_family(FAMILIES, "tex", {"heading": 1, "code": 2, "extra": 3})
    with pytest.raises(ValueError, match="produtos incompatíveis: faltam heading, link$"):
        m.add_family(FAMILIES, "tex", {})
    with pytest.raises(ValueError, match="produtos incompatíveis: sobram z$"):
        m.add_family(FAMILIES, "tex", {"heading": 1, "link": 2, "z": 3}, like="md")
    with pytest.raises(KeyError):
        m.add_family(FAMILIES, "tex", {}, like="nope")


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["abstract_factory_classico", "abstract_factory_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
