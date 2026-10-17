import importlib
import sys
import textwrap

import pytest


def _fresh_import(monkeypatch, root, name):
    monkeypatch.syspath_prepend(str(root))
    sys.modules.pop(name, None)
    importlib.invalidate_caches()
    return importlib.import_module(name)


def test_make_package(load_exercise, tmp_path, monkeypatch):
    make_package = load_exercise("ex01_public_api").make_package
    make_package(
        tmp_path, "shop_pkg_t1",
        {"core": "def run():\n    return 'ok'\n",
         "_helpers": "def h():\n    return 1\n"},
        {"core": ["run"]})
    try:
        pkg = _fresh_import(monkeypatch, tmp_path, "shop_pkg_t1")
        assert pkg.run() == "ok"
        assert pkg.__all__ == ["run"]
        assert (tmp_path / "shop_pkg_t1" / "_helpers.py").exists()
        ns = {}
        exec("from shop_pkg_t1 import *", ns)
        assert "run" in ns and "h" not in ns
    finally:
        for key in [k for k in sys.modules if k.startswith("shop_pkg_t1")]:
            del sys.modules[key]


def test_find_cycle(load_exercise):
    find_cycle = load_exercise("ex02_import_cycle").find_cycle
    assert find_cycle({"a": ["b"], "b": ["c"], "c": []}) is None
    assert find_cycle({}) is None
    assert find_cycle({"a": ["b"], "b": ["a"]}) in (["a", "b", "a"],
                                                    ["b", "a", "b"])
    cycle = find_cycle({"main": ["a"], "a": ["b"], "b": ["c"],
                        "c": ["a"]})
    assert cycle[0] == cycle[-1]
    assert set(cycle) == {"a", "b", "c"}
    assert find_cycle({"a": ["a"]}) == ["a", "a"]
    # diamante nao e ciclo
    assert find_cycle({"a": ["b", "c"], "b": ["d"], "c": ["d"]}) is None


def test_modules_loaded_by(load_exercise):
    modules_loaded_by = load_exercise("ex03_loaded_by").modules_loaded_by
    loaded = modules_loaded_by("json")
    assert "json" in loaded
    assert {"json.decoder", "json.encoder"} <= loaded
    assert "os" not in loaded       # ja carregado na inicializacao
    assert "colorsys" in modules_loaded_by("colorsys")


def test_load_plugins(load_exercise, tmp_path):
    load_plugins = load_exercise("ex04_plugin_loader").load_plugins
    (tmp_path / "a_upper.py").write_text(textwrap.dedent("""
        def register():
            return {"name": "upper", "run": str.upper}
    """))
    (tmp_path / "b_double.py").write_text(textwrap.dedent("""
        def register():
            return {"name": "double", "run": lambda x: x * 2}
    """))
    (tmp_path / "_private.py").write_text(
        "def register():\n    return {'name': 'x', 'run': None}\n")
    (tmp_path / "c_broken.py").write_text("raise RuntimeError('boom')\n")
    (tmp_path / "d_noreg.py").write_text("X = 1\n")
    before = list(sys.path)
    plugins = load_plugins(tmp_path)
    assert list(plugins) == ["upper", "double"]
    assert plugins["upper"]("ab") == "AB"
    assert plugins["double"](3) == 6
    assert sys.path == before


SAMPLE = """\
import time: self [us] | cumulative | imported package
import time:       100 |        100 |   _io
import time:       808 |      13785 | json
import time:       300 |        900 |   re
"""


def test_parse_importtime(load_exercise):
    parse = load_exercise("ex05_import_cost").parse_importtime
    assert parse(SAMPLE, "json") == 13785
    assert parse(SAMPLE, "_io") == 100
    assert parse(SAMPLE, "re") == 900
    with pytest.raises(ValueError):
        parse(SAMPLE, "decimal")


def test_most_expensive(load_exercise):
    most_expensive = load_exercise("ex05_import_cost").most_expensive
    name, micros = most_expensive(["colorsys", "decimal"])
    assert name == "decimal"
    assert isinstance(micros, int) and micros > 0


def test_find_shadowed(load_exercise, tmp_path):
    find_shadowed = load_exercise("ex06_shadowing").find_shadowed
    (tmp_path / "random.py").write_text("")
    (tmp_path / "utils.py").write_text("")
    (tmp_path / "json").mkdir()
    (tmp_path / "notes.txt").write_text("")
    (tmp_path / "email.txt").write_text("")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "myapp").mkdir()
    assert find_shadowed(tmp_path) == ["json", "random"]
    assert find_shadowed(tmp_path / "myapp") == []
