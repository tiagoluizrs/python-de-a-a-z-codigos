import threading
import time

import psycopg
import pytest
from psycopg.rows import dict_row


# ---------- ex01 (sem servidor) ----------
def test_connect_with_retry_succeeds_after_failures(load_exercise):
    connect_with_retry = load_exercise("ex01_connect_retry").connect_with_retry
    calls, sleeps = [], []

    def flaky():
        calls.append(1)
        if len(calls) < 4:
            raise psycopg.OperationalError("o banco ainda está subindo")
        return "conexão"

    assert connect_with_retry(flaky, attempts=5, delay=0.1, max_delay=0.25, sleep=sleeps.append) == "conexão"
    assert len(calls) == 4 and sleeps == [0.1, 0.2, 0.25]


def test_connect_with_retry_exhausts_and_filters(load_exercise):
    connect_with_retry = load_exercise("ex01_connect_retry").connect_with_retry
    calls = []

    def down():
        calls.append(1)
        raise psycopg.OperationalError(f"falha {len(calls)}")

    with pytest.raises(psycopg.OperationalError, match="falha 3"):
        connect_with_retry(down, attempts=3, sleep=lambda s: None)
    assert len(calls) == 3

    def wrong():
        calls.append(1)
        raise ValueError("outro erro")

    calls.clear()
    with pytest.raises(ValueError):
        connect_with_retry(wrong, attempts=5, sleep=lambda s: None)
    assert len(calls) == 1
    with pytest.raises(ValueError):
        connect_with_retry(down, attempts=0)


# ---------- ex02 ----------
@pytest.fixture
def users(load_exercise, pg):
    m = load_exercise("ex02_user_repository")
    conn = pg.connect(autocommit=False)
    repo = m.UserRepository(conn)
    repo.create_schema()
    yield repo
    conn.close()


def test_user_repository_crud(users):
    ana = users.add("Ana@Exemplo.com", "Ana")
    assert ana["id"] == 1 and ana["name"] == "Ana" and ana["created_at"].tzinfo is not None
    assert users.get_by_email("ana@exemplo.COM")["id"] == 1 and users.get_by_email("nao@existe") is None
    assert users.rename(1, "Ana Maria") is True and users.rename(99, "x") is False
    assert users.get_by_email("ana@exemplo.com")["name"] == "Ana Maria"


def test_user_repository_duplicate_keeps_connection_usable(users):
    users.add("a@x.com", "A")
    with pytest.raises(ValueError):
        users.add("A@X.COM", "outro")
    assert users.add("b@x.com", "B")["id"] >= 2                                # a conexão não ficou "abortada"


def test_user_repository_keyset_pagination(users):
    for i in range(7):
        users.add(f"u{i}@x.com", f"U{i}")
    rows, cursor = users.page(limit=3)
    assert [r["email"] for r in rows] == ["u0@x.com", "u1@x.com", "u2@x.com"] and cursor == rows[-1]["id"]
    seen = [r["email"] for r in rows]
    while cursor:
        rows, cursor = users.page(after_id=cursor, limit=3)
        seen += [r["email"] for r in rows]
    assert seen == [f"u{i}@x.com" for i in range(7)]
    rows, cursor = users.page(after_id=0, limit=7)
    assert len(rows) == 7 and cursor is None                                     # exatamente o que cabe: sem próxima
    assert users.page(after_id=10_000) == ([], None)


# ---------- ex03 ----------
def test_copy_rows_loads_and_counts(load_exercise, pg):
    copy_rows = load_exercise("ex03_copy_rows").copy_rows
    with pg.connect() as conn:
        conn.execute("CREATE TABLE item (id serial PRIMARY KEY, name text NOT NULL, price numeric(8, 2))")
        assert copy_rows(conn, "item", ["name", "price"], ((f"n{i}", i / 4) for i in range(1000))) == 1000
        assert conn.execute("SELECT count(*) AS n FROM item").fetchone()["n"] == 1000
        assert copy_rows(conn, "item", ["name"], []) == 0


def test_copy_rows_is_atomic_and_safe(load_exercise, pg):
    copy_rows = load_exercise("ex03_copy_rows").copy_rows
    with pg.connect() as conn:
        conn.execute("CREATE TABLE item (id serial PRIMARY KEY, name text NOT NULL)")
        conn.commit()
        with pytest.raises(psycopg.Error):
            copy_rows(conn, "item", ["name"], [("a",), ("b",), (None,)])
        conn.rollback()
        assert conn.execute("SELECT count(*) AS n FROM item").fetchone()["n"] == 0
        with pytest.raises(ValueError):
            copy_rows(conn, "item", [], [("a",)])
        with pytest.raises(psycopg.Error):
            copy_rows(conn, 'item"; DROP TABLE item; --', ["name"], [("a",)])
        conn.rollback()
        assert conn.execute("SELECT count(*) AS n FROM item").fetchone()["n"] == 0


# ---------- ex04 ----------
def test_job_queue_basic(load_exercise, pg):
    m = load_exercise("ex04_job_queue")
    with pg.connect(autocommit=False) as conn:
        m.create_schema(conn)
        ids = m.enqueue(conn, [f"t{i}" for i in range(7)])
        assert ids == list(range(1, 8))
        assert m.claim(conn, "A", limit=3) == [1, 2, 3]
        assert m.claim(conn, "B", limit=10) == [4, 5, 6, 7]
        assert m.claim(conn, "C") == []
        assert m.finish(conn, 1, "A") is True and m.finish(conn, 1, "A") is False
        assert m.finish(conn, 4, "A") is False and m.finish(conn, 4, "B") is True


def test_job_queue_skip_locked_concurrent_workers(load_exercise, pg):
    m = load_exercise("ex04_job_queue")
    with pg.connect(autocommit=False) as setup:
        m.create_schema(setup)
        m.enqueue(setup, [f"t{i}" for i in range(10)])
    claimed = {}

    def worker(name):
        with pg.connect(autocommit=False) as conn:
            claimed[name] = m.claim(conn, name, limit=5, hold=0.4)

    threads = [threading.Thread(target=worker, args=(n,)) for n in ("A", "B")]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join(20)
    elapsed = time.perf_counter() - start
    assert sorted(claimed["A"] + claimed["B"]) == list(range(1, 11)) and not set(claimed["A"]) & set(claimed["B"])
    assert len(claimed["A"]) == 5 and len(claimed["B"]) == 5
    assert elapsed < 0.75                                                            # NÃO esperaram um pelo outro (2 x 0,4 s seria 0,8)


# ---------- ex05 ----------
@pytest.fixture
def accounts(pg):
    with pg.connect() as conn:
        conn.execute("CREATE TABLE account (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0))")
        conn.execute("INSERT INTO account VALUES (1, 100), (2, 100), (3, 0)")
    return pg


def balances(pg):
    with pg.connect() as conn:
        return {r["id"]: r["balance"] for r in conn.execute("SELECT * FROM account")}


def test_transfer_moves_money_and_validates(load_exercise, accounts):
    transfer = load_exercise("ex05_transfer").transfer
    with accounts.connect(autocommit=False) as conn:
        transfer(conn, 1, 2, 30)
        conn.commit()
        for args in ((1, 1, 5), (1, 2, 0), (1, 2, -5), (1, 99, 5), (3, 1, 1), (2, 1, 10_000)):
            with pytest.raises(ValueError):
                transfer(conn, *args)
            conn.rollback()
    assert balances(accounts) == {1: 70, 2: 130, 3: 0}


def test_transfer_opposite_directions_no_deadlock(load_exercise, accounts):
    transfer = load_exercise("ex05_transfer").transfer
    errors = []

    def loop(source, target):
        try:
            with accounts.connect(autocommit=False) as conn:
                for _ in range(40):
                    transfer(conn, source, target, 1)
                    conn.commit()
        except Exception as error:
            errors.append(error)

    threads = [threading.Thread(target=loop, args=(1, 2)), threading.Thread(target=loop, args=(2, 1)),
               threading.Thread(target=loop, args=(1, 2)), threading.Thread(target=loop, args=(2, 1))]
    for t in threads:
        t.start()
    for t in threads:
        t.join(60)
    assert not errors, errors
    assert sum(balances(accounts).values()) == 200 and balances(accounts)[1] == 100


# ---------- ex06 ----------
def test_plan_nodes_and_uses_index(load_exercise, pg):
    m = load_exercise("ex06_plans_and_pools")
    with pg.connect() as conn:
        conn.execute("CREATE TABLE t (id serial PRIMARY KEY, email text, kind int)")
        conn.execute("INSERT INTO t (email, kind) SELECT 'u' || g, g % 10 FROM generate_series(1, 20000) g")
        conn.execute("ANALYZE t")
        seq = m.plan_nodes(conn, "SELECT * FROM t WHERE email = %s", ("u500",))
        assert "Seq Scan" in seq and not m.uses_index(seq)
        conn.execute("CREATE INDEX t_email ON t (email)")
        conn.execute("ANALYZE t")
        idx = m.plan_nodes(conn, "SELECT * FROM t WHERE email = %s", ("u500",))
        assert m.uses_index(idx) and "Seq Scan" not in idx
        joined = m.plan_nodes(conn, "SELECT * FROM t a JOIN t b ON a.kind = b.id WHERE a.email = %s", ("u1",))
        assert len(joined) >= 2
        assert conn.execute("SELECT count(*) AS n FROM t").fetchone()["n"] == 20000


def test_uses_index_pure(load_exercise):
    m = load_exercise("ex06_plans_and_pools")
    assert m.uses_index({"Bitmap Heap Scan", "Bitmap Index Scan"}) and m.uses_index({"Index Only Scan"})
    assert not m.uses_index({"Seq Scan", "Hash Join"}) and not m.uses_index(set())


def test_pool_size(load_exercise):
    pool_size = load_exercise("ex06_plans_and_pools").pool_size
    assert pool_size(200, 0.02) == 6                                      # 200 x 0,02 = 4 x 1,5
    assert pool_size(1, 0.001) == 1 and pool_size(10_000, 1, max_connections=50) == 50
    assert pool_size(100, 0.05, headroom=1) == 5
    for args in ((0, 1), (1, 0), (1, 1, 0.5), (1, 1, 1.5, 0)):
        with pytest.raises(ValueError):
            pool_size(*args)
