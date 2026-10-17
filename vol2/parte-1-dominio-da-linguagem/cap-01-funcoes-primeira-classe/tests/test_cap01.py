import functools


def test_compose(load_exercise):
    m = load_exercise("ex01_compose")
    assert m.compose(str, abs)(-3) == "3"
    assert m.compose()(5) == 5
    assert m.compose(lambda x: x + 1, lambda x: x * 2)(5) == 11
    # a última função aceita vários argumentos
    assert m.compose(str, max)(1, 9, 4) == "9"
    assert m.compose(len, str.strip)("  ab ") == 2


def test_pipe(load_exercise):
    m = load_exercise("ex01_compose")
    assert m.pipe(" Hello ", str.strip, str.lower, len) == 5
    assert m.pipe(3) == 3
    assert m.pipe(2, lambda x: x + 1, lambda x: x * 10) == 30


def test_curry(load_exercise):
    curry = load_exercise("ex02_curry").curry
    add3 = curry(lambda a, b, c: a + b + c)
    assert add3(1)(2)(3) == 6
    assert add3(1, 2)(3) == 6
    assert add3(1, 2, 3) == 6
    step = add3(1)
    assert step(2)(3) == 6 and step(5)(5) == 11   # reutilizável

    def f(a, b=10):
        return a + b
    assert curry(f)(1) == 11                       # b tem padrão


def test_memoize(load_exercise):
    memoize = load_exercise("ex03_memo").memoize
    calls = []

    def slow(n):
        calls.append(n)
        return n * n

    fast = memoize(slow)
    assert [fast(4), fast(4), fast(5)] == [16, 16, 25]
    assert calls == [4, 5]
    assert (fast.hits, fast.misses) == (1, 2)
    assert fast.cache == {(4,): 16, (5,): 25}


def test_fib_calls(load_exercise):
    fn = load_exercise("ex03_memo").count_calls_fib
    assert fn(30) == (832040, 59)
    assert fn(1) == (1, 1)
    assert fn(0) == (0, 1)


def test_lru_cache_matches_manual(load_exercise):
    # comparação: lru_cache e memoize manual contam o mesmo
    memoize = load_exercise("ex03_memo").memoize

    def fib(n):
        return n if n < 2 else fast(n - 1) + fast(n - 2)

    fast = memoize(fib)

    @functools.lru_cache(maxsize=None)
    def lru(n):
        return n if n < 2 else lru(n - 1) + lru(n - 2)

    assert fast(20) == lru(20) == 6765
    info = lru.cache_info()
    assert (fast.hits, fast.misses) == (info.hits, info.misses)


def test_describe(load_exercise):
    d = load_exercise("ex04_dispatch").describe
    assert d(3) == "int:3"
    assert d(True) == "bool:True"
    assert d("abc") == "str:3"
    assert d([1, "ab"]) == "seq[int:1,str:2]"
    assert d((1, [True])) == "seq[int:1,seq[bool:True]]"
    assert d({"a": 1}) == "map:1"
    assert d(None) == "none"
    assert d(2.5) == "object:float"


ROWS = [
    {"name": "bia", "dept": "ops", "salary": 10},
    {"name": "ana", "dept": "dev", "salary": 20},
    {"name": "caio", "dept": "dev", "salary": 30},
    {"name": "abel", "dept": "ops", "salary": 10},
    {"name": "duda", "dept": "dev", "salary": 20},
]


def test_sort_staff(load_exercise):
    m = load_exercise("ex05_sort_multi")
    original = [dict(r) for r in ROWS]
    out = m.sort_staff(ROWS)
    assert [r["name"] for r in out] == [
        "caio", "ana", "duda", "abel", "bia"]
    assert ROWS == original                      # entrada intacta
    assert out is not ROWS


def test_top_per_dept(load_exercise):
    m = load_exercise("ex05_sort_multi")
    assert m.top_per_dept(ROWS) == {"dev": "caio", "ops": "abel"}


def test_signature_dict(load_exercise):
    sd = load_exercise("ex06_signature_dict").signature_dict

    def f(a: int, b: "list[int]" = None, /, *args, c, d: str = "x",
          **kw) -> str: ...

    out = sd(f)
    assert out["returns"] == "str"
    names = [p["name"] for p in out["params"]]
    assert names == ["a", "b", "args", "c", "d", "kw"]
    a, b, args, c, d, kw = out["params"]
    assert a == {"name": "a", "kind": "POSITIONAL_ONLY",
                 "required": True, "default": None, "annotation": "int"}
    assert b["required"] is False and b["annotation"] == "list[int]"
    assert args["kind"] == "VAR_POSITIONAL" and not args["required"]
    assert c["kind"] == "KEYWORD_ONLY" and c["required"]
    assert c["annotation"] is None
    assert d["default"] == "x" and d["annotation"] == "str"
    assert kw["kind"] == "VAR_KEYWORD" and not kw["required"]
    assert sd(max) is None
    assert sd(lambda: 1) == {"params": [], "returns": None}
