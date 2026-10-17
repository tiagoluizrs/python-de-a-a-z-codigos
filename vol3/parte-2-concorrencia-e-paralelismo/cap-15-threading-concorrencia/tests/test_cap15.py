import queue
import threading
import time

import pytest


def hammer(fn, threads=8, repeat=2000):
    ts = [threading.Thread(target=lambda: [fn() for _ in range(repeat)]) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()


def test_counter_is_exact_even_with_a_window(load_exercise):
    SafeCounter = load_exercise("ex01_counter").SafeCounter
    counter = SafeCounter(on_step=lambda: time.sleep(0))
    hammer(lambda: counter.add(), threads=8, repeat=500)
    assert counter.value == 4000
    assert SafeCounter(5).add(3) == 8 and SafeCounter(on_step=None).add() == 1


def test_counter_compare_and_set_and_update(load_exercise):
    SafeCounter = load_exercise("ex01_counter").SafeCounter
    counter = SafeCounter(10)
    assert counter.compare_and_set(10, 11) is True and counter.compare_and_set(10, 99) is False and counter.value == 11
    assert counter.update(lambda v: v * 2) == 22 and counter.value == 22
    winners = []
    shared = SafeCounter(0)

    def race():
        if shared.compare_and_set(0, 1):
            winners.append(1)

    ts = [threading.Thread(target=race) for _ in range(16)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert sum(winners) == 1                                                     # só UMA vence

    slow = SafeCounter(0)
    hammer(lambda: slow.update(lambda v: (time.sleep(0), v + 1)[1]), threads=4, repeat=200)
    assert slow.value == 800


def test_bounded_buffer_basic_and_timeouts(load_exercise):
    m = load_exercise("ex02_bounded_buffer")
    with pytest.raises(ValueError):
        m.BoundedBuffer(0)
    buf = m.BoundedBuffer(2)
    buf.put(1)
    buf.put(2)
    assert len(buf) == 2
    start = time.perf_counter()
    with pytest.raises(queue.Full):
        buf.put(3, timeout=0.1)
    assert 0.09 <= time.perf_counter() - start < 1
    assert buf.get() == 1 and buf.get() == 2
    with pytest.raises(queue.Empty):
        buf.get(timeout=0.05)


def test_bounded_buffer_producers_consumers(load_exercise):
    m = load_exercise("ex02_bounded_buffer")
    buf = m.BoundedBuffer(3)
    produced = list(range(200))
    consumed = []
    lock = threading.Lock()

    def producer(chunk):
        for item in chunk:
            buf.put(item)

    def consumer():
        while True:
            try:
                item = buf.get()
            except m.Closed:
                return
            with lock:
                consumed.append(item)

    producers = [threading.Thread(target=producer, args=(produced[i::2],)) for i in range(2)]
    consumers = [threading.Thread(target=consumer) for _ in range(3)]
    for t in producers + consumers:
        t.start()
    for t in producers:
        t.join(5)
    buf.close()
    for t in consumers:
        t.join(5)
    assert not any(t.is_alive() for t in producers + consumers) and sorted(consumed) == produced


def test_bounded_buffer_close_semantics(load_exercise):
    m = load_exercise("ex02_bounded_buffer")
    buf = m.BoundedBuffer(5)
    buf.put("a")
    buf.close()
    with pytest.raises(m.Closed):
        buf.put("b")
    assert buf.get() == "a"                                                        # entrega o que sobrou
    with pytest.raises(m.Closed):
        buf.get(timeout=1)
    empty = m.BoundedBuffer(1)
    got = []
    waiter = threading.Thread(target=lambda: got.append(pytest.raises(m.Closed).__class__) or _catch(empty, m))
    result = []

    def blocked_get():
        try:
            empty.get()
        except m.Closed:
            result.append("acordou")

    waiter = threading.Thread(target=blocked_get)
    waiter.start()
    time.sleep(0.1)
    empty.close()
    waiter.join(2)
    assert result == ["acordou"] and not waiter.is_alive()


def _catch(buf, m):
    try:
        buf.get()
    except m.Closed:
        pass


def test_transfer_basic(load_exercise):
    m = load_exercise("ex03_transfer")
    a, b = m.Account(1, 100), m.Account(2, 50)
    m.transfer(a, b, 30)
    assert (a.balance, b.balance) == (70, 80)
    with pytest.raises(ValueError):
        m.transfer(a, b, 500)
    assert (a.balance, b.balance) == (70, 80)
    with pytest.raises(ValueError):
        m.transfer(a, a, 1)
    with pytest.raises(ValueError):
        m.transfer(a, b, 0)
    a.deposit(5)
    assert a.balance == 75
    with pytest.raises(ValueError):
        a.withdraw(1000)


def test_transfer_opposite_directions_no_deadlock(load_exercise):
    m = load_exercise("ex03_transfer")
    a, b = m.Account(1, 10_000), m.Account(2, 10_000)

    def loop(source, target):
        for _ in range(2000):
            m.transfer(source, target, 1)

    t1, t2 = threading.Thread(target=loop, args=(a, b)), threading.Thread(target=loop, args=(b, a))
    t1.start()
    t2.start()
    t1.join(10)
    t2.join(10)
    assert not t1.is_alive() and not t2.is_alive(), "deadlock!"
    assert a.balance + b.balance == 20_000 and a.balance == 10_000


def test_worker_pool_runs_tasks(load_exercise):
    m = load_exercise("ex04_worker_pool")
    with m.WorkerPool(3) as pool:
        assert len(pool.threads) == 3 and all(t.name.startswith("pool-") for t in pool.threads)
        handles = [pool.submit(pow, 2, n) for n in range(10)]
        assert [h.result(timeout=5) for h in handles] == [2**n for n in range(10)]
        assert pool.submit(lambda x, y=1: x + y, 1, y=5).result(5) == 6
    assert not any(t.is_alive() for t in pool.threads)


def test_worker_pool_errors_timeouts_and_shutdown(load_exercise):
    m = load_exercise("ex04_worker_pool")
    pool = m.WorkerPool(2)
    bad = pool.submit(lambda: 1 / 0)
    with pytest.raises(ZeroDivisionError):
        bad.result(5)
    assert bad.done() and pool.submit(lambda: "ainda funciona").result(5) == "ainda funciona"
    slow = pool.submit(time.sleep, 0.3)
    with pytest.raises(TimeoutError):
        slow.result(timeout=0.05)
    assert slow.done() is False
    pool.shutdown(wait=True)
    assert slow.done()
    with pytest.raises(RuntimeError):
        pool.submit(print)
    pool.shutdown()                                                                  # idempotente
    with pytest.raises(ValueError):
        m.WorkerPool(0)


def test_worker_pool_parallel_io_and_order(load_exercise):
    m = load_exercise("ex04_worker_pool")
    start = time.perf_counter()
    with m.WorkerPool(8) as pool:
        handles = [pool.submit(time.sleep, 0.1) for _ in range(16)]
        for h in handles:
            h.result(5)
    assert time.perf_counter() - start < 0.8                                         # 16 × 0,1 s em 8 workers ≈ 0,2 s
    seen = []
    with m.WorkerPool(1) as pool:
        for i in range(20):
            pool.submit(seen.append, i)
    assert seen == list(range(20))                                                   # 1 worker: ordem de submissão


class FakeTime:
    def __init__(self):
        self.now = 0.0
        self.slept = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds


def test_rate_limiter_token_bucket(load_exercise):
    m = load_exercise("ex05_rate_limiter")
    t = FakeTime()
    limiter = m.RateLimiter(rate=2, burst=3, clock=t.clock, sleep=t.sleep)
    assert [limiter.try_acquire() for _ in range(4)] == [True, True, True, False]
    t.now += 0.5                                                                      # 1 ficha
    assert limiter.try_acquire() is True and limiter.try_acquire() is False
    t.now += 100                                                                      # enche, mas só até 3
    assert [limiter.try_acquire() for _ in range(4)] == [True, True, True, False]
    assert limiter.try_acquire(0) is True
    with pytest.raises(ValueError):
        limiter.try_acquire(4)
    for kwargs in ({"rate": 0, "burst": 1}, {"rate": 1, "burst": 0}, {"rate": -1, "burst": 1}):
        with pytest.raises(ValueError):
            m.RateLimiter(**kwargs)


def test_rate_limiter_acquire_waits(load_exercise):
    m = load_exercise("ex05_rate_limiter")
    t = FakeTime()
    limiter = m.RateLimiter(rate=4, burst=2, clock=t.clock, sleep=t.sleep)
    assert limiter.acquire() == 0.0 and limiter.acquire() == 0.0 and t.slept == []
    assert limiter.acquire() == pytest.approx(0.25) and t.slept == [pytest.approx(0.25)]
    assert limiter.acquire(2) == pytest.approx(0.5)


def test_rate_limiter_thread_safe_and_does_not_sleep_locked(load_exercise):
    m = load_exercise("ex05_rate_limiter")
    limiter = m.RateLimiter(rate=1000, burst=50)
    start = time.perf_counter()
    granted = []

    def worker():
        for _ in range(25):
            limiter.acquire()
            granted.append(1)

    ts = [threading.Thread(target=worker) for _ in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(10)
    elapsed = time.perf_counter() - start
    assert len(granted) == 200 and not any(t.is_alive() for t in ts)
    assert 0.1 < elapsed < 3                                                          # 200 fichas: 50 de início + 150 a 1000/s


def test_threaded_map_order_and_parallelism(load_exercise):
    threaded_map = load_exercise("ex06_parallel_map").threaded_map
    assert threaded_map(lambda x: x * x, range(20), workers=4) == [x * x for x in range(20)]
    start = time.perf_counter()
    assert threaded_map(lambda x: (time.sleep(0.1), x)[1], range(8), workers=8) == list(range(8))
    assert time.perf_counter() - start < 0.5
    assert threaded_map(len, []) == [] and threaded_map(len, ["ab"], workers=10) == [2]
    with pytest.raises(ValueError):
        threaded_map(len, ["a"], workers=0)


def test_threaded_map_errors(load_exercise):
    threaded_map = load_exercise("ex06_parallel_map").threaded_map

    def func(x):
        if x in (3, 7):
            raise ValueError(f"item {x}")
        return x

    with pytest.raises(ValueError, match="item 3"):
        threaded_map(func, range(10), workers=4)
    started = []

    def tracked(x):
        started.append(x)
        time.sleep(0.01)
        if x == 0:
            raise RuntimeError("falhou")
        return x

    with pytest.raises(RuntimeError):
        threaded_map(tracked, range(200), workers=2, stop_on_error=True)
    assert len(started) < 100                                                          # parou de começar itens novos
    started.clear()
    with pytest.raises(RuntimeError):
        threaded_map(tracked, range(30), workers=2, stop_on_error=False)
    assert len(started) == 30
