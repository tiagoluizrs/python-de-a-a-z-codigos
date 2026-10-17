import inspect
import warnings

import pytest


# ---- ex01 ---------------------------------------------------------
def test_make_multipliers(load_exercise):
    make = load_exercise("ex01_closures").make_multipliers
    assert [f(10) for f in make(3)] == [0, 10, 20]
    assert make(0) == []
    fns = make(5)
    assert [fns[i](2) for i in range(5)] == [0, 2, 4, 6, 8]


def test_make_accumulator(load_exercise):
    make = load_exercise("ex01_closures").make_accumulator
    add, total, reset = make(10)
    assert total() == 10
    assert add(5) == 15
    assert add(1) == 16
    assert total() == 16
    assert reset() is None
    assert total() == 10


def test_accumulators_are_independent(load_exercise):
    make = load_exercise("ex01_closures").make_accumulator
    add1, total1, _ = make()
    add2, total2, _ = make()
    add1(5)
    assert (total1(), total2()) == (5, 0)


# ---- ex02 ---------------------------------------------------------
def test_timer(load_exercise):
    import time
    timer = load_exercise("ex02_timer_retry").timer

    @timer
    def nap(x):
        """Dorme um pouco."""
        time.sleep(0.01)
        return x

    assert nap.last_elapsed is None
    assert nap(7) == 7
    assert nap.last_elapsed >= 0.009
    assert nap.__name__ == "nap" and nap.__doc__ == "Dorme um pouco."


def test_timer_records_on_exception(load_exercise):
    timer = load_exercise("ex02_timer_retry").timer

    @timer
    def boom():
        raise KeyError("x")

    with pytest.raises(KeyError):
        boom()
    assert boom.last_elapsed is not None


def test_retry_succeeds_after_failures(load_exercise):
    retry = load_exercise("ex02_timer_retry").retry
    sleeps, calls = [], []

    @retry(4, (ConnectionError,), delay=1, backoff=2, sleep=sleeps.append)
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError
        return "ok"

    assert flaky() == "ok"
    assert len(calls) == 3
    assert sleeps == [1, 2]
    assert flaky.__name__ == "flaky"


def test_retry_gives_up_and_raises_last(load_exercise):
    retry = load_exercise("ex02_timer_retry").retry
    sleeps = []

    @retry(3, (ValueError,), delay=1, backoff=3, sleep=sleeps.append)
    def always():
        raise ValueError("nope")

    with pytest.raises(ValueError, match="nope"):
        always()
    assert sleeps == [1, 3]   # nenhuma espera depois da última


def test_retry_ignores_other_exceptions(load_exercise):
    retry = load_exercise("ex02_timer_retry").retry
    sleeps, calls = [], []

    @retry(5, (ConnectionError,), sleep=sleeps.append)
    def wrong():
        calls.append(1)
        raise ValueError

    with pytest.raises(ValueError):
        wrong()
    assert len(calls) == 1 and sleeps == []


# ---- ex03 ---------------------------------------------------------
def test_memoize_hits_and_expiry(load_exercise):
    memoize = load_exercise("ex03_memoize_ttl").memoize
    now, calls = [0.0], []

    @memoize(10, clock=lambda: now[0])
    def square(n, scale=1):
        """Quadrado."""
        calls.append(n)
        return n * n * scale

    assert square(3) == 9 and square(3) == 9
    assert calls == [3]
    now[0] = 9.9
    square(3)
    assert calls == [3]
    now[0] = 10.0
    square(3)
    assert calls == [3, 3]
    assert square.__name__ == "square" and square.__doc__ == "Quadrado."


def test_memoize_keys_and_clear(load_exercise):
    memoize = load_exercise("ex03_memoize_ttl").memoize
    calls = []

    @memoize(100, clock=lambda: 0.0)
    def f(a, b=0, c=0):
        calls.append((a, b, c))
        return a + b + c

    f(1, b=2, c=3)
    f(1, c=3, b=2)       # mesma chamada, outra ordem
    assert len(calls) == 1
    f(1, 2, 3)           # posicional != nomeado: chave diferente
    assert len(calls) == 2
    assert f.cache_size() == 2
    f.cache_clear()
    assert f.cache_size() == 0


def test_memoize_does_not_cache_exceptions(load_exercise):
    memoize = load_exercise("ex03_memoize_ttl").memoize
    calls = []

    @memoize(100, clock=lambda: 0.0)
    def risky(x):
        calls.append(x)
        if len(calls) == 1:
            raise RuntimeError
        return x

    with pytest.raises(RuntimeError):
        risky(1)
    assert risky(1) == 1
    assert risky.cache_size() == 1


# ---- ex04 ---------------------------------------------------------
def test_register_and_run(load_exercise):
    mod = load_exercise("ex04_registry_deprecated")
    mod.PLUGINS.clear()

    @mod.register("up")
    def up(text):
        return text.upper()

    assert mod.PLUGINS["up"] is up          # sem embrulho
    assert mod.run("up", "abc") == "ABC"
    with pytest.raises(KeyError, match="unknown plugin: nope"):
        mod.run("nope")
    with pytest.raises(ValueError):
        mod.register("up")(lambda: None)


def test_deprecated(load_exercise):
    deprecated = load_exercise("ex04_registry_deprecated").deprecated

    @deprecated("use new()")
    def old(x):
        """Antiga."""
        return x + 1

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert old(1) == 2
    assert len(caught) == 1
    w = caught[0]
    assert issubclass(w.category, DeprecationWarning)
    assert str(w.message) == "old is deprecated: use new()"
    assert w.filename == __file__          # aponta para o chamador
    assert old.__name__ == "old" and old.__doc__ == "Antiga."


# ---- ex05 ---------------------------------------------------------
def test_validate_types(load_exercise):
    validate_types = load_exercise("ex05_validate_types").validate_types

    @validate_types
    def create(name: str, age: int, tags: list[str] | None = None,
               active: bool = True, extra=None) -> str:
        """Cria."""
        return f"{name}:{age}"

    assert create("ana", 30) == "ana:30"
    assert create(name="bia", age=1, extra=object()) == "bia:1"
    with pytest.raises(TypeError, match="age must be int, got str"):
        create("ana", "30")
    with pytest.raises(TypeError, match="name must be str, got int"):
        create(name=1, age=2)
    assert create("x", True) == "x:True"     # bool é int
    assert create.__name__ == "create" and create.__doc__ == "Cria."
    assert inspect.signature(create).parameters["age"].annotation is int


def test_validate_types_checks_defaults_and_binding(load_exercise):
    validate_types = load_exercise("ex05_validate_types").validate_types

    @validate_types
    def f(a: int, b: str = 5):          # padrão com tipo errado
        return a

    with pytest.raises(TypeError, match="b must be str, got int"):
        f(1)
    with pytest.raises(TypeError):       # falta argumento: erro do bind
        f()
