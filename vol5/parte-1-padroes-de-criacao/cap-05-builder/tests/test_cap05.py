import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_request_builder_basic(load_exercise):
    m = load_exercise("ex01_fluent_builder")
    req = (m.RequestBuilder().url("https://api.x/users").header("Accept", "text/plain").param("page", 2).param("q", "a b").build())
    assert req.method == "GET" and req.headers == (("Accept", "text/plain"),) and req.params == (("page", "2"), ("q", "a b"))
    assert req.full_url == "https://api.x/users?page=2&q=a+b"
    assert m.RequestBuilder().url("http://x").build().full_url == "http://x"
    assert m.RequestBuilder().url("http://x?a=1").param("b", 2).build().full_url == "http://x?a=1&b=2"


def test_request_builder_json_and_methods(load_exercise):
    m = load_exercise("ex01_fluent_builder")
    req = m.RequestBuilder().method("post").url("http://x").json_body({"a": 1}).build()
    assert req.method == "POST" and req.body == '{"a": 1}' and ("Content-Type", "application/json") in req.headers
    builder = m.RequestBuilder().url("http://x")
    assert builder.header("X", "1").header("X", "2").build().headers == (("X", "1"), ("X", "2"))
    with pytest.raises(ValueError, match="método inválido: PATCH"):
        m.RequestBuilder().method("patch")
    with pytest.raises(ValueError, match="url obrigatória"):
        m.RequestBuilder().build()
    for verb in ("GET", "DELETE"):
        with pytest.raises(ValueError, match=f"{verb} não aceita corpo"):
            m.RequestBuilder().method(verb).url("http://x").json_body([1]).build()


def test_request_builder_reuse_does_not_leak(load_exercise):
    m = load_exercise("ex01_fluent_builder")
    b = m.RequestBuilder().url("http://x").header("A", "1")
    first = b.build()
    b.header("B", "2").param("p", 1)
    assert first.headers == (("A", "1"),) and first.params == ()
    assert b.build().headers == (("A", "1"), ("B", "2"))
    with pytest.raises(Exception):
        first.method = "POST"                                      # frozen


# ---------- ex02 ----------
def test_select_basic(load_exercise):
    m = load_exercise("ex02_immutable_query")
    assert m.Select("users").build() == ("SELECT * FROM users", ())
    q = m.Select("users").columns_("id", "name").where("age", ">=", 18).where("city", "=", "SP").order_by("name").order_by("age", descending=True).limit(10)
    assert q.build() == ("SELECT id, name FROM users WHERE age >= ? AND city = ? ORDER BY name ASC, age DESC LIMIT 10", (18, "SP"))


def test_select_in_offset(load_exercise):
    m = load_exercise("ex02_immutable_query")
    q = m.Select("orders").where_in("status", ["new", "paid"]).where("total", ">", 5)
    assert q.build() == ("SELECT * FROM orders WHERE status IN (?, ?) AND total > ?", ("new", "paid", 5))
    assert m.Select("users").offset(20).build() == ("SELECT * FROM users LIMIT -1 OFFSET 20", ())
    assert m.Select("users").limit(5).offset(10).build() == ("SELECT * FROM users LIMIT 5 OFFSET 10", ())
    assert m.Select("users").offset(0).build() == ("SELECT * FROM users", ())
    assert m.Select("users").limit("7").build()[0].endswith("LIMIT 7")


def test_select_immutable_and_reusable(load_exercise):
    m = load_exercise("ex02_immutable_query")
    base = m.Select("users").where("age", ">", 18)
    a = base.where("city", "=", "SP")
    b = base.where("city", "=", "RJ")
    assert base.build() == ("SELECT * FROM users WHERE age > ?", (18,))
    assert a.build()[1] == (18, "SP") and b.build()[1] == (18, "RJ")
    assert a is not base and a.table == "users"


def test_select_validation(load_exercise):
    m = load_exercise("ex02_immutable_query")
    with pytest.raises(ValueError, match="tabela desconhecida: logs"):
        m.Select("logs")
    q = m.Select("users")
    with pytest.raises(ValueError, match="coluna desconhecida: age; DROP"):
        q.where("age; DROP", "=", 1)
    with pytest.raises(ValueError, match="coluna desconhecida: total"):
        q.columns_("id", "total")
    with pytest.raises(ValueError, match="operador inválido: LIKE"):
        q.where("name", "LIKE", "a%")
    with pytest.raises(ValueError, match="lista vazia"):
        q.where_in("id", [])
    for bad in (lambda: q.limit(-1), lambda: q.offset(-5)):
        with pytest.raises(ValueError, match="valor negativo"):
            bad()
    sql, params = q.where("name", "=", "x'; DROP TABLE users; --").build()
    assert "DROP" not in sql and params == ("x'; DROP TABLE users; --",)


# ---------- ex03 ----------
def test_server_config_defaults_and_url(load_exercise):
    m = load_exercise("ex03_config_object")
    c = m.ServerConfig(host="localhost")
    assert (c.port, c.workers, c.tls, c.cert_path) == (8000, 1, False, None)
    assert c.url == "http://localhost:8000"
    assert m.ServerConfig(host="h", port=80).url == "http://h"
    assert m.ServerConfig(host="h", port=443, tls=True, cert_path="c.pem").url == "https://h"
    assert m.ServerConfig(host="h", port=8443, tls=True, cert_path="c.pem").url == "https://h:8443"
    with pytest.raises(TypeError):
        m.ServerConfig("localhost")                                # só por nome


@pytest.mark.parametrize("kwargs,message", [
    ({"host": "  "}, "host obrigatório"),
    ({"host": "h", "port": 0}, "porta inválida: 0"),
    ({"host": "h", "port": 70000}, "porta inválida: 70000"),
    ({"host": "h", "workers": 0}, "workers deve ser >= 1"),
    ({"host": "h", "tls": True}, "tls exige cert_path"),
    ({"host": "h", "cert_path": "c.pem"}, "cert_path sem tls"),
    ({"host": "", "port": 0}, "host obrigatório"),                 # a ordem das regras
])
def test_server_config_validation(load_exercise, kwargs, message):
    m = load_exercise("ex03_config_object")
    with pytest.raises(ValueError, match=message):
        m.ServerConfig(**kwargs)


def test_server_config_from_dict_and_with(load_exercise):
    m = load_exercise("ex03_config_object")
    c = m.ServerConfig.from_dict({"host": "h", "workers": 4})
    assert c.workers == 4
    with pytest.raises(ValueError, match="chaves desconhecidas: cor, zzz"):
        m.ServerConfig.from_dict({"host": "h", "zzz": 1, "cor": 2})
    d = c.with_(port=9000, workers=8)
    assert (d.port, d.workers, c.port, c.workers) == (9000, 8, 8000, 4)
    with pytest.raises(ValueError, match="tls exige cert_path"):
        c.with_(tls=True)
    with pytest.raises(ValueError, match="chaves desconhecidas: x"):
        c.with_(x=1)
    with pytest.raises(Exception):
        c.port = 1                                                  # frozen


# ---------- ex04 ----------
ROWS = [("maçã", 3), ("pera, verde", 5)]


def test_builders_formats(load_exercise):
    m = load_exercise("ex04_director")
    assert m.build_report(m.TextBuilder(), "Frutas", ROWS) == "FRUTAS\n- maçã: 3\n- pera, verde: 5"
    assert m.build_report(m.MarkdownBuilder(), "Frutas", ROWS) == "# Frutas\n\n- **maçã**: 3\n- **pera, verde**: 5"
    assert m.build_report(m.MarkdownBuilder(), "Vazio", []) == "# Vazio"
    assert m.build_report(m.CsvBuilder(), "ignorado", ROWS) == 'nome,valor\nmaçã,3\n"pera, verde",5\n'


def test_director_and_build_all(load_exercise):
    m = load_exercise("ex04_director")
    with pytest.raises(ValueError, match="título obrigatório"):
        m.build_report(m.TextBuilder(), "", ROWS)
    calls = []

    class Spy:
        def title(self, text):
            calls.append(("title", text))

        def row(self, name, value):
            calls.append(("row", name, value))

        def result(self):
            return "ok"

    assert m.build_report(Spy(), "T", [("a", 1), ("b", 2)]) == "ok"
    assert calls == [("title", "T"), ("row", "a", 1), ("row", "b", 2)]
    out = m.build_all({"text": m.TextBuilder(), "md": m.MarkdownBuilder()}, "X", [("a", 1)])
    assert list(out) == ["text", "md"] and out["text"] == "X\n- a: 1".replace("X", "X") and out["md"] == "# X\n\n- **a**: 1"


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["builder_classico", "builder_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
