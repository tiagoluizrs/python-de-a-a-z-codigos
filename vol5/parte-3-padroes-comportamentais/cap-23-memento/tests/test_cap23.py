import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_editor_basic_operations(load_exercise):
    m = load_exercise("ex01_text_editor")
    e = m.Editor()
    assert (e.text, e.cursor, e.selection) == ("", 0, None)
    e.type("olá mundo")
    assert e.text == "olá mundo" and e.cursor == 9
    e.move(3)
    e.type(",")
    assert e.text == "olá, mundo" and e.cursor == 4
    e.select(5, 10)
    assert e.selection == (5, 10) and e.cursor == 10
    e.delete_selection()
    assert e.text == "olá, " and e.cursor == 5 and e.selection is None
    e.select(0, 3)
    e.type("x")
    assert e.selection is None


def test_editor_errors(load_exercise):
    m = load_exercise("ex01_text_editor")
    e = m.Editor()
    e.type("abc")
    for bad in (-1, 4):
        with pytest.raises(IndexError):
            e.move(bad)
    for start, end in ((2, 1), (-1, 2), (0, 4)):
        with pytest.raises(ValueError, match="seleção inválida"):
            e.select(start, end)
    with pytest.raises(ValueError, match="sem seleção"):
        e.delete_selection()
    e.select(1, 2)
    e.move(0)
    assert e.selection is None


def test_memento_save_restore_and_owner(load_exercise):
    m = load_exercise("ex01_text_editor")
    e, other = m.Editor(), m.Editor()
    e.type("abc")
    e.select(0, 2)
    memento = e.save()
    assert isinstance(memento, m.EditorMemento)
    e.type("ZZZ")
    e.restore(memento)
    assert (e.text, e.cursor, e.selection) == ("abc", 2, (0, 2))
    e.type("!")
    e.restore(memento)
    assert e.text == "abc"
    with pytest.raises(ValueError, match="memento de outro editor"):
        other.restore(memento)
    with pytest.raises(TypeError):
        e.restore("abc")
    with pytest.raises(AttributeError):
        memento._text = "hack"


def test_history_undo_redo(load_exercise):
    m = load_exercise("ex01_text_editor")
    e = m.Editor()
    h = m.History(e)
    assert h.can_undo is False and h.can_redo is False and h.undo() is False and h.redo() is False
    h.do(e.type, "olá")
    h.do(e.type, ", mundo")
    assert e.text == "olá, mundo" and h.can_undo and not h.can_redo
    assert h.undo() is True and e.text == "olá" and h.can_redo
    assert h.undo() is True and e.text == "" and not h.can_undo
    assert h.redo() is True and h.redo() is True and e.text == "olá, mundo" and h.redo() is False
    h.undo()
    h.do(e.type, "!")
    assert h.can_redo is False and e.text == "olá!"


def test_history_do_failure_restores_and_records_nothing(load_exercise):
    m = load_exercise("ex01_text_editor")
    e = m.Editor()
    h = m.History(e)
    h.do(e.type, "abc")

    def broken():
        e.type("lixo")
        e.move(999)

    with pytest.raises(IndexError):
        h.do(broken)
    assert e.text == "abc" and e.cursor == 3
    h.undo()
    assert e.text == "" and h.can_undo is False
    assert h.do(lambda a, b: a + b, 2, 3) == 5


def test_history_limit(load_exercise):
    m = load_exercise("ex01_text_editor")
    e = m.Editor()
    h = m.History(e, limit=2)
    for ch in "abcd":
        h.do(e.type, ch)
    assert h.undo() and h.undo() and h.undo() is False
    assert e.text == "ab"
    for bad in (0, -3):
        with pytest.raises(ValueError, match="limite inválido"):
            m.History(e, limit=bad)


# ---------- ex02 ----------
def test_inventory_basic(load_exercise):
    m = load_exercise("ex02_inventory_transaction")
    inv = m.Inventory()
    inv.add("maçã", 5)
    inv.add("maçã", 2)
    inv.label("maçã", "fruta")
    assert inv.quantity("maçã") == 7 and inv.quantity("pera") == 0 and inv.labels_of("maçã") == ["fruta"] and inv.labels_of("pera") == []
    inv.labels_of("maçã").append("x")
    assert inv.labels_of("maçã") == ["fruta"]
    inv.remove("maçã", 7)
    assert inv.quantity("maçã") == 0 and inv.labels_of("maçã") == []
    for bad in (0, -1, 1.5, True, "2"):
        with pytest.raises(ValueError, match="quantidade inválida"):
            inv.add("x", bad)
    with pytest.raises(ValueError, match="estoque insuficiente: pera"):
        inv.remove("pera", 1)
    inv.add("pera", 1)
    with pytest.raises(ValueError, match="estoque insuficiente: pera"):
        inv.remove("pera", 2)
    with pytest.raises(LookupError):
        inv.label("uva", "x")
    assert (inv.commits, inv.rollbacks) == (0, 0)


def test_transaction_commit_and_rollback(load_exercise):
    m = load_exercise("ex02_inventory_transaction")
    inv = m.Inventory()
    inv.add("maçã", 5)
    inv.label("maçã", "fruta")
    with inv.transaction():
        inv.remove("maçã", 2)
        inv.add("pera", 1)
    assert inv.quantity("maçã") == 3 and inv.quantity("pera") == 1 and (inv.commits, inv.rollbacks) == (1, 0)
    with pytest.raises(ValueError, match="estoque insuficiente"):
        with inv.transaction():
            inv.add("uva", 9)
            inv.label("maçã", "oferta")                    # uma lista interna: a cópia rasa NÃO restauraria
            inv.remove("maçã", 3)                          # o item some
            inv.remove("pera", 5)
    assert inv.quantity("uva") == 0 and inv.quantity("maçã") == 3 and inv.labels_of("maçã") == ["fruta"]
    assert (inv.commits, inv.rollbacks) == (1, 1)


def test_transaction_rolls_back_base_exceptions(load_exercise):
    m = load_exercise("ex02_inventory_transaction")
    inv = m.Inventory()
    inv.add("a", 1)
    with pytest.raises(KeyboardInterrupt):
        with inv.transaction():
            inv.add("a", 10)
            raise KeyboardInterrupt
    assert inv.quantity("a") == 1 and inv.rollbacks == 1


def test_transaction_dry_run(load_exercise):
    m = load_exercise("ex02_inventory_transaction")
    inv = m.Inventory()
    inv.add("a", 1)
    with inv.transaction(dry_run=True):
        inv.add("a", 99)
        assert inv.quantity("a") == 100
    assert inv.quantity("a") == 1 and (inv.commits, inv.rollbacks) == (0, 1)
    with pytest.raises(RuntimeError):
        with inv.transaction(dry_run=True):
            raise RuntimeError
    assert (inv.commits, inv.rollbacks) == (0, 2)


def test_nested_transactions(load_exercise):
    m = load_exercise("ex02_inventory_transaction")
    inv = m.Inventory()
    inv.add("a", 10)
    with inv.transaction():
        inv.remove("a", 1)
        try:
            with inv.transaction():
                inv.remove("a", 5)
                raise ValueError("falhou por dentro")
        except ValueError:
            pass
        assert inv.quantity("a") == 9                       # só a de dentro foi desfeita
        inv.remove("a", 2)
    assert inv.quantity("a") == 7 and (inv.commits, inv.rollbacks) == (1, 1)
    with pytest.raises(ValueError):
        with inv.transaction():
            inv.remove("a", 1)
            with inv.transaction():
                inv.remove("a", 1)
            raise ValueError("falhou por fora")
    assert inv.quantity("a") == 7


# ---------- ex03 ----------
class Doc:
    def __init__(self):
        self.items = []

    def snapshot(self):
        return list(self.items)

    def restore(self, snapshot):
        self.items = list(snapshot)


def test_undo_manager_requires_snapshottable(load_exercise):
    m = load_exercise("ex03_undo_manager")
    with pytest.raises(TypeError, match="alvo sem snapshot/restore"):
        m.UndoManager(object())
    with pytest.raises(TypeError):
        m.UndoManager([1, 2])
    for bad in (0, -1):
        with pytest.raises(ValueError, match="limite inválido"):
            m.UndoManager(Doc(), limit=bad)


def test_undo_redo_flow(load_exercise):
    m = load_exercise("ex03_undo_manager")
    d = Doc()
    u = m.UndoManager(d)
    assert not u.can_undo and not u.can_redo
    with pytest.raises(LookupError, match="nada para desfazer"):
        u.undo()
    with pytest.raises(LookupError, match="nada para refazer"):
        u.redo()
    for name in ("a", "b", "c"):
        u.checkpoint(f"digitar {name}")
        d.items.append(name)
    assert d.items == ["a", "b", "c"] and u.labels() == ["digitar a", "digitar b", "digitar c"]
    assert u.undo() == "digitar c" and d.items == ["a", "b"] and u.can_redo
    assert u.undo() == "digitar b" and d.items == ["a"]
    assert u.redo() == "digitar b" and d.items == ["a", "b"]
    assert u.redo() == "digitar c" and d.items == ["a", "b", "c"] and not u.can_redo
    assert u.labels() == ["digitar a", "digitar b", "digitar c"]


def test_new_checkpoint_clears_redo(load_exercise):
    m = load_exercise("ex03_undo_manager")
    d = Doc()
    u = m.UndoManager(d)
    u.checkpoint("x")
    d.items.append(1)
    u.undo()
    assert u.can_redo
    u.checkpoint()
    assert not u.can_redo and u.labels() == [None]


def test_undo_manager_limit(load_exercise):
    m = load_exercise("ex03_undo_manager")
    d = Doc()
    u = m.UndoManager(d, limit=2)
    for i in range(4):
        u.checkpoint(str(i))
        d.items.append(i)
    assert u.labels() == ["2", "3"]
    u.undo()
    u.undo()
    assert d.items == [0, 1] and not u.can_undo


def test_goto(load_exercise):
    m = load_exercise("ex03_undo_manager")
    d = Doc()
    u = m.UndoManager(d)
    for name in ("a", "b", "c", "b"):
        u.checkpoint(name)
        d.items.append(name)
    assert d.items == ["a", "b", "c", "b"]
    assert u.goto("c") == 2 and d.items == ["a", "b"] and u.labels() == ["a", "b"]
    assert u.redo() == "c" and u.redo() == "b" and d.items == ["a", "b", "c", "b"]
    with pytest.raises(LookupError, match="checkpoint desconhecido: zzz"):
        u.goto("zzz")
    assert d.items == ["a", "b", "c", "b"] and not u.can_redo
    assert u.goto("a") == 4 and d.items == []
    assert u.redo() == "a"


# ---------- ex04 ----------
def lines(n):
    return [f"linha {i}" for i in range(n)]


def test_document_immutable_and_structural(load_exercise):
    m = load_exercise("ex04_versioned_document")
    doc = m.Document(lines(3))
    assert doc.lines == ("linha 0", "linha 1", "linha 2") and isinstance(doc.lines, tuple) and len(doc) == 3
    assert m.Document.of("a", "b").text == "a\nb" and m.Document().lines == () and m.Document.of("x") == m.Document(["x"])
    with pytest.raises(AttributeError):
        doc.lines = ()
    new = doc.replace(1, "OUTRA")
    assert new.lines == ("linha 0", "OUTRA", "linha 2") and doc.lines[1] == "linha 1"
    assert new.lines[0] is doc.lines[0] and new.lines[2] is doc.lines[2]
    assert doc.insert(0, "topo").lines[0] == "topo" and doc.insert(3, "fim").lines[-1] == "fim"
    assert doc.delete(0).lines == ("linha 1", "linha 2") and doc.delete(2).lines == ("linha 0", "linha 1")
    assert doc.lines == ("linha 0", "linha 1", "linha 2")


def test_document_index_errors(load_exercise):
    m = load_exercise("ex04_versioned_document")
    doc = m.Document.of("a", "b")
    for call in (lambda: doc.insert(-1, "x"), lambda: doc.insert(3, "x"), lambda: doc.delete(2), lambda: doc.delete(-1), lambda: doc.replace(2, "x"), lambda: doc.replace(-1, "x")):
        with pytest.raises(IndexError, match="linha fora do documento"):
            call()
    with pytest.raises(IndexError):
        m.Document().delete(0)
    assert doc.insert(2, "c").lines == ("a", "b", "c")


def test_repository_commits_log_checkout(load_exercise):
    m = load_exercise("ex04_versioned_document")
    repo = m.Repository()
    assert repo.head == m.Document() and len(repo) == 0 and repo.log() == []
    d1 = m.Document(lines(4))
    d2 = d1.replace(1, "mudou")
    d3 = d2.delete(0)
    assert (repo.commit(d1, "início"), repo.commit(d2, "troca"), repo.commit(d3, "remove")) == (1, 2, 3)
    assert repo.head is d3 and len(repo) == 3
    assert repo.log() == [(3, "remove"), (2, "troca"), (1, "início")]
    assert repo.checkout(1) is d1 and repo.head is d1 and repo.get(2) is d2
    assert repo.commit(d1.insert(0, "novo"), "ramo") == 4 and len(repo) == 4 and repo.log()[0] == (4, "ramo")
    with pytest.raises(LookupError, match="commit desconhecido: 9"):
        repo.checkout(9)
    with pytest.raises(LookupError):
        repo.get(0)
    with pytest.raises(ValueError, match="mensagem vazia"):
        repo.commit(d1, "   ")
    with pytest.raises(TypeError):
        repo.commit("texto", "msg")
    assert len(repo) == 4


def test_repository_diff(load_exercise):
    m = load_exercise("ex04_versioned_document")
    repo = m.Repository()
    a = repo.commit(m.Document.of("x", "y", "z"), "a")
    b = repo.commit(m.Document.of("x", "Y", "z", "w"), "b")
    c = repo.commit(m.Document.of("z"), "c")
    assert repo.diff(a, b) == {"removed": ["y"], "added": ["Y", "w"]}
    assert repo.diff(a, c) == {"removed": ["x", "y"], "added": []}
    assert repo.diff(c, a) == {"removed": [], "added": ["x", "y"]}
    assert repo.diff(a, a) == {"removed": [], "added": []}
    with pytest.raises(LookupError):
        repo.diff(a, 99)


def test_repository_shares_line_objects(load_exercise):
    m = load_exercise("ex04_versioned_document")
    repo = m.Repository()
    doc = m.Document(lines(1000))
    first = repo.commit(doc, "base")
    for i in range(10):
        doc = doc.replace(i, f"editada {i}")
        repo.commit(doc, f"edição {i}")
    assert repo.shared_lines(first, 1) == 1000 and repo.shared_lines(first, 2) == 999
    assert repo.shared_lines(first, 11) == 990 and repo.shared_lines(2, 11) == 991 and repo.shared_lines(first, first) == 1000


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["memento_classico", "memento_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
