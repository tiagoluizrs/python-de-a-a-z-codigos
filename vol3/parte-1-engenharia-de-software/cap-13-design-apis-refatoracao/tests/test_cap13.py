import inspect
import types
import warnings

import pytest


def f_old(url, timeout, /, retries=3, *, verbose=False):
    pass


def make(src):
    namespace = {}
    exec(src, namespace)
    return namespace["f"]


def changes(load_exercise, old_src, new_src):
    return load_exercise("ex01_signature_compat").breaking_changes(make(old_src), make(new_src))


OLD = "def f(url, timeout, retries=3, *, verbose=False): pass"


@pytest.mark.parametrize("new, expected", [
    ("def f(url, timeout, retries=3, *, verbose=False, extra=1): pass", []),
    ("def f(url, timeout, retries=5, *, verbose=True): pass", []),
    ("def f(url, timeout, retries=3, *, verbose=False, **kw): pass", []),
    ("def f(url, timeout, retries=3, *, verbose=False, flag): pass", ["new-required: flag"]),
    ("def f(url, timeout, retries=3): pass", ["removed: verbose"]),
    ("def f(timeout, url, retries=3, *, verbose=False): pass", ["reordered: timeout", "reordered: url"]),
    ("def f(url, seconds, retries=3, *, verbose=False): pass", ["new-required: seconds", "removed: timeout"]),
    ("def f(url, timeout, *, retries=3, verbose=False): pass", ["kind: retries"]),
    ("def f(url, timeout, retries, *, verbose=False): pass", ["lost-default: retries"]),
    ("def f(url, timeout, retries=3, verbose=False): pass", []),
    ("def f(url, timeout, retries=3, *, verbose=False, **kw): pass", []),
])
def test_breaking_changes(load_exercise, new, expected):
    assert changes(load_exercise, OLD, new) == expected


def test_breaking_changes_kwonly_absorbed_and_identical(load_exercise):
    assert changes(load_exercise, "def f(a, *, b=1): pass", "def f(a, **kw): pass") == []
    assert changes(load_exercise, "def f(a, b): pass", "def f(a, b): pass") == []
    assert changes(load_exercise, "def f(a, b): pass", "def f(a): pass") == ["removed: b"]


def test_deprecated_decorator(load_exercise):
    deprecated = load_exercise("ex02_deprecation").deprecated

    @deprecated("2.1", "3.0", alternative="new_api()")
    def old(x):
        """Faz algo."""
        return x * 2

    assert old.__name__ == "old" and old.__doc__ == "Faz algo.\n\nObsoleta desde 2.1."
    with pytest.warns(DeprecationWarning) as record:
        assert old(4) == 8
    assert str(record[0].message) == "old está obsoleta desde 2.1 e será removida na 3.0; use new_api()"
    assert record[0].filename == __file__                          # stacklevel=2: aponta para o chamador

    @deprecated("1.0", "2.0")
    def bare():
        pass

    assert bare.__doc__ == "\n\nObsoleta desde 1.0."
    with pytest.warns(DeprecationWarning, match="bare está obsoleta desde 1.0 e será removida na 2.0$"):
        bare()


def test_renamed_parameter(load_exercise):
    renamed = load_exercise("ex02_deprecation").renamed_parameter

    @renamed("timeout", "seconds", since="1.4")
    def wait(seconds=5):
        return seconds

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert wait(seconds=3) == 3 and wait() == 5 and wait(2) == 2
    with pytest.warns(DeprecationWarning, match="parâmetro 'timeout' foi renomeado para 'seconds' na versão 1.4") as record:
        assert wait(timeout=9) == 9
    assert record[0].filename == __file__
    with pytest.raises(TypeError, match="não use 'timeout' e 'seconds' juntos"):
        wait(timeout=1, seconds=2)


def test_options_value_object(load_exercise):
    m = load_exercise("ex03_options")
    o = m.Options()
    assert (o.method, o.timeout, o.retries, o.verify, o.headers, o.proxy, o.follow) == ("GET", 10.0, 3, True, (), None, True)
    assert m.Options(method="post").method == "POST"
    with pytest.raises(Exception):
        o.timeout = 1                                               # congelada
    for kwargs in ({"timeout": 0}, {"timeout": -1}, {"retries": -1}, {"method": "FETCH"}):
        with pytest.raises(ValueError):
            m.Options(**kwargs)


def test_options_with_and_legacy(load_exercise):
    m = load_exercise("ex03_options")
    base = m.Options(retries=5)
    new = base.with_(timeout=2.5, method="put")
    assert new is not base and (new.retries, new.timeout, new.method) == (5, 2.5, "PUT") and base.timeout == 10.0
    with pytest.raises(TypeError, match="opção desconhecida: 'tmieout'"):
        base.with_(tmieout=1)
    legacy = m.request_legacy("http://x", "POST", 2.0, 1, False, {"A": "1"}, "proxy:80", False)
    options = m.Options.from_legacy(method="POST", timeout=2.0, retries=1, verify=False, headers={"A": "1"}, proxy="proxy:80", follow=False)
    assert options.headers == (("A", "1"),)
    assert (legacy[0], *legacy[1:]) == ("http://x", options.method, options.timeout, options.retries, options.verify, options.headers, options.proxy, options.follow)


def test_request_with_options(load_exercise):
    m = load_exercise("ex03_options")
    url, final = m.request("http://x")
    assert url == "http://x" and final == m.Options()
    url, final = m.request("http://x", options=m.Options(retries=1), timeout=3.0)
    assert (final.retries, final.timeout) == (1, 3.0)
    with pytest.raises(TypeError):
        m.request("http://x", nope=1)
    with pytest.raises(ValueError):
        m.request("http://x", timeout=0)
    with pytest.raises(TypeError):
        m.request("http://x", m.Options())                           # options é só-nomeado


def test_result_ok_err(load_exercise):
    m = load_exercise("ex04_result")
    ok, err = m.Ok(2), m.Err("x")
    assert ok.is_ok and not ok.is_err and err.is_err and not err.is_ok
    assert ok.unwrap() == 2 and ok.unwrap_or(9) == 2 and err.unwrap_or(9) == 9
    assert ok.map(lambda v: v + 1) == m.Ok(3) and err.map(lambda v: v + 1) == err
    assert ok.and_then(lambda v: m.Ok(v * 10)) == m.Ok(20) and ok.and_then(lambda v: m.Err("falhou")) == m.Err("falhou")
    assert err.and_then(lambda v: m.Ok(1)) == err and err.map_err(str.upper) == m.Err("X") and ok.map_err(str.upper) == ok
    assert repr(ok) == "Ok(2)" and repr(err) == "Err('x')" and m.Ok(1) != m.Err(1) and m.Ok(1) != m.Ok(2)
    with pytest.raises(RuntimeError, match="unwrap em Err: 'x'"):
        err.unwrap()
    with pytest.raises(AttributeError):
        ok.value = 5


def test_try_call_and_collect(load_exercise):
    m = load_exercise("ex04_result")
    assert m.try_call(int, "7") == m.Ok(7)
    result = m.try_call(int, "x")
    assert result.is_err and isinstance(result.error, ValueError)
    assert m.try_call(lambda: 1 / 0, catch=(ZeroDivisionError,)).is_err
    with pytest.raises(ZeroDivisionError):
        m.try_call(lambda: 1 / 0, catch=(ValueError,))
    assert m.try_call(pow, 2, 3, mod=5) == m.Ok(3)
    assert m.collect([m.Ok(1), m.Ok(2)]) == m.Ok([1, 2]) and m.collect([]) == m.Ok([])
    first = m.Err("a")
    assert m.collect([m.Ok(1), first, m.Err("b")]) is first
    chained = m.try_call(int, "12").map(lambda n: n * 2).and_then(lambda n: m.Ok(n + 1))
    assert chained == m.Ok(25)


def test_capture_and_diff(load_exercise):
    m = load_exercise("ex05_characterize")

    def f(a, b):
        if b == 0:
            raise ZeroDivisionError("zero!")
        return a / b

    inputs = [(1, 2), (1, 0), (4, 2)]
    master = m.capture(f, inputs)
    assert master == {(1, 2): 0.5, (1, 0): "ZeroDivisionError: zero!", (4, 2): 2.0} and list(master) == inputs
    other = {(1, 2): 0.5, (1, 0): "outro", (9, 9): 1}
    assert m.diff_masters(master, other) == {"changed": {(1, 0): ("ZeroDivisionError: zero!", "outro")}, "missing": [(4, 2)], "extra": [(9, 9)]}
    assert m.diff_masters(master, master) == {"changed": {}, "missing": [], "extra": []}


def test_refactor_is_safe(load_exercise):
    m = load_exercise("ex05_characterize")

    def old(n):
        if n < 0:
            raise ValueError("negativo")
        return n * (n + 1) // 2

    def good(n):
        if n < 0:
            raise ValueError("negativo")
        return sum(range(n + 1))

    def wrong_message(n):
        if n < 0:
            raise ValueError("n < 0")
        return n * (n + 1) // 2

    def wrong_value(n):
        return good(n) + (n > 100)

    inputs = [(i,) for i in (-1, 0, 1, 5, 101)]
    assert m.refactor_is_safe(old, good, inputs) == (True, {})
    ok, diff = m.refactor_is_safe(old, wrong_message, inputs)
    assert ok is False and diff == {(-1,): ("ValueError: negativo", "ValueError: n < 0")}
    ok, diff = m.refactor_is_safe(old, wrong_value, [(1,), (101,)])
    assert ok is False and list(diff) == [(101,)]


def build_module(name, src):
    module = types.ModuleType(name)
    exec(src, module.__dict__)
    for obj in list(vars(module).values()):
        if inspect.isfunction(obj) or inspect.isclass(obj):
            obj.__module__ = name
    return module


V1 = """
import os
def connect(url, *, timeout=10): pass
def helper(): pass
def _private(): pass
class Client:
    def __init__(self, url): pass
CONSTANT = 3
"""


def test_public_api(load_exercise):
    m = load_exercise("ex06_public_api_diff")
    assert m.public_api(build_module("lib", V1)) == {"connect": "(url, *, timeout=10)", "helper": "()", "Client": "(url)"}
    with_all = build_module("lib", V1 + "__all__ = ['connect', 'Client', 'ghost']")
    assert m.public_api(with_all) == {"connect": "(url, *, timeout=10)", "Client": "(url)"}


def test_diff_api_and_bump(load_exercise):
    m = load_exercise("ex06_public_api_diff")
    old = m.public_api(build_module("lib", V1))
    same = m.public_api(build_module("lib", V1))
    assert m.diff_api(old, same) == {"removed": [], "added": [], "changed": []} and m.required_bump(m.diff_api(old, same)) == "patch"
    added = m.public_api(build_module("lib", V1 + "def extra(x): pass"))
    assert m.diff_api(old, added) == {"removed": [], "added": ["extra"], "changed": []} and m.required_bump(m.diff_api(old, added)) == "minor"
    changed = m.public_api(build_module("lib", V1.replace("timeout=10", "timeout=10, retries=3")))
    assert m.diff_api(old, changed)["changed"] == ["connect"] and m.required_bump(m.diff_api(old, changed)) == "major"
    removed = m.public_api(build_module("lib", V1.replace("def helper(): pass", "")))
    assert m.diff_api(old, removed) == {"removed": ["helper"], "added": [], "changed": []} and m.required_bump(m.diff_api(old, removed)) == "major"
    mixed = {"removed": [], "added": ["a"], "changed": ["b"]}
    assert m.required_bump(mixed) == "major"
