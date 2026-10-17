import asyncio
import time

import pytest


def run(coro):
    return asyncio.run(coro)


async def sleeper(value, delay):
    await asyncio.sleep(delay)
    return value


def test_gather_limited_order_and_limit(load_exercise):
    gather_limited = load_exercise("ex01_gather_limited").gather_limited
    state = {"now": 0, "peak": 0}

    async def job(i):
        state["now"] += 1
        state["peak"] = max(state["peak"], state["now"])
        await asyncio.sleep(0.01 * (5 - i % 5))
        state["now"] -= 1
        return i * 2

    result = run(gather_limited([lambda i=i: job(i) for i in range(20)], limit=4))
    assert result == [i * 2 for i in range(20)] and state["peak"] == 4


def test_gather_limited_errors_and_edges(load_exercise):
    gather_limited = load_exercise("ex01_gather_limited").gather_limited
    assert run(gather_limited([], 3)) == []
    with pytest.raises(ValueError):
        run(gather_limited([lambda: sleeper(1, 0)], 0))

    async def bad():
        raise KeyError("x")

    started = []

    async def tracked(i):
        started.append(i)
        await asyncio.sleep(0.01)
        return i

    with pytest.raises(ExceptionGroup) as info:
        run(gather_limited([lambda: tracked(0), bad] + [lambda i=i: tracked(i) for i in range(1, 30)], limit=2))
    assert isinstance(info.value.exceptions[0], KeyError) and len(started) < 30


def test_gather_limited_is_concurrent(load_exercise):
    gather_limited = load_exercise("ex01_gather_limited").gather_limited
    start = time.perf_counter()
    run(gather_limited([lambda: sleeper(1, 0.1) for _ in range(20)], limit=20))
    assert time.perf_counter() - start < 0.5


def test_retry_async_succeeds_and_backoff(load_exercise):
    retry_async = load_exercise("ex02_retry_async").retry_async
    calls, sleeps = [], []

    async def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError("não ainda")
        return "ok"

    async def fake_sleep(seconds):
        sleeps.append(seconds)

    assert run(retry_async(flaky, retries=3, delay=0.5, sleep=fake_sleep)) == "ok"
    assert len(calls) == 3 and sleeps == [0.5, 1.0]


def test_retry_async_exhausts_and_filters(load_exercise):
    retry_async = load_exercise("ex02_retry_async").retry_async
    calls = []

    async def always():
        calls.append(1)
        raise ConnectionError(f"n{len(calls)}")

    with pytest.raises(ConnectionError, match="n3"):
        run(retry_async(always, retries=2))
    calls.clear()

    async def wrong():
        calls.append(1)
        raise KeyError("k")

    with pytest.raises(KeyError):
        run(retry_async(wrong, retries=5, retry_on=(ConnectionError,)))
    assert len(calls) == 1
    with pytest.raises(ValueError):
        run(retry_async(wrong, retries=-1))


def test_retry_async_attempt_timeout(load_exercise):
    retry_async = load_exercise("ex02_retry_async").retry_async
    attempts = []

    async def slow_then_fast():
        attempts.append(1)
        await asyncio.sleep(1 if len(attempts) < 3 else 0)
        return "pronto"

    start = time.perf_counter()
    assert run(retry_async(slow_then_fast, retries=3, attempt_timeout=0.05)) == "pronto"
    assert len(attempts) == 3 and time.perf_counter() - start < 0.5

    async def never():
        await asyncio.sleep(5)

    with pytest.raises(TimeoutError):
        run(retry_async(never, retries=1, attempt_timeout=0.02))


def test_pipeline_order_and_parallelism(load_exercise):
    run_pipeline = load_exercise("ex03_pipeline").run_pipeline

    async def worker(x):
        await asyncio.sleep(0.01 * (3 - x % 3))
        return x * x

    assert run(run_pipeline(range(30), worker, workers=4, queue_size=2)) == [x * x for x in range(30)]
    assert run(run_pipeline([], worker)) == []
    start = time.perf_counter()

    async def wait_a_bit(x):
        await asyncio.sleep(0.1)
        return x

    run(run_pipeline(range(10), wait_a_bit, workers=10, queue_size=10))
    assert time.perf_counter() - start < 0.5


def test_pipeline_backpressure_and_errors(load_exercise):
    run_pipeline = load_exercise("ex03_pipeline").run_pipeline
    consumed = []

    def gen():
        for i in range(1000):
            consumed.append(i)
            yield i

    async def worker(x):
        await asyncio.sleep(0.05)
        if x == 10:
            raise RuntimeError("dez")
        return x

    async def main():
        task = asyncio.create_task(run_pipeline(gen(), worker, workers=2, queue_size=3))
        await asyncio.sleep(0.02)
        in_flight = len(consumed)
        await asyncio.gather(task, return_exceptions=True)
        return in_flight

    assert run(main()) <= 3 + 2 + 2                                              # fila + trabalhadores (+ folga)
    with pytest.raises(ExceptionGroup):
        run(run_pipeline(range(20), worker, workers=2, queue_size=2))
    for kwargs in ({"workers": 0}, {"queue_size": 0}):
        with pytest.raises(ValueError):
            run(run_pipeline([1], worker, **kwargs))


def test_first_of_wins_and_cleans_up(load_exercise):
    first_of = load_exercise("ex04_first_of").first_of
    state = {"cleaned": False}

    async def slow():
        try:
            await asyncio.sleep(5)
        finally:
            state["cleaned"] = True

    async def fails():
        raise OSError("falhou")

    start = time.perf_counter()
    assert run(first_of(slow, fails, lambda: sleeper("rapida", 0.05))) == "rapida"
    assert state["cleaned"] and time.perf_counter() - start < 1


def test_first_of_all_fail_and_empty(load_exercise):
    first_of = load_exercise("ex04_first_of").first_of

    def failing(n):
        async def run_():
            await asyncio.sleep(0.01 * n)
            raise ValueError(n)
        return run_

    with pytest.raises(ExceptionGroup) as info:
        run(first_of(failing(1), failing(2)))
    assert sorted(e.args[0] for e in info.value.exceptions) == [1, 2]
    with pytest.raises(ValueError):
        run(first_of())


def test_collect_with_timeout(load_exercise):
    collect = load_exercise("ex05_collect_with_timeout").collect_with_timeout
    state = {"cancelled": 0}

    async def late():
        try:
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            state["cancelled"] += 1
            raise

    results, late_ones = run(collect([lambda: sleeper("a", 0.01), late, lambda: sleeper("c", 0.02), late], timeout=0.3))
    assert results == {0: "a", 2: "c"} and late_ones == [1, 3] and state["cancelled"] == 2
    assert run(collect([], 1)) == ({}, [])
    results, late_ones = run(collect([lambda: sleeper(1, 0)], timeout=0))
    assert late_ones == [0] and results == {}


def test_collect_with_timeout_error(load_exercise):
    collect = load_exercise("ex05_collect_with_timeout").collect_with_timeout

    async def bad():
        await asyncio.sleep(0.01)
        raise KeyError("k")

    with pytest.raises(KeyError):
        run(collect([bad, lambda: sleeper(1, 5)], timeout=1))


async def numbers(prefix, count, delay):
    for i in range(count):
        await asyncio.sleep(delay)
        yield f"{prefix}{i}"


def test_merge_streams_interleaves(load_exercise):
    merge_streams = load_exercise("ex06_merge_streams").merge_streams

    async def main():
        return [item async for item in merge_streams(numbers("a", 3, 0.03), numbers("b", 3, 0.03))]

    items = run(main())
    assert sorted(items) == ["a0", "a1", "a2", "b0", "b1", "b2"]

    async def timed():
        start = time.perf_counter()
        out = [item async for item in merge_streams(*(numbers(str(k), 5, 0.02) for k in range(5)))]
        return out, time.perf_counter() - start

    out, elapsed = run(timed())
    assert len(out) == 25 and elapsed < 0.4                                          # concorrentes: ~0,1 s, não 0,5 s

    async def empty():
        return [item async for item in merge_streams()]

    assert run(empty()) == []


def test_merge_streams_error_and_early_stop(load_exercise):
    import contextlib
    merge_streams = load_exercise("ex06_merge_streams").merge_streams
    state = {"closed": 0}

    async def endless():
        try:
            i = 0
            while True:
                await asyncio.sleep(0.01)
                yield i
                i += 1
        finally:
            state["closed"] += 1

    async def broken():
        await asyncio.sleep(0.03)
        raise RuntimeError("fluxo quebrou")
        yield  # noqa

    async def with_error():
        async for _ in merge_streams(endless(), broken()):
            pass

    with pytest.raises((RuntimeError, ExceptionGroup)):
        run(with_error())
    assert state["closed"] >= 1

    async def early():
        async with contextlib.aclosing(merge_streams(endless(), endless())) as merged:
            async for item in merged:
                break
        await asyncio.sleep(0.05)
        return state["closed"]

    state["closed"] = 0
    assert run(early()) == 2
