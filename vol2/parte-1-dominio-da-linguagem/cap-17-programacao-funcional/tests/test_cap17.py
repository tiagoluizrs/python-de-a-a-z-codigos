import pytest


def test_memoize_lru_and_stats(load_exercise):
    memoize = load_exercise("ex01_memoize").memoize
    calls = []

    @memoize(maxsize=2)
    def double(x, *, k=1):
        """doc"""
        calls.append(x)
        return x * 2 * k

    assert double.__name__ == "double" and double.__doc__ == "doc"
    assert double(1) == 2 and double(1) == 2 and calls == [1]
    double(2)
    double(1)                                  # acerto: 1 vira o mais recente
    double(3)                                  # despeja o 2
    info = double.cache_info()
    assert (info.hits, info.misses, info.maxsize, info.currsize) == (2, 3, 2, 2)
    double(2)
    assert calls == [1, 2, 3, 2]
    assert double(1, k=3) == 6 and double(k=3, x=1) == 6
    double.cache_clear()
    assert double.cache_info().currsize == 0 and double.cache_info().hits == 0


def test_memoize_unbounded_and_unhashable(load_exercise):
    memoize = load_exercise("ex01_memoize").memoize

    @memoize(maxsize=None)
    def ident(x):
        return x

    for n in range(500):
        ident(n)
    assert ident.cache_info().currsize == 500
    with pytest.raises(TypeError):
        ident([1])


def test_compose_and_pipe(load_exercise):
    module = load_exercise("ex02_compose")
    compose, pipe = module.compose, module.pipe
    inc = lambda x: x + 1
    double = lambda x: x * 2
    assert compose(inc, double)(5) == 11 and compose(double, inc)(5) == 12
    assert compose()(7) == 7
    assert compose(str, lambda a, b: a + b)(1, 2) == "3"
    assert pipe(5, inc, double) == 12 and pipe(5) == 5


def test_curry(load_exercise):
    curry = load_exercise("ex02_compose").curry
    add3 = curry(lambda a, b, c: a + b + c)
    assert add3(1)(2)(3) == 6 and add3(1, 2)(3) == 6 and add3(1)(2, 3) == 6 and add3(1, 2, 3) == 6
    partial = add3(10)
    assert partial(1, 1) == 12 and partial(2)(2) == 14
    with_default = curry(lambda a, b=5: a + b)
    assert with_default(1) == 6


def test_describe_dispatch(load_exercise):
    describe = load_exercise("ex03_dispatch").describe
    assert hasattr(describe, "register")
    assert describe(True) == "yes" and describe(False) == "no"
    assert describe(3) == "int(3)" and describe(1) == "int(1)" and describe(0.26) == "float(0.3)"
    assert describe("abc") == "'abc'" and describe(None) == "nothing"
    assert describe([1, "a", (2.0,)]) == "[int(1), 'a', [float(2.0)]]"
    assert describe({"k": [True]}) == "{'k': [yes]}"
    assert describe({3, 1, 2}) == "[int(1), int(2), int(3)]"
    assert describe(b"x") == "<bytes>" and describe(object()) == "<object>"


def test_sort_by(load_exercise):
    sort_by = load_exercise("ex04_sorting").sort_by
    people = [{"name": "ana", "age": 30}, {"name": "bia", "age": 25},
              {"name": "caio", "age": 30}, {"name": "dani", "age": 25}]
    original = list(people)
    assert [p["name"] for p in sort_by(people, "-age", "name")] == ["ana", "caio", "bia", "dani"]
    assert [p["name"] for p in sort_by(people, "age", "-name")] == ["dani", "bia", "caio", "ana"]
    assert people == original
    assert sort_by([], "x") == []


def test_largest_number(load_exercise):
    largest = load_exercise("ex04_sorting").sort_numbers_largest
    assert largest([3, 30, 34, 5, 9]) == "9534330"
    assert largest([10, 2]) == "210" and largest([0, 0]) == "00" and largest([]) == ""


def test_reduce_tools(load_exercise):
    module = load_exercise("ex05_reduce_tools")
    a, b = {"x": 1, "y": 2}, {"y": 3}
    assert module.merge_dicts(a, b, {"z": 4}) == {"x": 1, "y": 3, "z": 4}
    assert a == {"x": 1, "y": 2} and module.merge_dicts() == {}
    data = {"a": [{"b": 5}]}
    assert module.deep_get(data, ["a", 0, "b"]) == 5
    assert module.deep_get(data, ["a", 1, "b"], "?") == "?" and module.deep_get(data, ["z"]) is None
    assert module.deep_get(data, ["a", "b"], "T") == "T"
    assert module.product([2, 3, 4]) == 24 and module.product([]) == 1
    groups = module.group_by(["ab", "cd", "e", "fgh", "ij"], len)
    assert groups == {2: ["ab", "cd", "ij"], 1: ["e"], 3: ["fgh"]} and list(groups) == [2, 1, 3]
