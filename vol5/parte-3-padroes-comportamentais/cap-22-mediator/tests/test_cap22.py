import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_form_initial_state_follows_rule(load_exercise):
    m = load_exercise("ex01_form_mediator")
    f = m.FormMediator()
    assert f.error.text == "aceite os termos" and f.submit.enabled is False and f.submit.clicks == 0
    assert f.agree.mediator is f and f.email.mediator is f and f.submit.mediator is f


def test_form_rules(load_exercise):
    m = load_exercise("ex01_form_mediator")
    f = m.FormMediator()
    f.agree.toggle()
    assert f.error.text == "e-mail inválido" and f.submit.enabled is False
    f.email.type("ana")
    assert f.error.text == "e-mail inválido"
    f.email.type("ana@site.com")
    assert f.error.text == "" and f.submit.enabled is True
    f.email.type("@site.com")
    assert f.submit.enabled is False and f.error.text == "e-mail inválido"
    f.email.type("ana@")
    assert f.submit.enabled is False
    f.email.type("ana@site.com")
    f.agree.toggle()
    assert f.error.text == "aceite os termos" and f.submit.enabled is False


def test_form_submit(load_exercise):
    m = load_exercise("ex01_form_mediator")
    f = m.FormMediator()
    with pytest.raises(RuntimeError, match="botão desabilitado"):
        f.submit.click()
    f.agree.set(True)
    f.email.type("a@b.c")
    assert f.submit.click() == {"email": "a@b.c"} and f.submit.clicks == 1
    assert f.submissions == [{"email": "a@b.c"}]
    assert f.submit.enabled is True


def test_form_notifies_only_on_change(load_exercise):
    m = load_exercise("ex01_form_mediator")
    calls = []

    class Spy(m.FormMediator):
        def notify(self, sender):
            calls.append(type(sender).__name__)
            super().notify(sender)

    f = Spy()
    calls.clear()
    f.email.type("")
    f.agree.set(False)
    assert calls == []
    f.email.type("x")
    f.agree.set(True)
    assert calls == ["TextBox", "Checkbox"]
    f.email.type("x@y")
    calls.clear()
    f.submit.click()
    assert calls == ["Button"] and f.submit.enabled is True


def test_component_without_mediator(load_exercise):
    m = load_exercise("ex01_form_mediator")
    box, button = m.TextBox(), m.Button()
    box.type("oi")
    assert box.text == "oi" and m.Checkbox().checked is False
    button.enabled = True
    assert button.click() is None and button.clicks == 1


# ---------- ex02 ----------
def room(m, *names):
    r = m.ChatRoom()
    inbox = {n: [] for n in names}
    for n in names:
        r.join(n, lambda s, t, p, n=n: inbox[n].append((s, t, p)))
    return r, inbox


def test_chat_broadcast_and_members(load_exercise):
    m = load_exercise("ex02_chat_room")
    r, inbox = room(m, "bia", "ana", "caio")
    assert r.members() == ["ana", "bia", "caio"]
    assert r.send("ana", "oi") == 2
    assert inbox["ana"] == [] and inbox["bia"] == [("ana", "oi", False)] and inbox["caio"] == [("ana", "oi", False)]
    assert r.history == [("ana", None, "oi")]
    r.history.append("x")
    assert len(r.history) == 1


def test_chat_private_and_errors(load_exercise):
    m = load_exercise("ex02_chat_room")
    r, inbox = room(m, "ana", "bia", "caio")
    assert r.send("ana", "psiu", to="bia") == 1
    assert inbox["bia"] == [("ana", "psiu", True)] and inbox["caio"] == []
    assert r.send("ana", "eu mesma", to="ana") == 0
    with pytest.raises(LookupError, match="usuário desconhecido: zé"):
        r.send("ana", "oi", to="zé")
    with pytest.raises(LookupError, match="usuário desconhecido: zé"):
        r.send("zé", "oi")
    with pytest.raises(ValueError, match="nome já em uso: ana"):
        r.join("ana", print)
    with pytest.raises(TypeError):
        r.join("novo", "não chamável")
    with pytest.raises(LookupError):
        r.leave("zé")


def test_chat_mute_unmute_and_leave(load_exercise):
    m = load_exercise("ex02_chat_room")
    r, inbox = room(m, "ana", "bia", "caio")
    r.mute("bia", "ana")
    assert r.send("ana", "oi") == 1
    assert inbox["bia"] == [] and len(inbox["caio"]) == 1
    assert r.history == [("ana", None, "oi")]
    assert r.send("ana", "só pra você", to="bia") == 0
    assert r.send("caio", "e eu?") == 2 and len(inbox["bia"]) == 1
    r.unmute("bia", "ana")
    r.unmute("bia", "ana")
    r.unmute("bia", "caio")
    assert r.send("ana", "voltei") == 2
    r.mute("bia", "ana")
    r.leave("ana")
    inbox["bia"].clear()
    r.join("ana", lambda s, t, p: inbox["ana"].append((s, t, p)))
    assert r.send("ana", "de novo") == 2 and len(inbox["bia"]) == 1
    with pytest.raises(ValueError, match="não pode silenciar a si mesmo"):
        r.mute("ana", "ana")
    with pytest.raises(LookupError):
        r.mute("ana", "zé")
    with pytest.raises(LookupError):
        r.mute("zé", "ana")


def test_chat_banned_words(load_exercise):
    m = load_exercise("ex02_chat_room")
    r, inbox = room(m, "ana", "bia")
    r.ban_word("Gato")
    r.ban_word("spoiler")
    assert r.send("ana", "o gatos dorme") == 1
    with pytest.raises(ValueError, match="palavra proibida: gato"):
        r.send("ana", "o GATO dorme")
    with pytest.raises(ValueError, match="palavra proibida: spoiler"):
        r.send("ana", "olha o spoiler, gato!", to="bia")
    with pytest.raises(ValueError, match="palavra proibida: gato"):
        r.send("ana", "Gato.")
    assert len(inbox["bia"]) == 1 and len(r.history) == 1


# ---------- ex03 ----------
def test_store_derive_and_set(load_exercise):
    m = load_exercise("ex03_reactive_store")
    s = m.Store(price=10, qty=2)
    s.derive("subtotal", lambda p, q: p * q, "price", "qty")
    s.derive("total", lambda sub: round(sub * 1.1, 2), "subtotal")
    assert s.get("subtotal") == 20 and s["total"] == 22.0
    s.set("qty", 3)
    assert s["subtotal"] == 30 and s["total"] == 33.0
    assert s.recomputed == ["subtotal", "total"]
    s.recomputed.append("x")
    assert s.recomputed == ["subtotal", "total"]
    s.clear_log()
    assert s.recomputed == []
    s.set("coupon", "X")
    assert s["coupon"] == "X" and s.recomputed == []


def test_store_set_same_value_does_nothing(load_exercise):
    m = load_exercise("ex03_reactive_store")
    s = m.Store(a=1)
    s.derive("b", lambda a: a + 1, "a")
    seen = []
    s.watch("a", lambda o, n: seen.append(("a", o, n)))
    s.watch("b", lambda o, n: seen.append(("b", o, n)))
    s.clear_log()
    s.set("a", 1)
    assert s.recomputed == [] and seen == []
    s.set("a", 5)
    assert seen == [("a", 1, 5), ("b", 2, 6)] and s.recomputed == ["b"]


def test_store_diamond_recomputes_once_in_order(load_exercise):
    m = load_exercise("ex03_reactive_store")
    s = m.Store(x=1)
    s.derive("left", lambda x: x + 1, "x")
    s.derive("right", lambda x: x * 10, "x")
    s.derive("both", lambda a, b: a + b, "left", "right")
    s.derive("label", lambda v: f"v={v}", "both")
    s.clear_log()
    s.set("x", 2)
    assert s.recomputed == ["left", "right", "both", "label"] and s["label"] == "v=23"


def test_store_derived_not_recomputed_when_deps_unchanged(load_exercise):
    m = load_exercise("ex03_reactive_store")
    s = m.Store(n=3)
    s.derive("is_even", lambda n: n % 2 == 0, "n")
    s.derive("message", lambda e: "par" if e else "ímpar", "is_even")
    seen = []
    s.watch("message", lambda o, n: seen.append((o, n)))
    s.clear_log()
    s.set("n", 5)
    assert s.recomputed == ["is_even"] and seen == []
    s.set("n", 4)
    assert s.recomputed == ["is_even", "is_even", "message"] and seen == [("ímpar", "par")]


def test_store_errors_and_watch_returns_callback(load_exercise):
    m = load_exercise("ex03_reactive_store")
    s = m.Store(a=1)
    s.derive("b", lambda a: a, "a")
    with pytest.raises(ValueError, match="derivado não pode ser alterado"):
        s.set("b", 9)
    with pytest.raises(ValueError, match="ciclo"):
        s.derive("c", lambda c: c, "c")
    with pytest.raises(ValueError, match="já existe: a"):
        s.derive("a", lambda: 0)
    with pytest.raises(ValueError, match="já existe: b"):
        s.derive("b", lambda: 0)
    with pytest.raises(KeyError):
        s.derive("d", lambda z: z, "z")
    with pytest.raises(KeyError):
        s.get("nada")
    with pytest.raises(KeyError):
        s["nada"]
    with pytest.raises(KeyError):
        s.watch("nada", print)

    def cb(old, new):
        pass

    assert s.watch("a", cb) is cb


def test_store_watchers_in_registration_order(load_exercise):
    m = load_exercise("ex03_reactive_store")
    s = m.Store(a=0)
    order = []
    s.watch("a", lambda o, n: order.append(1))
    s.watch("a", lambda o, n: order.append(2))
    s.set("a", 1)
    assert order == [1, 2]


# ---------- ex04 ----------
def test_tower_basic_flow(load_exercise):
    m = load_exercise("ex04_air_traffic")
    t = m.Tower()
    a, b, c = m.Plane("A"), m.Plane("B"), m.Plane("C")
    assert t.runway is None and len(t) == 0
    assert t.request_landing(a) == 0 and t.runway is a and a.messages == ["pouso autorizado"]
    assert t.request_landing(b) == 1 and b.messages == ["na fila: posição 1"]
    assert t.request_landing(c) == 2 and c.messages == ["na fila: posição 2"]
    assert len(t) == 3 and t.waiting() == ["B", "C"]
    assert t.landed(a) is b and t.runway is b
    assert b.messages == ["na fila: posição 1", "pouso autorizado"] and c.messages == ["na fila: posição 2", "na fila: posição 1"]
    assert t.landed(b) is c and t.landed(c) is None and t.runway is None and len(t) == 0


def test_tower_emergency_order(load_exercise):
    m = load_exercise("ex04_air_traffic")
    t = m.Tower()
    a, n1, n2, e1, e2 = (m.Plane(x) for x in ["A", "N1", "N2", "E1", "E2"])
    t.request_landing(a)
    t.request_landing(n1)
    t.request_landing(n2)
    assert t.request_landing(e1, emergency=True) == 1
    assert t.waiting() == ["E1", "N1", "N2"]
    assert n1.messages == ["na fila: posição 1", "na fila: posição 2"] and n2.messages == ["na fila: posição 2", "na fila: posição 3"]
    assert t.request_landing(e2, emergency=True) == 2
    assert t.waiting() == ["E1", "E2", "N1", "N2"]
    assert e1.messages == ["na fila: posição 1"]


def test_tower_no_repeated_notifications(load_exercise):
    m = load_exercise("ex04_air_traffic")
    t = m.Tower()
    a, b, c = m.Plane("A"), m.Plane("B"), m.Plane("C")
    t.request_landing(a)
    t.request_landing(b)
    t.request_landing(c)
    t.cancel(c)
    assert b.messages == ["na fila: posição 1"] and c.messages == ["na fila: posição 2"]
    d = m.Plane("D")
    t.request_landing(d)
    t.cancel(b)
    assert d.messages == ["na fila: posição 2", "na fila: posição 1"] and t.waiting() == ["D"]


def test_tower_errors(load_exercise):
    m = load_exercise("ex04_air_traffic")
    t = m.Tower()
    a, b, c = m.Plane("A"), m.Plane("B"), m.Plane("C")
    t.request_landing(a)
    t.request_landing(b)
    with pytest.raises(ValueError, match="A já está no sistema"):
        t.request_landing(a)
    with pytest.raises(ValueError, match="B já está no sistema"):
        t.request_landing(b)
    with pytest.raises(ValueError, match="B não está na pista"):
        t.landed(b)
    with pytest.raises(ValueError, match="avião na pista não pode cancelar"):
        t.cancel(a)
    with pytest.raises(LookupError, match="C não está na fila"):
        t.cancel(c)
    assert len(t) == 2


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["mediator_classico", "mediator_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
