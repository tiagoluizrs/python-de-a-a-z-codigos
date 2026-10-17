"""Corrige os exercícios.

Os exercícios 1 a 4 pedem que VOCÊ escreva testes; aqui eles são executados
contra a implementação correta (devem passar) e contra mutantes (devem falhar).
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
FOLDER = "gabaritos" if os.environ.get("CHECK_GABARITOS") else "exercicios"

TARGETS = {
    "ex01_test_slugify": ("slugify", "slugify_impl"),
    "ex02_test_stack": ("stack", "stack_impl"),
    "ex03_test_interest": ("interest", "interest_impl"),
    "ex04_test_overdue": ("overdue", "overdue_impl"),
}


def run_student_tests(test_name, implementation_file, module_name):
    with tempfile.TemporaryDirectory() as folder:
        shutil.copy(implementation_file, Path(folder) / f"{module_name}.py")
        env = {**os.environ, "PYTHONPATH": folder, "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(ROOT / FOLDER / f"{test_name}.py"), "-q", "--no-header",
             "-p", "no:cacheprovider", "--rootdir", folder, "-c", os.devnull],
            capture_output=True, text=True, env=env, encoding="utf-8")
        return result.returncode == 0, result.stdout


@pytest.mark.parametrize("test_name", list(TARGETS))
def test_student_tests_pass_on_correct_implementation(test_name):
    target, module_name = TARGETS[test_name]
    passed, output = run_student_tests(test_name, ROOT / "alvos" / target / "correto.py", module_name)
    assert passed, f"seus testes falham até na implementação CORRETA:\n{output[-1500:]}"


@pytest.mark.parametrize("test_name", list(TARGETS))
def test_student_tests_kill_all_mutants(test_name):
    target, module_name = TARGETS[test_name]
    survivors = []
    for mutant in sorted((ROOT / "alvos" / target).glob("mutante_*.py")):
        passed, _ = run_student_tests(test_name, mutant, module_name)
        if passed:
            survivors.append(mutant.stem.removeprefix("mutante_"))
    assert not survivors, f"mutantes que SOBREVIVERAM (seus testes não os detectam): {survivors}"


def test_mini_pytest_raises(load_exercise):
    raises = load_exercise("ex05_mini_pytest").raises
    with raises(ValueError) as info:
        raise ValueError("deu ruim")
    assert str(info.value) == "deu ruim"
    with raises(ArithmeticError):
        1 / 0                                                  # subclasse conta
    with raises(KeyError, match="chave|key"):
        {}["chave"]
    with pytest.raises(AssertionError, match="DID NOT RAISE ValueError"):
        with raises(ValueError):
            pass
    with pytest.raises(AssertionError):
        with raises(ValueError, match="xyz"):
            raise ValueError("abc")
    with pytest.raises(TypeError):
        with raises(ValueError):
            raise TypeError("outro tipo propaga")


def test_mini_pytest_runs_and_summarizes(load_exercise):
    module = load_exercise("ex05_mini_pytest")
    suite = types.SimpleNamespace()

    def test_ok():
        assert 1 + 1 == 2

    def test_bad():
        assert 1 + 1 == 3

    def test_err():
        {}["x"]

    def helper():                                              # não começa com test_
        raise RuntimeError

    @module.parametrize("a, b, expected", [(1, 2, 3), (2, 2, 4), (2, 2, 5)])
    def test_sum(a, b, expected):
        assert a + b == expected

    @module.parametrize("n", [1, 2, 0])
    def test_inverse(n):
        assert 1 / n

    for func in (test_ok, test_bad, helper, test_err, test_sum, test_inverse):
        setattr(suite, func.__name__, func)
    suite.test_not_callable = 42
    results = module.run_tests(suite)
    assert results == {
        "test_ok": "passed", "test_bad": "failed", "test_err": "error",
        "test_sum[0]": "passed", "test_sum[1]": "passed", "test_sum[2]": "failed",
        "test_inverse[0]": "passed", "test_inverse[1]": "passed", "test_inverse[2]": "error"}
    assert list(results)[:3] == ["test_ok", "test_bad", "test_err"]
    assert module.summary(results) == "5 passed, 2 failed, 2 error"


def test_mini_pytest_summary(load_exercise):
    summary = load_exercise("ex05_mini_pytest").summary
    assert summary({}) == "no tests ran"
    assert summary({"a": "passed"}) == "1 passed"
    assert summary({"a": "error", "b": "failed", "c": "passed", "d": "passed"}) == "2 passed, 1 failed, 1 error"


CASES = [
    (1.0, 1.0000001, True), (1.0, 1.01, False), (0.1 + 0.2, 0.3, True), (0, 1e-13, True), (0, 1e-6, False),
    (1e9, 1e9 + 100, True), (1e9, 1e9 + 1e4, False), (math.inf, math.inf, True), (math.inf, 1e308, False),
    (-math.inf, math.inf, False), (math.nan, math.nan, False), ([1, 2], [1, 2.0000001], True),
    ([1, 2], [1, 2, 3], False), ((1.0, 2.0), [1.0, 2.0], True), ({"a": 0.3}, {"a": 0.1 + 0.2}, True),
    ({"a": 1}, {"b": 1}, False), ({"a": [1, {"b": 2}]}, {"a": [1, {"b": 2.0000000001}]}, True),
    ("abc", "abc", True), ("abc", "abd", False), (1, "1", False), ([1], 1, False), (True, True, True),
    (True, 1, False), (1, True, False), (None, None, True), (None, 0, False),
]


@pytest.mark.parametrize("actual, expected, result", CASES)
def test_approx_equal_matches_expectations(load_exercise, actual, expected, result):
    approx_equal = load_exercise("ex06_approx").approx_equal
    assert approx_equal(actual, expected) is result


def test_approx_equal_options_and_agreement_with_pytest(load_exercise):
    approx_equal = load_exercise("ex06_approx").approx_equal
    assert approx_equal(math.nan, math.nan, nan_ok=True) is True
    assert approx_equal(100, 110, rel=0.2) is True and approx_equal(100, 110, rel=0.05) is False
    assert approx_equal(0, 0.5, abs_tol=1) is True
    for actual, expected in [(0.1 + 0.2, 0.3), (1.0, 1.0001), (5, 5.0), (100, 100.00001)]:
        assert approx_equal(actual, expected) == (actual == pytest.approx(expected))
