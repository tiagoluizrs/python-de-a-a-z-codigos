import gc
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_signal_basics(load_exercise):
    m = load_exercise("ex01_signal")
    sig = m.Signal()
    calls = []

    @sig.connect
    def a(x, y=None):
        calls.append(("a", x))

    b = sig.connect(lambda x, y=0: calls.append(("b", x, y)))
    assert len(sig) == 2 and a in sig and b in sig and sig.emit(1, y=2) == 2
    assert calls == [("a", 1), ("b", 1, 2)]
    sig.disconnect(a)
    assert a not in sig and sig.emit(3) == 1
    with pytest.raises(ValueError, match="não conectado"):
        sig.disconnect(a)
    with pytest.raises(ValueError, match="já conectado"):
        sig.connect(b)
    with pytest.raises(TypeError, match="observador precisa ser chamável"):
        sig.connect("x")
    assert m.Signal().emit() == 0


def test_signal_once_and_copy(load_exercise):
    m = load_exercise("ex01_signal")
    sig = m.Signal()
    log = []
    sig.connect(lambda: log.append("um"), once=True)
    sig.connect(lambda: log.append("fixo"))
    sig.emit()
    sig.emit()
    assert log == ["um", "fixo", "fixo"] and len(sig) == 1

    @sig.connect(once=True)
    def decorated():
        log.append("decorado")

    sig.emit()
    sig.emit()
    assert log.count("decorado") == 1 and decorated not in sig
    sig2 = m.Signal()
    order = []

    def quitter():
        order.append("quitter")
        sig2.disconnect(second)

    def second():
        order.append("second")

    def late():
        order.append("late")

    def adder():
        order.append("adder")
        sig2.connect(late)

    sig2.connect(quitter)
    sig2.connect(second)
    sig2.connect(adder)
    assert sig2.emit() == 3 and order == ["quitter", "second", "adder"]                # second ainda foi chamado; late só na próxima
    assert len(sig2) == 3 and late in sig2


def test_signal_exception_group(load_exercise):
    m = load_exercise("ex01_signal")
    sig = m.Signal()
    seen = []

    def bad1():
        raise ValueError("um")

    def bad2():
        raise KeyError("dois")

    sig.connect(bad1)
    sig.connect(lambda: seen.append("ok1"))
    sig.connect(bad2)
    sig.connect(lambda: seen.append("ok2"))
    with pytest.raises(ExceptionGroup) as info:
        sig.emit()
    assert seen == ["ok1", "ok2"] and info.value.message == "observadores falharam"
    assert [type(e) for e in info.value.exceptions] == [ValueError, KeyError]


# ---------- ex02 ----------
class Listener:
    def __init__(self):
        self.got = []

    def on_event(self, value):
        self.got.append(value)

    def other(self, value):
        self.got.append(("other", value))


def test_weak_signal_collects_dead_owners(load_exercise):
    m = load_exercise("ex02_weak_signal")
    sig = m.WeakSignal()
    l1, l2 = Listener(), Listener()
    sig.connect(l1.on_event)
    sig.connect(l2.on_event)
    assert len(sig) == 2 and sig.emit(1) == 2 and l1.got == [1] and l2.got == [1]
    del l1
    gc.collect()
    assert len(sig) == 1 and sig.emit(2) == 1 and l2.got == [1, 2]
    del l2
    gc.collect()
    assert len(sig) == 0 and sig.emit(3) == 0


def test_weak_signal_functions_strong_and_errors(load_exercise):
    m = load_exercise("ex02_weak_signal")
    sig = m.WeakSignal()
    log = []
    sig.connect(lambda v: log.append(v))                                                # nada mais referencia a lambda: ela precisa sobreviver
    gc.collect()
    assert len(sig) == 1 and sig.emit(5) == 1 and log == [5]
    listener = Listener()
    sig.connect(listener.on_event)
    with pytest.raises(ValueError, match="já conectado"):
        sig.connect(listener.on_event)
    sig.connect(listener.other)
    assert len(sig) == 3
    sig.disconnect(listener.on_event)
    assert len(sig) == 2
    with pytest.raises(ValueError, match="não conectado"):
        sig.disconnect(listener.on_event)
    with pytest.raises(TypeError):
        sig.connect(3)
    boom = m.WeakSignal()
    seen = []

    def bad(v):
        raise RuntimeError("falhou")

    boom.connect(bad)
    boom.connect(seen.append)
    with pytest.raises(RuntimeError, match="falhou"):
        boom.emit(1)
    assert seen == [1]


# ---------- ex03 ----------
def test_observed_descriptor(load_exercise):
    m = load_exercise("ex03_observable")

    class Ticker:
        price = m.observed(default=0)
        name = m.observed(default="?")

    t = Ticker()
    events = []
    assert t.price == 0 and isinstance(Ticker.price, m.observed)
    m.watch(t, "price", lambda obj, name, old, new: events.append((name, old, new)))
    t.price = 10
    t.price = 10                                                                        # igual: não avisa
    t.price = 12
    assert events == [("price", 0, 10), ("price", 10, 12)] and t.price == 12
    t.name = "x"                                                                        # outro atributo, sem observadores
    assert len(events) == 2
    other = Ticker()
    other.price = 99
    assert len(events) == 2 and t.price == 12                                           # por instância


def test_watch_order_unwatch_and_errors(load_exercise):
    m = load_exercise("ex03_observable")

    class Box:
        value = m.observed(default=1)
        plain = 5

    box = Box()
    order = []
    f = m.watch(box, "value", lambda *a: order.append("f"))
    g = m.watch(box, "value", lambda *a: order.append("g"))
    box.value = 2
    assert order == ["f", "g"]
    m.unwatch(box, "value", f)
    box.value = 3
    assert order == ["f", "g", "g"]
    with pytest.raises(ValueError, match="não registrado"):
        m.unwatch(box, "value", f)
    with pytest.raises(AttributeError, match="'plain' não é observável"):
        m.watch(box, "plain", g)
    with pytest.raises(AttributeError, match="'nada' não é observável"):
        m.watch(box, "nada", g)
    with pytest.raises(TypeError):
        m.watch(box, "value", 3)

    class Sub(Box):
        pass

    sub = Sub()
    seen = []
    m.watch(sub, "value", lambda *a: seen.append(a[2:]))
    sub.value = 7
    assert seen == [(1, 7)]


def test_observed_validate_and_callback_error(load_exercise):
    m = load_exercise("ex03_observable")

    def positive(v):
        if v < 0:
            raise ValueError("negativo")

    class Account:
        balance = m.observed(default=0, validate=positive)

    a = Account()
    events = []
    m.watch(a, "balance", lambda *args: events.append(args[2:]))
    a.balance = 5
    with pytest.raises(ValueError, match="negativo"):
        a.balance = -1
    assert a.balance == 5 and events == [(0, 5)]

    def angry(*args):
        raise RuntimeError("observador falhou")

    m.watch(a, "balance", angry)
    after = []
    m.watch(a, "balance", lambda *args: after.append(1))
    with pytest.raises(RuntimeError):
        a.balance = 9
    assert a.balance == 9 and after == []                                              # o valor já estava guardado; os seguintes não rodaram


# ---------- ex04 ----------
def test_event_bus_patterns(load_exercise):
    m = load_exercise("ex04_event_bus")
    bus = m.EventBus()
    log = []

    def on_order(topic, payload):
        log.append(("order", topic, payload))

    def on_any(topic, payload):
        log.append(("any", topic, payload))

    bus.subscribe("order.*", on_order)
    assert bus.subscribe("*", on_any) is on_any
    assert bus.publish("order.created", {"id": 1}) == 2
    assert bus.publish("user.signup") == 1 and bus.publish("order") == 1
    assert log == [("order", "order.created", {"id": 1}), ("any", "order.created", {"id": 1}), ("any", "user.signup", None), ("any", "order", None)]
    assert bus.subscribers("order.paid") == [on_order, on_any] and bus.subscribers("x") == [on_any]
    assert bus.history == [("order.created", {"id": 1}), ("user.signup", None), ("order", None)]
    bus.unsubscribe("*", on_any)
    assert bus.publish("user.signup") == 0 and len(bus.history) == 4


def test_event_bus_errors_and_validation(load_exercise):
    m = load_exercise("ex04_event_bus")
    bus = m.EventBus()
    seen = []

    def explode(topic, payload):
        raise KeyError("boom")

    bus.subscribe("a.*", explode)
    bus.subscribe("a.*", lambda t, p: seen.append(p))
    assert bus.publish("a.b", 7) == 1 and seen == [7]
    topic, name, error = bus.errors[0]
    assert (topic, name) == ("a.b", "explode") and isinstance(error, KeyError)
    bus.subscribe("a.b", lambda t, p: 1 / 0)
    assert bus.publish("a.b", 1) == 1
    assert bus.errors[-1][1] == "<lambda>" and isinstance(bus.errors[-1][2], ZeroDivisionError) and len(bus.errors) == 3
    with pytest.raises(ValueError, match="já assinado"):
        bus.subscribe("a.*", explode)
    bus.subscribe("b.*", explode)                                                       # o mesmo fn em outro padrão é permitido
    with pytest.raises(ValueError, match="não assinado"):
        bus.unsubscribe("z.*", explode)
    with pytest.raises(TypeError):
        bus.subscribe("a", "nope")
    with pytest.raises(ValueError, match="tópico vazio"):
        bus.publish("")
    copy = bus.errors
    copy.clear()
    assert len(bus.errors) == 3


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["observer_classico", "observer_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
