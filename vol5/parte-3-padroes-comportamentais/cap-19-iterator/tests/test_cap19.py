import io
import itertools
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def test_countdown(load_exercise):
    m = load_exercise("ex01_iterators")
    c = m.Countdown(3)
    assert list(c) == [3, 2, 1, 0] and list(c) == [3, 2, 1, 0] and len(c) == 4 and sum(c) == 6
    assert 2 in c and 0 in c and 4 not in c and -1 not in c and "a" not in c and 1.5 not in c and True not in m.Countdown(0)
    it = iter(c)
    assert iter(it) is it and type(it).__name__ == "CountdownIterator" and it is not iter(c)
    assert [next(it) for _ in range(4)] == [3, 2, 1, 0]
    for _ in range(2):
        with pytest.raises(StopIteration):
            next(it)
    with pytest.raises(ValueError, match="start negativo"):
        m.Countdown(-1)
    assert list(m.Countdown(0)) == [0]


def test_fibonacci(load_exercise):
    m = load_exercise("ex01_iterators")
    f = m.Fibonacci()
    assert iter(f) is f and list(itertools.islice(f, 8)) == [0, 1, 1, 2, 3, 5, 8, 13]
    assert list(itertools.islice(f, 2)) == [21, 34]                                      # continua de onde parou (uma passada)
    assert list(m.Fibonacci(5)) == [0, 1, 1, 2, 3] and list(m.Fibonacci(0)) == [] and list(m.Fibonacci(1)) == [0]
    limited = m.Fibonacci(2)
    assert list(limited) == [0, 1] and list(limited) == []
    with pytest.raises(ValueError, match="limit negativo"):
        m.Fibonacci(-1)


def test_peekable(load_exercise):
    m = load_exercise("ex01_iterators")
    p = m.PeekableIterator("abc")
    assert iter(p) is p and p.peek() == "a" and p.peek() == "a" and p.has_next() and next(p) == "a"
    assert p.peek() == "b" and next(p) == "b" and next(p) == "c"
    assert not p.has_next() and p.peek("fim") == "fim" and p.peek(None) is None
    with pytest.raises(StopIteration):
        p.peek()
    with pytest.raises(StopIteration):
        next(p)
    p.push_back("x")
    p.push_back("y")
    assert p.has_next() and p.peek() == "y" and list(p) == ["y", "x"]
    q = m.PeekableIterator([1, 2, 3])
    q.push_back(0)
    assert list(q) == [0, 1, 2, 3]
    gen = m.PeekableIterator(x for x in range(2))
    assert gen.peek() == 0 and list(gen) == [0, 1]
    empty = m.PeekableIterator([])
    assert not empty.has_next() and list(empty) == []


# ---------- ex02 ----------
class Counting:
    """Uma fonte que conta quantos itens foram consumidos."""

    def __init__(self, items):
        self.items, self.consumed = items, 0

    def __iter__(self):
        for item in self.items:
            self.consumed += 1
            yield item


def test_chunks_and_window(load_exercise):
    m = load_exercise("ex02_generators")
    assert list(m.chunks(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]] and list(m.chunks([], 3)) == [] and list(m.chunks("abcd", 2)) == [["a", "b"], ["c", "d"]]
    with pytest.raises(ValueError, match="size deve ser >= 1"):
        m.chunks([1], 0)                                                                # já na chamada
    src = Counting(range(100))
    gen = m.chunks(src, 4)
    assert next(gen) == [0, 1, 2, 3] and src.consumed == 4
    assert list(m.sliding_window("abcd", 2)) == [("a", "b"), ("b", "c"), ("c", "d")] and list(m.sliding_window("ab", 3)) == [] and list(m.sliding_window([1], 1)) == [(1,)]
    with pytest.raises(ValueError, match="n deve ser >= 1"):
        m.sliding_window([1], 0)
    src2 = Counting(range(100))
    next(m.sliding_window(src2, 3))
    assert src2.consumed == 3


def test_unique_and_merge(load_exercise):
    m = load_exercise("ex02_generators")
    assert list(m.unique_everseen([3, 1, 3, 2, 1])) == [3, 1, 2] and list(m.unique_everseen("aAbB", key=str.lower)) == ["a", "b"]
    src = Counting([1, 1, 2, 3, 4, 5])
    gen = m.unique_everseen(src)
    assert next(gen) == 1 and src.consumed == 1 and next(gen) == 2 and src.consumed == 3
    assert list(m.merge_sorted([1, 4, 7], [2, 5], [3, 6, 9])) == [1, 2, 3, 4, 5, 6, 7, 9] and list(m.merge_sorted()) == [] and list(m.merge_sorted([], [1])) == [1]
    tagged = list(m.merge_sorted([(1, "a"), (2, "a")], [(1, "b"), (2, "b")]))
    assert tagged == [(1, "a"), (1, "b"), (2, "a"), (2, "b")]                           # empate: o primeiro argumento sai antes
    a, b = Counting([1, 3, 5, 7]), Counting([2, 4, 6, 8])
    merged = m.merge_sorted(a, b)
    assert next(merged) == 1 and a.consumed + b.consumed <= 3                             # só o primeiro de cada um (e no máximo mais um)
    assert list(m.merge_sorted(iter([1, 3]), iter([2]))) == [1, 2, 3]


def test_flatten_and_read_blocks(load_exercise):
    m = load_exercise("ex02_generators")
    assert list(m.flatten([1, [2, (3, 4)], 5])) == [1, 2, 3, 4, 5] and list(m.flatten([["ab", b"cd"], "ef"])) == ["ab", b"cd", "ef"] and list(m.flatten([])) == []
    nested = [1, [2, [3, [4]]]]
    assert list(m.flatten(nested, levels=0)) == [1, [2, [3, [4]]]] and list(m.flatten(nested, levels=1)) == [1, 2, [3, [4]]] and list(m.flatten(nested, levels=2)) == [1, 2, 3, [4]]
    deep = ["fundo"]
    for _ in range(5000):
        deep = [deep]
    assert list(m.flatten(deep)) == ["fundo"]
    assert list(m.read_blocks(io.BytesIO(b"abcdefg"), 3)) == [b"abc", b"def", b"g"] and list(m.read_blocks(io.StringIO("abcde"), 2)) == ["ab", "cd", "e"] and list(m.read_blocks(io.BytesIO(b""), 4)) == []
    with pytest.raises(ValueError, match="size deve ser >= 1"):
        m.read_blocks(io.BytesIO(b"x"), 0)


# ---------- ex03 ----------
LOG = """2026-10-15 12:00:01 INFO web: iniciado
2026-10-15 12:00:02 ERROR db: disco cheio

2026-10-15 12:00:03 ERROR db: sem espaço
2026-10-15 12:00:04 CRITICAL web: caiu
2026-10-15 12:00:05 WARN cache: lento
2026-10-15 12:00:06 ERROR api: timeout
""".splitlines()


def test_parse_and_filters(load_exercise):
    m = load_exercise("ex03_pipeline")
    records = list(m.parse_lines(LOG))
    assert len(records) == 6 and records[1] == {"time": "2026-10-15 12:00:02", "level": "ERROR", "source": "db", "message": "disco cheio"}
    assert [r["message"] for r in m.only_levels(records, "CRITICAL", "WARN")] == ["caiu", "lento"] and list(m.only_levels(records)) == []
    assert [r["source"] for r in m.only_source(records, "d")] == ["db", "db"]
    assert list(m.take(records, 2)) == records[:2] and list(m.take(records, 0)) == [] and list(m.take(records, 99)) == records


def test_parse_errors_and_laziness(load_exercise):
    m = load_exercise("ex03_pipeline")
    gen = m.parse_lines(["2026-10-15 12:00:01 INFO web: ok", "lixo", "2026-10-15 12:00:02 INFO web: ok"])
    assert next(gen)["message"] == "ok"
    with pytest.raises(ValueError, match="linha 2 inválida: 'lixo'"):
        next(gen)
    gen2 = m.parse_lines(["", "  ", "2026-10-15 12:00:01 INFO web ok"])
    with pytest.raises(ValueError, match="linha 3 inválida"):
        list(gen2)
    src = Counting(LOG)
    first = next(m.parse_lines(src))
    assert first["level"] == "INFO" and src.consumed == 1
    with pytest.raises(ValueError, match="n negativo"):
        m.take([], -1)
    src2 = Counting(range(100))
    assert list(m.take(src2, 3)) == [0, 1, 2] and src2.consumed == 3                     # não puxa o quarto
    src3 = Counting(range(100))
    assert list(m.take(src3, 0)) == [] and src3.consumed == 0


def test_count_by_and_composition(load_exercise):
    m = load_exercise("ex03_pipeline")
    records = list(m.parse_lines(LOG))
    assert m.count_by(records, "level") == {"ERROR": 3, "CRITICAL": 1, "INFO": 1, "WARN": 1}
    assert list(m.count_by(records, "source")) == ["db", "web", "api", "cache"]            # db 2, web 2 (empate: alfabético), api 1, cache 1
    assert m.errors_per_source(LOG) == {"db": 2, "api": 1, "web": 1}
    src = Counting(LOG)
    assert m.errors_per_source(src, limit=2) == {"db": 2} and src.consumed == 4            # parou ao achar o 2º erro (a 4ª linha)
    assert m.errors_per_source([]) == {}


# ---------- ex04 ----------
def sample(m):
    return m.BST([8, 3, 10, 1, 6, 14, 4, 7, 13])


def test_bst_traversals(load_exercise):
    m = load_exercise("ex04_tree_iter")
    t = sample(m)
    assert list(t) == [1, 3, 4, 6, 7, 8, 10, 13, 14] and len(t) == 9 and 7 in t and 5 not in t
    assert list(t.preorder()) == [8, 3, 1, 6, 4, 7, 10, 14, 13] and list(t.postorder()) == [1, 4, 7, 6, 3, 13, 14, 10, 8]
    assert list(t.levelorder()) == [8, 3, 10, 1, 6, 14, 4, 7, 13] and t.height() == 4 and t.min() == 1 and t.max() == 14
    assert t.add(5) is True and t.add(5) is False and len(t) == 10 and 5 in t
    empty = m.BST()
    assert list(empty) == [] and list(empty.preorder()) == [] and list(empty.postorder()) == [] and list(empty.levelorder()) == [] and empty.height() == 0 and len(empty) == 0 and 1 not in empty
    for fn in (empty.min, empty.max):
        with pytest.raises(ValueError, match="árvore vazia"):
            fn()
    assert m.BST([1]).height() == 1 and list(m.BST([5, 5, 5])) == [5]


def test_bst_range_and_pruning(load_exercise):
    m = load_exercise("ex04_tree_iter")
    t = sample(m)
    assert list(t.range(4, 10)) == [4, 6, 7, 8, 10] and list(t.range(100, 200)) == [] and list(t.range(0, 1)) == [1] and list(t.range(7, 7)) == [7] and list(t.range(9, 5)) == []
    big = m.BST(range(0, 2000, 2))
    assert list(big.range(100, 110)) == [100, 102, 104, 106, 108, 110]
    assert list(itertools.islice(big.range(0, 10_000), 3)) == [0, 2, 4]


def test_bst_degenerate_deep_tree_is_iterative(load_exercise):
    m = load_exercise("ex04_tree_iter")
    t = m.BST(range(3000))                                                              # lista ligada à direita: 3.000 níveis
    assert len(t) == 3000 and t.height() == 3000 and t.max() == 2999 and 2999 in t
    assert sum(1 for _ in t) == 3000 and next(iter(t.preorder())) == 0 and list(t.postorder())[-1] == 0 and list(t.levelorder())[:3] == [0, 1, 2]
    left = m.BST(range(3000, 0, -1))
    assert left.height() == 3000 and left.min() == 1 and list(left)[:2] == [1, 2] and list(left.postorder())[:2] == [1, 2]


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["iterator_classico", "iterator_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
