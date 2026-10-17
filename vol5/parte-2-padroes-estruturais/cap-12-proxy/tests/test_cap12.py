import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
class Doc:
    def __init__(self):
        self.title = "t"
        self.rows = [1, 2, 3]

    def total(self):
        return sum(self.rows)

    def __call__(self, x):
        return x * 2

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, *exc):
        self.exited = True
        return False


def test_lazy_proxy_loads_once_and_delegates(load_exercise):
    m = load_exercise("ex01_virtual_proxy")
    loads = []
    p = m.LazyProxy(lambda: loads.append(1) or Doc())
    assert not p.is_loaded and loads == []
    assert repr(p) == "<LazyProxy não carregado>" and loads == []                    # repr não carrega
    assert p.title == "t" and p.total() == 6 and p.is_loaded and loads == [1]
    p.title = "novo"
    assert p.unwrap().title == "novo" and p.rows is p.unwrap().rows
    del p.title
    assert not hasattr(p.unwrap(), "title")
    assert repr(p).startswith("<LazyProxy <") and p(4) == 8
    with p as inner:
        assert inner is p.unwrap()
    assert p.unwrap().entered and p.unwrap().exited and loads == [1]


def test_lazy_proxy_special_methods(load_exercise):
    m = load_exercise("ex01_virtual_proxy")
    p = m.LazyProxy(lambda: [10, 20, 30])
    assert len(p) == 3 and list(p) == [10, 20, 30] and p[1] == 20 and 20 in p and 99 not in p and bool(p) is True and str(p) == "[10, 20, 30]"
    p[0] = 11
    del p[2]
    assert p.unwrap() == [11, 20] and p == [11, 20] and [11, 20] == p.unwrap()
    assert isinstance(p, list) and p.__class__ is list and type(p).__name__ == "LazyProxy"
    assert p == m.LazyProxy(lambda: [11, 20])
    empty = m.LazyProxy(list)
    assert bool(empty) is False and not empty
    h = m.LazyProxy(lambda: "chave")
    assert hash(h) == hash("chave") and {h: 1}["chave"] == 1
    assert p.append(5) is None and p.unwrap() == [11, 20, 5]


def test_lazy_proxy_failure_reset_and_threads(load_exercise):
    m = load_exercise("ex01_virtual_proxy")
    attempts = []

    def factory():
        attempts.append(1)
        if len(attempts) == 1:
            raise OSError("sem arquivo")
        return [1]

    p = m.LazyProxy(factory)
    with pytest.raises(OSError):
        len(p)
    assert not p.is_loaded and len(p) == 1 and len(attempts) == 2
    p.reset()
    assert not p.is_loaded and len(p) == 1 and len(attempts) == 3
    calls = []

    def slow():
        time.sleep(0.02)
        calls.append(1)
        return [7]

    q = m.LazyProxy(slow)
    barrier = threading.Barrier(8)
    seen = []

    def work():
        barrier.wait()
        seen.append(q[0])

    threads = [threading.Thread(target=work) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert seen == [7] * 8 and len(calls) == 1


# ---------- ex02 ----------
class Store:
    def __init__(self):
        self.items = {"a": 1}
        self.version = 1
        self._secret = "s"

    def get(self, key):
        return self.items[key]

    def delete(self, key):
        return self.items.pop(key)


def test_protected_proxy(load_exercise):
    m = load_exercise("ex02_protection_proxy")
    store = Store()
    viewer = m.ProtectedProxy(store, "ana", {"viewer"}, {"delete": "admin", "version": "admin"})
    assert viewer.get("a") == 1 and viewer.items is store.items
    with pytest.raises(PermissionError, match="ana não pode acessar delete"):
        viewer.delete
    with pytest.raises(PermissionError, match="ana não pode acessar version"):
        viewer.version
    with pytest.raises(PermissionError, match="ana não pode alterar version"):
        viewer.version = 2
    viewer.items = {"b": 2}
    assert store.items == {"b": 2} and store.version == 1
    admin = m.ProtectedProxy(store, "root", {"admin"}, {"delete": "admin", "version": "admin"})
    assert admin.delete("b") == 2 and admin.version == 1
    admin.version = 9
    assert store.version == 9


def test_protected_proxy_audit_and_private(load_exercise):
    m = load_exercise("ex02_protection_proxy")
    p = m.ProtectedProxy(Store(), "bia", {"viewer"}, {"delete": "admin"})
    p.get("a")
    with pytest.raises(PermissionError):
        p.delete
    p.version = 3
    assert p.audit == [("bia", "get", "read", True), ("bia", "delete", "read", False), ("bia", "version", "write", True)]
    with pytest.raises(AttributeError, match="acesso a _secret bloqueado"):
        p._secret
    with pytest.raises(AttributeError, match="acesso a _x bloqueado"):
        p._x = 1
    assert len(p.audit) == 3                                                           # as tentativas "_" não entram
    assert p.can("get") is True and p.can("delete") is False and len(p.audit) == 3
    copy = p.audit
    copy.clear()
    assert len(p.audit) == 3


# ---------- ex03 ----------
class Service:
    def __init__(self):
        self.calls = []
        self.label = "svc"

    def slow(self, x, y=0):
        self.calls.append(("slow", x, y))
        return x + y

    def other(self, x):
        self.calls.append(("other", x))
        return x * 2

    def boom(self, x):
        self.calls.append(("boom", x))
        raise ValueError("falhou")


def test_caching_proxy_hits_and_passthrough(load_exercise):
    m = load_exercise("ex03_caching_proxy")
    svc = Service()
    p = m.CachingProxy(svc, ["slow"])
    assert p.slow(1, y=2) == 3 and p.slow(1, y=2) == 3 and p.slow(1, 2) == 3 and p.slow(y=2, x=1) == 3 and p.slow(x=1, y=2) == 3
    assert len(svc.calls) == 3
    assert p.stats == {"hits": 2, "misses": 3, "bypassed": 0}                         # argumentos posicionais e nomeados formam chaves diferentes; a ordem dos nomeados não importa
    assert p.other(5) == 10 and p.other(5) == 10 and svc.calls.count(("other", 5)) == 2     # não listado: sem cache
    assert p.label == "svc" and p.stats["hits"] == 2


def test_caching_proxy_bypass_errors_ttl_invalidate(load_exercise):
    m = load_exercise("ex03_caching_proxy")
    svc = Service()
    now = [0.0]
    p = m.CachingProxy(svc, ["slow", "boom"], ttl=10, clock=lambda: now[0])

    class Sum:
        def total(self, items):
            return sum(items)

    q = m.CachingProxy(Sum(), ["total"])
    assert q.total([1, 2]) == 3 and q.total([1, 2]) == 3 and q.stats == {"hits": 0, "misses": 0, "bypassed": 2}
    assert q.total((1, 2)) == 3 and q.total((1, 2)) == 3 and q.stats["hits"] == 1 and q.stats["misses"] == 1
    assert p.slow(1) == 1
    now[0] = 9.9
    assert p.slow(1) == 1 and p.stats["hits"] == 1
    now[0] = 10.0
    assert p.slow(1) == 1 and p.stats == {"hits": 1, "misses": 2, "bypassed": 0}       # venceu: recalculou
    for _ in range(2):
        with pytest.raises(ValueError):
            p.boom(1)
    assert svc.calls.count(("boom", 1)) == 2 and p.stats["misses"] == 4
    assert p.slow(2) == 2
    assert p.invalidate("slow") == 2 and p.invalidate("slow") == 0
    assert p.slow(1) == 1 and p.stats["misses"] == 6 and p.invalidate() == 1


def test_caching_proxy_validation_and_stats_copy(load_exercise):
    m = load_exercise("ex03_caching_proxy")
    svc = Service()
    with pytest.raises(AttributeError, match="nada"):
        m.CachingProxy(svc, ["nada"])
    with pytest.raises(ValueError, match="não é um método: label"):
        m.CachingProxy(svc, ["label"])
    p = m.CachingProxy(svc, ["slow"])
    p.stats["hits"] = 99
    assert p.stats["hits"] == 0
    assert p.slow.__name__ == "slow"


# ---------- ex04 ----------
def test_lazy_descriptor(load_exercise):
    m = load_exercise("ex04_descriptors")
    loads = []

    class Data:
        @m.lazy
        def rows(self):
            loads.append(1)
            return [1, 2, 3]

    d = Data()
    assert "rows" not in d.__dict__ and Data.rows.name == "rows" and isinstance(Data.rows, m.lazy)
    assert d.rows is d.rows and loads == [1] and "rows" in d.__dict__
    other = Data()
    assert other.rows is not d.rows and loads == [1, 1]
    d.rows = ["manual"]
    assert d.rows == ["manual"]
    del d.rows
    assert d.rows == [1, 2, 3] and len(loads) == 3
    assert m.reset_lazy(d, "rows") is True and m.reset_lazy(d, "rows") is False
    assert d.rows == [1, 2, 3] and len(loads) == 4


def test_lazy_descriptor_failure_not_cached(load_exercise):
    m = load_exercise("ex04_descriptors")
    attempts = []

    class Flaky:
        @m.lazy
        def value(self):
            attempts.append(1)
            if len(attempts) == 1:
                raise OSError("falhou")
            return 42

    f = Flaky()
    with pytest.raises(OSError):
        f.value
    assert f.value == 42 and f.value == 42 and len(attempts) == 2


def test_bounded_descriptor(load_exercise):
    m = load_exercise("ex04_descriptors")

    class Product:
        price = m.Bounded(minimum=0)
        stock = m.Bounded(0, 100, kind=int)

    p = Product()
    p.price = 9.5
    p.stock = 10
    assert p.price == 9.5 and p.stock == 10 and isinstance(Product.price, m.Bounded) and p.__dict__ == {"_price": 9.5, "_stock": 10}
    for bad in ("1", None, True, [1]):
        with pytest.raises(TypeError, match="price deve ser numérico"):
            p.price = bad
    with pytest.raises(TypeError, match="stock deve ser numérico"):
        p.stock = 1.5
    with pytest.raises(ValueError, match=r"price fora do intervalo \[0, None\]"):
        p.price = -1
    with pytest.raises(ValueError, match=r"stock fora do intervalo \[0, 100\]"):
        p.stock = 101
    p.stock = 100
    p.stock = 0
    assert p.stock == 0 and p.price == 9.5
    with pytest.raises(AttributeError, match="price não pode ser apagado"):
        del p.price
    with pytest.raises(AttributeError, match="price não foi definido"):
        Product().price
    q = Product()
    q.price = 1
    assert p.price == 9.5 and q.price == 1                                             # cada instância tem o seu valor


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["proxy_classico", "proxy_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
