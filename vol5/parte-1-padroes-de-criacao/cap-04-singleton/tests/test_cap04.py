import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def hammer(fn, threads=8):
    barrier = threading.Barrier(threads)
    found, errors = [], []

    def work():
        barrier.wait()
        try:
            found.append(fn())
        except BaseException as error:
            errors.append(error)

    workers = [threading.Thread(target=work) for _ in range(threads)]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    return found, errors


# ---------- ex01 ----------
def test_config_identity_and_state(load_exercise):
    m = load_exercise("ex01_singleton_new")
    m.Config.reset_for_tests()
    a = m.Config({"debug": True})
    b = m.Config()
    assert a is b and b.get("debug") is True and b.get("x", 7) == 7
    b.set("x", 1)
    assert m.Config().get("x") == 1 and m.Config().get("debug") is True      # o estado sobrevive às novas chamadas
    with pytest.raises(ValueError, match="Config já foi criada; use set"):
        m.Config({"outro": 1})
    m.Config.reset_for_tests()


def test_config_copies_values_and_resets(load_exercise):
    m = load_exercise("ex01_singleton_new")
    m.Config.reset_for_tests()
    source = {"a": 1}
    c = m.Config(source)
    source["a"] = 99
    assert c.get("a") == 1
    before = m.Config.created
    m.Config.reset_for_tests()
    d = m.Config({"b": 2})
    assert d is not c and d.get("a") is None and d.get("b") == 2
    assert m.Config.created == before + 1
    m.Config.reset_for_tests()


def test_config_subclasses_have_their_own(load_exercise):
    m = load_exercise("ex01_singleton_new")

    class Sub(m.Config):
        pass

    m.Config.reset_for_tests()
    Sub.reset_for_tests()
    base = m.Config({"k": "base"})
    sub = Sub({"k": "sub"})
    assert sub is Sub() and sub is not base and base is m.Config()
    assert base.get("k") == "base" and sub.get("k") == "sub"
    assert Sub.created == 1
    m.Config.reset_for_tests()
    Sub.reset_for_tests()
    assert Sub() is not sub


# ---------- ex02 ----------
def test_singleton_decorator_basics(load_exercise):
    m = load_exercise("ex02_thread_safe")
    inits = []

    @m.singleton
    class Pool:
        def __init__(self, size=4):
            inits.append(size)
            self.size = size

    a, b = Pool(8), Pool(2)
    assert a is b and a.size == 8 and inits == [8]
    assert isinstance(a, Pool) and Pool.singleton_created() == 1
    Pool.reset_singleton()
    c = Pool(3)
    assert c is not a and c.size == 3 and inits == [8, 3] and Pool.singleton_created() == 2


def test_singleton_decorator_threads(load_exercise):
    m = load_exercise("ex02_thread_safe")
    inits = []

    @m.singleton
    class Slow:
        def __init__(self):
            time.sleep(0.02)
            inits.append(1)
            self.ready = True

    found, errors = hammer(Slow)
    assert not errors and len(inits) == 1 and len({id(x) for x in found}) == 1
    assert all(x.ready for x in found)


def test_singleton_decorator_failure_not_cached(load_exercise):
    m = load_exercise("ex02_thread_safe")
    attempts = []

    @m.singleton
    class Flaky:
        def __init__(self):
            attempts.append(1)
            if len(attempts) == 1:
                raise RuntimeError("falhou")

    with pytest.raises(RuntimeError):
        Flaky()
    ok = Flaky()
    assert Flaky() is ok and len(attempts) == 2


# ---------- ex03 ----------
def test_getter_lazy_and_cached(load_exercise):
    m = load_exercise("ex03_lazy_getter")
    calls = []
    get = m.make_getter(lambda: calls.append(1) or {"v": 1})
    assert not get.is_loaded() and calls == []
    first = get()
    assert get() is first and get.is_loaded() and len(calls) == 1
    get.cache_clear()
    assert not get.is_loaded()
    assert get() is not first and len(calls) == 2


def test_getter_none_is_a_value_and_errors_not_cached(load_exercise):
    m = load_exercise("ex03_lazy_getter")
    calls = []
    get_none = m.make_getter(lambda: calls.append(1))
    assert get_none() is None and get_none() is None and len(calls) == 1 and get_none.is_loaded()
    attempts = []

    def loader():
        attempts.append(1)
        if len(attempts) == 1:
            raise OSError("sem rede")
        return "ok"

    get = m.make_getter(loader)
    with pytest.raises(OSError):
        get()
    assert not get.is_loaded()
    assert get() == "ok" and len(attempts) == 2


def test_getter_threads(load_exercise):
    m = load_exercise("ex03_lazy_getter")
    calls = []

    def loader():
        time.sleep(0.02)
        calls.append(1)
        return object()

    get = m.make_getter(loader)
    found, errors = hammer(get)
    assert not errors and len(calls) == 1 and len({id(x) for x in found}) == 1


# ---------- ex04 ----------
def test_borg_shares_state(load_exercise):
    m = load_exercise("ex04_borg")

    class Config1(m.Borg):
        pass

    class Config2(m.Borg):
        pass

    a, b = Config1(), Config1()
    a.color = "azul"
    assert a is not b and b.color == "azul" and a == b and hash(a) == hash(b)
    c = Config2()
    assert not hasattr(c, "color") and a != c
    c.color = "verde"
    assert a.color == "azul"
    Config1.reset_state()
    assert not hasattr(a, "color") and not hasattr(b, "color") and c.color == "verde"
    base = m.Borg()
    base.x = 1
    assert m.Borg().x == 1 and not hasattr(Config1(), "x")
    m.Borg.reset_state()


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["singleton_classico", "singleton_pythonico", "singleton_processos"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()


def test_classic_example_shows_the_race():
    r = subprocess.run([sys.executable, "singleton_classico.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    sem_trava = next(l for l in r.stdout.splitlines() if l.startswith("sem trava:"))
    created = int(sem_trava.split()[2])
    assert created > 1                                    # a corrida existe de verdade
    assert "com trava e dupla verificação: 1 instância criada" in r.stdout
