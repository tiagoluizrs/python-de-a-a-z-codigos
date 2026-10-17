import math
import sys

import pytest


def test_summarize(load_exercise):
    summarize = load_exercise("ex01_summarize").summarize
    assert summarize("t", 1, 2, 4, precision=1, unit="kg") == {
        "title": "t", "count": 3, "total": 7, "mean": 2.3, "unit": "kg"}
    assert summarize("empty")["mean"] is None
    assert summarize("t", 10, 20)["mean"] == 15.0
    assert summarize("t", 1, 2, 2, precision=0)["mean"] == 2
    with pytest.raises(TypeError):
        summarize(title="t")          # título é somente posicional


def test_add_tag_no_shared_default(load_exercise):
    add_tag = load_exercise("ex02_mutable_default").add_tag
    assert add_tag("a") == ["a"]
    assert add_tag("b") == ["b"]
    assert add_tag("c", None) == ["c"]
    mine = ["x"]
    assert add_tag("y", mine) is mine
    assert mine == ["x", "y"]
    assert not isinstance(add_tag.__defaults__[0], list)


def test_first_or(load_exercise):
    first_or = load_exercise("ex02_mutable_default").first_or
    assert first_or([5, 6]) == 5
    assert first_or([], None) is None
    assert first_or([], 0) == 0
    with pytest.raises(ValueError):
        first_or([])


def test_ids(load_exercise):
    mod = load_exercise("ex03_scope")
    mod.reset_ids()
    assert [mod.next_id(), mod.next_id(), mod.next_id()] == [1, 2, 3]
    mod.reset_ids(100)
    assert mod.next_id() == 101


def test_unbound_message(load_exercise):
    message = load_exercise("ex03_scope").unbound_message()
    assert "cannot access local variable" in message


def test_factorials(load_exercise):
    mod = load_exercise("ex04_recursion")
    for n in (0, 1, 5, 20, 100):
        assert mod.fact_recursive(n) == math.factorial(n)
        assert mod.fact_iterative(n) == math.factorial(n)
    for fn in (mod.fact_recursive, mod.fact_iterative):
        with pytest.raises(ValueError):
            fn(-1)
    # a versão recursiva esbarra no limite; a iterativa não
    n = sys.getrecursionlimit() * 2
    assert mod.fact_iterative(n) == math.factorial(n)
    with pytest.raises(RecursionError):
        mod.fact_recursive(n)


def test_fib_iterative(load_exercise):
    fib = load_exercise("ex04_recursion").fib_iterative
    assert [fib(n) for n in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert fib(5000) > 10**1000


def test_measured_depth(load_exercise):
    depth = load_exercise("ex04_recursion").measured_depth()
    limit = sys.getrecursionlimit()
    assert 0.9 * limit < depth <= limit


def test_signature_report(load_exercise):
    report = load_exercise("ex05_signature_report").signature_report

    def f(a, /, b=1, *args, c, d=2, **kw):
        ...

    assert report(f) == [
        ("a", "POSITIONAL_ONLY", False),
        ("b", "POSITIONAL_OR_KEYWORD", True),
        ("args", "VAR_POSITIONAL", False),
        ("c", "KEYWORD_ONLY", False),
        ("d", "KEYWORD_ONLY", True),
        ("kw", "VAR_KEYWORD", False),
    ]
    assert report(lambda: 0) == []
