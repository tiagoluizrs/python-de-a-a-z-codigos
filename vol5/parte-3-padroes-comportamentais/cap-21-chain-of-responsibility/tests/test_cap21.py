import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def chain(m):
    return m.build_chain(m.Approver("líder", 1_000), m.Approver("gerente", 10_000), m.Approver("diretor", 100_000))


def test_chain_handles_and_traces(load_exercise):
    m = load_exercise("ex01_approval_chain")
    c = chain(m)
    assert c.handle(m.Expense(300, "livro")) == "líder aprovou livro" and c.handle(m.Expense(5_000, "servidor")) == "gerente aprovou servidor"
    assert c.handle(m.Expense(100_000, "licenças")) == "diretor aprovou licenças" and c.handle(m.Expense(100_001, "prédio")) is None
    assert c.trace(m.Expense(300, "x")) == ["líder"] and c.trace(m.Expense(5_000, "x")) == ["líder", "gerente"] and c.trace(m.Expense(9e9, "x")) == ["líder", "gerente", "diretor"]
    a = m.Approver("a", 1)
    assert a.set_next(m.Approver("b", 2)).name == "b" and a.name == "a" and m.Approver("z", 0).handle(m.Expense(5, "x")) is None
    with pytest.raises(ValueError, match="cadeia vazia"):
        m.build_chain()


def test_category_and_mixed_chain(load_exercise):
    m = load_exercise("ex01_approval_chain")
    c = m.build_chain(m.CategoryApprover("jurídico", "legal"), m.Approver("líder", 1_000), m.CategoryApprover("TI", "ti"))
    assert c.handle(m.Expense(9e6, "contrato", "legal")) == "jurídico aprovou contrato (legal)"
    assert c.handle(m.Expense(500, "caneta")) == "líder aprovou caneta"
    assert c.handle(m.Expense(5_000, "servidor", "ti")) == "TI aprovou servidor (ti)" and c.handle(m.Expense(5_000, "viagem")) is None
    assert c.trace(m.Expense(5_000, "x", "ti")) == ["jurídico", "líder", "TI"]


def test_chain_has_no_recursion_and_no_cycles(load_exercise):
    m = load_exercise("ex01_approval_chain")
    head = current = m.Approver("h0", -1)
    for i in range(1, 5_000):
        current = current.set_next(m.Approver(f"h{i}", -1))
    current.limit = 10
    assert head.handle(m.Expense(1, "x")) == "h4999 aprovou x" and len(head.trace(m.Expense(1, "x"))) == 5_000
    a, b, c = m.Approver("a", 0), m.Approver("b", 0), m.Approver("c", 0)
    a.set_next(b).set_next(c)
    with pytest.raises(ValueError, match="ciclo na cadeia"):
        c.set_next(a)
    with pytest.raises(ValueError, match="ciclo na cadeia"):
        a.set_next(a)
    d = m.Approver("d", 0)
    c.set_next(d)
    assert a.trace(m.Expense(1, "x")) == ["a", "b", "c", "d"]


# ---------- ex02 ----------
def test_first_match(load_exercise):
    m = load_exercise("ex02_handler_list")
    calls = []

    def a(x):
        calls.append("a")

    def b(x):
        calls.append("b")
        return 0                                                                        # 0 é um resultado!

    def c(x):
        calls.append("c")
        return "c"

    assert m.first_match([a, b, c], 1) == 0 and calls == ["a", "b"]
    assert m.first_match([a], 1, default="padrão") == "padrão" and m.first_match([], 1) is None
    calls.clear()
    assert m.first_match((h for h in [a, c, b]), 1) == "c" and calls == ["a", "c"]
    assert m.first_match([lambda x: "", lambda x: "z"], 1) == "" and m.first_match([lambda x: False], 1) is False


def test_router(load_exercise):
    m = load_exercise("ex02_handler_list")
    r = m.Router()

    def to_int(request):
        return int(request)

    def shout(request):
        return request.upper()

    assert r.register(str.isdigit, to_int) is to_int
    r.register(lambda req: True, shout)
    assert r.route("42") == 42 and r.route("ola") == "OLA" and len(r) == 2 and r.handlers() == [to_int, shout]
    def special(request):
        return "especial"
    r.insert(0, lambda req: req == "42", special)
    assert r.route("42") == "especial" and r.route("7") == 7
    assert r.remove(special) == 1 and r.remove(special) == 0 and r.route("42") == 42
    empty = m.Router()
    with pytest.raises(LookupError, match="nenhuma rota para 'x'"):
        empty.route("x")
    assert m.Router(fallback=lambda req: f"padrão:{req}").route("x") == "padrão:x"
    r2 = m.Router()
    r2.register(lambda req: True, lambda req: None)
    assert r2.route("y") is None                                                         # None do handler é um resultado válido


@pytest.mark.parametrize("text,label", [("COMPRE AGORA!!!", "spam"), ("É urgente", "urgente"), ("socorro!!!", "urgente"), ("tudo bem?", "pergunta"), ("bom dia", "comum"),
                                         ("   ", "vazia"), ("", "vazia"), ("compre agora ou urgente?", "spam"), ("urgente?", "urgente")])
def test_classify(load_exercise, text, label):
    m = load_exercise("ex02_handler_list")
    assert m.classify(text) == label


# ---------- ex03 ----------
def app(request):
    return {"status": 200, "body": f"olá {request['path']}"}


def test_compose_order(load_exercise):
    m = load_exercise("ex03_middleware")
    events = []

    def tag(name):
        def mw(request, call_next):
            events.append(f"in {name}")
            response = call_next(request)
            events.append(f"out {name}")
            return response
        return mw

    handler = m.compose(tag("a"), tag("b"), tag("c"))(app)
    assert handler({"path": "/"})["status"] == 200
    assert events == ["in a", "in b", "in c", "out c", "out b", "out a"]
    assert m.compose()(app) is app
    with pytest.raises(TypeError, match="middleware precisa ser chamável"):
        m.compose("x")(app)


def test_logging_and_auth(load_exercise):
    m = load_exercise("ex03_middleware")
    log = []
    pipeline = m.compose(m.logging_mw(log), m.auth_mw({"segredo"}))(app)
    assert pipeline({"path": "/home", "token": "segredo"}) == {"status": 200, "body": "olá /home"} and log == ["-> /home", "<- 200"]
    log.clear()
    assert pipeline({"path": "/admin"}) == {"status": 401, "body": "não autorizado"} and log == ["-> /admin", "<- 401"]
    inner = m.compose(m.auth_mw({"x"}), m.logging_mw(log))(app)
    log.clear()
    assert inner({"path": "/a", "token": "errado"})["status"] == 401 and log == []

    def boom(request):
        raise KeyError("x")

    log.clear()
    with pytest.raises(KeyError):
        m.compose(m.logging_mw(log))(boom)({"path": "/b"})
    assert log == ["-> /b", "!! KeyError"]


def test_rate_limit(load_exercise):
    m = load_exercise("ex03_middleware")
    now = [0.0]
    calls = []

    def counting(request):
        calls.append(1)
        return {"status": 200, "body": "ok"}

    handler = m.compose(m.rate_limit_mw(2, 10, lambda: now[0]))(counting)
    assert handler({"path": "/", "client": "a"})["status"] == 200 and handler({"path": "/", "client": "a"})["status"] == 200
    assert handler({"path": "/", "client": "a"}) == {"status": 429, "body": "muitos pedidos"} and len(calls) == 2
    assert handler({"path": "/", "client": "b"})["status"] == 200 and handler({"path": "/"})["status"] == 200
    now[0] = 9.9
    assert handler({"path": "/", "client": "a"})["status"] == 429
    now[0] = 10.0
    assert handler({"path": "/", "client": "a"})["status"] == 200
    for args in ((0, 10), (1, 0)):
        with pytest.raises(ValueError):
            m.rate_limit_mw(*args, clock=lambda: 0)


def test_cache(load_exercise):
    m = load_exercise("ex03_middleware")
    calls = []

    def counting(request):
        calls.append(request["path"])
        status = 404 if request["path"] == "/missing" else 200
        return {"status": status, "body": request["path"]}

    handler = m.compose(m.cache_mw())(counting)
    first = handler({"path": "/a"})
    second = handler({"path": "/a"})
    assert first == {"status": 200, "body": "/a"} and second == {"status": 200, "body": "/a", "cached": True} and calls == ["/a"]
    assert "cached" not in first                                                      # a original não mudou
    handler({"path": "/missing"})
    handler({"path": "/missing"})
    assert calls == ["/a", "/missing", "/missing"]                                    # 404 não é guardado
    handler({"path": "/a", "method": "POST"})
    assert calls[-1] == "/a" and len(calls) == 4
    assert "cached" not in handler({"path": "/a"}) and len(calls) == 5                # o POST invalidou a entrada


# ---------- ex04 ----------
def config(m):
    return m.LayeredConfig(cli={"color": "verde"}, env={"debug": True}, file={"size": 12, "color": "roxo"}, defaults={"color": "azul", "size": 10, "debug": False, "mode": "x"})


def test_layered_lookup(load_exercise):
    m = load_exercise("ex04_layered_config")
    c = config(m)
    assert c["color"] == "verde" and c["size"] == 12 and c["debug"] is True and c["mode"] == "x" and c.get("nada") is None and c.get("nada", 5) == 5
    assert [c.source(k) for k in ("color", "debug", "size", "mode")] == ["cli", "env", "file", "defaults"]
    assert c.layers == ["cli", "env", "file", "defaults"] and "color" in c and "z" not in c and len(c) == 4 and sorted(c) == ["color", "debug", "mode", "size"]
    with pytest.raises(KeyError):
        c["z"]
    with pytest.raises(KeyError):
        c.source("z")
    assert c.shadowed("color") == [("cli", "verde"), ("file", "roxo"), ("defaults", "azul")] and c.shadowed("z") == []
    assert c.flatten() == {"color": "verde", "size": 12, "debug": True, "mode": "x"}
    with pytest.raises(ValueError, match="sem camadas"):
        m.LayeredConfig()


def test_layered_write_copy_and_derive(load_exercise):
    m = load_exercise("ex04_layered_config")
    cli = {"color": "verde"}
    c = m.LayeredConfig(cli=cli, defaults={"size": 10})
    cli["color"] = "mudou"
    assert c["color"] == "verde"                                                       # as camadas foram copiadas
    c["size"] = 99
    assert c["size"] == 99 and c.source("size") == "cli" and c.shadowed("size") == [("cli", 99), ("defaults", 10)]
    over = c.override(size=1, extra=True)
    assert over["size"] == 1 and over.source("size") == "override" and over.layers[0] == "override" and over["extra"] is True
    assert c["size"] == 99 and "extra" not in c and c.layers == ["cli", "defaults"]
    gone = c.without("size")
    assert "size" not in gone and c["size"] == 99 and gone["color"] == "verde"


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["chain_classico", "chain_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
