import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
FOLDER = "gabaritos" if os.environ.get("CHECK_GABARITOS") else "exercicios"


def mypy(code_file, usage=""):
    """Roda ``mypy --strict`` na solução (copiada) e em um arquivo de uso opcional."""
    with tempfile.TemporaryDirectory() as folder:
        module = Path(folder) / "solution.py"
        module.write_text(Path(code_file).read_text(encoding="utf-8"), encoding="utf-8")
        targets = [str(module)]
        if usage:
            user = Path(folder) / "usage.py"
            user.write_text(usage, encoding="utf-8")
            targets.append(str(user))
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "--strict", "--no-incremental", "--cache-dir", folder, "--python-version", "3.15",
             "--no-color-output", "--no-error-summary", *targets],
            capture_output=True, text=True, encoding="utf-8", cwd=folder)
        return result.stdout.replace(folder + os.sep, "")


def solution(name):
    return ROOT / FOLDER / f"{name}.py"


# ---------- exercício 1 ----------
def test_ex01_strict_clean(load_exercise):
    output = mypy(solution("ex01_annotate"))
    assert output.strip() == "", output


def test_ex01_inferred_types():
    usage = """
from solution import first, apply_twice, count_words, safe_div, pairs, log_level
reveal_type(first([1, 2]))
reveal_type(first(["a"]))
reveal_type(apply_twice(str.upper, "a"))
reveal_type(count_words("a b"))
reveal_type(safe_div(1, 2))
reveal_type(pairs([1], ["a"]))
log_level("trace")
"""
    output = mypy(solution("ex01_annotate"), usage)
    for expected in ('int | None', 'str | None', 'Revealed type is "str"', "dict[str, int]",
                     "float | None", "list[tuple[int, str]]"):
        assert expected in output, output
    assert 'usage.py:9: error: Argument 1 to "log_level"' in output


# ---------- exercício 2 ----------
def test_ex02_runtime(load_exercise):
    module = load_exercise("ex02_protocols")
    assert module.total_area([module.Square(2), module.Square(3)]) == 13
    assert module.total_area([]) == 0

    class Good:
        def close(self):
            pass

    class Bad:
        def close(self):
            raise RuntimeError("falhou B")

    class Worse:
        def close(self):
            raise ValueError("falhou C")

    assert module.close_all([Good(), Bad(), Good(), Worse()]) == ["falhou B", "falhou C"]
    assert isinstance(Good(), module.Closeable) and not isinstance(object(), module.Closeable)


def test_ex02_static():
    assert mypy(solution("ex02_protocols")).strip() == ""
    usage = """
from solution import Circle, Square, total_area, close_all
total_area([Circle(1), Square(2)])
class NoArea:
    pass
total_area([NoArea()])
close_all([open("x")])
close_all([object()])
"""
    output = mypy(solution("ex02_protocols"), usage)
    assert "usage.py:6" in output and "usage.py:8" in output and "usage.py:7" not in output, output


# ---------- exercício 3 ----------
def test_ex03_runtime(load_exercise):
    module = load_exercise("ex03_typeddict")
    good = {"name": "Ana", "age": 30, "address": {"street": "Rua A", "city": "Recife", "zip": "1"}, "extra": 1}
    assert module.parse_user(good) == {"name": "Ana", "age": 30, "address": {"street": "Rua A", "city": "Recife"}}
    assert module.parse_user({**good, "email": "a@x.com"})["email"] == "a@x.com"
    assert module.summary(module.parse_user(good)) == "Ana (30), Recife"
    assert module.summary(module.parse_user({**good, "email": "a@x.com"})) == "Ana (30), Recife <a@x.com>"
    cases = [({k: v for k, v in good.items() if k != "name"}, "name"), ({**good, "age": True}, "age"),
             ({**good, "age": "30"}, "age"), ({**good, "address": "x"}, "address"),
             ({**good, "address": {"street": "R", "city": 5}}, "address.city"),
             ({**good, "address": {"street": "R"}}, "address.city"), ({**good, "email": 3}, "email")]
    for data, path in cases:
        with pytest.raises(ValueError) as info:
            module.parse_user(data)
        assert str(info.value) == path


def test_ex03_static():
    assert mypy(solution("ex03_typeddict")).strip() == ""
    usage = """
from solution import User, parse_user, summary
ok: User = {"name": "a", "age": 1, "address": {"street": "s", "city": "c"}}
bad: User = {"age": 1, "address": {"street": "s", "city": "c"}}
user = parse_user({})
reveal_type(user)
reveal_type(summary(user))
"""
    output = mypy(solution("ex03_typeddict"), usage)
    assert 'usage.py:4: error: Missing key "name" for TypedDict "User"' in output and "usage.py:3" not in output, output
    assert 'Revealed type is "TypedDict(' in output or '"solution.User"' in output or "User" in output


# ---------- exercício 4 ----------
def test_ex04_runtime(load_exercise):
    module = load_exercise("ex04_generics")
    stack = module.Stack()
    assert stack.push(1).push(2).push(3) is stack and len(stack) == 3
    assert list(stack) == [3, 2, 1] and stack.peek() == 3 and stack.pop() == 3 and len(stack) == 2
    stack.pop()
    stack.pop()
    with pytest.raises(IndexError, match="pilha vazia"):
        stack.pop()
    with pytest.raises(IndexError):
        stack.peek()
    box = module.Box(3).map(str).map(lambda s: s + "!")
    assert box.value == "3!" and module.Box([1]).map(len).value == 1
    assert module.merge_sorted([1, 3, 5], [2, 3, 4, 9]) == [1, 2, 3, 3, 4, 5, 9]
    assert module.merge_sorted([], ["a"]) == ["a"] and module.merge_sorted([], []) == []
    first, second = (1, "a"), (1, "b")
    items = module.merge_sorted([first], [second])
    assert items[0] is first


def test_ex04_static():
    assert mypy(solution("ex04_generics")).strip() == ""
    usage = """
from solution import Stack, Box, merge_sorted
s = Stack[int]()
reveal_type(s.pop())
reveal_type(s.push(1))
reveal_type(Box(3).map(str))
reveal_type(merge_sorted([1], [2]))
class NoOrder:
    pass
merge_sorted([NoOrder()], [NoOrder()])
s.push("texto")
"""
    output = mypy(solution("ex04_generics"), usage)
    assert 'Revealed type is "int"' in output and "solution.Stack[int]" in output, output
    assert "solution.Box[str]" in output and "list[int]" in output, output
    assert "usage.py:10" in output and "usage.py:11" in output, output


# ---------- exercício 5 ----------
HINT_CASES = [
    (1, int, True), (True, int, False), (1, float, True), (1.5, float, True), (True, float, False), ("a", str, True),
    (None, None, True), (None, type(None), True), (0, None, False), (1, object, True),
]


@pytest.mark.parametrize("value, hint, expected", HINT_CASES)
def test_ex05_simple(load_exercise, value, hint, expected):
    assert load_exercise("ex05_runtime_check").conforms(value, hint) is expected


def test_ex05_compound(load_exercise):
    from typing import Any, Literal, Optional
    conforms = load_exercise("ex05_runtime_check").conforms
    assert conforms([1, 2], list[int]) and not conforms([1, "a"], list[int]) and not conforms((1,), list[int])
    assert conforms({"a": 1}, dict[str, int]) and not conforms({"a": "x"}, dict[str, int]) and not conforms({1: 1}, dict[str, int])
    assert conforms({1, 2}, set[int]) and conforms(frozenset({"a"}), frozenset[str])
    assert conforms((1, "a"), tuple[int, str]) and not conforms((1,), tuple[int, str]) and not conforms((1, 2), tuple[int, str])
    assert conforms((1, 2, 3), tuple[int, ...]) and conforms((), tuple[int, ...]) and not conforms((1, "a"), tuple[int, ...])
    assert conforms(None, int | None) and conforms("a", int | str) and not conforms(1.5, int | str)
    assert conforms(None, Optional[int]) and conforms(3, Optional[int])
    assert conforms("r", Literal["r", "w"]) and not conforms("x", Literal["r", "w"]) and not conforms(True, Literal[1])
    assert conforms(object(), Any) and conforms([[1], [2, 3]], list[list[int]]) and not conforms([[1], ["a"]], list[list[int]])
    assert conforms({"k": [1, None]}, dict[str, list[int | None]])


def test_ex05_check_call(load_exercise):
    check_call = load_exercise("ex05_runtime_check").check_call

    def repeat(text: str, times: int, sep=",") -> str:
        return sep.join([text] * times)

    assert check_call(repeat, "a", 2) == "a,a" and check_call(repeat, "a", times=2, sep="-") == "a-a"
    with pytest.raises(TypeError, match="times: '2' não é"):
        check_call(repeat, "a", "2")
    with pytest.raises(TypeError, match="text: 1 não é"):
        check_call(repeat, 1, 2)

    def liar(x: int) -> int:
        return "oops"                                  # type: ignore[return-value]

    with pytest.raises(TypeError, match="retorno: 'oops' não é"):
        check_call(liar, 1)

    def untyped(x, y):
        return x + y

    assert check_call(untyped, 1, 2) == 3


# ---------- exercício 6 ----------
def test_ex06_runtime(load_exercise):
    module = load_exercise("ex06_overloads")
    assert module.parse("42") == 42 and module.parse(b"abc") == "abc" and module.parse(None) is None
    data = {"a": 1, "b": 2}
    assert module.get(data, "a") == 1 and module.get(data, "z") is None and module.get(data, "z", "padrão") == "padrão"
    assert module.get(data, "a", 99) == 1


def test_ex06_static():
    assert mypy(solution("ex06_overloads")).strip() == ""
    usage = """
from solution import parse, get
reveal_type(parse("1"))
reveal_type(parse(b"x"))
reveal_type(parse(None))
parse(1.5)
data: dict[str, int] = {"a": 1}
reveal_type(get(data, "a"))
reveal_type(get(data, "a", "d"))
reveal_type(get(data, "a", 0))
"""
    output = mypy(solution("ex06_overloads"), usage)
    assert 'usage.py:3: note: Revealed type is "int"' in output, output
    assert 'usage.py:4: note: Revealed type is "str"' in output and 'usage.py:5: note: Revealed type is "None"' in output, output
    assert "usage.py:6: error: No overload variant" in output, output
    assert 'int | None' in output and "int | str" in output, output
