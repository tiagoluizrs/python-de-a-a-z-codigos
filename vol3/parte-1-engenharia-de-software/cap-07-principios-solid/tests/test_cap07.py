import subprocess
import sys
import textwrap
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 SRP ----------
GOD = textwrap.dedent('''
    class Report:
        def __init__(self):
            self.rows = []
            self.path = ""
            self.smtp = None
        def add(self, row):
            self.rows.append(row)
        def total(self):
            return sum(self.rows)
        def save(self):
            open(self.path, "w").write("x")
        def load(self):
            self.rows = []
        def send(self):
            self.smtp.send("x")
        def helper(self):
            return 1
''')


def test_lcom4_god_class(load_exercise):
    m = load_exercise("ex01_srp")
    assert m.lcom4(GOD) == {"Report": 4}


def test_lcom4_cohesive_and_calls(load_exercise):
    m = load_exercise("ex01_srp")
    src = '''
class A:
    def __init__(self):
        self.x = 0
    def a(self):
        return self.b()
    def b(self):
        return self.x
    def c(self):
        self.x += 1
class Empty:
    def __init__(self):
        pass
class Alone:
    def f(self):
        return 1
'''
    assert m.lcom4(src) == {"A": 1, "Empty": 0, "Alone": 1}


def test_lcom4_nested_and_async(load_exercise):
    m = load_exercise("ex01_srp")
    src = '''
class Outer:
    async def a(self):
        return self.v
    def b(self):
        return self.v
    class Inner:
        def p(self):
            return self.q
        def q(self):
            return 1
        def r(self):
            return self.zzz
'''
    r = m.lcom4(src)
    assert r["Outer"] == 1 and r["Inner"] == 2


def test_split_candidates_and_groups(load_exercise):
    m = load_exercise("ex01_srp")
    assert m.split_candidates(GOD) == ["Report"]
    assert m.split_candidates(GOD, threshold=5) == []
    assert m.attribute_groups(GOD, "Report") == [["add", "load", "total"], ["helper"], ["save"], ["send"]] or \
        m.attribute_groups(GOD, "Report") == [["add", "load", "save", "total"], ["helper"], ["send"]]
    with pytest.raises(KeyError):
        m.attribute_groups(GOD, "Nope")


def test_groups_exact(load_exercise):
    m = load_exercise("ex01_srp")
    # add/total/load compartilham rows; save/load compartilham path -> um grupo só; send usa smtp e path (liga!)
    src = textwrap.dedent('''
        class C:
            def a(self): return self.x
            def b(self): return self.x
            def c(self): return self.y
            def d(self): return self.d2()
            def d2(self): return 1
    ''')
    assert m.attribute_groups(src, "C") == [["a", "b"], ["c"], ["d", "d2"]]


# ---------- ex02 OCP ----------
def test_ocp_registry(load_exercise):
    m = load_exercise("ex02_ocp")
    m.reset_registry()

    @m.shipping_method("sedex", min_price=15.0)
    def sedex(w, d):
        return w * 2 + d * 0.1

    @m.shipping_method("pac")
    def pac(w, d):
        return w * 1.0 + d * 0.05

    assert sedex(1, 1) == pytest.approx(2.1)
    assert m.available_methods() == ["pac", "sedex"]
    assert m.shipping_cost("sedex", 1, 1) == 15.0
    assert m.shipping_cost("pac", 10, 100) == 15.0
    assert m.shipping_cost("pac", 1.234, 3.3) == round(1.234 + 3.3 * 0.05, 2)
    assert m.cheapest(1, 1) == ("pac", 1.05)
    m.reset_registry()


def test_ocp_errors_and_ties(load_exercise):
    m = load_exercise("ex02_ocp")
    m.reset_registry()
    with pytest.raises(m.UnknownShippingMethod, match="nenhum método registrado"):
        m.cheapest(1, 1)
    m.shipping_method("b")(lambda w, d: 5.0)
    m.shipping_method("a")(lambda w, d: 5.0)
    assert m.cheapest(1, 1) == ("a", 5.0)
    with pytest.raises(ValueError, match="método já registrado: a"):
        m.shipping_method("a")(lambda w, d: 1.0)
    with pytest.raises(ValueError):
        m.shipping_method("")
    with pytest.raises(ValueError):
        m.shipping_cost("zzz", 0, 1)  # validação antes de procurar o método
    with pytest.raises(ValueError):
        m.shipping_cost("a", 1, -1)
    with pytest.raises(m.UnknownShippingMethod, match="método desconhecido: zzz"):
        m.shipping_cost("zzz", 1, 1)
    m.reset_registry()
    assert m.available_methods() == []


# ---------- ex03 LSP ----------
def test_limited_dict_all_write_paths(load_exercise):
    m = load_exercise("ex03_lsp")
    d = m.LimitedDict(max_items=2, validator=lambda v: v >= 0)
    d["a"] = 1
    d.update(b=2)
    assert d == {"a": 1, "b": 2} and list(d) == ["a", "b"]
    with pytest.raises(OverflowError, match="dicionário cheio"):
        d["c"] = 3
    with pytest.raises(OverflowError):
        d.setdefault("c", 3)
    with pytest.raises(OverflowError):
        d.update({"c": 3})
    d["a"] = 10  # atualizar chave existente é permitido
    with pytest.raises(ValueError, match="valor inválido: -1"):
        d["a"] = -1
    with pytest.raises(ValueError):
        d.update(a=-5)
    assert d == {"a": 10, "b": 2}


def test_limited_dict_constructor_and_contract(load_exercise):
    m = load_exercise("ex03_lsp")
    with pytest.raises(ValueError):
        m.LimitedDict(max_items=0)
    with pytest.raises(OverflowError):
        m.LimitedDict(max_items=1, initial={"a": 1, "b": 2})
    with pytest.raises(ValueError):
        m.LimitedDict(validator=lambda v: v > 0, initial=[("a", 0)])
    d = m.LimitedDict(max_items=3, initial=[("x", 1), ("y", 2)])
    assert len(d) == 2 and "x" in d and d.get("zz") is None
    assert d.pop("x") == 1
    with pytest.raises(KeyError):
        d["x"]
    with pytest.raises(KeyError):
        del d["x"]
    assert d.popitem() == ("y", 2)
    d.update(p=1, q=2)
    d.clear()
    assert len(d) == 0
    assert list(m.LimitedDict(initial={"k": 1}).items()) == [("k", 1)]


def test_limited_dict_copy(load_exercise):
    m = load_exercise("ex03_lsp")
    d = m.LimitedDict(max_items=2, validator=lambda v: v > 0, initial={"a": 1})
    c = d.copy()
    assert isinstance(c, m.LimitedDict) and c == d and c is not d
    c["b"] = 2
    assert "b" not in d
    with pytest.raises(OverflowError):
        c["z"] = 1
    with pytest.raises(ValueError):
        c["a"] = 0


# ---------- ex04 ISP ----------
def test_isp_minimal_doubles(load_exercise):
    m = load_exercise("ex04_isp")

    class OnlyGet:
        def get(self, user_id):
            return {"first": "Ana", "last": "Lima"} if user_id == 1 else ({"first": "Bob", "last": ""} if user_id == 2 else None)

    assert m.display_name(OnlyGet(), 1) == "Ana Lima"
    assert m.display_name(OnlyGet(), 2) == "Bob"
    with pytest.raises(LookupError, match="usuário 3 não existe"):
        m.display_name(OnlyGet(), 3)


def test_purge_inactive(load_exercise):
    m = load_exercise("ex04_isp")
    users = {1: {"active": True}, 2: {"active": False}, 3: {}, 4: {"active": 0}}
    deleted = []

    class L:
        def list_ids(self):
            return [1, 2, 3, 4, 5]

    class R:
        def get(self, i):
            return users.get(i)

    class D:
        def delete(self, i):
            deleted.append(i)

    assert m.purge_inactive(L(), R(), D()) == [2, 3, 4]
    assert deleted == [2, 3, 4]


def test_iterable_and_sequence(load_exercise):
    m = load_exercise("ex04_isp")
    assert m.total_length(["ab", "c"]) == 3
    assert m.total_length(("ab",)) == 2
    assert m.total_length(x for x in ["abc", "de"]) == 5
    assert m.total_length({"xx"}) == 2
    ann = m.total_length.__annotations__["items"]
    assert "Iterable" in str(ann)
    assert m.first_and_last([1, 2, 3]) == (1, 3)
    assert m.first_and_last("abc") == ("a", "c")
    assert m.first_and_last((9,)) == (9, 9)
    with pytest.raises(ValueError, match="sequência vazia"):
        m.first_and_last([])
    assert "Sequence" in str(m.first_and_last.__annotations__["items"])


# ---------- ex05 DIP ----------
class FakeStore:
    def __init__(self, reminders):
        self.reminders = list(reminders)
        self.sent = []

    def pending(self):
        return [r for r in self.reminders if r.id not in self.sent]

    def mark_sent(self, rid):
        self.sent.append(rid)


NOW = datetime(2030, 1, 1, 12, 0)


def make(m, due_offsets):
    return [m.Reminder(i + 1, NOW + timedelta(minutes=off), "a@x.com", f"t{i + 1}") for i, off in enumerate(due_offsets)]


def test_service_sends_due_and_waits(load_exercise):
    m = load_exercise("ex05_dip")
    store = FakeStore(make(m, [-10, 0, 5]))
    sent = []
    svc = m.ReminderService(store, lambda to, text: sent.append((to, text)), lambda: NOW)
    assert svc.run() == {"sent": [1, 2], "failed": [], "waiting": [3]}
    assert sent == [("a@x.com", "t1"), ("a@x.com", "t2")]
    assert store.sent == [1, 2]
    assert svc.run() == {"sent": [], "failed": [], "waiting": [3]}


def test_service_retries_and_fails(load_exercise):
    m = load_exercise("ex05_dip")
    store = FakeStore(make(m, [-1, -1]))
    calls = {"n": 0}

    def flaky(to, text):
        calls["n"] += 1
        if text == "t1":
            raise ConnectionError("fora do ar")
        if calls["n"] < 5:
            raise ConnectionError("ainda não")

    svc = m.ReminderService(store, flaky, lambda: NOW, max_attempts=3)
    result = svc.run()
    assert result["failed"] == [1] and result["sent"] == [2]
    assert store.sent == [2]
    assert calls["n"] == 3 + 2  # 3 tentativas do 1; do 2, falha na 4ª e ok na 5ª


def test_service_other_exception_and_single_now(load_exercise):
    m = load_exercise("ex05_dip")
    store = FakeStore(make(m, [-1]))

    def boom(to, text):
        raise RuntimeError("bug")

    with pytest.raises(RuntimeError):
        m.ReminderService(store, boom, lambda: NOW).run()
    assert store.sent == []
    ticks = []

    def clock():
        ticks.append(1)
        return NOW

    m.ReminderService(FakeStore(make(m, [-1, -2, -3])), lambda to, text: None, clock).run()
    assert len(ticks) == 1


def test_build_service(load_exercise):
    m = load_exercise("ex05_dip")
    store = FakeStore(make(m, [-1]))
    svc = m.build_service({"MAX_ATTEMPTS": "5"}, store, clock=lambda: NOW)
    assert svc.max_attempts == 5 and svc.run()["sent"] == [1]
    assert svc.outbox == [("a@x.com", "t1")]
    got = []
    store2 = FakeStore(make(m, [-1]))
    svc2 = m.build_service({"SMTP_HOST": "mail.local"}, store2, smtp_send=lambda h, to, t: got.append((h, to, t)), clock=lambda: NOW)
    svc2.run()
    assert got == [("mail.local", "a@x.com", "t1")]
    with pytest.raises(ValueError, match="smtp_send ausente"):
        m.build_service({"SMTP_HOST": "h"}, store)
    assert m.build_service({}, store).now is datetime.now or m.build_service({}, store).now == datetime.now


# ---------- ex06 smells ----------
SMELLY = '''
class Base:
    def f(self):
        raise NotImplementedError

class Child(Base):
    def f(self):
        raise NotImplementedError("não sei")
    def g(self):
        return 1

def price(kind, qty):
    if kind == "a":
        return 1
    elif kind == "b":
        return 2
    elif kind == "c":
        return 3
    elif kind in ("d", "e"):
        return 4
    return 0

def short(kind):
    if kind == "a":
        return 1
    elif kind == "b":
        return 2
    elif kind == "c":
        return 3

def mixed(a, b):
    if a == 1:
        return 1
    elif b == 2:
        return 2
    elif a == 3:
        return 3
    elif a == 4:
        return 4

def send(text):
    import smtplib
    s = smtplib.SMTP("localhost")
    stamp = datetime.now()
    t = time.time()
    return s, stamp, t

TOP = datetime.now()

class Svc:
    def run(self):
        db = connect("x")
        def inner():
            return Redis()
        return db, inner
'''


def test_find_smells(load_exercise):
    m = load_exercise("ex06_smells")
    found = [(s.kind, s.where, s.line) for s in m.find_smells(SMELLY)]
    lines = SMELLY.splitlines()

    def line_of(text, nth=0):
        return [i + 1 for i, ln in enumerate(lines) if text in ln][nth]

    assert ("LSP", "Child.f", line_of('raise NotImplementedError("não')) in found
    assert not any(k == "LSP" and w == "Base.f" for k, w, _ in found)
    assert ("OCP", "price", line_of('if kind == "a"')) in found
    assert not any(w == "short" or w == "mixed" for _, w, _ in found)
    assert ("DIP", "send", line_of("smtplib.SMTP")) in found
    assert ("DIP", "send", line_of("datetime.now()")) in found
    assert ("DIP", "send", line_of("time.time()")) in found
    assert ("DIP", "Svc.run", line_of('connect("x")')) in found
    assert ("DIP", "inner", line_of("Redis()")) in found
    assert not any(l == line_of("TOP = ") for _, _, l in found)
    assert found == sorted(found, key=lambda t: (t[2], t[0]))
    assert len(found) == 7


def test_find_smells_clean(load_exercise):
    m = load_exercise("ex06_smells")
    assert m.find_smells("def f(now):\n    return now()\n") == []


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["srp_cohesion", "ocp_extension", "lsp_contracts", "isp_protocols", "dip_injection", "overengineering"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"exemplos/{name}.py"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
