import inspect
import io
import tracemalloc
from itertools import islice

import pytest


def test_fibonacci(load_exercise):
    mod = load_exercise("ex01_fibonacci")
    assert list(mod.FibIterator(10)) == [0, 1, 1, 2, 3, 5, 8]
    assert list(mod.fib_gen(10)) == [0, 1, 1, 2, 3, 5, 8]
    assert list(mod.fib_gen(0)) == [0]
    assert list(islice(mod.FibIterator(), 8)) == [0, 1, 1, 2, 3, 5, 8, 13]
    assert list(islice(mod.fib_gen(), 8)) == [0, 1, 1, 2, 3, 5, 8, 13]
    it = mod.FibIterator(5)
    assert iter(it) is it
    assert list(it) == [0, 1, 1, 2, 3, 5]
    assert list(it) == []          # esgotado
    assert inspect.isgeneratorfunction(mod.fib_gen)
    with pytest.raises(ValueError):
        mod.FibIterator(-1)


def test_read_in_chunks(load_exercise):
    mod = load_exercise("ex02_read_in_chunks")
    assert list(mod.read_in_chunks(io.BytesIO(b"abcde"), 2)) == [
        b"ab", b"cd", b"e"]
    assert list(mod.read_in_chunks(io.StringIO("xyz"), 10)) == ["xyz"]
    assert list(mod.read_in_chunks(io.BytesIO(b""), 3)) == []
    with pytest.raises(ValueError):
        list(mod.read_in_chunks(io.BytesIO(b"a"), 0))
    assert mod.count_bytes(io.BytesIO(b"x" * 10_000), 777) == 10_000
    assert inspect.isgeneratorfunction(mod.read_in_chunks)


def test_flatten(load_exercise):
    mod = load_exercise("ex03_flatten")
    assert list(mod.flatten([1, [2, (3, "ab")], 4])) == [1, 2, 3, "ab", 4]
    assert list(mod.flatten([])) == []
    assert list(mod.flatten([[], [[]]])) == []
    assert list(mod.flatten([b"xy", [{5}]])) == [b"xy", 5]
    assert list(mod.flatten(iter([1, iter([2, 3])]))) == [1, 2, 3]
    assert mod.depth_of(5) == 0
    assert mod.depth_of([]) == 1
    assert mod.depth_of([1]) == 1
    assert mod.depth_of([[1], [2, [3]]]) == 3
    assert mod.depth_of("abc") == 0


def test_take_windowed(load_exercise):
    mod = load_exercise("ex04_windows")
    it = iter(range(10))
    assert mod.take(2, it) == [0, 1]
    assert next(it) == 2
    assert mod.take(5, "ab") == ["a", "b"]
    assert mod.take(0, "ab") == []
    assert list(mod.windowed("abcd", 3)) == [
        ("a", "b", "c"), ("b", "c", "d")]
    assert list(mod.windowed("ab", 3)) == []
    assert list(mod.windowed(iter([1, 2, 3]), 1)) == [(1,), (2,), (3,)]
    with pytest.raises(ValueError):
        list(mod.windowed("abc", 0))
    assert list(mod.moving_average([1, 2, 3, 4], 2)) == [1.5, 2.5, 3.5]
    assert inspect.isgeneratorfunction(mod.windowed)


def test_log_pipeline(load_exercise):
    mod = load_exercise("ex05_log_pipeline")
    lines = ["ERROR db 10", "", "INFO web 5", "bad line", "ERROR db 30",
             "ERROR web x", "WARN web 7"]
    assert list(mod.parse(lines)) == [
        ("ERROR", "db", 10), ("INFO", "web", 5),
        ("ERROR", "db", 30), ("WARN", "web", 7)]
    result = mod.total_by_service(
        mod.only_levels(mod.parse(lines), {"ERROR", "WARN"}))
    assert result == {"db": (2, 40), "web": (1, 7)}
    assert inspect.isgeneratorfunction(mod.parse)
    assert inspect.isgeneratorfunction(mod.only_levels)


def test_log_pipeline_constant_memory(load_exercise):
    mod = load_exercise("ex05_log_pipeline")

    def source(n):
        for i in range(n):
            yield f"{'ERROR' if i % 3 == 0 else 'INFO'} svc{i % 5} {i}"

    tracemalloc.start()
    result = mod.total_by_service(
        mod.only_levels(mod.parse(source(300_000)), {"ERROR"}))
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    assert sum(count for count, _ in result.values()) == 100_000
    assert peak < 1_000_000, f"pico de memória alto: {peak} bytes"


def test_averager(load_exercise):
    mod = load_exercise("ex06_averager")
    log = []
    avg = mod.make_averager(log)
    assert inspect.getgeneratorstate(avg) == "GEN_SUSPENDED"
    assert avg.send(10) == 10.0
    assert avg.send(20) == 15.0
    assert avg.send(None) == 15.0
    assert avg.send(60) == 30.0
    avg.close()
    assert log == [3]
    fresh = mod.make_averager()
    assert fresh.send(None) is None
    fresh.close()
