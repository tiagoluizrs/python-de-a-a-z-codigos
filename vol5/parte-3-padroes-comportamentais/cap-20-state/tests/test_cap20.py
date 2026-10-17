import subprocess
import sys
from enum import Enum
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_order_happy_path(load_exercise):
    m = load_exercise("ex01_order_state")
    o = m.Order()
    assert o.state_name == "new" and o.history == ["new"] and not o.is_final and o.refund is False
    o.pay()
    o.ship()
    assert o.state_name == "shipped"
    o.deliver()
    assert o.state_name == "delivered" and o.is_final and o.history == ["new", "paid", "shipped", "delivered"]
    h = o.history
    h.append("lixo")
    assert o.history == ["new", "paid", "shipped", "delivered"]


@pytest.mark.parametrize("setup,event,state", [
    ([], "ship", "new"), ([], "deliver", "new"), (["pay"], "pay", "paid"), (["pay"], "deliver", "paid"),
    (["pay", "ship"], "cancel", "shipped"), (["pay", "ship"], "pay", "shipped"), (["pay", "ship", "deliver"], "cancel", "delivered"),
    (["cancel"], "pay", "cancelled"), (["cancel"], "cancel", "cancelled"),
])
def test_order_invalid_transitions(load_exercise, setup, event, state):
    m = load_exercise("ex01_order_state")
    o = m.Order()
    for e in setup:
        getattr(o, e)()
    history = o.history
    with pytest.raises(m.InvalidTransition, match=f"{event} não permitido em {state}"):
        getattr(o, event)()
    assert o.state_name == state and o.history == history


def test_order_cancel_and_refund(load_exercise):
    m = load_exercise("ex01_order_state")
    a = m.Order()
    a.cancel()
    assert a.state_name == "cancelled" and a.refund is False and a.is_final and a.history == ["new", "cancelled"]
    b = m.Order()
    b.pay()
    b.cancel()
    assert b.refund is True and b.history == ["new", "paid", "cancelled"]
    assert isinstance(m.Order().state, m.New) and all(issubclass(c, m.State) for c in (m.New, m.Paid, m.Shipped, m.Delivered, m.Cancelled))
    assert m.Delivered().name == "delivered"


# ---------- ex02 ----------
TABLE = {("new", "pay"): "paid", ("new", "cancel"): "cancelled", ("paid", "ship"): "shipped", ("paid", "cancel"): "cancelled", ("shipped", "deliver"): "delivered"}


def test_state_machine_basic(load_exercise):
    m = load_exercise("ex02_state_machine")
    sm = m.StateMachine(TABLE, "new")
    seen = []
    assert sm.on_transition(lambda o, e, d: seen.append((o, e, d))) is not None
    assert sm.state == "new" and sm.allowed() == ["cancel", "pay"] and sm.can("pay") and not sm.can("ship") and not sm.is_terminal
    assert sm.fire("pay") == "paid" and sm.fire("ship") == "shipped" and sm.state == "shipped"
    assert seen == [("new", "pay", "paid"), ("paid", "ship", "shipped")] and sm.history == ["new", "paid", "shipped"]
    with pytest.raises(m.InvalidTransition, match="cancel não permitido em shipped"):
        sm.fire("cancel")
    assert sm.state == "shipped" and len(seen) == 2
    sm.fire("deliver")
    assert sm.is_terminal and sm.allowed() == []
    sm.reset()
    assert sm.state == "new" and sm.history == ["new"]
    with pytest.raises(ValueError, match="estado inicial desconhecido: 'x'"):
        m.StateMachine(TABLE, "x")
    assert m.StateMachine(TABLE, "delivered").is_terminal


def test_state_machine_with_enums(load_exercise):
    m = load_exercise("ex02_state_machine")

    class S(Enum):
        A = "a"
        B = "b"

    sm = m.StateMachine({(S.A, "go"): S.B}, S.A)
    assert sm.fire("go") is S.B
    with pytest.raises(m.InvalidTransition, match="go não permitido em b"):
        sm.fire("go")
    cbs = []
    sm.on_transition(lambda *a: cbs.append(1))
    sm.on_transition(lambda *a: cbs.append(2))
    sm.reset()
    sm.fire("go")
    assert cbs == [1, 2]


def test_validate_table(load_exercise):
    m = load_exercise("ex02_state_machine")
    assert m.validate_table(TABLE, "new") == {"unreachable": [], "terminal": ["cancelled", "delivered"], "dead_events": []}
    broken = {("a", "go"): "b", ("b", "stop"): "c", ("x", "jump"): "y", ("y", "go"): "x", ("z", "fly"): "a"}
    result = m.validate_table(broken, "a")
    assert result == {"unreachable": ["x", "y", "z"], "terminal": ["c"], "dead_events": ["fly", "jump"]}              # 'go' também existe em a->b, então não é morto


def test_shortest_path(load_exercise):
    m = load_exercise("ex02_state_machine")
    assert m.shortest_path(TABLE, "new", "delivered") == ["pay", "ship", "deliver"] and m.shortest_path(TABLE, "new", "cancelled") == ["cancel"]
    assert m.shortest_path(TABLE, "new", "new") == [] and m.shortest_path(TABLE, "delivered", "new") is None
    table = {("a", "z"): "goal", ("a", "b"): "goal", ("a", "c"): "mid", ("mid", "x"): "goal"}
    assert m.shortest_path(table, "a", "goal") == ["b"]                                                               # entre os de mesmo tamanho, o evento alfabético


# ---------- ex03 ----------
def test_turnstile_flow(load_exercise):
    m = load_exercise("ex03_guards_actions")
    t = m.turnstile(price=2)
    assert t.state == "locked" and t.credit == 0 and t.passed == 0 and t.price == 2
    with pytest.raises(m.InvalidTransition, match="push não permitido em locked"):
        t.fire("push")
    with pytest.raises(m.GuardFailed, match="guarda recusou coin em locked"):
        t.fire("coin", amount=1)
    assert t.credit == 0 and t.state == "locked"
    assert t.fire("coin", amount=5) == 5 and t.state == "unlocked"
    assert t.fire("coin", amount=1) == 6
    assert t.fire("push") == "passou" and t.state == "locked" and t.passed == 1 and t.credit == 4
    assert t.log == [("locked", "coin", "unlocked"), ("unlocked", "coin", "unlocked"), ("unlocked", "push", "locked")]


def test_turnstile_refund_and_context(load_exercise):
    m = load_exercise("ex03_guards_actions")
    t = m.turnstile(price=2, owner="metrô")
    assert t.owner == "metrô"
    with pytest.raises(m.GuardFailed):
        t.fire("refund")
    t.fire("coin", amount=3)
    assert t.fire("refund") == 3 and t.credit == 0 and t.state == "locked"
    t.fire("coin", amount=2)
    t.fire("push")
    assert t.credit == 0 and t.passed == 1
    t.fire("coin", amount=9)
    t.fire("push")
    assert t.state == "locked" and t.credit == 7
    assert t.fire("refund") == 7 and t.credit == 0


def test_machine_generic_semantics(load_exercise):
    m = load_exercise("ex03_guards_actions")
    order = []

    def guard(machine):
        order.append(("guard", dict(machine.args)))
        return machine.args.get("ok", False)

    def action(machine):
        order.append(("action", machine.state))
        return "feito"

    def broken(machine):
        raise RuntimeError("ação falhou")

    machine = m.Machine({("a", "go"): m.Transition("b", guard=guard, action=action), ("b", "boom"): m.Transition("c", action=broken), ("b", "plain"): m.Transition("c")}, "a", x=1)
    assert machine.x == 1
    with pytest.raises(m.GuardFailed):
        machine.fire("go")
    assert machine.state == "a" and order == [("guard", {})]
    order.clear()
    assert machine.fire("go", ok=True) == "feito" and machine.state == "b" and order == [("guard", {"ok": True}), ("action", "a")]      # a ação roda ANTES da troca
    with pytest.raises(RuntimeError):
        machine.fire("boom")
    assert machine.state == "b"                                                                                                       # a ação falhou: o estado não mudou
    assert machine.fire("plain") is None and machine.state == "c" and len(machine.log) == 2


# ---------- ex04 ----------
def test_light_enum(load_exercise):
    m = load_exercise("ex04_enum_states")
    assert [light.seconds for light in m.Light] == [30, 25, 5] and m.Light.RED.next() is m.Light.GREEN
    assert m.Light.GREEN.next() is m.Light.YELLOW and m.Light.YELLOW.next() is m.Light.RED
    assert m.TrafficLight.cycle_length() == 60


def test_traffic_light_ticks(load_exercise):
    m = load_exercise("ex04_enum_states")
    t = m.TrafficLight()
    assert t.state is m.Light.RED and t.elapsed == 0 and t.remaining == 30
    assert t.tick(10) == [] and t.elapsed == 10 and t.remaining == 20
    assert t.tick(20) == [m.Light.GREEN] and t.elapsed == 0 and t.state is m.Light.GREEN
    assert t.tick(26) == [m.Light.YELLOW] and t.elapsed == 1 and t.remaining == 4
    assert t.tick(100) == [m.Light.RED, m.Light.GREEN, m.Light.YELLOW, m.Light.RED, m.Light.GREEN] and t.state is m.Light.GREEN and t.elapsed == 6
    with pytest.raises(ValueError, match="tempo negativo"):
        t.tick(-1)
    y = m.TrafficLight(m.Light.YELLOW)
    assert y.tick(5.5) == [m.Light.RED] and abs(y.elapsed - 0.5) < 1e-9


def test_door_match(load_exercise):
    m = load_exercise("ex04_enum_states")
    assert m.door("closed", "open") == "open" and m.door("open", "close") == "closed" and m.door("closed", "lock") == "locked" and m.door("locked", "unlock") == "closed"
    for state, event in [("closed", "close"), ("closed", "unlock"), ("open", "open"), ("open", "lock"), ("locked", "open"), ("locked", "close")]:
        with pytest.raises(ValueError, match=f"{event} não permitido em {state}"):
            m.door(state, event)
    with pytest.raises(ValueError, match="estado desconhecido: broken"):
        m.door("broken", "open")
    with pytest.raises(ValueError, match="evento desconhecido: kick"):
        m.door("closed", "kick")
    with pytest.raises(ValueError, match="estado desconhecido: x"):
        m.door("x", "kick")


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["state_classico", "state_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
