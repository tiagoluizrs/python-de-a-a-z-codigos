import subprocess
import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_base_decorator_delegates(load_exercise):
    m = load_exercise("ex01_stream_decorators")
    sink = m.MemorySink()
    d = m.Decorator(sink)
    assert d.write(b"abc") == 3
    d.flush()
    d.close()
    assert sink.getvalue() == b"abc" and sink.flushes == 1 and sink.closed


def test_counting_and_prefix(load_exercise):
    m = load_exercise("ex01_stream_decorators")
    sink = m.MemorySink()
    counting = m.CountingSink(m.PrefixSink(sink, b"> "))
    assert counting.write(b"oi") == 2 and counting.write(b"tudo bem") == 8
    assert counting.count == 10 and counting.writes == 2 and counting.count == 10
    assert sink.getvalue() == b"> oi> tudo bem"
    sink2 = m.MemorySink()
    counter = m.CountingSink(sink2)
    m.PrefixSink(counter, b"> ").write(b"oi")
    assert sink2.getvalue() == b"> oi" and counter.count == 4                       # a ORDEM: o contador interno vê o prefixo


def test_limit_sink(load_exercise):
    m = load_exercise("ex01_stream_decorators")
    sink = m.MemorySink()
    limited = m.LimitSink(sink, 5)
    assert limited.write(b"abc") == 3 and limited.write(b"de") == 2                 # exatamente 5
    with pytest.raises(m.LimitExceeded, match="limite de 5 bytes"):
        limited.write(b"f")
    assert sink.getvalue() == b"abcde"
    limited2 = m.LimitSink(m.MemorySink(), 4)
    limited2.write(b"ab")
    with pytest.raises(m.LimitExceeded):
        limited2.write(b"cde")                                                       # nada daquela chamada é escrito
    assert limited2.write(b"cd") == 2


def test_buffered_sink(load_exercise):
    m = load_exercise("ex01_stream_decorators")
    sink = m.MemorySink()
    buffered = m.BufferedSink(sink, 5)
    assert buffered.write(b"ab") == 2 and buffered.write(b"cd") == 2
    assert sink.chunks == []
    assert buffered.write(b"ef") == 2
    assert sink.chunks == [b"abcdef"]                                                # UMA chamada, no write que completou o buffer
    buffered.write(b"gh")
    buffered.flush()
    assert sink.chunks == [b"abcdef", b"gh"] and sink.flushes == 1
    buffered.flush()
    assert sink.chunks == [b"abcdef", b"gh"] and sink.flushes == 2                   # nada a enviar, mas repassa o flush
    buffered.write(b"z")
    buffered.close()
    assert sink.getvalue() == b"abcdefghz" and sink.closed


def test_stacking_layers(load_exercise):
    m = load_exercise("ex01_stream_decorators")
    sink = m.MemorySink()
    stack = m.CountingSink(m.BufferedSink(m.PrefixSink(sink, b"#"), 4))
    for chunk in (b"ab", b"cd", b"e"):
        stack.write(chunk)
    stack.close()
    assert sink.getvalue() == b"#abcd#e" and stack.count == 5 and sink.closed and sink.chunks == [b"#abcd", b"#e"]


# ---------- ex02 ----------
def test_retry(load_exercise):
    m = load_exercise("ex02_function_decorators")
    calls, sleeps = [], []

    @m.retry(3, exceptions=(ConnectionError,), delay=0.5, sleep=sleeps.append)
    def flaky():
        """doc"""
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError("caiu")
        return "ok"

    assert flaky() == "ok" and len(calls) == 3 and sleeps == [0.5, 0.5] and flaky.attempts == 3
    assert flaky.__name__ == "flaky" and flaky.__doc__ == "doc" and flaky.__wrapped__ is not flaky

    @m.retry(2, exceptions=(ConnectionError,))
    def always():
        raise ConnectionError("x")

    with pytest.raises(ConnectionError):
        always()
    assert always.attempts == 2

    @m.retry(5, exceptions=(ConnectionError,))
    def other():
        raise KeyError("k")

    with pytest.raises(KeyError):
        other()
    assert other.attempts == 1
    with pytest.raises(ValueError):
        m.retry(0)


def test_timed(load_exercise):
    m = load_exercise("ex02_function_decorators")
    ticks = iter([0.0, 1.5, 10.0, 10.25, 20.0, 21.0])

    @m.timed(clock=lambda: next(ticks))
    def work(x):
        if x < 0:
            raise ValueError("negativo")
        return x * 2

    assert work.last() is None and work(2) == 4 and work.last() == 1.5
    assert work(3) == 6 and work.durations == [1.5, 0.25]
    with pytest.raises(ValueError):
        work(-1)
    assert work.durations == [1.5, 0.25, 1.0]


def test_memoize(load_exercise):
    m = load_exercise("ex02_function_decorators")
    calls = []

    @m.memoize
    def f(a, b=0):
        calls.append((a, b))
        return a + b

    assert f(1, 2) == 3 and f(1, 2) == 3 and f(1, b=2) == 3 and len(calls) == 2
    assert (f.hits, f.misses) == (1, 2)
    assert f(b=2, a=1) == 3 and f(a=1, b=2) == 3 and len(calls) == 3 and (f.hits, f.misses) == (2, 3)
    f.cache_clear()
    assert (f.hits, f.misses) == (0, 0)
    f(1, 2)
    assert f.misses == 1
    with pytest.raises(TypeError):
        f([1])                                                                       # não hashable

    @m.memoize
    def boom(x):
        calls.append("boom")
        raise ValueError("x")

    for _ in range(2):
        with pytest.raises(ValueError):
            boom(1)
    assert calls.count("boom") == 2                                                  # exceções NÃO são guardadas
    assert f.__name__ == "f"


def test_memoize_kwargs_order(load_exercise):
    m = load_exercise("ex02_function_decorators")

    @m.memoize
    def f(a, b):
        return a * b

    f(a=2, b=3)
    f(b=3, a=2)
    assert (f.hits, f.misses) == (1, 1)


def test_deprecated(load_exercise):
    m = load_exercise("ex02_function_decorators")
    seen = []

    @m.deprecated("use g()", warn=seen.append)
    def old(x):
        """Original."""
        return x + 1

    assert old(1) == 2 and seen == ["old está obsoleta: use g()"] and old.__doc__ == "Original." and old.__name__ == "old"

    @m.deprecated("use h()")
    def older():
        return 1

    with pytest.warns(DeprecationWarning, match="older está obsoleta: use h"):
        assert older() == 1
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        older()
    assert caught[0].filename == __file__                                            # stacklevel=2: aponta para quem chamou


# ---------- ex03 ----------
def test_auto_repr(load_exercise):
    m = load_exercise("ex03_class_decorators")

    @m.auto_repr
    class P:
        def __init__(self, x, y):
            self.y, self.x = y, x

    class Sub(P):
        pass

    assert repr(P(1, "a")) == "P(x=1, y='a')" and repr(Sub(2, 3)) == "Sub(x=2, y=3)"

    @m.auto_repr
    class Custom:
        def __repr__(self):
            return "meu"

    assert repr(Custom()) == "meu"
    assert m.auto_repr(P) is P


def test_register_in(load_exercise):
    m = load_exercise("ex03_class_decorators")
    registry = {}

    @m.register_in(registry)
    class A:
        pass

    @m.register_in(registry, name="bee")
    class B:
        pass

    assert registry == {"A": A, "bee": B} and A().__class__ is A
    with pytest.raises(ValueError, match="nome já registrado: A"):
        m.register_in(registry)(type("A", (), {}))


def test_write_once(load_exercise):
    m = load_exercise("ex03_class_decorators")

    @m.write_once("id", "created")
    class Entity:
        def __init__(self, id):
            self.id = id
            self.created = "hoje"
            self.name = "n"

    e = Entity(1)
    e.name = "outro"
    e.tags = []
    with pytest.raises(AttributeError, match="id já foi definido"):
        e.id = 2
    with pytest.raises(AttributeError, match="created não pode ser apagado"):
        del e.created
    del e.name
    assert e.id == 1 and not hasattr(e, "name")

    class Child(Entity):
        pass

    c = Child(5)
    with pytest.raises(AttributeError):
        c.id = 6


def test_add_methods(load_exercise):
    m = load_exercise("ex03_class_decorators")

    @m.add_methods(double=lambda self: self.n * 2, triple=lambda self: self.n * 3)
    class N:
        def __init__(self, n):
            self.n = n

    assert N(2).double() == 4 and N(2).triple() == 6
    class Z:
        def double(self):
            return 0

    with pytest.raises(ValueError, match="double já existe em Z"):
        m.add_methods(fresh=lambda self: 1, double=lambda self: 2)(Z)
    assert not hasattr(Z, "fresh")
    with pytest.raises(ValueError, match="__repr__ já existe em Q"):
        m.add_methods(__repr__=lambda self: "x")(type("Q", (), {}))                  # herdado de object também conta


# ---------- ex04 ----------
def test_stack_and_labeled(load_exercise):
    m = load_exercise("ex04_stacking")
    log = []

    def f():
        log.append("f")

    m.stack(f, m.labeled("A", log), m.labeled("B", log))()
    assert log == ["entra A", "entra B", "f", "sai B", "sai A"]
    assert m.stack(f) is f


def test_labeled_on_exception_and_identity(load_exercise):
    m = load_exercise("ex04_stacking")
    log = []

    @m.labeled("X", log)
    def boom():
        """doc"""
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        boom()
    assert log == ["entra X", "sai X"] and boom.__name__ == "boom" and boom.__doc__ == "doc"


def test_explain_order_and_chain(load_exercise):
    m = load_exercise("ex04_stacking")
    assert m.explain_order(["A", "B"]) == ["entra A", "entra B", "f", "sai B", "sai A"]
    assert m.explain_order(["A", "B", "C"]) == ["entra A", "entra B", "entra C", "f", "sai C", "sai B", "sai A"]
    assert m.explain_order([]) == ["f"]
    log = []

    def base():
        pass

    wrapped = m.stack(base, m.labeled("A", log), m.labeled("B", log))
    chain = m.unwrap_chain(wrapped)
    assert chain[0] is wrapped and chain[-1] is base and len(chain) == 3 and m.count_layers(wrapped) == 2
    assert m.unwrap_chain(base) == [base] and m.count_layers(base) == 0


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["decorator_classico", "decorator_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
