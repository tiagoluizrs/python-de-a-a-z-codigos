import sys


def test_is_in_virtualenv(load_exercise):
    result = load_exercise("ex01_venv").is_in_virtualenv()
    assert result == (sys.prefix != sys.base_prefix)


def test_parse_pyvenv_cfg(load_exercise):
    parse = load_exercise("ex02_pyvenv_cfg").parse_pyvenv_cfg
    text = "home = /usr/bin\nversion = 3.15\n\ncommand = python -m venv --prompt=x .venv\n"
    assert parse(text) == {
        "home": "/usr/bin",
        "version": "3.15",
        "command": "python -m venv --prompt=x .venv",
    }
    assert parse("") == {}


def test_dependency_names(load_exercise):
    names = load_exercise("ex03_requirements").dependency_names
    deps = ["Requests>=2.34", "rich", 'numpy==2.0.1; python_version>="3.9"', "my_pkg.sub[extra]~=1.0"]
    assert names(deps) == ["requests", "rich", "numpy", "my_pkg.sub"]
