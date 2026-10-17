import dataclasses
import gc
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_glyph_validation_and_immutability(load_exercise):
    m = load_exercise("ex01_glyph_flyweight")
    g = m.Glyph("a", "serif", 12)
    assert (g.char, g.font, g.size) == ("a", "serif", 12) and not hasattr(g, "__dict__")
    with pytest.raises(dataclasses.FrozenInstanceError):
        g.size = 14
    with pytest.raises(ValueError, match="char deve ter um caractere"):
        m.Glyph("ab", "serif", 12)
    with pytest.raises(ValueError, match="char deve ter um caractere"):
        m.Glyph("", "serif", 12)
    with pytest.raises(ValueError, match="font vazia"):
        m.Glyph("a", "", 12)
    for size in (0, -1):
        with pytest.raises(ValueError, match="size inválido"):
            m.Glyph("a", "serif", size)
    assert m.Glyph("a", "serif", 12) == g and hash(m.Glyph("a", "serif", 12)) == hash(g)


def test_factory_shares(load_exercise):
    m = load_exercise("ex01_glyph_flyweight")
    f = m.GlyphFactory()
    a1, a2, b = f.get("a", "serif", 12), f.get("a", "serif", 12), f.get("a", "serif", 14)
    assert a1 is a2 and a1 is not b and f.count == 2 and (f.hits, f.misses) == (1, 2)
    with pytest.raises(ValueError):
        f.get("ab", "serif", 12)
    assert f.count == 2 and f.misses == 2                                                  # o erro não deixou nada
    f.clear()
    assert f.count == 0 and f.get("a", "serif", 12) is not a1


def test_document(load_exercise):
    m = load_exercise("ex01_glyph_flyweight")
    f = m.GlyphFactory()
    doc = m.Document(f)
    doc.add_text("abab", "serif", 12, x=10, y=2, advance=1.5)
    doc.add_text("a b", "mono", 10)
    assert doc.text() == "ababa b" and doc.render() == ["a@10,2", "b@11.5,2", "a@13,2", "b@14.5,2", "a@0,0", " @1,0", "b@2,0"]
    assert doc.stats() == {"characters": 7, "glyphs": 5}                                   # a/b em serif12 + a/espaço/b em mono10
    assert f.count == 5
    doc.add_text("", "serif", 12)
    assert doc.stats()["characters"] == 7
    other = m.Document(f)
    other.add_text("aa", "serif", 12)
    assert other.stats() == {"characters": 2, "glyphs": 1} and f.count == 5
    big = m.Document(f)
    big.add_text("lorem ipsum dolor sit amet " * 400, "serif", 12)
    assert big.stats()["characters"] == 10800 and big.stats()["glyphs"] <= 15


# ---------- ex02 ----------
def test_color_validation(load_exercise):
    m = load_exercise("ex02_cache_factory")
    assert m.Color(1, 2, 3).g == 2
    for args, bad in [((256, 0, 0), "r=256"), ((0, -1, 0), "g=-1"), ((0, 0, 1.5), "b=1.5"), ((True, 0, 0), "r=True"), ((0, "0", 0), "g='0'")]:
        with pytest.raises(ValueError, match=f"componente inválido: {bad}"):
            m.Color(*args)
    with pytest.raises(dataclasses.FrozenInstanceError):
        m.Color(1, 2, 3).r = 9


def test_color_pool(load_exercise):
    m = load_exercise("ex02_cache_factory")
    pool = m.ColorPool(maxsize=2)
    a = pool.color(1, 2, 3)
    assert pool.color(1, 2, 3) is a and pool.info() == {"hits": 1, "misses": 1, "size": 1, "maxsize": 2}
    pool.color(4, 5, 6)
    pool.color(7, 8, 9)                                                                   # expulsa o menos recente (1, 2, 3)
    assert pool.info()["size"] == 2 and pool.color(1, 2, 3) is not a
    with pytest.raises(ValueError):
        pool.color(0, 0, 300)
    assert pool.info()["size"] == 2
    other = m.ColorPool()
    assert other.color(7, 8, 9) is not pool.color(7, 8, 9) and other.info()["maxsize"] == 128
    pool.clear()
    assert pool.info() == {"hits": 0, "misses": 0, "size": 0, "maxsize": 2}
    with pytest.raises(ValueError, match="maxsize deve ser >= 1"):
        m.ColorPool(0)


class Thing:
    def __init__(self, key):
        self.key = key


def test_weak_pool(load_exercise):
    m = load_exercise("ex02_cache_factory")
    pool = m.WeakPool(Thing)
    a1, a2 = pool.get("a"), pool.get("a")
    assert a1 is a2 and a1.key == "a" and len(pool) == 1 and "a" in pool and "b" not in pool
    assert pool.stats == {"created": 1, "reused": 1}
    b = pool.get("b")
    assert len(pool) == 2
    del a1, a2
    gc.collect()
    assert len(pool) == 1 and "a" not in pool and "b" in pool
    a3 = pool.get("a")
    assert a3.key == "a" and pool.stats == {"created": 3, "reused": 1} and b is pool.get("b")
    with pytest.raises(TypeError):
        m.WeakPool(lambda k: k).get("texto")                                              # str não aceita referência fraca


# ---------- ex03 ----------
class Dicty:
    def __init__(self):
        self.a, self.b = 1, 2


class Slotty:
    __slots__ = ("a", "b")

    def __init__(self):
        self.a, self.b = 1, 2


def test_deep_size(load_exercise):
    m = load_exercise("ex03_memory_report")
    assert m.deep_size(5) == sys.getsizeof(5) and m.deep_size("abc") == sys.getsizeof("abc") and m.deep_size(None) == sys.getsizeof(None)
    lst = [1000, 2000]
    assert m.deep_size(lst) == sys.getsizeof(lst) + sys.getsizeof(1000) + sys.getsizeof(2000)
    text = "x" * 100
    twice = [text, text]
    assert m.deep_size(twice) == sys.getsizeof(twice) + sys.getsizeof(text)               # o mesmo objeto conta uma vez
    d = {"k": [1, 2]}
    assert m.deep_size(d) == sys.getsizeof(d) + sys.getsizeof("k") + sys.getsizeof([1, 2]) + sys.getsizeof(1) + sys.getsizeof(2)
    assert m.deep_size((1, (2, 3))) > m.deep_size((1, 2, 3)) - 1
    seen = set()
    obj = [1]
    assert m.deep_size(obj, seen) > 0 and m.deep_size(obj, seen) == 0
    cyc = []
    cyc.append(cyc)
    assert m.deep_size(cyc) == sys.getsizeof(cyc)                                         # ciclos não travam


def test_deep_size_objects(load_exercise):
    m = load_exercise("ex03_memory_report")
    d, s = Dicty(), Slotty()
    assert m.deep_size(d) > sys.getsizeof(d) + sys.getsizeof(d.__dict__) - 1
    assert m.deep_size(s) >= sys.getsizeof(s) and m.deep_size(s) < m.deep_size(d)
    class Child(Slotty):
        __slots__ = ("c",)
    c = Child()
    c.a, c.b = 10_000, 20_000                                                             # c.c nunca foi definido: ignorado
    assert m.deep_size(c) >= sys.getsizeof(c) + sys.getsizeof(10_000) + sys.getsizeof(20_000)


def test_per_object_and_ratios(load_exercise):
    m = load_exercise("ex03_memory_report")
    result = m.per_object({"dict": lambda i: Dicty(), "slots": lambda i: Slotty(), "tuple": lambda i: (i, i)}, 200)
    assert result["slots"] < result["dict"] and set(result) == {"dict", "slots", "tuple"} and all(isinstance(v, float) for v in result.values())
    with pytest.raises(ValueError, match="n deve ser >= 1"):
        m.per_object({}, 0)
    assert m.savings_ratio(300, 100) == 3.0 and m.savings_ratio(10, 4) == 2.5
    with pytest.raises(ValueError, match="after deve ser positivo"):
        m.savings_ratio(1, 0)
    a, b = object(), object()
    assert m.shared_fraction([a, a, b]) == 0.333 and m.shared_fraction([a, b]) == 0.0 and m.shared_fraction([]) == 0.0 and m.shared_fraction([a, a, a, a]) == 0.75


# ---------- ex04 ----------
def test_interner(load_exercise):
    m = load_exercise("ex04_intern")
    it = m.Interner()
    s1 = "".join(["ver", "de"])
    s2 = "".join(["ver", "de"])
    assert s1 == s2 and s1 is not s2
    assert it.intern(s1) is s1 and it.intern(s2) is s1 and len(it) == 1
    assert it.intern(1) == 1 and it.intern(True) is True and it.intern(1.0) == 1.0 and len(it) == 4       # 1, True e 1.0 são valores DIFERENTES aqui
    assert it.stats() == {"calls": 5, "unique": 4}
    t1, t2 = tuple(["a", "b"]), tuple(["a", "b"])
    assert it.intern(t1) is t1 and it.intern(t2) is t1
    for bad, name in [([1], "list"), ({}, "dict"), ({1}, "set")]:
        with pytest.raises(TypeError, match=f"valor não hashable: {name}"):
            it.intern(bad)
    it.clear()
    assert len(it) == 0 and it.stats() == {"calls": 0, "unique": 0}


def make_rows():
    return [{"cidade": "".join(["São ", "Paulo"]), "uf": "".join(["S", "P"]), "n": i, "tags": ("".join(["a", "b"]), "c")} for i in range(5)]


def test_dedupe_records(load_exercise):
    m = load_exercise("ex04_intern")
    rows = make_rows()
    assert m.distinct_objects(rows, "cidade") == 5 and m.distinct_objects(rows, "nada") == 0
    out = m.dedupe_records(rows)
    assert out == rows and m.distinct_objects(out, "cidade") == 1 and m.distinct_objects(out, "uf") == 1 and m.distinct_objects(out, "n") == 5
    assert out is not rows and out[0] is not rows[0] and m.distinct_objects(rows, "cidade") == 5            # originais intactos
    assert m.distinct_objects(out, "tags") == 1 and out[0]["tags"][0] is out[3]["tags"][0]
    assert len({id(k) for row in out for k in row if k == "cidade"}) == 1
    shared = m.Interner()
    first = m.dedupe_records(make_rows(), shared)
    second = m.dedupe_records(make_rows(), shared)
    assert first[0]["cidade"] is second[4]["cidade"] and shared.stats()["unique"] < shared.stats()["calls"]
    assert m.dedupe_records([]) == []


def test_duplication_report(load_exercise):
    m = load_exercise("ex04_intern")
    rows = make_rows() + [{"cidade": "Rio", "uf": "RJ", "n": 9, "nota": None}]
    assert m.duplication_report(rows) == {"cidade": (6, 2), "uf": (6, 2)}
    assert m.duplication_report([]) == {} and m.duplication_report([{"n": 1}]) == {}


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["flyweight_classico", "flyweight_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
