import platform
import sys
import time


def test_describe_runtime(load_exercise):
    result = load_exercise("ex01_runtime").describe_runtime()
    assert result["implementation"] == platform.python_implementation()
    assert result["version"] == platform.python_version()


def test_count_instructions(load_exercise):
    count = load_exercise("ex02_bytecode").count_instructions

    def add(a, b):
        return a + b

    assert count(add) >= 4  # RESUME, LOAD, LOAD, BINARY_OP, RETURN
    assert count(lambda: None) < count(add)


def test_best_time_returns_minimum(load_exercise):
    best_time = load_exercise("ex03_benchmark").best_time
    durations = iter([0.06, 0.01, 0.06])  # a segunda execução é a mais rápida
    result = best_time(lambda: time.sleep(next(durations)), repeat=3)
    assert 0.009 <= result < 0.04


def test_python_is_recent():
    assert sys.version_info >= (3, 15)
