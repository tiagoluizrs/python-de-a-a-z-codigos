import dataclasses
import sys
import types

import pytest


def test_package_name(load_exercise):
    package_name = load_exercise("ex01_scaffold").package_name
    assert package_name("My-App.Tool") == "my_app_tool" and package_name("abc") == "abc"
    with pytest.raises(ValueError):
        package_name("1abc")
    with pytest.raises(ValueError):
        package_name("a b")


def test_create_project(load_exercise, tmp_path):
    import tomllib
    module = load_exercise("ex01_scaffold")
    created = module.create_project(tmp_path, "my-app")
    assert created == sorted(created)
    for expected in ("pyproject.toml", "README.md", ".gitignore", "src/my_app/__init__.py",
                     "src/my_app/__main__.py", "src/my_app/cli.py", "tests/test_smoke.py"):
        assert expected in created and (tmp_path / "my-app" / expected).is_file()
    config = tomllib.loads((tmp_path / "my-app" / "pyproject.toml").read_text(encoding="utf-8"))
    assert config["project"]["name"] == "my-app" and config["project"]["scripts"] == {"my-app": "my_app.cli:main"}
    assert config["build-system"]["build-backend"] == "uv_build"
    assert (tmp_path / "my-app" / "README.md").read_text().startswith("# my-app")
    with pytest.raises(FileExistsError):
        module.create_project(tmp_path, "my-app")


def test_generated_project_is_valid(load_exercise, tmp_path):
    scaffold, layout = load_exercise("ex01_scaffold"), load_exercise("ex02_check_layout")
    scaffold.create_project(tmp_path, "good-one")
    assert layout.check_layout(tmp_path / "good-one") == []


def test_check_layout_problems(load_exercise, tmp_path):
    check_layout = load_exercise("ex02_check_layout").check_layout
    (tmp_path / "mylib").mkdir()
    (tmp_path / "mylib" / "__init__.py").write_text("")
    (tmp_path / "mylib" / "sub").mkdir()
    (tmp_path / "mylib" / "sub" / "x.py").write_text("")
    assert check_layout(tmp_path) == ["flat-layout", "missing-init", "no-pyproject", "no-readme", "no-tests"]

    other = tmp_path / "other"
    (other / "src" / "pkg").mkdir(parents=True)
    (other / "src" / "pkg" / "__init__.py").write_text("")
    (other / "src" / "pkg" / "test_inside.py").write_text("")
    (other / "tests").mkdir()
    (other / "pyproject.toml").write_text("")
    (other / "README.md").write_text("")
    assert check_layout(other) == ["tests-in-package"]


def test_read_project(load_exercise, tmp_path):
    read_project = load_exercise("ex03_pyproject_reader").read_project
    path = tmp_path / "pyproject.toml"
    path.write_text('''[project]
name = "demo"
version = "1.2.3"
requires-python = ">=3.15"
dependencies = ["requests>=2"]
[project.scripts]
demo = "demo:main"
[build-system]
build-backend = "uv_build"
[dependency-groups]
dev = ["pytest"]
''')
    assert read_project(str(path)) == {
        "name": "demo", "version": "1.2.3", "requires_python": ">=3.15", "dependencies": ["requests>=2"],
        "scripts": {"demo": "demo:main"}, "build_backend": "uv_build", "groups": {"dev": ["pytest"]}}
    path.write_text('[project]\nname = "min"\n')
    result = read_project(path)
    assert result["version"] is None and result["dependencies"] == [] and result["groups"] == {}
    path.write_text("[tool.x]\na = 1\n")
    with pytest.raises(ValueError):
        read_project(path)


def test_entry_points(load_exercise, tmp_path, monkeypatch):
    module = load_exercise("ex04_entry_points")
    assert module.parse_entry_point("pkg.mod:func") == ("pkg.mod", "func")
    assert module.parse_entry_point("a:B.c") == ("a", "B.c")
    for bad in ("nocolon", "a:", ":b", "a b:c", "a:b:c"):
        with pytest.raises(ValueError):
            module.parse_entry_point(bad)
    (tmp_path / "myentry.py").write_text(
        "class Tool:\n    @staticmethod\n    def run(argv):\n        return len(argv)\n"
        "def ok(argv):\n    return None\ndef text(argv):\n    return 'falhou'\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    assert module.load_entry_point("myentry:Tool.run")(["a", "b"]) == 2
    assert module.run_entry_point("myentry:ok", []) == 0
    assert module.run_entry_point("myentry:text", []) == 1
    assert module.run_entry_point("myentry:Tool.run", ["x", "y", "z"]) == 3
    with pytest.raises(ImportError):
        module.load_entry_point("nao_existe_xyz:f")
    with pytest.raises(AttributeError):
        module.load_entry_point("myentry:missing")


def test_public_api(load_exercise):
    module = load_exercise("ex05_public_api")
    plain = types.ModuleType("plain")
    plain.b, plain.a, plain._hidden, plain.sys = 1, 2, 3, sys
    assert module.public_names(plain) == ["a", "b"] and module.broken_exports(plain) == []
    declared = types.ModuleType("declared")
    declared.x = 1
    declared.__all__ = ["x", "ghost", "also_ghost"]
    assert module.public_names(declared) == ["also_ghost", "ghost", "x"]
    assert module.broken_exports(declared) == ["also_ghost", "ghost"]
    assert module.star_import_names(declared) == ["x"]


def _make_package(root, files):
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def test_import_graph(load_exercise, tmp_path):
    graph = load_exercise("ex06_import_graph").import_graph
    _make_package(tmp_path, {
        "pkg/__init__.py": "from . import core\nfrom .util import helper\nimport os\n",
        "pkg/core.py": "from pkg.util import helper\nimport json\n",
        "pkg/util.py": "def helper(): pass\n",
        "pkg/sub/__init__.py": "",
        "pkg/sub/leaf.py": "from .. import util\nfrom ..core import x\nfrom . import other\n",
        "pkg/sub/other.py": "def f():\n    import pkg.core\n",
    })
    result = graph(tmp_path, "pkg")
    assert result == {
        "pkg": {"pkg.core", "pkg.util"}, "pkg.core": {"pkg.util"}, "pkg.util": set(), "pkg.sub": set(),
        "pkg.sub.leaf": {"pkg.util", "pkg.core", "pkg.sub.other"}, "pkg.sub.other": {"pkg.core"}}


def test_find_cycle(load_exercise, tmp_path):
    module = load_exercise("ex06_import_graph")
    assert module.find_cycle({"a": {"b"}, "b": {"c"}, "c": set()}) is None
    cycle = module.find_cycle({"a": {"b"}, "b": {"c"}, "c": {"a"}, "d": set()})
    assert cycle[0] == cycle[-1] and set(cycle) == {"a", "b", "c"}
    _make_package(tmp_path, {"p/__init__.py": "", "p/a.py": "from . import b\n", "p/b.py": "from .a import x\n"})
    cycle = module.find_cycle(module.import_graph(tmp_path, "p"))
    assert cycle and cycle[0] == cycle[-1] and set(cycle) == {"p.a", "p.b"}
