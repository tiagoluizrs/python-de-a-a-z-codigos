import random
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

UTC = timezone.utc


# ---------- ex01 ----------
def test_delay_ceiling_and_jitter(load_exercise):
    m = load_exercise("ex01_backoff")
    p = m.RetryPolicy(base=0.5, factor=2.0, cap=3.0, jitter="none")
    assert [m.delay_ceiling(p, k) for k in range(1, 6)] == [0.5, 1.0, 2.0, 3.0, 3.0]
    assert [m.delay(p, k, random.Random(1)) for k in (1, 2, 3)] == [0.5, 1.0, 2.0]
    rng = random.Random(7)
    full = m.RetryPolicy(base=1.0, cap=10.0, jitter="full")
    samples = [m.delay(full, 3, rng) for _ in range(2000)]
    assert 0 <= min(samples) < 0.2 and 3.7 < max(samples) <= 4.0 and 1.8 < sum(samples) / len(samples) < 2.2
    equal = m.RetryPolicy(base=1.0, cap=10.0, jitter="equal")
    samples = [m.delay(equal, 3, rng) for _ in range(2000)]
    assert 2.0 <= min(samples) and max(samples) <= 4.0
    with pytest.raises(ValueError):
        m.delay(m.RetryPolicy(jitter="x"), 1, rng)


def test_retry_call(load_exercise):
    m = load_exercise("ex01_backoff")
    sleeps, attempts = [], []

    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError("falhou")
        return "ok"

    policy = m.RetryPolicy(max_attempts=4, base=1.0, jitter="none")
    assert m.retry_call(flaky, policy, sleeps.append, random.Random(0)) == "ok" and sleeps == [1.0, 2.0] and len(attempts) == 3


def test_retry_exhausted_and_non_retryable(load_exercise):
    m = load_exercise("ex01_backoff")
    sleeps = []

    def always():
        raise TimeoutError("lento")

    policy = m.RetryPolicy(max_attempts=3, base=0.5, jitter="none")
    with pytest.raises(m.RetriesExhausted) as info:
        m.retry_call(always, policy, sleeps.append, random.Random(0))
    assert info.value.attempts == 3 and isinstance(info.value.last_error, TimeoutError) and sleeps == [0.5, 1.0]
    calls = []

    def bug():
        calls.append(1)
        raise KeyError("bug")

    with pytest.raises(KeyError):
        m.retry_call(bug, policy, sleeps.append, random.Random(0))
    assert len(calls) == 1 and sleeps == [0.5, 1.0]
    assert m.retry_call(lambda: 42, policy, sleeps.append, random.Random(0)) == 42
    assert m.total_wait_ceiling(m.RetryPolicy(max_attempts=5, base=1.0, cap=3.0)) == 1 + 2 + 3 + 3 and m.total_wait_ceiling(m.RetryPolicy(max_attempts=1)) == 0


# ---------- ex02 ----------
def test_queue_fifo_ack_and_visibility(load_exercise):
    m = load_exercise("ex02_queue")
    clock = m.FakeClock(100.0)
    q = m.ReliableQueue(clock, visibility=10.0)
    ids = [q.put(f"p{i}") for i in range(3)]
    assert ids == ["m1", "m2", "m3"] and q.sizes() == {"ready": 3, "inflight": 0, "delayed": 0, "dead": 0}
    assert q.get() == ("m1", "p0") and q.sizes()["inflight"] == 1
    q.ack("m1")
    with pytest.raises(KeyError):
        q.ack("m1")
    assert q.get() == ("m2", "p1")                              # m2 fica em processamento
    assert q.reap() == 0
    clock.advance(10.0)
    assert q.reap() == 1 and q.attempts("m2") == 1 and q.sizes() == {"ready": 2, "inflight": 0, "delayed": 0, "dead": 0}
    assert q.get() == ("m2", "p1")                              # a reentrega: a mais antiga primeiro (ordem do put)
    assert q.get() == ("m3", "p2") and q.get() is None


def test_queue_delay_nack_and_dead(load_exercise):
    m = load_exercise("ex02_queue")
    clock = m.FakeClock(0.0)
    q = m.ReliableQueue(clock, max_attempts=3, retry_delay=lambda attempts: 2.0 * attempts)
    q.put("later", delay=5.0)
    q.put("now")
    assert q.get() == ("m2", "now") and q.get() is None and q.sizes()["delayed"] == 1
    assert q.nack("m2") == 2.0 and q.sizes() == {"ready": 0, "inflight": 0, "delayed": 2, "dead": 0}
    clock.advance(2.0)
    assert q.get() == ("m2", "now")                             # m1 (adiada) ainda não: só às 5,0; m2 volta às 2,0
    assert q.nack("m2") == 4.0 and q.attempts("m2") == 2
    clock.advance(4.0)                                           # agora = 6: as duas estão disponíveis; m1 é a mais antiga
    assert q.get() == ("m1", "later") and q.get() == ("m2", "now")
    assert q.nack("m2") is None and q.dead == ["m2"] and q.sizes()["dead"] == 1
    with pytest.raises(KeyError):
        q.nack("m2")


def test_queue_reap_exhausts_attempts(load_exercise):
    m = load_exercise("ex02_queue")
    clock = m.FakeClock()
    q = m.ReliableQueue(clock, visibility=1.0, max_attempts=2)
    q.put("x")
    q.get()
    clock.advance(1.0)
    assert q.reap() == 1 and q.get() == ("m1", "x")
    clock.advance(1.0)
    assert q.reap() == 1 and q.dead == ["m1"] and q.get() is None


# ---------- ex03 ----------
def test_idempotent_basic_and_failure(load_exercise):
    m = load_exercise("ex03_idempotency")
    clock = m.FakeClock() if hasattr(m, "FakeClock") else (lambda: 0.0)
    ex = m.IdempotentExecutor(lambda: 0.0)
    effects = []
    assert ex.run("a", lambda: effects.append("a") or "ra") == "ra" and ex.run("a", lambda: effects.append("a2") or "x") == "ra" and effects == ["a"]
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("falhou")
        return "ok"

    with pytest.raises(RuntimeError):
        ex.run("b", flaky)
    assert ex.run("b", flaky) == "ok" and len(calls) == 2 and ex.run("b", flaky) == "ok" and len(calls) == 2
    assert ex.stats == {"executed": 2, "replayed": 2, "failed": 1}


def test_idempotent_ttl(load_exercise):
    m = load_exercise("ex03_idempotency")
    now = {"t": 0.0}
    ex = m.IdempotentExecutor(lambda: now["t"], ttl=10.0)
    count = []
    ex.run("k", lambda: count.append(1) or len(count))
    now["t"] = 9.9
    assert ex.run("k", lambda: count.append(1) or len(count)) == 1
    now["t"] = 10.0
    assert ex.run("k", lambda: count.append(1) or len(count)) == 2 and len(count) == 2


def test_idempotent_concurrent_same_key_runs_once(load_exercise):
    m = load_exercise("ex03_idempotency")
    ex = m.IdempotentExecutor(lambda: 0.0)
    effects, results = [], []

    def slow_effect():
        time.sleep(0.1)
        effects.append(1)
        return "pago"

    threads = [threading.Thread(target=lambda: results.append(ex.run("order-7", slow_effect))) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert effects == [1] and results == ["pago"] * 8 and ex.stats == {"executed": 1, "replayed": 7, "failed": 0}


def test_idempotent_different_keys_do_not_block(load_exercise):
    m = load_exercise("ex03_idempotency")
    ex = m.IdempotentExecutor(lambda: 0.0)
    start = time.perf_counter()
    threads = [threading.Thread(target=lambda i=i: ex.run(f"k{i}", lambda: time.sleep(0.15))) for i in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert time.perf_counter() - start < 0.5
    assert m.make_key("pay", order=7, coupon=None, amount=10) == "pay|amount=10|order=7" and m.make_key("noop") == "noop"


# ---------- ex04 ----------
def test_outbox_atomic_place_order(load_exercise):
    m = load_exercise("ex04_outbox")
    db = m.make_db()
    m.place_order(db, 1, 100)
    assert m.pending(db) == 1
    with pytest.raises(sqlite3.IntegrityError):
        m.place_order(db, 1, 200)
    with pytest.raises(ValueError):
        m.place_order(db, 2, -5)
    assert db.execute("select count(*) from orders").fetchone()[0] == 1 and m.pending(db) == 1          # nada ficou pela metade


def test_outbox_relay_order_and_failure(load_exercise):
    m = load_exercise("ex04_outbox")
    db = m.make_db()
    for i in range(1, 6):
        m.place_order(db, i, 10)
    sent = []

    def publish(topic, body):
        if body == "3" and not sent.count(("order_created", "3")) and not getattr(publish, "tried", False):
            publish.tried = True
            raise ConnectionError("fora do ar")
        sent.append((topic, body))

    result = m.relay(db, publish)
    assert result == {"sent": 2, "failed": 1, "pending": 3} and [b for _, b in sent] == ["1", "2"]               # parou ali, preservando a ordem
    result = m.relay(db, publish)
    assert result == {"sent": 3, "failed": 0, "pending": 0} and [b for _, b in sent] == ["1", "2", "3", "4", "5"]
    assert m.relay(db, publish) == {"sent": 0, "failed": 0, "pending": 0}


def test_outbox_batch_and_drain(load_exercise):
    m = load_exercise("ex04_outbox")
    db = m.make_db()
    for i in range(250):
        m.place_order(db, i, 1)
    out = []
    assert m.relay(db, lambda t, b: out.append(b), batch=100)["sent"] == 100
    rng = random.Random(3)

    def flaky(topic, body):
        if rng.random() < 0.3:
            raise ConnectionError("x")
        out.append(body)

    rounds = m.drain(db, flaky, max_rounds=1000)
    assert m.pending(db) == 0 and rounds > 1 and len(out) == 250 and out == [str(i) for i in range(250)]
    assert m.drain(db, flaky) == 0


# ---------- ex05 ----------
NY = ZoneInfo("America/New_York")


def test_next_every_no_drift(load_exercise):
    m = load_exercise("ex05_scheduler")
    start = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    five = timedelta(minutes=5)
    assert m.next_every(datetime(2026, 1, 1, 0, 3, tzinfo=UTC), start, five) == datetime(2026, 1, 1, 0, 5, tzinfo=UTC)
    assert m.next_every(datetime(2026, 1, 1, 0, 5, tzinfo=UTC), start, five) == datetime(2026, 1, 1, 0, 10, tzinfo=UTC)
    assert m.next_every(datetime(2025, 12, 31, tzinfo=UTC), start, five) == start
    assert m.next_every(datetime(2026, 1, 1, 0, 7, 30, tzinfo=NY), start, five) == datetime(2026, 1, 1, 5, 10, tzinfo=UTC)
    with pytest.raises(ValueError):
        m.next_every(start, start, timedelta(0))


def test_next_daily_normal_and_dst_gap(load_exercise):
    m = load_exercise("ex05_scheduler")
    assert m.next_daily(datetime(2026, 6, 1, 12, 0, tzinfo=NY), 9, 0, NY) == datetime(2026, 6, 2, 13, 0, tzinfo=UTC)
    assert m.next_daily(datetime(2026, 6, 1, 8, 0, tzinfo=NY), 9, 0, NY) == datetime(2026, 6, 1, 13, 0, tzinfo=UTC)
    assert m.next_daily(datetime(2026, 6, 1, 9, 0, tzinfo=NY), 9, 0, NY) == datetime(2026, 6, 2, 13, 0, tzinfo=UTC)
    assert m.next_daily(datetime(2026, 1, 15, 12, 0, tzinfo=NY), 9, 0, NY) == datetime(2026, 1, 16, 14, 0, tzinfo=UTC)         # inverno: UTC-5
    gap = m.next_daily(datetime(2026, 3, 7, 12, 0, tzinfo=NY), 2, 30, NY)                  # 02:30 de 8/3 não existe
    assert gap == datetime(2026, 3, 8, 7, 0, tzinfo=UTC) and gap.astimezone(NY).strftime("%H:%M") == "03:00"
    after_gap = m.next_daily(gap, 2, 30, NY)
    assert after_gap == datetime(2026, 3, 9, 6, 30, tzinfo=UTC)                           # no dia seguinte já é 02:30 EDT normal


def test_next_daily_dst_overlap(load_exercise):
    m = load_exercise("ex05_scheduler")
    first = m.next_daily(datetime(2026, 10, 31, 12, 0, tzinfo=NY), 1, 30, NY)
    assert first == datetime(2026, 11, 1, 5, 30, tzinfo=UTC)                                # primeira ocorrência (EDT)
    second = m.next_daily(first, 1, 30, NY)
    assert second == datetime(2026, 11, 2, 6, 30, tzinfo=UTC)                               # NÃO roda de novo às 06:30 UTC (EST)


def test_missed_runs(load_exercise):
    m = load_exercise("ex05_scheduler")
    start = datetime(2026, 1, 1, tzinfo=UTC)
    period = timedelta(hours=1)
    last = datetime(2026, 1, 1, 3, 0, tzinfo=UTC)
    now = datetime(2026, 1, 1, 8, 20, tzinfo=UTC)
    hours = [datetime(2026, 1, 1, h, 0, tzinfo=UTC) for h in (4, 5, 6, 7, 8)]
    assert m.missed_runs(last, now, start, period, "all") == hours
    assert m.missed_runs(last, now, start, period, "all", limit=2) == hours[:2]
    assert m.missed_runs(last, now, start, period, "latest") == hours[-1:] and m.missed_runs(last, now, start, period, "none") == []
    assert m.missed_runs(last, last + timedelta(minutes=30), start, period, "latest") == []
    assert m.missed_runs(last, datetime(2026, 1, 1, 8, 0, tzinfo=UTC), start, period, "all")[-1] == hours[-1]            # now inclusive
    with pytest.raises(ValueError):
        m.missed_runs(last, now, start, period, "talvez")


# ---------- ex06 ----------
def test_worker_pool_ok_and_order(load_exercise):
    m = load_exercise("ex06_worker_pool")
    report = m.run_workers(list(range(50)), lambda x: x * x, concurrency=4, queue_size=5)
    assert report["ok"] == [x * x for x in range(50)] and report["failed"] == [] and set(report["attempts"].values()) == {1} and len(report["attempts"]) == 50
    assert m.run_workers([], lambda x: x) == {"ok": [], "failed": [], "attempts": {}}


def test_worker_pool_retries_and_failures(load_exercise):
    m = load_exercise("ex06_worker_pool")
    seen = {}
    lock = threading.Lock()

    def handler(item):
        with lock:
            seen[item] = seen.get(item, 0) + 1
            n = seen[item]
        if item % 5 == 0 and n < 3:
            raise ConnectionError(f"{item} falhou {n}")
        if item % 7 == 0 and item % 5 != 0:
            raise ValueError("sempre falha")
        return item

    report = m.run_workers(list(range(20)), handler, concurrency=3, max_attempts=3, queue_size=4)
    assert report["ok"] == [i for i in range(20) if not (i % 7 == 0 and i % 5 != 0)]
    assert [item for item, _ in report["failed"]] == [7, 14] and all(isinstance(e, ValueError) for _, e in report["failed"])
    assert report["attempts"][5] == 3 and report["attempts"][7] == 3 and report["attempts"][1] == 1


def test_worker_pool_is_concurrent_and_clean(load_exercise):
    m = load_exercise("ex06_worker_pool")
    before = threading.active_count()
    start = time.perf_counter()
    report = m.run_workers(list(range(16)), lambda x: time.sleep(0.1) or x, concurrency=8, queue_size=2)
    assert time.perf_counter() - start < 0.6 and len(report["ok"]) == 16
    time.sleep(0.05)
    assert threading.active_count() == before                                  # nenhuma thread ficou pendurada
    for bad in ({"concurrency": 0}, {"max_attempts": 0}):
        with pytest.raises(ValueError):
            m.run_workers([1], lambda x: x, **bad)


def test_worker_pool_backpressure(load_exercise):
    m = load_exercise("ex06_worker_pool")
    active, peak = [0], [0]
    lock = threading.Lock()

    def slow(item):
        with lock:
            active[0] += 1
            peak[0] = max(peak[0], active[0])
        time.sleep(0.02)
        with lock:
            active[0] -= 1
        return item

    assert len(m.run_workers(list(range(40)), slow, concurrency=3, queue_size=1)["ok"]) == 40 and peak[0] <= 3
