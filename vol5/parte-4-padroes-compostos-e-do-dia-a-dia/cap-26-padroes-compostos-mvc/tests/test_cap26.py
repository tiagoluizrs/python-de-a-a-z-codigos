import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def build(m):
    model, text, stats = m.Model(), [], []
    m.TextView(model, text)
    m.StatsView(model, stats)
    return model, m.Controller(model), text, stats


def test_model_basics_and_notifications(load_exercise):
    m = load_exercise("ex01_todo_mvc")
    model = m.Model()
    calls = []

    class Obs:
        def __init__(self, name):
            self.name = name

        def update(self, model):
            calls.append((self.name, model.items))

    a, b = Obs("a"), Obs("b")
    model.subscribe(a)
    model.subscribe(b)
    model.add("  leite  ")
    assert model.items == [("leite", False)] and calls == [("a", [("leite", False)]), ("b", [("leite", False)])]
    items = model.items
    items.append("lixo")
    assert model.items == [("leite", False)]
    model.toggle(0)
    model.remove(0)
    assert len(calls) == 6 and model.items == []
    calls.clear()
    for call in (lambda: model.add("   "), lambda: model.toggle(0), lambda: model.remove(-1)):
        with pytest.raises((ValueError, IndexError)):
            call()
    assert calls == []
    model.unsubscribe(a)
    model.add("x")
    assert [name for name, _ in calls] == ["b"]
    with pytest.raises(ValueError, match="não inscrito"):
        model.unsubscribe(a)


def test_model_index_errors(load_exercise):
    m = load_exercise("ex01_todo_mvc")
    model = m.Model()
    model.add("a")
    for index in (1, -1, 99):
        with pytest.raises(IndexError, match=f"tarefa inexistente: {index}$"):
            model.toggle(index)
        with pytest.raises(IndexError, match=f"tarefa inexistente: {index}$"):
            model.remove(index)
    with pytest.raises(ValueError, match="texto vazio"):
        model.add("")


def test_snapshot_restore_are_independent(load_exercise):
    m = load_exercise("ex01_todo_mvc")
    model, _, text, _ = build(m)
    model.add("a")
    model.add("b")
    snap = model.snapshot()
    model.toggle(0)
    model.remove(1)
    text.clear()
    model.restore(snap)
    assert model.items == [("a", False), ("b", False)] and text == ["[ ] a | [ ] b"]
    model.toggle(0)
    model.restore(snap)                                          # o mesmo snapshot serve de novo
    assert model.items == [("a", False), ("b", False)]
    snap[0][1] = True                                            # mexer no snapshot não mexe no modelo
    assert model.items[0] == ("a", False)


def test_batch(load_exercise):
    m = load_exercise("ex01_todo_mvc")
    model, _, text, _ = build(m)
    with model.batch():
        model.add("a")
        model.add("b")
        with model.batch():
            model.toggle(0)
        assert text == []
    assert text == ["[x] a | [ ] b"]
    with model.batch():
        pass
    assert len(text) == 1
    with pytest.raises(RuntimeError):
        with model.batch():
            model.add("c")
            raise RuntimeError("falhou no meio")
    assert len(text) == 2 and model.items[-1] == ("c", False)


def test_views_output(load_exercise):
    m = load_exercise("ex01_todo_mvc")
    model, _, text, stats = build(m)
    assert text == [] and stats == []
    model.add("leite")
    model.add("pão")
    model.toggle(0)
    assert text == ["[ ] leite", "[ ] leite | [ ] pão", "[x] leite | [ ] pão"]
    assert stats == ["0/1 feitas", "0/2 feitas", "1/2 feitas"]
    model.remove(0)
    model.remove(0)
    assert text[-1] == "(vazio)" and stats[-1] == "0/0 feitas"


def test_controller_flow_undo_redo(load_exercise):
    m = load_exercise("ex01_todo_mvc")
    model, c, text, stats = build(m)
    for line in ("add leite", "add pão", "done 1", "rm 2"):
        c.handle(line)
    assert model.items == [("leite", True)] and text[-1] == "[x] leite" and stats[-1] == "1/1 feitas" and len(text) == 4
    c.handle("undo")
    assert model.items == [("leite", True), ("pão", False)] and len(text) == 5
    c.handle("undo")
    assert model.items == [("leite", False), ("pão", False)]
    c.handle("redo")
    assert model.items == [("leite", True), ("pão", False)]
    c.handle("redo")
    assert model.items == [("leite", True)]
    with pytest.raises(LookupError, match="nada para refazer"):
        c.handle("redo")
    for _ in range(4):
        c.handle("undo")
    assert model.items == []
    with pytest.raises(LookupError, match="nada para desfazer"):
        c.handle("undo")


def test_new_command_clears_redo(load_exercise):
    m = load_exercise("ex01_todo_mvc")
    model, c, _, _ = build(m)
    c.handle("add a")
    c.handle("undo")
    c.handle("add b")
    with pytest.raises(LookupError, match="nada para refazer"):
        c.handle("redo")
    assert model.items == [("b", False)]


def test_failed_commands_leave_no_trace(load_exercise):
    m = load_exercise("ex01_todo_mvc")
    model, c, text, _ = build(m)
    c.handle("add a")
    c.handle("add b")
    size = len(text)
    for line, error, message in (
        ("done 9", IndexError, "tarefa inexistente: 9"),
        ("done 0", IndexError, "tarefa inexistente: 0"),
        ("rm 3", IndexError, "tarefa inexistente: 3"),
        ("done x", ValueError, "número inválido: x"),
        ("rm", ValueError, "número inválido: $"),
        ("add    ", ValueError, "texto vazio"),
        ("fly", ValueError, "comando desconhecido: fly"),
        ("", ValueError, "comando desconhecido: $"),
    ):
        with pytest.raises(error, match=message):
            c.handle(line)
    assert len(text) == size and model.items == [("a", False), ("b", False)]
    c.handle("undo")
    c.handle("undo")
    assert model.items == []
    with pytest.raises(LookupError):
        c.handle("undo")


def test_clear_done_is_one_step(load_exercise):
    m = load_exercise("ex01_todo_mvc")
    model, c, text, stats = build(m)
    for line in ("add a", "add b", "add c", "done 1", "done 3"):
        c.handle(line)
    size = len(text)
    c.handle("clear")
    assert model.items == [("b", False)] and len(text) == size + 1 and stats[-1] == "0/1 feitas"
    c.handle("clear")                                            # nada feito: nada acontece
    assert len(text) == size + 1
    c.handle("undo")
    assert model.items == [("a", True), ("b", False), ("c", True)]
    c.handle("redo")
    assert model.items == [("b", False)]
    c.handle("undo")
    c.handle("undo")                                             # desfaz o "done 3", não um "clear" fantasma
    assert model.items == [("a", True), ("b", False), ("c", False)]


# ---------- ex02 ----------
def cart_of(m, *msgs):
    cart = m.Cart()
    for msg in msgs:
        cart = m.update(cart, msg)
    return cart


def test_update_items(load_exercise):
    m = load_exercise("ex02_cart_update")
    cart = cart_of(m, m.AddItem("Café", 350), m.AddItem("Pão", 120), m.AddItem("Café", 999))
    assert cart.items == (m.Item("Café", 350, 2), m.Item("Pão", 120, 1))
    assert m.update(cart, m.RemoveItem("Café")).items == (m.Item("Pão", 120, 1),)
    assert m.update(cart, m.SetQty("Pão", 5)).items[1] == m.Item("Pão", 120, 5)
    assert m.update(cart, m.SetQty("Café", 0)).items == (m.Item("Pão", 120, 1),)
    assert cart.items == (m.Item("Café", 350, 2), m.Item("Pão", 120, 1)) and isinstance(cart.items, tuple)
    assert m.update(m.Cart(), m.AddItem("x", 1)) is not None


def test_update_errors(load_exercise):
    m = load_exercise("ex02_cart_update")
    cart = cart_of(m, m.AddItem("Café", 350))
    with pytest.raises(ValueError, match="item inexistente: Chá"):
        m.update(cart, m.RemoveItem("Chá"))
    with pytest.raises(ValueError, match="item inexistente: Chá"):
        m.update(cart, m.SetQty("Chá", 2))
    with pytest.raises(ValueError, match="quantidade inválida"):
        m.update(cart, m.SetQty("Café", -1))
    with pytest.raises(ValueError, match="quantidade inválida"):
        m.update(cart, m.SetQty("Chá", -1))                       # a quantidade é conferida antes
    with pytest.raises(ValueError, match="cupom inválido: XYZ"):
        m.update(cart, m.ApplyCoupon("XYZ"))
    with pytest.raises(ValueError, match="mensagem inválida"):
        m.update(cart, "comprar")


def test_coupons(load_exercise):
    m = load_exercise("ex02_cart_update")
    cart = cart_of(m, m.AddItem("Café", 350), m.ApplyCoupon("DEZ"))
    assert cart.coupon == "DEZ"
    assert m.update(cart, m.ApplyCoupon("CINCO")).coupon == "CINCO"
    assert m.update(cart, m.ClearCoupon()).coupon is None and m.update(m.update(cart, m.ClearCoupon()), m.ClearCoupon()).coupon is None
    assert cart_of(m, m.ClearCoupon()) == m.Cart()


def test_totals(load_exercise):
    m = load_exercise("ex02_cart_update")
    cart = cart_of(m, m.AddItem("Café", 350), m.AddItem("Café", 350), m.AddItem("Pão", 120))
    assert m.subtotal_cents(cart) == 820 and m.discount_cents(cart) == 0 and m.total_cents(cart) == 820
    ten = m.update(cart, m.ApplyCoupon("DEZ"))
    assert m.discount_cents(ten) == 82 and m.total_cents(ten) == 738
    odd = cart_of(m, m.AddItem("x", 999), m.ApplyCoupon("DEZ"))
    assert m.discount_cents(odd) == 99 and m.total_cents(odd) == 900
    five = cart_of(m, m.AddItem("y", 1999), m.ApplyCoupon("CINCO"))
    assert m.discount_cents(five) == 99 and m.total_cents(five) == 1900
    assert m.subtotal_cents(m.Cart()) == 0 and m.total_cents(m.Cart()) == 0


def test_view(load_exercise):
    m = load_exercise("ex02_cart_update")
    assert m.view(m.Cart()) == "carrinho vazio"
    cart = cart_of(m, m.AddItem("Café", 350), m.AddItem("Café", 350), m.AddItem("Pão", 120))
    assert m.view(cart) == "2x Café: R$ 7,00\n1x Pão: R$ 1,20\ntotal: R$ 8,20"
    assert m.view(m.update(cart, m.ApplyCoupon("DEZ"))) == "2x Café: R$ 7,00\n1x Pão: R$ 1,20\ncupom DEZ: -R$ 0,82\ntotal: R$ 7,38"
    assert m.view(cart_of(m, m.AddItem("Bala", 5))) == "1x Bala: R$ 0,05\ntotal: R$ 0,05"


# ---------- ex03 ----------
def add(state, msg):
    if msg == "boom":
        raise RuntimeError("falhou")
    return state + msg


def test_store_dispatch_and_history(load_exercise):
    m = load_exercise("ex03_store")
    s = m.Store(add, 0)
    assert s.state == 0 and not s.can_undo and not s.can_redo and s.undo() is False and s.redo() is False
    assert s.dispatch(1) is True and s.dispatch(2) is True and s.dispatch(0) is False and s.state == 3
    assert s.timeline() == [0, 1, 3] and s.position == 2 and s.can_undo
    assert s.undo() is True and s.state == 1 and s.can_redo and s.timeline() == [0, 1, 3] and s.position == 1
    assert s.redo() is True and s.state == 3 and not s.can_redo
    s.undo()
    s.dispatch(10)
    assert s.timeline() == [0, 1, 11] and not s.can_redo and s.redo() is False


def test_store_errors_leave_no_trace(load_exercise):
    m = load_exercise("ex03_store")
    s = m.Store(add, 5)
    seen = []
    s.subscribe(seen.append)
    with pytest.raises(RuntimeError, match="falhou"):
        s.dispatch("boom")
    assert s.state == 5 and s.timeline() == [5] and seen == []
    for bad in (0, -2):
        with pytest.raises(ValueError, match="limite inválido"):
            m.Store(add, 0, limit=bad)


def test_store_subscribers(load_exercise):
    m = load_exercise("ex03_store")
    s = m.Store(add, 0)
    a, b = [], []
    unsub_a = s.subscribe(a.append)
    s.subscribe(b.append)
    s.dispatch(1)
    s.dispatch(0)
    s.undo()
    s.redo()
    assert a == [1, 0, 1] and b == [1, 0, 1]
    unsub_a()
    unsub_a()
    s.dispatch(5)
    assert a == [1, 0, 1] and b == [1, 0, 1, 6]
    assert s.undo() and s.undo() and not s.undo() and b[-2:] == [1, 0]


def test_unsubscribe_during_notification(load_exercise):
    m = load_exercise("ex03_store")
    s = m.Store(add, 0)
    calls = []

    def once(state):
        calls.append(("once", state))
        unsub()

    unsub = s.subscribe(once)
    s.subscribe(lambda state: calls.append(("other", state)))
    s.dispatch(1)
    s.dispatch(1)
    assert calls == [("once", 1), ("other", 1), ("other", 2)]


def test_store_limit(load_exercise):
    m = load_exercise("ex03_store")
    s = m.Store(add, 0, limit=2)
    for n in (1, 2, 3, 4):
        s.dispatch(n)
    assert s.state == 10 and s.timeline() == [3, 6, 10] and s.position == 2
    assert s.undo() and s.undo() and s.state == 3 and s.undo() is False


def test_store_jump(load_exercise):
    m = load_exercise("ex03_store")
    s = m.Store(add, 0)
    for n in (1, 2, 3):
        s.dispatch(n)
    seen = []
    s.subscribe(seen.append)
    s.jump(1)
    assert s.state == 1 and s.position == 1 and s.timeline() == [0, 1, 3, 6] and seen == [1]
    s.jump(1)
    assert seen == [1]
    s.jump(3)
    assert s.state == 6 and s.can_undo and not s.can_redo and seen == [1, 6]
    s.jump(0)
    assert s.redo() and s.state == 1
    for bad in (-1, 4):
        with pytest.raises(IndexError, match=f"posição inexistente: {bad}$"):
            s.jump(bad)
    s.jump(0)
    s.dispatch(7)
    assert s.timeline() == [0, 7] and not s.can_redo


# ---------- ex04 ----------
class FakeView:
    def __init__(self):
        self.calls = []

    def clear_errors(self):
        self.calls.append(("clear_errors",))

    def clear_error(self, field):
        self.calls.append(("clear_error", field))

    def show_error(self, field, message):
        self.calls.append(("show_error", field, message))

    def set_busy(self, busy):
        self.calls.append(("set_busy", busy))

    def show_success(self, name):
        self.calls.append(("show_success", name))


def make(m, result="Ana Silva", **kwargs):
    view, seen = FakeView(), []

    def auth(username, password):
        seen.append((username, password))
        if isinstance(result, Exception):
            raise result
        return result

    return m.LoginPresenter(view, auth, **kwargs), view, seen


def test_login_success(load_exercise):
    m = load_exercise("ex04_login_presenter")
    p, view, seen = make(m)
    assert p.on_submit("  ANA ", "Senha 1234") is True
    assert seen == [("ana", "Senha 1234")]
    assert view.calls == [("clear_errors",), ("set_busy", True), ("set_busy", False), ("show_success", "Ana Silva")]
    assert p.failures == 0 and p.blocked is False


def test_login_validation(load_exercise):
    m = load_exercise("ex04_login_presenter")
    p, view, seen = make(m)
    assert p.on_submit("", "") is False
    assert view.calls == [("clear_errors",), ("show_error", "username", "informe o usuário"), ("show_error", "password", "informe a senha")]
    view.calls.clear()
    assert p.on_submit("ab", "1234567") is False
    assert view.calls == [("clear_errors",), ("show_error", "username", "mínimo de 3 caracteres"), ("show_error", "password", "mínimo de 8 caracteres")]
    view.calls.clear()
    assert p.on_submit("   ", "12345678") is False
    assert view.calls == [("clear_errors",), ("show_error", "username", "informe o usuário")]
    view.calls.clear()
    assert p.on_submit("abc", "        ") is True                    # 8 espaços são 8 caracteres
    assert seen == [("abc", "        ")] and p.failures == 0


def test_login_rejected_and_block(load_exercise):
    m = load_exercise("ex04_login_presenter")
    p, view, seen = make(m, result=None)
    assert p.on_submit("ana", "senha1234") is False
    assert view.calls == [("clear_errors",), ("set_busy", True), ("set_busy", False), ("show_error", "form", "usuário ou senha inválidos")]
    assert p.failures == 1 and not p.blocked
    p.on_submit("ana", "senha1234")
    view.calls.clear()
    assert p.on_submit("ana", "senha1234") is False
    assert view.calls[-1] == ("show_error", "form", "conta bloqueada") and p.blocked and p.failures == 3 and len(seen) == 3
    view.calls.clear()
    assert p.on_submit("ana", "senha1234") is False
    assert view.calls == [("clear_errors",), ("show_error", "form", "conta bloqueada")] and len(seen) == 3
    p.reset()
    assert p.blocked is False and p.failures == 0
    p.on_submit("ana", "senha1234")
    assert len(seen) == 4


def test_login_failures_reset_after_success_and_max_attempts(load_exercise):
    m = load_exercise("ex04_login_presenter")
    view, answers = FakeView(), iter([None, None, "Ana", None])
    p = m.LoginPresenter(view, lambda u, pw: next(answers))
    for _ in range(4):
        p.on_submit("ana", "senha1234")
    assert p.failures == 1 and not p.blocked
    p1, view1, _ = make(m, result=None, max_attempts=1)
    p1.on_submit("ana", "senha1234")
    assert p1.blocked and view1.calls[-1] == ("show_error", "form", "conta bloqueada")


def test_login_connection_error_and_unexpected_error(load_exercise):
    m = load_exercise("ex04_login_presenter")
    p, view, _ = make(m, result=ConnectionError("fora do ar"))
    assert p.on_submit("ana", "senha1234") is False
    assert view.calls == [("clear_errors",), ("set_busy", True), ("set_busy", False), ("show_error", "form", "sem conexão, tente de novo")]
    assert p.failures == 0
    p2, view2, _ = make(m, result=RuntimeError("bug"))
    with pytest.raises(RuntimeError, match="bug"):
        p2.on_submit("ana", "senha1234")
    assert ("set_busy", False) in view2.calls and view2.calls[-1] == ("set_busy", False)


def test_login_input_changed(load_exercise):
    m = load_exercise("ex04_login_presenter")
    p, view, _ = make(m)
    p.on_input_changed("username")
    assert view.calls == [("clear_error", "username")]


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["mvc_classico", "mvc_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
