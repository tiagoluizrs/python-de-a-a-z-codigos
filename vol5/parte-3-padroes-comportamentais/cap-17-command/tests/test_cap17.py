import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_insert_delete_undo(load_exercise):
    m = load_exercise("ex01_editor_undo")
    ed = m.Editor("olá")
    h = m.History()
    h.run(m.Insert(ed, 3, ", mundo"))
    h.run(m.Delete(ed, 0, 1))
    assert ed.text == "lá, mundo" and len(h) == 2 and h.can_undo and not h.can_redo
    assert h.undo() is True and ed.text == "olá, mundo" and h.can_redo
    assert h.undo() is True and ed.text == "olá" and h.undo() is False and not h.can_undo
    assert h.redo() is True and ed.text == "olá, mundo" and h.redo() is True and ed.text == "lá, mundo" and h.redo() is False


def test_new_run_clears_redo_and_errors(load_exercise):
    m = load_exercise("ex01_editor_undo")
    ed = m.Editor("abc")
    h = m.History()
    h.run(m.Insert(ed, 0, "X"))
    h.undo()
    assert h.can_redo
    h.run(m.Insert(ed, 3, "Y"))
    assert not h.can_redo and ed.text == "abcY"
    for cmd, message in [(m.Insert(ed, 99, "z"), "posição inválida: 99"), (m.Insert(ed, -1, "z"), "posição inválida: -1"),
                         (m.Delete(ed, 2, 1), "intervalo inválido: 2-1"), (m.Delete(ed, 0, 99), "intervalo inválido: 0-99")]:
        with pytest.raises(ValueError, match=message):
            h.run(cmd)
    assert ed.text == "abcY" and len(h) == 1                                        # falhas não alteram nada nem entram no histórico


def test_delete_redo_uses_current_text_and_limit(load_exercise):
    m = load_exercise("ex01_editor_undo")
    ed = m.Editor("0123456789")
    h = m.History(limit=2)
    for start in (0, 0, 0):
        h.run(m.Delete(ed, start, 2))
    assert ed.text == "6789"
    assert len(h) == 2
    h.undo()
    h.undo()
    assert h.undo() is False                                                          # o mais antigo foi esquecido
    assert ed.text == "23456789"
    with pytest.raises(ValueError, match="limit deve ser >= 1"):
        m.History(limit=0)
    ed2 = m.Editor("abcdef")
    h2 = m.History()
    h2.run(m.Delete(ed2, 1, 3))
    h2.undo()
    assert ed2.text == "abcdef"
    h2.redo()
    assert ed2.text == "adef"


# ---------- ex02 ----------
def test_macro_atomic(load_exercise):
    m = load_exercise("ex02_macro")
    store = {"a": 1}
    macro = m.Macro(m.SetValue(store, "a", 2), m.SetValue(store, "b", 3))
    macro.execute()
    assert store == {"a": 2, "b": 3} and len(macro) == 2
    macro.undo()
    assert store == {"a": 1}
    with pytest.raises(RuntimeError, match="macro não executada"):
        macro.undo()
    failing = m.Fail("meio do caminho")
    bad = m.Macro(m.SetValue(store, "x", 1), m.SetValue(store, "a", 99), failing, m.SetValue(store, "z", 1))
    with pytest.raises(RuntimeError, match="meio do caminho"):
        bad.execute()
    assert store == {"a": 1} and failing.undone is False                              # compensou os anteriores; o que falhou não é desfeito
    with pytest.raises(RuntimeError):
        bad.undo()


def test_macro_nested_and_empty(load_exercise):
    m = load_exercise("ex02_macro")
    store = {}
    inner = m.Macro(m.SetValue(store, "a", 1), m.SetValue(store, "b", 2))
    outer = m.Macro(m.SetValue(store, "z", 0), inner)
    outer.execute()
    assert store == {"z": 0, "a": 1, "b": 2}
    outer.undo()
    assert store == {}
    broken = m.Macro(m.SetValue(store, "z", 0), m.Macro(m.SetValue(store, "a", 1), m.Fail()))
    with pytest.raises(RuntimeError):
        broken.execute()
    assert store == {}
    empty = m.Macro()
    empty.execute()
    empty.undo()
    assert len(empty) == 0


def test_macro_failure_in_compensation_keeps_original(load_exercise):
    m = load_exercise("ex02_macro")

    class BadUndo(m.Command):
        def __init__(self):
            self.ran = False

        def execute(self):
            self.ran = True

        def undo(self):
            raise OSError("desfazer falhou")

    store = {}
    first = m.SetValue(store, "a", 1)
    bad = BadUndo()
    macro = m.Macro(first, bad, m.Fail("original"))
    with pytest.raises(RuntimeError, match="original"):
        macro.execute()
    assert store == {}                                                                # o undo do primeiro ainda rodou


def test_run_all(load_exercise):
    m = load_exercise("ex02_macro")
    store = {}
    cmds = [m.SetValue(store, "a", 1), m.SetValue(store, "b", 2)]
    assert m.run_all(cmds) == cmds and store == {"a": 1, "b": 2}
    with pytest.raises(RuntimeError):
        m.run_all([m.SetValue(store, "c", 3), m.Fail()])
    assert store == {"a": 1, "b": 2}


# ---------- ex03 ----------
def test_pairs(load_exercise):
    m = load_exercise("ex03_callable_commands")
    store = {"a": 1}
    do, undo = m.make_set(store, "a", 5)
    with pytest.raises(RuntimeError, match="comando não executado"):
        undo()
    do()
    assert store == {"a": 5}
    undo()
    assert store == {"a": 1}
    do2, undo2 = m.make_set(store, "novo", 0)
    do2()
    undo2()
    assert "novo" not in store
    items = []
    d, u = m.make_append(items, "x")
    d()
    d2, u2 = m.make_append(items, "y")
    d2()
    u2()
    u()
    assert items == []
    d()
    items.append("intruso")
    with pytest.raises(RuntimeError, match="lista alterada por fora"):
        u()
    counters = {"hits": 2}
    di, ui = m.make_increment(counters, "hits", 3)
    di()
    assert counters == {"hits": 5}
    ui()
    assert counters == {"hits": 2}
    dn, un = m.make_increment(counters, "novo")
    dn()
    assert counters["novo"] == 1
    un()
    assert "novo" not in counters
    with pytest.raises(ValueError, match="incremento nulo"):
        m.make_increment(counters, "x", 0)


def test_undo_stack(load_exercise):
    m = load_exercise("ex03_callable_commands")
    store, items = {}, []
    s = m.UndoStack()
    s.do(m.make_set(store, "a", 1))
    s.do(m.make_append(items, "x"))
    assert len(s) == 2 and store == {"a": 1} and items == ["x"]
    assert s.undo() is True and items == [] and len(s) == 1
    s.do(m.make_set(store, "b", 2))
    assert s.undo_all() == 2 and store == {} and s.undo() is False and s.undo_all() == 0
    s.do(m.make_set(store, "c", 3))
    assert s.commit() == 1 and len(s) == 0 and store == {"c": 3}

    def boom():
        raise ValueError("falhou")

    before = len(s)
    with pytest.raises(ValueError):
        s.do((boom, lambda: None))
    assert len(s) == before


def test_undo_stack_context_and_errors(load_exercise):
    m = load_exercise("ex03_callable_commands")
    store = {}
    with pytest.raises(KeyError):
        with m.UndoStack() as stack:
            stack.do(m.make_set(store, "a", 1))
            stack.do(m.make_set(store, "b", 2))
            raise KeyError("no meio")
    assert store == {}
    with m.UndoStack() as ok:
        ok.do(m.make_set(store, "a", 1))
    assert store == {"a": 1} and len(ok) == 1                                         # saída normal: nada desfeito
    log = []
    s = m.UndoStack()
    s.do((lambda: None, lambda: log.append("um")))
    s.do((lambda: None, lambda: (_ for _ in ()).throw(OSError("falhou"))))
    s.do((lambda: None, lambda: log.append("tres")))
    with pytest.raises(OSError):
        s.undo_all()
    assert log == ["tres", "um"] and len(s) == 0


def test_command_queue(load_exercise):
    m = load_exercise("ex03_callable_commands")
    q = m.CommandQueue()
    assert q.submit(pow, 2, 5) == 0 and q.submit(lambda: 1 / 0) == 1 and q.submit(str.upper, "ok") == 2 and len(q) == 3
    results = q.run_all()
    assert results[0] == 32 and isinstance(results[1], ZeroDivisionError) and results[2] == "OK" and len(q) == 0
    q.submit(print)
    assert q.clear() == 1 and q.run_all() == []
    with pytest.raises(TypeError):
        q.submit("nao")
    q.submit(dict, a=1)
    assert q.run_all() == [{"a": 1}]


# ---------- ex04 ----------
def registry(m):
    r = m.CommandRegistry()

    @r.handler("deposit")
    def deposit(state, amount):
        return state + amount

    @r.handler("withdraw")
    def withdraw(state, amount):
        if amount > state:
            raise ValueError("saldo insuficiente")
        return state - amount

    @r.handler("reset")
    def reset(state):
        return 0

    return r


def test_registry_execute_and_errors(load_exercise):
    m = load_exercise("ex04_command_log")
    r = registry(m)
    assert r.execute(10, {"name": "deposit", "args": {"amount": 5}}) == 15 and r.execute(7, {"name": "reset"}) == 0
    with pytest.raises(ValueError, match="comando já registrado: reset"):
        r.handler("reset")(lambda s: s)
    for bad in ("texto", {"args": {}}, {"name": "deposit", "args": [1]}, 3, None):
        with pytest.raises(ValueError, match="comando inválido"):
            r.execute(0, bad)
    with pytest.raises(KeyError, match="comando desconhecido: fly"):
        r.execute(0, {"name": "fly"})


def test_replay(load_exercise):
    m = load_exercise("ex04_command_log")
    r = registry(m)
    log = [{"name": "deposit", "args": {"amount": 100}}, {"name": "withdraw", "args": {"amount": 30}}, {"name": "deposit", "args": {"amount": 5}}]
    assert r.replay(0, log) == 75 and r.replay(0, []) == 0 and r.replay(10, log[:1]) == 110
    with pytest.raises(RuntimeError, match="comando 1 falhou: saldo insuficiente") as info:
        r.replay(0, [{"name": "deposit", "args": {"amount": 10}}, {"name": "withdraw", "args": {"amount": 50}}])
    assert isinstance(info.value.__cause__, ValueError)
    with pytest.raises(KeyError):
        r.replay(0, [{"name": "voar"}])
    with pytest.raises(ValueError, match="comando inválido"):
        r.replay(0, ["x"])


def test_journal(load_exercise):
    m = load_exercise("ex04_command_log")
    r = registry(m)
    j = m.Journal(r, 0)
    j.apply({"name": "deposit", "args": {"amount": 100}})
    j.apply({"name": "withdraw", "args": {"amount": 30}})
    with pytest.raises(ValueError, match="saldo insuficiente"):
        j.apply({"name": "withdraw", "args": {"amount": 500}})
    assert j.state == 70 and len(j.log) == 2
    j.log.append("lixo")
    j.log[0]["args"]["amount"] = 1
    assert len(j.log) == 2 and j.log[0]["args"]["amount"] == 100
    text = j.dumps()
    assert json.loads(text) == j.log and text.index('"args"') < text.index('"name"')
    rebuilt = m.Journal.loads(r, 0, text)
    assert rebuilt.state == 70 and rebuilt.log == j.log
    assert j.state_at(0, 0) == 0 and j.state_at(0, 1) == 100 and j.state_at(0, 2) == 70 and j.state_at(1000, 2) == 1070
    for bad in (-1, 3):
        with pytest.raises(ValueError, match="n fora do intervalo"):
            j.state_at(0, bad)


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["command_classico", "command_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
