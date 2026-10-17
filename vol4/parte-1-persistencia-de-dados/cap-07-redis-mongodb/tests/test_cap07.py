import decimal
import threading
import time

import pytest


# ---------- ex01 ----------
def test_rate_limiter_basic_and_window(load_exercise, rds):
    limiter = load_exercise("ex01_rate_limiter").FixedWindowLimiter(rds, limit=3, window_ms=500)
    assert [limiter.allow("ana")[:2] for _ in range(3)] == [(True, 2), (True, 1), (True, 0)]
    allowed, remaining, retry = limiter.allow("ana")
    assert allowed is False and remaining == 0 and 0 < retry <= 500
    assert limiter.allow("bia") == (True, 2, 0)                                         # chaves independentes
    time.sleep(0.6)
    assert limiter.allow("ana")[:2] == (True, 2)                                        # a janela virou
    assert rds.pttl("rl:ana") > 0                                                       # a expiração foi definida
    for kwargs in ({"limit": 0}, {"window_ms": 0}):
        with pytest.raises(ValueError):
            load_exercise("ex01_rate_limiter").FixedWindowLimiter(rds, **{"limit": 1, "window_ms": 100, **kwargs})


def test_rate_limiter_is_atomic_under_concurrency(load_exercise, rds):
    import redis

    m = load_exercise("ex01_rate_limiter")
    results = []
    lock = threading.Lock()

    def client():
        c = redis.Redis.from_url(rds.connection_pool.connection_kwargs and f"redis://{rds.connection_pool.connection_kwargs['host']}:{rds.connection_pool.connection_kwargs['port']}/15", decode_responses=True)
        limiter = m.FixedWindowLimiter(c, limit=25, window_ms=5000, prefix="conc")
        for _ in range(10):
            ok = limiter.allow("x")[0]
            with lock:
                results.append(ok)

    threads = [threading.Thread(target=client) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(results) == 80 and results.count(True) == 25                              # exatamente o limite
    assert rds.pttl("conc:x") > 0


# ---------- ex02 ----------
def test_cache_aside_hit_miss_and_ttl(load_exercise, rds):
    calls = []

    def loader(key):
        calls.append(key)
        return {"key": key, "n": len(calls)}

    cache = load_exercise("ex02_cache").CacheAside(rds, loader, ttl_seconds=1)
    assert cache.get("a") == {"key": "a", "n": 1} and cache.get("a") == {"key": "a", "n": 1}
    assert (cache.hits, cache.misses, calls) == (1, 1, ["a"])
    assert 0 < rds.ttl("cache:a") <= 1
    assert cache.invalidate("a") is True and cache.invalidate("a") is False
    assert cache.get("a")["n"] == 2
    time.sleep(1.1)
    assert cache.get("a")["n"] == 3                                                       # expirou


def test_cache_aside_prevents_stampede(load_exercise, rds):
    calls = []

    def slow_loader(key):
        calls.append(key)
        time.sleep(0.3)
        return {"v": key}

    cache = load_exercise("ex02_cache").CacheAside(rds, slow_loader, ttl_seconds=30)
    results = []
    start = time.perf_counter()
    threads = [threading.Thread(target=lambda: results.append(cache.get("hot"))) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(calls) == 1 and results == [{"v": "hot"}] * 10                             # UMA carga para 10 pedidos
    assert time.perf_counter() - start < 1.5
    assert cache.misses == 1 and cache.hits == 9
    assert rds.get("cache:lock:hot") is None                                              # a trava foi solta


def test_cache_aside_releases_lock_when_loader_fails(load_exercise, rds):
    def broken(key):
        raise RuntimeError("fonte fora do ar")

    cache = load_exercise("ex02_cache").CacheAside(rds, broken)
    with pytest.raises(RuntimeError):
        cache.get("x")
    assert rds.get("cache:lock:x") is None and rds.get("cache:x") is None


# ---------- ex03 ----------
def test_leaderboard(load_exercise, rds):
    lb = load_exercise("ex03_leaderboard").Leaderboard(rds, "jogo")
    assert lb.add("ana", 100) == 100.0 and lb.add("bia", 340) == 340.0 and lb.add("ana", 50) == 150.0
    for member, points in (("caio", 80), ("dora", 200), ("eli", 10)):
        lb.add(member, points)
    assert lb.top(3) == [("bia", 340.0), ("dora", 200.0), ("ana", 150.0)]
    assert lb.rank("bia") == 1 and lb.rank("caio") == 4 and lb.rank("zzz") is None
    assert lb.score("ana") == 150.0 and lb.score("zzz") is None and lb.size() == 5
    assert lb.around("ana", 1) == [(2, "dora", 200.0), (3, "ana", 150.0), (4, "caio", 80.0)]
    assert lb.around("bia", 2) == [(1, "bia", 340.0), (2, "dora", 200.0), (3, "ana", 150.0)]
    assert lb.remove("eli") is True and lb.remove("eli") is False and lb.size() == 4
    with pytest.raises(KeyError):
        lb.around("zzz", 1)
    with pytest.raises(ValueError):
        lb.top(0)


# ---------- ex04 ----------
def test_reliable_queue_flow(load_exercise, rds):
    q = load_exercise("ex04_reliable_queue").ReliableQueue(rds, "jobs")
    assert [q.put(f"j{i}") for i in range(3)] == [1, 2, 3]
    assert q.get("w1") == "j0" and q.pending("w1") == ["j0"] and q.size() == 2
    assert q.ack("w1", "j0") is True and q.ack("w1", "j0") is False and q.pending("w1") == []
    assert q.get("w1") == "j1" and q.get("w2") == "j2"
    assert q.get("w1", timeout=1) is None and q.size() == 0


def test_reliable_queue_recovers_after_crash(load_exercise, rds):
    q = load_exercise("ex04_reliable_queue").ReliableQueue(rds, "jobs")
    for item in ("a", "b", "c", "d"):
        q.put(item)
    assert q.get("w1") == "a" and q.get("w1") == "b"
    q.get("w2")                                                                             # o w2 pegou "c" e continua vivo
    assert q.recover("w1") == 2 and q.pending("w1") == []                                   # o w1 "morreu": volta tudo
    assert q.size() == 3 and q.pending("w2") == ["c"]
    assert [q.get("w3") for _ in range(3)] == ["a", "b", "d"]                              # a ordem original foi preservada
    assert q.recover("nunca-existiu") == 0


# ---------- ex05 ----------
@pytest.fixture
def store(load_exercise, mongo):
    s = load_exercise("ex05_product_store").ProductStore(mongo["product"])
    s.ensure_indexes()
    s.ensure_indexes()                                                                       # idempotente
    return s


def test_product_store_add_get(store):
    doc = store.add("A1", "caneta", decimal.Decimal("9.90"), 5)
    assert doc["sku"] == "A1" and doc["price"] == decimal.Decimal("9.90") and "_id" in doc
    got = store.get("A1")
    assert got["price"] == decimal.Decimal("9.90") and isinstance(got["price"], decimal.Decimal) and got["stock"] == 5
    assert store.get("ZZ") is None
    with pytest.raises(ValueError):
        store.add("A1", "outra", decimal.Decimal("1"))
    with pytest.raises(ValueError):
        store.add("B2", "x", decimal.Decimal("1"), stock=-1)
    assert store.get("B2") is None


def test_product_store_remove_stock_is_atomic(store):
    store.add("S", "x", decimal.Decimal("1"), 50)
    assert store.remove_stock("S", 20) == 30
    with pytest.raises(ValueError):
        store.remove_stock("S", 31)
    with pytest.raises(KeyError):
        store.remove_stock("NOPE", 1)
    with pytest.raises(ValueError):
        store.remove_stock("S", 0)
    assert store.get("S")["stock"] == 30
    sold = []
    lock = threading.Lock()

    def worker():
        for _ in range(10):
            try:
                store.remove_stock("S", 1)
                with lock:
                    sold.append(1)
            except ValueError:
                pass

    threads = [threading.Thread(target=worker) for _ in range(8)]                         # 80 tentativas, 30 em estoque
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(sold) == 30 and store.get("S")["stock"] == 0


def test_product_store_keyset_pagination(store):
    for i in range(7):
        store.add(f"P{i}", f"n{i}", decimal.Decimal(i))
    docs, cursor = store.page(limit=3)
    seen = [d["sku"] for d in docs]
    assert seen == ["P0", "P1", "P2"] and cursor == docs[-1]["_id"]
    while cursor:
        docs, cursor = store.page(after_id=cursor, limit=3)
        seen += [d["sku"] for d in docs]
    assert seen == [f"P{i}" for i in range(7)]
    docs, cursor = store.page(limit=7)
    assert len(docs) == 7 and cursor is None
    assert store.page(after_id=docs[-1]["_id"]) == ([], None)


# ---------- ex06 ----------
@pytest.fixture
def sales(mongo):
    collection = mongo["sale"]
    collection.insert_many([
        {"customer": "ana", "category": "livros", "amount": 40}, {"customer": "ana", "category": "jogos", "amount": 100},
        {"customer": "bia", "category": "livros", "amount": 60}, {"customer": "bia", "category": "livros", "amount": 10},
        {"customer": "caio", "category": "jogos", "amount": 100}, {"customer": "dora", "category": "casa", "amount": 5}])
    return collection


def test_sales_by_category(load_exercise, sales):
    m = load_exercise("ex06_analytics")
    assert m.sales_by_category(sales) == [("jogos", 200, 2), ("livros", 110, 3), ("casa", 5, 1)]
    assert m.sales_by_category(sales, min_amount=50) == [("jogos", 200, 2), ("livros", 60, 1)]
    assert m.sales_by_category(sales, min_amount=1000) == []


def test_top_customers(load_exercise, sales):
    m = load_exercise("ex06_analytics")
    assert m.top_customers(sales, 2) == [("ana", 140), ("caio", 100)]
    assert m.top_customers(sales, 10)[-1] == ("dora", 5) and len(m.top_customers(sales, 10)) == 4
    with pytest.raises(ValueError):
        m.top_customers(sales, 0)


def test_ttl_index_and_plans(load_exercise, sales):
    m = load_exercise("ex06_analytics")
    assert m.ensure_ttl_index(sales, "expires", 3600) is True
    assert m.ensure_ttl_index(sales, "expires", 3600) is False
    assert any(i.get("expireAfterSeconds") == 3600 for i in sales.list_indexes())
    with pytest.raises(ValueError):
        m.ensure_ttl_index(sales, "x", -1)
    assert m.winning_stages(sales, {"customer": "ana"}) == ["COLLSCAN"]
    sales.create_index("customer")
    stages = m.winning_stages(sales, {"customer": "ana"})
    assert stages[-1] == "IXSCAN" and "COLLSCAN" not in stages


# ---------- testes sem servidor: fakeredis ----------
def test_fakeredis_runs_the_same_logic_without_a_server(load_exercise):
    import fakeredis

    q = load_exercise("ex04_reliable_queue").ReliableQueue(fakeredis.FakeRedis(decode_responses=True), "x")
    q.put("a")
    assert q.get("w", timeout=1) == "a" and q.pending("w") == ["a"] and q.ack("w", "a") is True
    lb = load_exercise("ex03_leaderboard").Leaderboard(fakeredis.FakeRedis(decode_responses=True), "x")
    lb.add("ana", 3)
    lb.add("bia", 5)
    assert lb.top(2) == [("bia", 5.0), ("ana", 3.0)]
