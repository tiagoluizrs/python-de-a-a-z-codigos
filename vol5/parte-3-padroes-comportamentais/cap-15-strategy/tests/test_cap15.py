import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_policies(load_exercise):
    m = load_exercise("ex01_backoff")
    assert [m.fixed(2)(a) for a in (1, 2, 3)] == [2, 2, 2] and [m.linear(1.5)(a) for a in (1, 2, 3)] == [1.5, 3.0, 4.5]
    e = m.exponential(1, 2)
    assert [e(a) for a in (1, 2, 3, 4)] == [1, 2, 4, 8] and [m.exponential(1, 2, cap=5)(a) for a in (1, 2, 3, 4, 5)] == [1, 2, 4, 5, 5]
    assert m.exponential()(1) == 1.0 and m.exponential(0.5, 3)(3) == 4.5
    assert m.with_jitter(m.fixed(10), lambda: 0.25)(1) == 2.5
    assert m.total_wait(m.exponential(1, 2), 4) == 7 and m.total_wait(m.fixed(3), 1) == 0 and m.total_wait(m.linear(1), 5) == 10
    for bad in (lambda: m.fixed(-1), lambda: m.linear(-0.1)):
        with pytest.raises(ValueError, match="espera negativa"):
            bad()
    for kwargs in ({"base": -1}, {"factor": 0.5}, {"cap": -1}):
        with pytest.raises(ValueError, match="parâmetros inválidos"):
            m.exponential(**kwargs)
    with pytest.raises(ValueError):
        m.total_wait(m.fixed(1), 0)


def flaky(failures, error=ConnectionError):
    state = {"n": 0}

    def action():
        state["n"] += 1
        if state["n"] <= failures:
            raise error("caiu")
        return f"ok{state['n']}"

    action.state = state
    return action


def test_retry(load_exercise):
    m = load_exercise("ex01_backoff")
    waits = []
    action = flaky(2)
    assert m.retry(action, m.exponential(1, 2), 5, waits.append) == "ok3" and waits == [1, 2] and action.state["n"] == 3
    waits.clear()
    action = flaky(5)
    with pytest.raises(ConnectionError):
        m.retry(action, m.fixed(1), 3, waits.append)
    assert waits == [1, 1] and action.state["n"] == 3                                    # sem espera depois da última tentativa
    waits.clear()
    with pytest.raises(KeyError):
        m.retry(flaky(1, KeyError), m.fixed(1), 5, waits.append)
    assert waits == []
    assert m.retry(flaky(1, KeyError), m.fixed(1), 3, waits.append, retry_on=(KeyError,)) == "ok2" and waits == [1]
    assert m.retry(flaky(0), m.fixed(1), 1, waits.append) == "ok1"
    with pytest.raises(ValueError, match="attempts deve ser >= 1"):
        m.retry(flaky(0), m.fixed(1), 0, waits.append)


def test_make_policy(load_exercise):
    m = load_exercise("ex01_backoff")
    assert set(m.POLICIES) == {"fixed", "linear", "exponential"}
    assert m.make_policy("linear", 2)(3) == 6 and m.make_policy("exponential", base=2, cap=10)(4) == 10
    with pytest.raises(ValueError) as info:
        m.make_policy("quadratica")
    assert str(info.value) == "política desconhecida: 'quadratica'; disponíveis: exponential, fixed, linear"


# ---------- ex02 ----------
ITEMS = [{"name": "a", "price": 10, "rating": 4.0}, {"name": "b", "price": 5, "rating": 4.0}, {"name": "c", "price": 7, "rating": 5.0}, {"name": "d", "price": 5, "rating": 3.0}]


def names(items):
    return [i["name"] for i in items]


def test_rank(load_exercise):
    m = load_exercise("ex02_ranking")
    assert names(m.rank(ITEMS, m.by_attr("price"))) == ["b", "d", "c", "a"]                          # empate b/d: ordem original (ordenação estável)
    assert names(m.rank(ITEMS, m.by_attr("price"), m.by_attr("rating", descending=True))) == ["b", "d", "c", "a"]
    assert names(m.rank(ITEMS, m.by_attr("rating", descending=True), m.by_attr("price"))) == ["c", "b", "a", "d"]
    assert names(m.rank(ITEMS, m.by_attr("price"), reverse=True)) == ["a", "c", "d", "b"]
    assert m.rank(ITEMS) == ITEMS and m.rank(ITEMS) is not ITEMS and names(ITEMS) == ["a", "b", "c", "d"]
    assert m.by_attr("price").descending is False and m.by_attr("price", True).descending is True


class Obj:
    def __init__(self, v):
        self.v = v


def test_by_attr_objects_and_errors(load_exercise):
    m = load_exercise("ex02_ranking")
    objs = [Obj(3), Obj(1), Obj(2)]
    assert [o.v for o in m.rank(objs, m.by_attr("v"))] == [1, 2, 3] and [o.v for o in m.rank(objs, m.by_attr("v", descending=True))] == [3, 2, 1]
    with pytest.raises(KeyError):
        m.rank(ITEMS, m.by_attr("zzz"))
    with pytest.raises(AttributeError):
        m.rank(objs, m.by_attr("zzz"))


def test_top_n_and_weighted(load_exercise):
    m = load_exercise("ex02_ranking")
    assert names(m.top_n(ITEMS, m.by_attr("price"), 2)) == ["b", "d"] and names(m.top_n(ITEMS, m.by_attr("rating", True), 1)) == ["c"]
    assert len(m.top_n(ITEMS, m.by_attr("price"), 99)) == 4 and m.top_n(ITEMS, m.by_attr("price"), 0) == []
    with pytest.raises(ValueError, match="n negativo"):
        m.top_n(ITEMS, m.by_attr("price"), -1)
    score = m.weighted(price=-1, rating=2)
    assert score.descending is True and names(m.rank(ITEMS, score)) == ["b", "c", "d", "a"] and names(m.top_n(ITEMS, score, 2)) == ["b", "c"]
    with pytest.raises(ValueError, match="sem pesos"):
        m.weighted()
    with pytest.raises(KeyError):
        m.rank(ITEMS, m.weighted(nada=1))


# ---------- ex03 ----------
LINES = [("lapis", 10, 100), ("caneta", 2, 500), ("caderno", 1, 2000)]          # 1000 + 1000 + 2000 = 4000


def test_strategies(load_exercise):
    m = load_exercise("ex03_pricing")
    assert m.no_discount(4000, LINES) == 0 and m.percent(10)(4000, LINES) == 400 and m.percent(12.5)(999, LINES) == 125
    assert m.bulk(2, 10)(4000, LINES) == 200 and m.bulk(11, 10)(4000, LINES) == 0 and m.bulk(10, 15)(4000, [("a", 10, 33)]) == 50
    for bad in (lambda: m.percent(101), lambda: m.percent(-1), lambda: m.bulk(0, 10), lambda: m.bulk(2, 200), lambda: m.Loyalty(-1, 10), lambda: m.Loyalty(1, 101)):
        with pytest.raises(ValueError):
            bad()
    with pytest.raises(ValueError):
        m.best_of()


def test_loyalty_state(load_exercise):
    m = load_exercise("ex03_pricing")
    loyal = m.Loyalty(2, 10)
    assert [loyal(1000, LINES) for _ in range(4)] == [0, 0, 100, 100] and loyal.orders == 4
    loyal.reset()
    assert loyal.orders == 0 and loyal(1000, LINES) == 0
    assert m.Loyalty(0, 5)(200, LINES) == 10


def test_best_of_calls_each_once(load_exercise):
    m = load_exercise("ex03_pricing")
    loyal = m.Loyalty(0, 20)
    best = m.best_of(m.percent(10), loyal, m.bulk(2, 50))
    assert best(4000, LINES) == 1000 and loyal.orders == 1
    assert m.best_of(m.no_discount)(10, []) == 0


def test_checkout(load_exercise):
    m = load_exercise("ex03_pricing")
    c = m.Checkout()
    assert c.total(LINES) == 4000 and c.describe() == "no_discount" and c.strategy is m.no_discount
    c.strategy = m.percent(10)
    assert c.total(LINES) == 3600 and c.describe() == "<lambda>"
    c.strategy = loyal = m.Loyalty(0, 25)
    assert c.total(LINES) == 3000 and c.describe() == "Loyalty" and loyal.orders == 1
    c.strategy = lambda subtotal, lines: 10 ** 9
    assert c.total(LINES) == 0                                                           # o desconto nunca passa do subtotal
    assert m.Checkout(m.percent(50)).total([("x", 3, 100)]) == 150
    with pytest.raises(TypeError, match="estratégia precisa ser chamável"):
        c.strategy = "10%"
    for bad in ([("x", 0, 10)], [("x", 1, -1)]):
        loyal2 = m.Loyalty(0, 10)
        with pytest.raises(ValueError, match="linha inválida"):
            m.Checkout(loyal2).total(bad)
        assert loyal2.orders == 0                                                         # a estratégia nem foi chamada
    assert m.Checkout().total([]) == 0


# ---------- ex04 ----------
def test_registry_basic(load_exercise):
    m = load_exercise("ex04_registry")
    r = m.StrategyRegistry()
    with pytest.raises(LookupError, match="sem estratégia padrão"):
        r.get()
    with pytest.raises(KeyError, match="disponíveis: nenhuma"):
        r.get("x")

    @r.register("upper")
    def upper(text):
        return text.upper()

    @r.register("lower", default=True)
    def lower(text):
        return text.lower()

    assert upper("a") == "A" and r.get("upper") is upper and r.get() is lower and r.names() == ["lower", "upper"]
    with pytest.raises(KeyError, match="estratégia desconhecida: zzz; disponíveis: lower, upper"):
        r.get("zzz")
    with pytest.raises(ValueError, match="estratégia já registrada: upper"):
        r.register("upper")(lambda t: t)
    with pytest.raises(ValueError, match="já existe um padrão: lower"):
        r.register("outra", default=True)(lambda t: t)


def test_registry_rules(load_exercise):
    m = load_exercise("ex04_registry")
    r = m.StrategyRegistry()
    r.register("shout", default=False)(lambda t: t.upper() + "!")
    r.register("plain", default=True)(lambda t: t)
    r.register("short")(lambda t: t[:3])
    r.add_rule(lambda ctx: ctx["channel"] == "sms", "short")
    r.add_rule(lambda ctx: ctx["urgent"], "shout")
    assert r.run({"channel": "sms", "urgent": True}, "olá mundo") == "olá"             # a primeira regra que casa vence
    assert r.run({"channel": "email", "urgent": True}, "olá") == "OLÁ!"
    assert r.run({"channel": "email", "urgent": False}, "olá") == "olá"
    assert r.resolve({"channel": "x", "urgent": False}) is r.get("plain")
    with pytest.raises(KeyError):
        r.add_rule(lambda ctx: True, "inexistente")
    empty = m.StrategyRegistry()
    empty.register("a")(lambda: 1)
    empty.add_rule(lambda ctx: False, "a")
    with pytest.raises(LookupError, match="sem estratégia padrão"):
        empty.resolve({})


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["strategy_classico", "strategy_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
