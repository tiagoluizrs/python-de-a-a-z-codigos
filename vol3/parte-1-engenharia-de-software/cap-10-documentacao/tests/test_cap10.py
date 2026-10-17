import inspect
import types

import pytest

GOOGLE = """Soma dois números.

Mais detalhes em
duas linhas.

Args:
    a (int): O primeiro número,
        que pode ser negativo.
    b: O segundo.

Returns:
    A soma, como
    inteiro.

Raises:
    TypeError: Se não forem números.
    ValueError: Se o resultado overflow.

Example:
    >>> soma(1, 2)
    3
"""


def test_parse_google_docstring(load_exercise):
    parse = load_exercise("ex01_docstring_parser").parse_google_docstring
    result = parse(GOOGLE)
    assert result["summary"] == "Soma dois números." and result["description"] == "Mais detalhes em\nduas linhas."
    assert result["args"] == {"a": "O primeiro número, que pode ser negativo.", "b": "O segundo."}
    assert result["arg_types"] == {"a": "int"}
    assert result["returns"] == "A soma, como inteiro."
    assert result["raises"] == {"TypeError": "Se não forem números.", "ValueError": "Se o resultado overflow."}
    assert result["example"] == ">>> soma(1, 2)\n3"


def test_parse_google_minimal(load_exercise):
    parse = load_exercise("ex01_docstring_parser").parse_google_docstring
    assert parse("Só o resumo.") == {"summary": "Só o resumo.", "description": "", "args": {}, "arg_types": {}, "returns": "", "raises": {}, "example": ""}
    text = "Resumo.\n\nExamples:\n    >>> 1 + 1\n    2\n\n    >>> 2\n    2\n"
    assert parse(text)["example"] == ">>> 1 + 1\n2\n\n>>> 2\n2"


def make_module():
    module = types.ModuleType("demo")
    module.__doc__ = "Módulo de demonstração.\n\nMais texto."

    class Box:
        """Uma caixa.

        Detalhes.
        """

        def open(self, force=False):
            """Abre a caixa."""

        def close(self):
            pass

        def _hidden(self):
            """Interno."""

    def helper(x, *, y=1):
        """Faz algo."""

    def zeta():
        pass

    for obj in (Box, helper, zeta):
        obj.__module__ = "demo"
        setattr(module, obj.__name__, obj)
    module._private = lambda: None
    import os
    module.os = os
    return module


def test_api_markdown(load_exercise):
    to_md = load_exercise("ex02_api_markdown").module_to_markdown
    result = to_md(make_module())
    box_open = str(inspect.signature(make_module().Box.open)) if False else "(self, force=False)"
    assert result == (
        "# demo\n\nMódulo de demonstração.\n\n"
        "## `Box()` (classe)\n\nUma caixa.\n\n"
        f"- `close(self)`: (sem documentação)\n- `open{box_open}`: Abre a caixa.\n\n"
        "## `helper(x, *, y=1)` (função)\n\nFaz algo.\n\n"
        "## `zeta()` (função)\n\n(sem documentação)\n")


def test_api_markdown_with_all(load_exercise):
    to_md = load_exercise("ex02_api_markdown").module_to_markdown
    module = make_module()
    module.__all__ = ["zeta"]
    module.__doc__ = None
    assert to_md(module) == "# demo\n\n(sem documentação)\n\n## `zeta()` (função)\n\n(sem documentação)\n"


SOURCE = '''"""Módulo."""
class Public:
    """Doc."""
    def __init__(self):
        pass
    def documented(self):
        """ok"""
    def missing(self):
        pass
    def _private(self):
        pass

def top():
    def inner():
        pass
    return inner

def _hidden():
    pass

async def fetch():
    """Doc."""

class _Skipped:
    def method(self):
        pass
'''


def test_docstring_coverage(load_exercise):
    m = load_exercise("ex03_doc_coverage")
    documented, total, missing = m.docstring_coverage(SOURCE)
    assert (documented, total, missing) == (4, 6, ["Public.missing", "top"])
    assert m.docstring_coverage("x = 1") == (0, 1, ["<module>"])
    assert m.docstring_coverage('"""Só módulo."""') == (1, 1, [])


def test_percentage(load_exercise):
    percentage = load_exercise("ex03_doc_coverage").percentage
    assert percentage(2, 3) == 66.7 and percentage(0, 0) == 100.0 and percentage(1, 8) == 12.5


def test_anchor_and_toc(load_exercise):
    m = load_exercise("ex04_readme_check")
    assert m.anchor("Instalação e Uso!") == "instalação-e-uso" and m.anchor("  API v2.0 ") == "api-v20"
    md = "# Título\n\n## Instalação\ntexto\n```\n## não é título\n```\n### Passo 1\n## Uso\n### Passo 1\n#### Fundo\n## Uso\n"
    assert m.table_of_contents(md) == (
        "- [Instalação](#instalação)\n  - [Passo 1](#passo-1)\n- [Uso](#uso)\n  - [Passo 1](#passo-1-1)\n- [Uso](#uso-1)")
    assert m.table_of_contents(md, max_level=2) == "- [Instalação](#instalação)\n- [Uso](#uso)\n- [Uso](#uso-1)"


GOOD_README = "# Projeto\n\nDescrição.\n\n## Instalação\n\n```bash\npip install x\n```\n\n## Uso\n\nTexto.\n\n## Licença\n\nMIT\n"


def test_check_readme(load_exercise):
    check = load_exercise("ex04_readme_check").check_readme
    assert check(GOOD_README) == []
    assert check("") == ["no-code", "no-install", "no-license", "no-title", "no-usage", "too-short"]
    bad = "Sem título\n\n## Install\n[ver aqui]()\nlinha\nlinha\nlinha\n"
    assert check(bad) == ["empty-link", "no-code", "no-license", "no-title", "no-usage"]
    assert check(GOOD_README.replace("## Uso", "## Exemplos")) == []
    assert check(GOOD_README.replace("```", "~~~")) == ["no-code"]


CHANGELOG = """# Changelog

## [Unreleased]
### Changed
- algo em andamento

## [1.2.0] - 2026-10-13
### Added
- nova função
- outra função
### Fixed
- bug do relógio

texto solto ignorado

## [1.1.0] - 2026-09-01
### Added
- primeira
"""


def test_parse_changelog(load_exercise):
    parse = load_exercise("ex05_changelog").parse_changelog
    assert parse(CHANGELOG) == [
        {"version": "Unreleased", "date": None, "sections": {"Changed": ["algo em andamento"]}},
        {"version": "1.2.0", "date": "2026-10-13", "sections": {"Added": ["nova função", "outra função"], "Fixed": ["bug do relógio"]}},
        {"version": "1.1.0", "date": "2026-09-01", "sections": {"Added": ["primeira"]}}]
    assert parse("nada") == []


def test_next_version(load_exercise):
    nxt = load_exercise("ex05_changelog").next_version
    assert nxt("1.4.2", {"Fixed": ["x"]}) == "1.4.3" and nxt("1.4.2", {"Added": ["x"], "Fixed": ["y"]}) == "1.5.0"
    assert nxt("1.4.2", {"Changed": ["BREAKING: muda a API"]}) == "2.0.0" and nxt("1.4.2", {"Removed": ["f"]}) == "2.0.0"
    assert nxt("1.4.2", {"Removed": []}) == "1.4.3" and nxt("0.9.9", {}) == "0.9.10"
    for bad in ("1.4", "v1.4.2", "1.4.2rc1"):
        with pytest.raises(ValueError):
            nxt(bad, {})


def test_doctest_runner_passes(load_exercise):
    run = load_exercise("ex06_doctest_runner").run_examples
    doc = """Exemplos.

    >>> 1 + 1
    2
    >>> x = 10
    >>> x * 2
    20
    >>> print("a")
    a
    >>> for i in range(2):
    ...     print(i)
    0
    1
    >>> None
    >>> "texto"
    'texto'
    >>> int("x")
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 10: 'x'
    """
    assert run(doc) == []


def test_doctest_runner_failures(load_exercise):
    run = load_exercise("ex06_doctest_runner").run_examples
    failures = run(">>> 1 + 1\n3\n>>> print('ok')\nok\n>>> [1, 2]\n[1, 2, 3]\n>>> 1 / 0\n2\n")
    assert [f["source"] for f in failures] == ["1 + 1", "[1, 2]", "1 / 0"]
    assert failures[0] == {"source": "1 + 1", "expected": "3", "got": "2"}
    assert failures[2]["got"] == "ZeroDivisionError: division by zero"
    namespace = {}
    assert run(">>> y = 5\n", namespace) == [] and namespace["y"] == 5
    assert run(">>> y + 1\n6\n", namespace) == []
