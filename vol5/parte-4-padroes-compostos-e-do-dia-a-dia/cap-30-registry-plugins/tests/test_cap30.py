import importlib
import json
import subprocess
import sys
import threading
import time
import types
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_add_get_and_name_normalization(load_exercise):
    m = load_exercise("ex01_registry")
    reg = m.Registry("exportador")
    sentinel = object()
    assert reg.add(" CSV ", sentinel) is sentinel
    assert reg.get("csv") is sentinel and reg.get("Csv") is sentinel and reg.get("  CSV  ") is sentinel
    assert "csv" in reg and "CSV" in reg and " csv " in reg and "json" not in reg and "" not in reg and None not in reg and 3 not in reg
    for bad in ("", "   ", None, 3):
        with pytest.raises(ValueError, match="nome inválido"):
            reg.add(bad, sentinel)
    assert len(reg) == 1


def test_duplicates_and_replace(load_exercise):
    m = load_exercise("ex01_registry")
    reg = m.Registry("exportador")
    reg.add("csv", 1)
    with pytest.raises(ValueError, match="exportador já registrado: csv"):
        reg.add("CSV", 2)
    assert reg.get("csv") == 1
    assert reg.add("csv", 3, replace=True) == 3 and reg.get("csv") == 3
    with pytest.raises(ValueError, match="plugin já registrado: x"):
        r2 = m.Registry()
        r2.add("x", 1)
        r2.add("x", 2)


def test_decorator_forms(load_exercise):
    m = load_exercise("ex01_registry")
    reg = m.Registry()

    @reg.register("csv")
    def to_csv(rows):
        return "csv"

    @reg.register()
    def to_json(rows):
        return "json"

    @reg.register
    class ToXml:
        pass

    assert to_csv([]) == "csv" and to_json([]) == "json" and isinstance(ToXml(), ToXml)             # o decorado continua utilizável
    assert reg.names() == ["csv", "to_json", "toxml"]
    assert reg.get("csv") is to_csv and reg.get("TO_JSON") is to_json and reg.get("toxml") is ToXml

    with pytest.raises(ValueError, match="plugin já registrado: csv"):
        @reg.register("CSV")
        def other(rows):
            return "outro"

    @reg.register("csv", replace=True)
    def better(rows):
        return "melhor"

    assert reg.get("csv") is better
    with pytest.raises(ValueError, match="nome inválido"):
        reg.register("  ")(lambda: None)


def test_get_error_messages(load_exercise):
    m = load_exercise("ex01_registry")
    reg = m.Registry("exportador")
    with pytest.raises(KeyError) as empty:
        reg.get("yaml")
    assert empty.value.args[0] == "exportador desconhecido: 'yaml'; disponíveis: nenhum"
    reg.add("json", 1)
    reg.add("csv", 2)
    with pytest.raises(KeyError) as filled:
        reg.get(" YAML ")
    assert filled.value.args[0] == "exportador desconhecido: ' YAML '; disponíveis: csv, json"
    for bad in ("", None):
        with pytest.raises(KeyError, match="desconhecido"):
            reg.get(bad)


def test_create_iteration_and_listing(load_exercise):
    m = load_exercise("ex01_registry")
    reg = m.Registry()
    reg.add("point", lambda x, y=0: (x, y))
    reg.add("alpha", dict)
    assert reg.create("POINT", 1, y=2) == (1, 2) and reg.create("alpha", a=1) == {"a": 1}
    assert list(reg) == ["alpha", "point"] and reg.names() == ["alpha", "point"] and len(reg) == 2
    assert [name for name, _ in reg.items()] == ["alpha", "point"] and reg.items()[0] == ("alpha", dict)
    with pytest.raises(KeyError):
        reg.create("zzz")


def test_unregister_snapshot_restore(load_exercise):
    m = load_exercise("ex01_registry")
    reg = m.Registry()
    reg.add("a", 1)
    reg.add("b", 2)
    assert reg.unregister(" A ") == 1 and "a" not in reg and len(reg) == 1
    with pytest.raises(KeyError, match="desconhecido"):
        reg.unregister("a")
    reg.add("a", 10)
    snap = reg.snapshot()
    assert snap == {"a": 10, "b": 2} and isinstance(snap, dict)
    snap["z"] = 0
    assert "z" not in reg                                                  # é uma cópia
    reg.add("c", 3)
    reg.restore({"a": 1})
    assert reg.names() == ["a"] and reg.get("a") == 1


def test_isolated_restores_on_exit(load_exercise):
    m = load_exercise("ex01_registry")
    reg = m.Registry()
    reg.add("keep", 1)
    with reg.isolated() as inner:
        assert inner is reg
        reg.add("temp", 2)
        reg.unregister("keep")
        assert reg.names() == ["temp"]
    assert reg.names() == ["keep"] and reg.get("keep") == 1
    with pytest.raises(RuntimeError, match="boom"):
        with reg.isolated():
            reg.add("temp2", 3)
            raise RuntimeError("boom")
    assert reg.names() == ["keep"]
    with reg.isolated():
        with reg.isolated():
            reg.add("deep", 1)
        assert "deep" not in reg
        reg.add("mid", 1)
    assert reg.names() == ["keep"]


def test_freeze(load_exercise):
    m = load_exercise("ex01_registry")
    reg = m.Registry()
    reg.add("a", 1)
    assert reg.frozen is False and reg.freeze() is reg and reg.frozen is True and reg.freeze() is reg
    for call in (lambda: reg.add("b", 2), lambda: reg.register("c")(len), lambda: reg.register(len), lambda: reg.unregister("a"), lambda: reg.restore({}), lambda: reg.isolated().__enter__()):
        with pytest.raises(RuntimeError, match="registro congelado"):
            call()
    assert reg.get("a") == 1 and "a" in reg and len(reg) == 1 and reg.names() == ["a"] and reg.snapshot() == {"a": 1}


def test_thread_safety(load_exercise):
    m = load_exercise("ex01_registry")
    reg = m.Registry()
    threads = [threading.Thread(target=lambda i=i: reg.add(f"p{i}", i)) for i in range(60)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(reg) == 60 and reg.get("p17") == 17
    same, outcomes, barrier = m.Registry(), [], threading.Barrier(24)

    def contender(i):
        barrier.wait()
        try:
            same.add("same", i)
            outcomes.append("ok")
        except ValueError:
            outcomes.append("duplicado")

    workers = [threading.Thread(target=contender, args=(i,)) for i in range(24)]
    for t in workers:
        t.start()
    for t in workers:
        t.join()
    assert outcomes.count("ok") == 1 and outcomes.count("duplicado") == 23


# ---------- ex02 ----------
def test_auto_registration_and_names(load_exercise):
    m = load_exercise("ex02_init_subclass")

    class CsvExporter(m.Exporter):
        extension = ".csv"

    class JsonExporter(m.Exporter):
        pass

    class Xml(m.Exporter, name="XML-Export"):
        pass

    assert m.Exporter.names() == ["csv", "json", "xml-export"]
    assert m.Exporter.registry["csv"] is CsvExporter and m.Exporter.registry["xml-export"] is Xml
    assert isinstance(m.Exporter.create("csv"), CsvExporter) and isinstance(m.Exporter.create(" JSON "), JsonExporter)


def test_abstract_is_not_inherited_and_levels(load_exercise):
    m = load_exercise("ex02_init_subclass")

    class TextBase(m.Exporter, abstract=True):
        pass

    class Plain(TextBase):
        pass

    class Fancy(Plain):
        pass

    class MoreBase(Fancy, abstract=True):
        pass

    class Last(MoreBase):
        pass

    assert m.Exporter.names() == ["fancy", "last", "plain"] and "textbase" not in m.Exporter.registry and "morebase" not in m.Exporter.registry


def test_duplicates_empty_names_and_unknown_kwargs(load_exercise):
    m = load_exercise("ex02_init_subclass")

    class CsvExporter(m.Exporter):
        pass

    with pytest.raises(ValueError, match="exportador já registrado: csv"):
        class Csv(m.Exporter):
            pass

    with pytest.raises(ValueError, match="exportador já registrado: other"):
        class Other(m.Exporter, name="OTHER"):
            pass
        class Other2(m.Exporter, name="other"):
            pass

    assert m.Exporter.registry["csv"] is CsvExporter
    with pytest.raises(ValueError, match="nome vazio"):
        types.new_class("Exporter", (m.Exporter,))
    with pytest.raises(TypeError):
        class Bad(m.Exporter, name="bad", bogus=1):
            pass
    assert "bad" not in m.Exporter.registry


def test_create_names_unregister(load_exercise):
    m = load_exercise("ex02_init_subclass")

    class SepExporter(m.Exporter):
        def __init__(self, sep=","):
            self.sep = sep

    assert m.Exporter.create("sep", sep=";").sep == ";" and m.Exporter.create("SEP").sep == ","
    with pytest.raises(KeyError) as info:
        m.Exporter.create("yaml")
    assert info.value.args[0] == "exportador desconhecido: 'yaml'; disponíveis: sep"
    assert m.Exporter.unregister(" Sep ") is SepExporter and m.Exporter.names() == []
    with pytest.raises(KeyError) as empty:
        m.Exporter.unregister("sep")
    assert empty.value.args[0] == "exportador desconhecido: 'sep'; disponíveis: nenhum"
    with pytest.raises(KeyError, match="nenhum"):
        m.Exporter.create("x")


def test_for_extension_and_export(load_exercise):
    m = load_exercise("ex02_init_subclass")

    class ZetaExporter(m.Exporter):
        extension = ".txt"

    class AlphaExporter(m.Exporter):
        extension = ".TXT"

    class CsvExporter(m.Exporter):
        extension = ".csv"

        def export(self, rows):
            return "csv!"

    class NoExtExporter(m.Exporter):
        pass

    assert m.Exporter.for_extension(".txt") is AlphaExporter and m.Exporter.for_extension(".TXT") is AlphaExporter and m.Exporter.for_extension(".CSV") is CsvExporter
    with pytest.raises(KeyError, match="nenhum exportador para '.pdf'"):
        m.Exporter.for_extension(".pdf")
    assert m.Exporter.create("csv").export([]) == "csv!"
    with pytest.raises(NotImplementedError):
        m.Exporter.create("zeta").export([])
    assert m.Exporter.extension == "" and NoExtExporter.extension == ""


# ---------- ex03 ----------
@pytest.fixture
def plugin_env(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(tmp_path))
    created = []

    def make_package(modules):
        name = f"plug_{uuid.uuid4().hex[:8]}"
        package = tmp_path / name
        package.mkdir()
        (package / "__init__.py").write_text("", encoding="utf-8")
        for module, code in modules.items():
            (package / f"{module}.py").write_text(code, encoding="utf-8")
        importlib.invalidate_caches()
        created.append(name)
        return name

    yield tmp_path, make_package, created
    for loaded in list(sys.modules):
        if any(loaded == c or loaded.startswith(c + ".") for c in created):
            del sys.modules[loaded]
    importlib.invalidate_caches()


GOOD = 'NAME = "{name}"\nAPI_VERSION = 2\n\ndef run(rows):\n    return "{name}"\n'


def test_discover_valid_and_invalid_plugins(load_exercise, plugin_env):
    m = load_exercise("ex03_discovery")
    _, make_package, _ = plugin_env
    package = make_package({
        "a_csv": GOOD.format(name="csv"),
        "b_json": GOOD.format(name="json"),
        "c_old": 'NAME = "old"\nAPI_VERSION = 1\n\ndef run(rows):\n    return 1\n',
        "d_boom": 'raise RuntimeError("boom")\n',
        "e_missing": "import modulo_inexistente_zz\n",
        "f_noname": "API_VERSION = 2\n\ndef run(rows):\n    return 1\n",
        "g_norun": 'NAME = "x"\nAPI_VERSION = 2\n',
        "h_dup": GOOD.format(name="csv"),
        "i_noapi": 'NAME = "noapi"\n\ndef run(rows):\n    return 1\n',
        "j_emptyname": 'NAME = ""\nAPI_VERSION = 2\n\ndef run(rows):\n    return 1\n',
        "_private": GOOD.format(name="hidden"),
    })
    result = m.discover(package)
    assert list(result.plugins) == ["csv", "json"] and result.plugins["csv"].run([]) == "csv" and result.plugins["json"].__name__ == f"{package}.b_json"
    assert result.errors == {
        "c_old": "versão de API não suportada: 1",
        "d_boom": "RuntimeError: boom",
        "e_missing": "ModuleNotFoundError: No module named 'modulo_inexistente_zz'",
        "f_noname": "falta NAME",
        "g_norun": "falta run",
        "h_dup": "nome repetido: csv (já usado por a_csv)",
        "i_noapi": "versão de API não suportada: None",
        "j_emptyname": "falta NAME",
    }


def test_discover_sorts_plugin_names_and_checks_the_package(load_exercise, plugin_env):
    m = load_exercise("ex03_discovery")
    _, make_package, _ = plugin_env
    package = make_package({"a_zeta": GOOD.format(name="zeta"), "b_alpha": GOOD.format(name="alpha"), "c_mid": GOOD.format(name="mid")})
    result = m.discover(package)
    assert list(result.plugins) == ["alpha", "mid", "zeta"] and result.errors == {}
    with pytest.raises(ValueError, match="math não é um pacote"):
        m.discover("math")
    with pytest.raises(ModuleNotFoundError):
        m.discover("pacote_que_nao_existe_zz")
    empty = m.discover(make_package({}))
    assert empty.plugins == {} and empty.errors == {}


def make_dist(root, group, entries, dist_name=None, module=None):
    dist_name = dist_name or f"dist_{uuid.uuid4().hex[:8]}"
    info = root / f"{dist_name}-1.0.dist-info"
    info.mkdir()
    (info / "METADATA").write_text(f"Metadata-Version: 2.1\nName: {dist_name}\nVersion: 1.0\n", encoding="utf-8")
    lines = "".join(f"{name} = {value}\n" for name, value in entries)
    (info / "entry_points.txt").write_text(f"[{group}]\n{lines}", encoding="utf-8")
    if module:
        (root / f"{module[0]}.py").write_text(module[1], encoding="utf-8")
    importlib.invalidate_caches()


def test_load_entry_points(load_exercise, plugin_env):
    m = load_exercise("ex03_discovery")
    root, _, created = plugin_env
    group = f"cap30.group.{uuid.uuid4().hex[:8]}"
    mod = f"epmod_{uuid.uuid4().hex[:8]}"
    created.append(mod)
    make_dist(root, group, [("ok", f"{mod}:Good"), ("missing", f"{mod}:Missing"), ("no_module", "modulo_inexistente_zz:X"), ("also", f"{mod}:VALUE")],
              module=(mod, "class Good:\n    pass\n\nVALUE = 3\n"))
    result = m.load_entry_points(group)
    assert list(result.plugins) == ["also", "ok"] and result.plugins["also"] == 3 and result.plugins["ok"].__name__ == "Good"
    assert set(result.errors) == {"missing", "no_module"}
    assert result.errors["missing"].startswith("AttributeError: ") and "Missing" in result.errors["missing"]
    assert result.errors["no_module"] == "ModuleNotFoundError: No module named 'modulo_inexistente_zz'"
    assert m.load_entry_points(f"cap30.empty.{uuid.uuid4().hex[:8]}") == m.Discovery()


def test_entry_point_duplicate_names_from_two_distributions(load_exercise, plugin_env):
    m = load_exercise("ex03_discovery")
    root, _, created = plugin_env
    group = f"cap30.group.{uuid.uuid4().hex[:8]}"
    mod = f"epmod_{uuid.uuid4().hex[:8]}"
    created.append(mod)
    make_dist(root, group, [("same", f"{mod}:Second"), ("other", f"{mod}:Second")], module=(mod, "class First:\n    pass\n\nclass Second:\n    pass\n"))
    make_dist(root, group, [("same", f"{mod}:First")])
    result = m.load_entry_points(group)
    assert result.plugins["same"].__name__ == "First"                              # em ordem de (nome, valor): "mod:First" vem antes de "mod:Second"
    assert result.plugins["other"].__name__ == "Second" and result.errors == {"same": "nome repetido: same"}


# ---------- ex04 ----------
def test_lazy_register_validation(load_exercise):
    m = load_exercise("ex04_lazy_registry")
    reg = m.LazyRegistry()
    reg.register("dumps", "json:dumps")
    with pytest.raises(ValueError, match="já registrado: dumps"):
        reg.register("dumps", "json:loads")
    for bad in ("json", "json:", ":dumps", "json:dumps:extra", " json:dumps", "json: dumps", "", ":"):
        with pytest.raises(ValueError, match="caminho inválido"):
            reg.register("x", bad)
    assert reg.names() == ["dumps"] and len(reg) == 1 and "dumps" in reg and "x" not in reg


def test_lazy_get_imports_once(load_exercise, monkeypatch):
    m = load_exercise("ex04_lazy_registry")
    calls, real = [], importlib.import_module

    def counting(name, *a, **k):
        calls.append(name)
        return real(name, *a, **k)

    monkeypatch.setattr(m.importlib, "import_module", counting)
    reg = m.LazyRegistry()
    reg.register("dumps", "json:dumps")
    reg.register("sqrt", "math:sqrt")
    reg.register("odict", "collections:OrderedDict.fromkeys")
    assert calls == [] and reg.loaded() == [] and not reg.is_loaded("dumps")
    assert reg.get("dumps") is json.dumps and calls == ["json"] and reg.loaded() == ["dumps"] and reg.is_loaded("dumps")
    assert reg.get("dumps") is json.dumps and calls == ["json"]                    # em cache: não importa de novo
    assert reg.get("sqrt")(16) == 4 and calls == ["json", "math"]
    assert list(reg.get("odict")("ab")) == ["a", "b"] and reg.names() == ["dumps", "odict", "sqrt"]


def test_lazy_non_string_targets_and_replace(load_exercise):
    m = load_exercise("ex04_lazy_registry")
    reg = m.LazyRegistry()
    thing = object()
    reg.register("obj", thing)
    reg.register("lazy", "json:dumps")
    assert reg.is_loaded("obj") and reg.loaded() == ["obj"] and reg.get("obj") is thing
    reg.get("lazy")
    reg.register("lazy", "json:loads", replace=True)
    assert not reg.is_loaded("lazy") and reg.get("lazy") is json.loads
    reg.register("obj", "math:sqrt", replace=True)
    assert not reg.is_loaded("obj") and reg.get("obj")(9) == 3


def test_lazy_unknown_and_failures_are_not_cached(load_exercise, tmp_path, monkeypatch):
    m = load_exercise("ex04_lazy_registry")
    reg = m.LazyRegistry()
    with pytest.raises(KeyError) as empty:
        reg.get("x")
    assert empty.value.args[0] == "desconhecido: 'x'; disponíveis: nenhum"
    name = f"late_mod_{uuid.uuid4().hex[:8]}"
    reg.register("late", f"{name}:VALUE")
    reg.register("noattr", "json:nao_existe")
    reg.register("a", "json:dumps")
    with pytest.raises(KeyError) as filled:
        reg.get("zzz")
    assert filled.value.args[0] == "desconhecido: 'zzz'; disponíveis: a, late, noattr"
    with pytest.raises(LookupError, match=r"^não pôde ser carregado: 'late' \(ModuleNotFoundError: ") as info:
        reg.get("late")
    assert isinstance(info.value.__cause__, ModuleNotFoundError) and not isinstance(info.value, KeyError) and not reg.is_loaded("late")
    with pytest.raises(LookupError, match=r"AttributeError") as attr:
        reg.get("noattr")
    assert isinstance(attr.value.__cause__, AttributeError)
    (tmp_path / f"{name}.py").write_text("VALUE = 5\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    assert reg.get("late") == 5 and reg.is_loaded("late")
    sys.modules.pop(name, None)


def test_lazy_preload(load_exercise):
    m = load_exercise("ex04_lazy_registry")
    reg = m.LazyRegistry()
    reg.register("a", "json:dumps")
    reg.register("b", "math:sqrt")
    reg.register("c", "collections:OrderedDict")
    assert reg.preload("a") == ["a"] and reg.loaded() == ["a"]
    assert reg.preload("a", "b") == ["b"]
    assert reg.preload() == ["c"] and reg.loaded() == ["a", "b", "c"]
    assert m.LazyRegistry().preload() == []
    broken = m.LazyRegistry()
    broken.register("bad", "modulo_inexistente_zz:X")
    with pytest.raises(LookupError):
        broken.preload()


def test_lazy_threads_import_once(load_exercise, monkeypatch):
    m = load_exercise("ex04_lazy_registry")
    calls, real = [], importlib.import_module

    def slow(name, *a, **k):
        calls.append(name)
        time.sleep(0.05)
        return real(name, *a, **k)

    monkeypatch.setattr(m.importlib, "import_module", slow)
    reg = m.LazyRegistry()
    reg.register("dumps", "json:dumps")
    results = []
    threads = [threading.Thread(target=lambda: results.append(reg.get("dumps"))) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert calls == ["json"] and results == [json.dumps] * 8


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["registry_classico", "registry_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
