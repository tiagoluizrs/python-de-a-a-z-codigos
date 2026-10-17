import concurrent.futures as cf
import threading
import time

import pytest

import tasks


def test_fetch_all_isolates_errors_and_keeps_order(load_exercise):
    m = load_exercise("ex01_fetch_all")

    def func(x):
        time.sleep(0.05 * (5 - x))
        if x % 2:
            raise ConnectionError(f"x={x}")
        return x * 10

    outcomes = m.fetch_all(func, range(5), workers=5)
    assert [o.index for o in outcomes] == [0, 1, 2, 3, 4]
    assert [o.ok for o in outcomes] == [True, False, True, False, True]
    assert [o.value for o in outcomes if o.ok] == [0, 20, 40]
    assert isinstance(outcomes[1].error, ConnectionError) and outcomes[1].value is None


def test_fetch_all_edges_and_parallelism(load_exercise):
    m = load_exercise("ex01_fetch_all")
    assert m.fetch_all(len, []) == []
    with pytest.raises(ValueError):
        m.fetch_all(len, ["a"], workers=0)
    start = time.perf_counter()
    m.fetch_all(lambda _: time.sleep(0.1), range(8), workers=8)
    assert time.perf_counter() - start < 0.5


def test_first_success_returns_winner_and_cancels(load_exercise):
    first_success = load_exercise("ex02_first_success").first_success
    started = []

    def slow(tag, seconds):
        def run():
            started.append(tag)
            time.sleep(seconds)
            return tag
        return run

    def failing():
        raise OSError("falhou")

    assert first_success([failing, slow("rapida", 0.05), slow("lenta", 0.5)]) == "rapida"
    started.clear()
    funcs = [slow(f"t{i}", 0.2) for i in range(6)]
    start = time.perf_counter()
    assert first_success(funcs, workers=2) in {"t0", "t1"}
    assert time.perf_counter() - start < 0.6
    time.sleep(0.5)
    assert len(started) < 6                                                      # os pendentes foram cancelados


def test_first_success_all_fail_and_empty(load_exercise):
    first_success = load_exercise("ex02_first_success").first_success

    def fail_with(i):
        def run():
            raise ValueError(i)
        return run

    with pytest.raises(RuntimeError) as info:
        first_success([fail_with(1), fail_with(2)])
    assert info.value.args[0] == "todos falharam" and sorted(e.args[0] for e in info.value.args[1]) == [1, 2]
    with pytest.raises(ValueError):
        first_success([])


def test_map_with_progress(load_exercise):
    map_with_progress = load_exercise("ex03_progress_map").map_with_progress
    calls = []
    with cf.ThreadPoolExecutor(4) as pool:
        result = map_with_progress(pool, lambda x: (time.sleep(0.02 * (5 - x)), x * x)[1], range(5), lambda d, n: calls.append((d, n)))
    assert result == [0, 1, 4, 9, 16]
    assert calls == [(i, 5) for i in range(1, 6)]
    with cf.ThreadPoolExecutor(2) as pool:
        assert map_with_progress(pool, len, []) == []


def test_map_with_progress_error_cancels_pending(load_exercise):
    map_with_progress = load_exercise("ex03_progress_map").map_with_progress
    started = []

    def func(x):
        started.append(x)
        time.sleep(0.02)
        if x == 0:
            raise RuntimeError("boom")
        return x

    with cf.ThreadPoolExecutor(1) as pool:
        with pytest.raises(RuntimeError, match="boom"):
            map_with_progress(pool, func, range(50))
    assert len(started) < 50


def test_retry_succeeds_after_failures(load_exercise):
    submit_with_retry = load_exercise("ex04_retry").submit_with_retry
    calls, sleeps = [], []

    def flaky(x):
        calls.append(x)
        if len(calls) < 3:
            raise ConnectionError("ainda não")
        return x * 2

    with cf.ThreadPoolExecutor(1) as pool:
        assert submit_with_retry(pool, flaky, 21, retries=3, delay=0.5, sleep=sleeps.append) == 42
    assert len(calls) == 3 and sleeps == [0.5, 1.0]


def test_retry_exhausts_and_respects_retry_on(load_exercise):
    submit_with_retry = load_exercise("ex04_retry").submit_with_retry
    calls = []

    def always():
        calls.append(1)
        raise ConnectionError(f"tentativa {len(calls)}")

    with cf.ThreadPoolExecutor(1) as pool:
        with pytest.raises(ConnectionError, match="tentativa 3"):
            submit_with_retry(pool, always, retries=2)
        assert len(calls) == 3
        calls.clear()

        def wrong():
            calls.append(1)
            raise KeyError("x")

        with pytest.raises(KeyError):
            submit_with_retry(pool, wrong, retries=5, retry_on=(ConnectionError,))
        assert len(calls) == 1
        with pytest.raises(ValueError):
            submit_with_retry(pool, wrong, retries=-1)


def test_bounded_map_limits_in_flight(load_exercise):
    bounded_map = load_exercise("ex05_bounded_submit").bounded_map
    lock = threading.Lock()
    state = {"now": 0, "peak": 0}

    def func(x):
        with lock:
            state["now"] += 1
            state["peak"] = max(state["peak"], state["now"])
        time.sleep(0.01)
        with lock:
            state["now"] -= 1
        return x * 2

    with cf.ThreadPoolExecutor(16) as pool:
        assert bounded_map(pool, func, range(60), max_pending=3) == [x * 2 for x in range(60)]
    assert state["peak"] <= 3 and state["peak"] >= 2


def test_bounded_map_lazy_iterable_and_errors(load_exercise):
    bounded_map = load_exercise("ex05_bounded_submit").bounded_map
    consumed = []

    def generator():
        for i in range(100):
            consumed.append(i)
            yield i

    with cf.ThreadPoolExecutor(2) as pool:
        def func(x):
            time.sleep(0.01)
            if x == 5:
                raise ValueError("cinco")
            return x

        with pytest.raises(ValueError, match="cinco"):
            bounded_map(pool, func, generator(), max_pending=4)
        assert len(consumed) < 100                                                # não consumiu tudo
        assert bounded_map(pool, str, [], max_pending=2) == []
        with pytest.raises(ValueError):
            bounded_map(pool, str, [1], max_pending=0)


def test_make_executor(load_exercise):
    make_executor = load_exercise("ex06_make_executor").make_executor
    assert isinstance(make_executor("thread"), cf.ThreadPoolExecutor)
    assert isinstance(make_executor("process"), cf.ProcessPoolExecutor)
    assert isinstance(make_executor("interpreter"), cf.InterpreterPoolExecutor)
    for args in (("fork",), ("thread", 0)):
        with pytest.raises(ValueError):
            make_executor(*args)


@pytest.mark.parametrize("kind", ["thread", "process", "interpreter"])
def test_batched_map_all_executors(load_exercise, kind):
    m = load_exercise("ex06_make_executor")
    with m.make_executor(kind, 2) as pool:
        assert m.batched_map(pool, tasks.square, range(11), batch_size=4) == [x * x for x in range(11)]
        assert m.batched_map(pool, tasks.square, [], batch_size=3) == []
        with pytest.raises(ValueError):
            m.batched_map(pool, tasks.square, [1], batch_size=0)
