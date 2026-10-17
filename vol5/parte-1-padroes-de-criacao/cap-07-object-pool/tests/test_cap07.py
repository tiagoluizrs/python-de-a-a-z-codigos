import io
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class Res:
    count = 0

    def __init__(self):
        Res.count += 1
        self.id = Res.count
        self.closed = False
        self.dirty = False


@pytest.fixture(autouse=True)
def reset_counter():
    Res.count = 0


# ---------- ex01 ----------
def test_pool_lazy_creation_and_reuse(load_exercise):
    m = load_exercise("ex01_pool")
    pool = m.Pool(Res, 2)
    assert Res.count == 0 and pool.stats() == {"created": 0, "idle": 0, "in_use": 0, "discarded": 0}
    a = pool.acquire()
    pool.release(a)
    b = pool.acquire()
    assert b is a and Res.count == 1                                    # reaproveitou
    c = pool.acquire()
    assert c is not b and Res.count == 2
    assert pool.stats() == {"created": 2, "idle": 0, "in_use": 2, "discarded": 0}


def test_pool_fifo_and_lease(load_exercise):
    m = load_exercise("ex01_pool")
    pool = m.Pool(Res, 2)
    a, b = pool.acquire(), pool.acquire()
    pool.release(b)
    pool.release(a)
    assert pool.acquire() is b and pool.acquire() is a                  # mais antigo primeiro
    pool2 = m.Pool(Res, 1)
    with pool2.lease() as r:
        assert pool2.stats()["in_use"] == 1
    assert pool2.stats() == {"created": 1, "idle": 1, "in_use": 0, "discarded": 0}
    with pytest.raises(RuntimeError, match="boom"):
        with pool2.lease():
            raise RuntimeError("boom")
    assert pool2.stats()["idle"] == 1                                    # devolveu apesar da exceção


def test_pool_exhaustion_and_waiting(load_exercise):
    m = load_exercise("ex01_pool")
    pool = m.Pool(Res, 1)
    held = pool.acquire()
    t0 = time.monotonic()
    with pytest.raises(m.PoolExhausted, match="nenhum objeto livre em 0.1s"):
        pool.acquire(timeout=0.1)
    assert 0.08 <= time.monotonic() - t0 < 1.0 and issubclass(m.PoolExhausted, TimeoutError)
    got = []
    t = threading.Thread(target=lambda: got.append(pool.acquire(timeout=2)))
    t.start()
    time.sleep(0.05)
    pool.release(held)
    t.join()
    assert got == [held]


def test_pool_release_errors(load_exercise):
    m = load_exercise("ex01_pool")
    pool = m.Pool(Res, 2)
    a = pool.acquire()
    pool.release(a)
    with pytest.raises(ValueError, match="objeto não emprestado"):
        pool.release(a)
    with pytest.raises(ValueError, match="objeto não emprestado"):
        pool.release(Res())
    with pytest.raises(ValueError):
        m.Pool(Res, 0)


def test_pool_reset_validate_close(load_exercise):
    m = load_exercise("ex01_pool")
    closed = []

    def reset(obj):
        obj.dirty = False

    pool = m.Pool(Res, 2, reset=reset, validate=lambda o: not o.closed, close=lambda o: closed.append(o.id))
    a = pool.acquire()
    a.dirty = True
    pool.release(a)
    assert a.dirty is False
    a2 = pool.acquire()
    a2.closed = True                                                     # "morreu" enquanto emprestado
    pool.release(a2)
    b = pool.acquire()                                                   # validate recusa a2: descartado e criado outro
    assert b is not a2 and closed == [a2.id] and pool.stats() == {"created": 1, "idle": 0, "in_use": 1, "discarded": 1}


def test_pool_reset_failure_discards(load_exercise):
    m = load_exercise("ex01_pool")
    closed = []

    def bad_reset(obj):
        raise OSError("falhou")

    pool = m.Pool(Res, 1, reset=bad_reset, close=lambda o: closed.append(o.id))
    a = pool.acquire()
    with pytest.raises(OSError):
        pool.release(a)
    assert closed == [a.id] and pool.stats() == {"created": 0, "idle": 0, "in_use": 0, "discarded": 1}
    assert pool.acquire() is not a                                       # o espaço foi liberado para criar outro


def test_pool_close(load_exercise):
    m = load_exercise("ex01_pool")
    closed = []
    pool = m.Pool(Res, 3, close=lambda o: closed.append(o.id))
    a, b = pool.acquire(), pool.acquire()
    pool.release(a)
    pool.close()
    assert closed == [a.id]
    with pytest.raises(RuntimeError, match="pool fechado"):
        pool.acquire()
    pool.release(b)                                                      # estava emprestado: fecha na hora
    assert closed == [a.id, b.id]
    pool.close()
    assert closed == [a.id, b.id]


def test_pool_threads_never_exceed_size(load_exercise):
    m = load_exercise("ex01_pool")
    pool = m.Pool(Res, 3)
    state = {"now": 0, "peak": 0}
    lock = threading.Lock()

    def work():
        for _ in range(10):
            with pool.lease(timeout=5):
                with lock:
                    state["now"] += 1
                    state["peak"] = max(state["peak"], state["now"])
                time.sleep(0.002)
                with lock:
                    state["now"] -= 1

    threads = [threading.Thread(target=work) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert state["peak"] <= 3 and Res.count <= 3 and pool.stats()["in_use"] == 0


# ---------- ex02 ----------
def test_buffer_pool(load_exercise):
    m = load_exercise("ex02_buffer_pool")
    pool = m.BufferPool(8, 2)
    a, b = pool.acquire(), pool.acquire()
    assert isinstance(a, bytearray) and len(a) == 8 and a is not b and pool.free == 0
    with pytest.raises(BufferError, match="sem buffers livres"):
        pool.acquire()
    pool.release(a)
    assert pool.free == 1
    with pytest.raises(ValueError, match="buffer desconhecido"):
        pool.release(a)
    with pytest.raises(ValueError, match="buffer desconhecido"):
        pool.release(bytearray(8))
    assert pool.acquire() is a
    for bad in ((0, 1), (1, 0)):
        with pytest.raises(ValueError):
            m.BufferPool(*bad)


def test_copy_stream(load_exercise):
    m = load_exercise("ex02_buffer_pool")
    pool = m.BufferPool(7, 1)
    data = bytes(range(256)) * 3
    dst = io.BytesIO()
    assert m.copy_stream(io.BytesIO(data), dst, pool) == len(data)
    assert dst.getvalue() == data and pool.free == 1
    assert m.copy_stream(io.BytesIO(b""), io.BytesIO(), pool) == 0 and pool.free == 1


def test_copy_stream_returns_buffer_on_error(load_exercise):
    m = load_exercise("ex02_buffer_pool")
    pool = m.BufferPool(4, 1)

    class Broken:
        def write(self, data):
            raise OSError("disco cheio")

    with pytest.raises(OSError, match="disco cheio"):
        m.copy_stream(io.BytesIO(b"abcdefgh"), Broken(), pool)
    assert pool.free == 1


# ---------- ex03 ----------
def test_per_thread(load_exercise):
    m = load_exercise("ex03_thread_local")
    closed = []
    local = m.PerThread(Res, close=lambda r: closed.append(r.id))
    main = local.get()
    assert local.get() is main and local.count == 1
    seen = []

    def work():
        seen.append(local.get())
        seen.append(local.get())

    threads = [threading.Thread(target=work) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len({id(x) for x in seen}) == 3 and local.count == 4
    local.close_all()
    assert sorted(closed) == [1, 2, 3, 4] and local.count == 0
    again = local.get()
    assert again is not main and local.count == 1


def test_per_thread_close_errors(load_exercise):
    m = load_exercise("ex03_thread_local")
    closed = []

    def close(r):
        closed.append(r.id)
        if r.id == 1:
            raise OSError("fechar falhou")

    local = m.PerThread(Res, close=close)
    local.get()
    t = threading.Thread(target=local.get)
    t.start()
    t.join()
    with pytest.raises(OSError, match="fechar falhou"):
        local.close_all()
    assert sorted(closed) == [1, 2] and local.count == 0


# ---------- ex04 ----------
def test_lease_monitor(load_exercise):
    m = load_exercise("ex04_leak_monitor")
    now = [100.0]
    mon = m.LeaseMonitor(lambda: now[0])
    t1 = mon.acquired("req-a")
    now[0] += 10
    t2 = mon.acquired("req-b")
    now[0] += 5
    t3 = mon.acquired("req-c")
    assert (t1, t2, t3) == (1, 2, 3) and mon.active == 3
    now[0] += 5
    assert mon.overdue(10) == [("req-a", 20.0)]                         # b tem idade 10: não é MAIOR que 10
    assert mon.overdue(4) == [("req-a", 20.0), ("req-b", 10.0), ("req-c", 5.0)]
    mon.released(t1)
    assert mon.active == 2 and mon.overdue(7) == [("req-b", 10.0)]
    with pytest.raises(ValueError, match="token desconhecido"):
        mon.released(t1)
    with pytest.raises(ValueError, match="token desconhecido"):
        mon.released(99)
    with pytest.raises(ValueError):
        mon.overdue(-1)


def test_lease_monitor_report_and_ties(load_exercise):
    m = load_exercise("ex04_leak_monitor")
    now = [0.0]
    mon = m.LeaseMonitor(lambda: now[0])
    mon.acquired("zeta")
    mon.acquired("alfa")
    now[0] = 12.34
    mon.acquired("novo")
    now[0] = 20.0
    assert mon.overdue(1)[:2] == [("alfa", 20.0), ("zeta", 20.0)]
    assert mon.report(1) == "alfa: 20.0s\nzeta: 20.0s\nnovo: 7.7s"
    assert mon.report(100) == "sem vazamentos"


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["object_pool_classico", "object_pool_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
