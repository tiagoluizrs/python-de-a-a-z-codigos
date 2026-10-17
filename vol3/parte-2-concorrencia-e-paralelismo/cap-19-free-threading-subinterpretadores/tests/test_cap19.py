import sys
import sysconfig

import pytest

import tasks


def test_detect_runtime_matches_this_interpreter(load_exercise):
    info = load_exercise("ex01_detect_runtime").detect_runtime()
    assert info["free_threaded_build"] == bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
    assert info["gil_enabled"] == sys._is_gil_enabled()
    assert info["parallel_threads"] == (info["free_threaded_build"] and not info["gil_enabled"])
    assert info["version"] == (sys.version_info.major, sys.version_info.minor)


def test_describe_runtime(load_exercise):
    describe = load_exercise("ex01_detect_runtime").describe_runtime
    base = {"version": (3, 15), "parallel_threads": False}
    assert describe({**base, "free_threaded_build": False, "gil_enabled": True}) == "Python 3.15 (build com GIL)"
    assert describe({**base, "free_threaded_build": True, "gil_enabled": False}) == "Python 3.15 (build sem GIL, GIL desligado)"
    assert describe({**base, "free_threaded_build": True, "gil_enabled": True}) == "Python 3.15 (build sem GIL, GIL religado)"


def test_speedup_table(load_exercise):
    m = load_exercise("ex02_speedup_table")
    table = m.speedup_table(10.0, {4: 2.5, 1: 10.0, 2: 5.0, 8: 2.0})
    assert [row[0] for row in table] == [1, 2, 4, 8]
    assert table[2] == (4, pytest.approx(4.0), pytest.approx(1.0))
    assert table[3][1] == pytest.approx(5.0) and table[3][2] == pytest.approx(0.625)
    for args in ((0, {1: 1}), (1, {0: 1}), (1, {1: 0})):
        with pytest.raises(ValueError):
            m.speedup_table(*args)


def test_best_workers(load_exercise):
    m = load_exercise("ex02_speedup_table")
    table = m.speedup_table(1.24, {1: 1.60, 2: 0.76, 4: 0.44, 8: 0.34, 16: 0.42})
    assert m.best_workers(table, min_efficiency=0.4) == 8
    assert m.best_workers(table, min_efficiency=0.75) == 2
    assert m.best_workers(table, min_efficiency=0.95) == 1
    assert m.best_workers([], 0.5) == 1


def test_sharded_counter_exact_under_threads(load_exercise):
    import threading
    counter = load_exercise("ex03_sharded_counter").ShardedCounter(shards=4)

    def work():
        for _ in range(5_000):
            counter.add()

    threads = [threading.Thread(target=work) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert counter.total() == 40_000
    assert counter.reset() == 40_000 and counter.total() == 0
    counter.add(5)
    assert counter.total() == 5


def test_sharded_counter_validation_and_sharding(load_exercise):
    import threading
    m = load_exercise("ex03_sharded_counter")
    with pytest.raises(ValueError):
        m.ShardedCounter(0)
    counter = m.ShardedCounter(shards=8)
    thread = threading.Thread(target=lambda: counter.add(7))
    thread.start()
    thread.join()
    counter.add(3)
    assert counter.total() == 10


def test_split(load_exercise):
    split = load_exercise("ex04_parallel_sum").split
    assert split(range(7), 3) == [[0, 1, 2], [3, 4], [5, 6]]
    assert split([], 2) == [[], []]
    with pytest.raises(ValueError):
        split([1], 0)


@pytest.mark.parametrize("kind", ["thread", "process", "interpreter"])
def test_sum_squares_parallel(load_exercise, kind):
    parallel = load_exercise("ex04_parallel_sum").sum_squares_parallel
    data = list(range(1, 101))
    assert parallel(data, workers=3, kind=kind) == sum(x * x for x in data)


def test_sum_squares_parallel_edges(load_exercise):
    parallel = load_exercise("ex04_parallel_sum").sum_squares_parallel
    assert parallel([], 2, "process") == 0
    with pytest.raises(ValueError):
        parallel([1], 2, "fork")


def test_sum_in_interpreter(load_exercise):
    from concurrent import interpreters
    sum_in = load_exercise("ex05_sum_in_interpreter").sum_in_interpreter
    before = len(interpreters.list_all())
    assert sum_in([1, 2, 3, 4]) == 10 and sum_in([]) == 0 and sum_in(range(1000)) == 499_500
    assert len(interpreters.list_all()) == before                          # fechou todos


def test_choose_model(load_exercise):
    choose = load_exercise("ex06_choose_model").choose_model
    assert choose(cpu_bound=False) == "threads"
    assert choose(cpu_bound=False, many_connections=True) == "asyncio"
    assert choose(cpu_bound=True, free_threaded=True, shared_data=True) == "free-threaded threads"
    assert choose(cpu_bound=True) == "interpreters"
    assert choose(cpu_bound=True, uses_pure_python=False) == "processes"
    assert choose(cpu_bound=True, shared_data=True) == "interpreters"
    assert choose(cpu_bound=True, shared_data=True, uses_pure_python=False) == "processes"
    assert choose(cpu_bound=False, free_threaded=True) == "threads"


def test_tasks_module_sanity():
    assert tasks.sum_squares([1, 2, 3]) == 14 and tasks.cpu_sum(4) == 14
