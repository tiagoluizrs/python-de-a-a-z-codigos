import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
CSV = "name,age\n ana ,3\n,5\nbia,x\n"


def test_csv_and_json_importers(load_exercise):
    m = load_exercise("ex01_importer")
    sink = []
    result = m.CsvImporter(sink).run(CSV)
    assert result.ok == 3 and result.errors == [] and sink == [{"name": " ana ", "age": "3"}, {"name": "", "age": "5"}, {"name": "bia", "age": "x"}]
    sink2 = []
    r2 = m.JsonImporter(sink2).run('[{"name": "a"}, {"name": "b"}]')
    assert r2.ok == 2 and sink2 == [{"name": "a"}, {"name": "b"}]
    with pytest.raises(ValueError, match="json deve ser uma lista"):
        m.JsonImporter([]).run('{"name": "a"}')


def test_template_order_hooks_and_validation(load_exercise):
    m = load_exercise("ex01_importer")
    calls = []

    class Custom(m.CsvImporter):
        def before(self):
            calls.append("before")

        def parse(self, raw):
            calls.append("parse")
            return super().parse(raw)

        def validate(self, row):
            calls.append(f"validate:{row['name']!r}")
            if not row["name"].strip():
                raise ValueError("nome vazio")

        def transform(self, row):
            calls.append("transform")
            row["name"] = row["name"].strip().title()
            return row

        def save(self, rows):
            calls.append(f"save:{len(rows)}")
            super().save(rows)

        def after(self, result):
            calls.append(f"after:{result.ok}/{len(result.errors)}")

    sink = []
    custom = Custom(sink)
    result = custom.run(CSV)
    assert calls == ["before", "parse", "validate:' ana '", "transform", "validate:''", "validate:'bia'", "transform", "save:2", "after:2/1"]
    assert result.errors == [(1, "nome vazio")] and [r["name"] for r in sink] == ["Ana", "Bia"]


def test_after_always_runs_and_final(load_exercise):
    m = load_exercise("ex01_importer")
    events = []

    class BadParse(m.Importer):
        def parse(self, raw):
            raise OSError("sem arquivo")

        def save(self, rows):
            events.append("save")

        def after(self, result):
            events.append(("after", result.ok))

    with pytest.raises(OSError):
        BadParse().run("x")
    assert events == [("after", 0)]
    events.clear()

    class BadSave(m.Importer):
        def parse(self, raw):
            return [{"a": 1}]

        def save(self, rows):
            raise RuntimeError("disco cheio")

        def after(self, result):
            events.append(("after", result.ok))

    with pytest.raises(RuntimeError):
        BadSave().run("x")
    assert events == [("after", 1)]
    assert getattr(m.Importer.run, "__final__", False) is True
    with pytest.raises(TypeError):
        m.Importer()


def test_save_called_even_with_zero_rows(load_exercise):
    m = load_exercise("ex01_importer")
    saved = []

    class Empty(m.Importer):
        def parse(self, raw):
            return []

        def save(self, rows):
            saved.append(list(rows))

    assert Empty().run("") .ok == 0 and saved == [[]]


# ---------- ex02 ----------
def test_function_matches_class(load_exercise):
    f = load_exercise("ex02_pipeline_function")
    c = load_exercise("ex01_importer")
    import csv
    import io

    def parse(raw):
        return list(csv.DictReader(io.StringIO(raw)))

    def check_name(row):
        if not row["name"].strip():
            raise ValueError("nome vazio")

    def normalize(row):
        row["name"] = row["name"].strip().title()
        return row

    sink_f, sink_c = [], []
    rf = f.make_importer(parse, sink_f.extend, validate=check_name, transform=normalize)(CSV)

    class Same(c.CsvImporter):
        validate = staticmethod(check_name)
        transform = staticmethod(normalize)

    rc = Same(sink_c).run(CSV)
    assert (rf.rows, rf.errors, rf.ok) == (rc.rows, rc.errors, rc.ok) and sink_f == sink_c


def test_make_importer_hooks_and_errors(load_exercise):
    f = load_exercise("ex02_pipeline_function")
    log = []
    run = f.make_importer(lambda raw: [{"a": 1}, {"a": 2}], lambda rows: log.append(("save", len(rows))), before=lambda: log.append("before"), after=lambda r: log.append(("after", r.ok)))
    assert run("x").ok == 2 and log == ["before", ("save", 2), ("after", 2)]
    log.clear()

    def bad_save(rows):
        raise RuntimeError("falhou")

    with pytest.raises(RuntimeError):
        f.make_importer(lambda raw: [{"a": 1}], bad_save, after=lambda r: log.append("after"))("x")
    assert log == ["after"]
    log.clear()
    with pytest.raises(OSError):
        f.make_importer(lambda raw: (_ for _ in ()).throw(OSError("x")), lambda rows: None, after=lambda r: log.append("after"))("x")
    assert log == ["after"]
    for bad in ((None, print), (print, "x")):
        with pytest.raises(TypeError, match="passo obrigatório precisa ser chamável"):
            f.make_importer(*bad)


def test_compose_and_validators(load_exercise):
    f = load_exercise("ex02_pipeline_function")
    assert f.compose_steps(str.strip, str.title)("  ana maria ") == "Ana Maria" and f.compose_steps()(5) == 5
    with pytest.raises(TypeError):
        f.compose_steps(str.strip, "x")
    order = []

    def r1(row):
        order.append("r1")

    def r2(row):
        order.append("r2")
        raise ValueError("falhou r2")

    def r3(row):
        order.append("r3")

    check = f.validators(r1, r2, r3)
    with pytest.raises(ValueError, match="falhou r2"):
        check({})
    assert order == ["r1", "r2"] and f.validators()({}) is None


# ---------- ex03 ----------
def test_transaction(load_exercise):
    m = load_exercise("ex03_context_templates")
    store = {"a": 1}
    with m.transaction(store) as s:
        assert s is store
        s["b"] = 2
        s["a"] = 9
    assert store == {"a": 9, "b": 2}
    ident = id(store)
    with pytest.raises(RuntimeError):
        with m.transaction(store):
            store["c"] = 3
            del store["a"]
            raise RuntimeError("falhou")
    assert store == {"a": 9, "b": 2} and id(store) == ident


def test_temporary_attr_and_collect_errors(load_exercise):
    m = load_exercise("ex03_context_templates")

    class Obj:
        x = 1

    o = Obj()
    with m.temporary_attr(o, "x", 5):
        assert o.x == 5
    assert o.x == 1
    with pytest.raises(KeyError):
        with m.temporary_attr(o, "novo", 1):
            assert o.novo == 1
            raise KeyError("k")
    assert not hasattr(o, "novo")
    errors = []
    with m.collect_errors(errors):
        raise ValueError("a")
    with m.collect_errors(errors, KeyError):
        raise KeyError("b")
    assert [type(e) for e in errors] == [ValueError, KeyError]
    with pytest.raises(ZeroDivisionError):
        with m.collect_errors(errors, KeyError):
            1 / 0
    with pytest.raises(KeyboardInterrupt):
        with m.collect_errors(errors):
            raise KeyboardInterrupt
    assert len(errors) == 2


def test_ordered_cleanup_and_run_steps(load_exercise):
    m = load_exercise("ex03_context_templates")
    log = []
    with m.ordered_cleanup(log, "db") as name:
        assert name == "db"
    assert log == ["abrir db", "fechar db"]
    log.clear()
    with pytest.raises(ValueError):
        with m.ordered_cleanup(log, "net"):
            raise ValueError("x")
    assert log == ["abrir net", "erro em net: ValueError", "fechar net"]
    log.clear()
    assert m.run_steps([("a", lambda: 1), ("b", lambda: 2)], log) == [1, 2]
    assert log == ["abrir a", "fechar a", "abrir b", "fechar b"]
    log.clear()
    ran = []

    def boom():
        raise RuntimeError("quebrou")

    with pytest.raises(RuntimeError):
        m.run_steps([("a", lambda: ran.append("a")), ("b", boom), ("c", lambda: ran.append("c"))], log)
    assert ran == ["a"] and log[-3:] == ["abrir b", "erro em b: RuntimeError", "fechar b"] and "abrir c" not in log


# ---------- ex04 ----------
def test_countdown(load_exercise):
    m = load_exercise("ex04_abc_mixins")
    c = m.Countdown(4)
    assert len(c) == 5 and c[0] == 4 and c[-1] == 0 and c[1:3] == [3, 2] and list(c) == [4, 3, 2, 1, 0]
    assert 2 in c and 9 not in c and list(reversed(c)) == [0, 1, 2, 3, 4] and c.index(1) == 3 and c.count(3) == 1
    with pytest.raises(IndexError):
        c[5]
    with pytest.raises(ValueError, match="start negativo"):
        m.Countdown(-1)
    assert isinstance(c, m.Sequence) and sorted(c) == [0, 1, 2, 3, 4] and max(c) == 4


def test_case_insensitive_map(load_exercise):
    m = load_exercise("ex04_abc_mixins")
    d = m.CaseInsensitiveMap({"Content-Type": "text", "X-Id": 7})
    assert d["content-type"] == "text" and d["X-ID"] == 7 and len(d) == 2 and list(d) == ["Content-Type", "X-Id"]
    assert d.get("x-id") == 7 and d.get("nada", "?") == "?" and "CONTENT-TYPE" in d and 3 not in d
    assert dict(d.items()) == {"Content-Type": "text", "X-Id": 7} and list(d.values()) == ["text", 7] and list(d.keys()) == ["Content-Type", "X-Id"]
    with pytest.raises(KeyError):
        d["zzz"]
    with pytest.raises(KeyError):
        d[3]
    with pytest.raises(ValueError, match="chave duplicada: A"):
        m.CaseInsensitiveMap({"a": 1, "A": 2})
    assert d == {"Content-Type": "text", "X-Id": 7} and isinstance(d, m.Mapping)


def test_ordered_set(load_exercise):
    m = load_exercise("ex04_abc_mixins")
    a, b = m.OrderedSet([3, 1, 2, 3]), m.OrderedSet([2, 5])
    assert list(a) == [3, 1, 2] and len(a) == 3 and 1 in a and 9 not in a and repr(a) == "OrderedSet([3, 1, 2])"
    assert list(a | b) == [3, 1, 2, 5] and list(a & b) == [2] and list(a - b) == [3, 1] and list(a ^ b) == [3, 1, 5]
    assert isinstance(a | b, m.OrderedSet) and a.isdisjoint({9}) and not a.isdisjoint({1}) and (a & b) <= a and a == m.OrderedSet([1, 2, 3])
    a.add(7)
    a.discard(1)
    a.discard(999)
    assert list(a) == [3, 2, 7]
    a.remove(2)
    with pytest.raises(KeyError):
        a.remove(2)
    assert a.pop() == 3 and list(a) == [7]
    a |= {8, 9}
    assert list(a) == [7, 8, 9]
    a.clear()
    assert len(a) == 0 and list(m.OrderedSet()) == []


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["template_classico", "template_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
