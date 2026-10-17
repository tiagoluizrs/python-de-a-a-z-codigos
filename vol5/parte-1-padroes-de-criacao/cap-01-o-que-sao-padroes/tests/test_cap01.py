import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

CLASSIC = '''
from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def apply(self, x): ...

class Base:
    pass

class Child(Base):
    def go(self):
        return lambda y: y

class Grand(Child):
    pass

class Other(dict):
    pass
'''


def test_measure(load_exercise):
    m = load_exercise("ex01_measure")
    r = m.measure(CLASSIC)
    assert r["classes"] == 5 and r["abstract"] == 1 and r["depth"] == 3
    assert r["functions"] == 3          # apply, go, lambda
    assert r["lines"] == 13             # sem linhas vazias


def test_measure_edge_cases(load_exercise):
    m = load_exercise("ex01_measure")
    assert m.measure("# nada\n") == {"lines": 0, "classes": 0, "functions": 0, "abstract": 0, "depth": 0}
    r = m.measure("""
        import abc
        class A(abc.ABC):
            pass
        class B:
            @abc.abstractmethod
            def f(self): ...
        class C(B):
            async def g(self): ...
    """)
    assert r["abstract"] == 2 and r["depth"] == 2 and r["functions"] == 2 and r["lines"] == 8


def test_ceremony_ratio(load_exercise):
    m = load_exercise("ex01_measure")
    assert m.ceremony_ratio("a = 1\nb = 2\nc = 3\nd = 4\n", "a = 1\nb = 2\n") == 2.0
    assert m.ceremony_ratio("a\nb\nc\n", "x\ny") == 1.5
    with pytest.raises(ValueError):
        m.ceremony_ratio("a = 1", "# nada")


HINTS_SRC = '''
class Discount:
    def __init__(self, p):
        self.p = p
    def apply(self, total):
        return total

class Runner:
    def __call__(self):
        pass

class Big:
    def a(self): ...
    def b(self): ...

class Empty:
    pass

class Config:
    _instance = None
    def __new__(cls):
        return cls._instance

class Typed:
    _instance: "Typed | None" = None

class Counter:
    def __iter__(self):
        return self
    def __next__(self):
        raise StopIteration

class Hub:
    def __init__(self):
        self.listeners = []
        self.other = []
    def emit(self):
        pass
    def add(self):
        pass

class Hub2:
    def setup(self):
        self.subscribers = set()
        self.callbacks = list()
    def x(self): ...
    def y(self): ...

class Private:
    def _helper(self): ...
'''


def test_pattern_hints(load_exercise):
    m = load_exercise("ex02_hints")
    hints = {(h.pattern, h.where) for h in m.pattern_hints(HINTS_SRC)}
    assert hints == {
        ("Strategy/Command", "Discount"), ("Strategy/Command", "Runner"),
        ("Singleton", "Config"), ("Singleton", "Typed"),
        ("Iterator", "Counter"), ("Observer", "Hub"), ("Observer", "Hub2"),
    }


def test_pattern_hints_lines_and_order(load_exercise):
    m = load_exercise("ex02_hints")
    hints = m.pattern_hints(HINTS_SRC)
    assert hints == sorted(hints, key=lambda h: (h.line, h.pattern))
    lines = HINTS_SRC.splitlines()
    discount = next(h for h in hints if h.where == "Discount")
    assert lines[discount.line - 1].startswith("class Discount")
    assert m.pattern_hints("x = 1") == []


def test_multiple_hints_one_class(load_exercise):
    m = load_exercise("ex02_hints")
    src = '''
class Weird:
    _instance = None
    def __iter__(self): ...
    def __next__(self): ...
'''
    assert {h.pattern for h in m.pattern_hints(src)} == {"Singleton", "Iterator"}


def test_percent_fixed(load_exercise):
    m = load_exercise("ex03_strategies")
    assert m.percent(10)(200.0) == pytest.approx(180.0)
    assert m.percent(0)(50.0) == 50.0 and m.percent(100)(50.0) == 0.0
    for bad in (-1, 100.1):
        with pytest.raises(ValueError, match="percentual inválido"):
            m.percent(bad)
    assert m.fixed(30)(100.0) == 70.0 and m.fixed(30)(10.0) == 0.0
    with pytest.raises(ValueError):
        m.fixed(-1)


def test_tiered_best_of_then(load_exercise):
    m = load_exercise("ex03_strategies")
    t = m.tiered((500, 10), (100, 5))
    assert t(50.0) == 50.0 and t(100.0) == pytest.approx(95.0) and t(499.0) == pytest.approx(474.05) and t(500.0) == pytest.approx(450.0)
    with pytest.raises(ValueError):
        m.tiered()
    best = m.best_of(m.percent(10), m.fixed(30))
    assert best(100.0) == pytest.approx(70.0) and best(1000.0) == pytest.approx(900.0)
    with pytest.raises(ValueError):
        m.best_of()
    chain = m.then(m.percent(10), m.fixed(5))
    assert chain(100.0) == pytest.approx(85.0)
    assert m.then()(7.0) == 7.0


def test_checkout(load_exercise):
    m = load_exercise("ex03_strategies")
    assert m.checkout(19.999) == 20.0
    assert m.checkout(200.0, m.percent(15)) == 170.0
    with pytest.raises(ValueError):
        m.checkout(-1)


CATALOG = [
    {"name": "Strategy", "family": "comportamental", "chapter": 15, "verdict": "embutido"},
    {"name": "Singleton", "family": "criação", "chapter": 4, "verdict": "embutido"},
    {"name": "Builder", "family": "criação", "chapter": 5, "verdict": "simplificado"},
    {"name": "Facade", "family": "estrutural", "chapter": 9, "verdict": "igual"},
]
EXTRAS = [{"name": "Object Pool", "chapter": 7}]


def test_catalog_queries(load_exercise):
    m = load_exercise("ex04_catalog")
    assert m.by_family(CATALOG) == {"comportamental": ["Strategy"], "criação": ["Singleton", "Builder"], "estrutural": ["Facade"]}
    assert list(m.by_family(CATALOG)) == ["comportamental", "criação", "estrutural"]
    assert m.verdict_counts(CATALOG) == {"embutido": 2, "igual": 1, "simplificado": 1}
    assert list(m.verdict_counts(CATALOG)) == ["embutido", "igual", "simplificado"]
    assert m.embedded(CATALOG) == ["Singleton", "Strategy"]
    assert m.chapters_of(CATALOG, "builder", "STRATEGY") == [5, 15]
    with pytest.raises(KeyError):
        m.chapters_of(CATALOG, "Nope")
    assert m.python_share(CATALOG) == 0.75
    with pytest.raises(ValueError):
        m.python_share([])


def test_missing_chapters(load_exercise):
    m = load_exercise("ex04_catalog")
    assert m.missing_chapters(CATALOG, EXTRAS, 4, 9) == [6, 8]
    assert m.missing_chapters(CATALOG, EXTRAS, 4, 5) == []
    assert m.missing_chapters([], [], 1, 3) == [1, 2, 3]


@pytest.mark.parametrize("name", ["strategy_classico_vs_funcao", "catalogo", "padroes_embutidos"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()


def test_catalog_has_23_gof_and_no_gaps():
    import importlib.util
    spec = importlib.util.spec_from_file_location("catalogo_demo", ROOT / "exemplos" / "catalogo.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert len(mod.CATALOG) == 23
    families = {}
    for p in mod.CATALOG:
        families[p["family"]] = families.get(p["family"], 0) + 1
    assert families == {"criação": 5, "estrutural": 7, "comportamental": 11}
    chapters = sorted([p["chapter"] for p in mod.CATALOG] + [e["chapter"] for e in mod.EXTRAS])
    assert chapters == list(range(2, 32))
