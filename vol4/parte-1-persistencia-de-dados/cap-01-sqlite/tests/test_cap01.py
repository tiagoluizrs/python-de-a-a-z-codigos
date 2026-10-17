import sqlite3

import pytest


# ---------- ex01 ----------
def test_open_database_pragmas(load_exercise, tmp_path):
    m = load_exercise("ex01_database")
    conn = m.open_database()
    assert conn.row_factory is sqlite3.Row and conn.isolation_level is None
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert conn.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "memory"
    file_conn = m.open_database(str(tmp_path / "a.db"))
    assert file_conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    file_conn.close()


def test_transaction_commit_and_rollback(load_exercise):
    m = load_exercise("ex01_database")
    conn = m.open_database()
    conn.execute("CREATE TABLE t (x INTEGER)")
    with m.transaction(conn):
        conn.execute("INSERT INTO t VALUES (1)")
        assert conn.in_transaction
    assert not conn.in_transaction and conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
    with pytest.raises(RuntimeError):
        with m.transaction(conn):
            conn.execute("INSERT INTO t VALUES (2)")
            raise RuntimeError("falha")
    assert not conn.in_transaction and conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1


def test_transaction_nested_savepoints(load_exercise):
    m = load_exercise("ex01_database")
    conn = m.open_database()
    conn.execute("CREATE TABLE t (x INTEGER)")
    with m.transaction(conn):
        conn.execute("INSERT INTO t VALUES (1)")
        with pytest.raises(ValueError):
            with m.transaction(conn):
                conn.execute("INSERT INTO t VALUES (99)")
                raise ValueError("só o interno")
        with m.transaction(conn):
            conn.execute("INSERT INTO t VALUES (2)")
        assert conn.in_transaction
    assert [r[0] for r in conn.execute("SELECT x FROM t ORDER BY x")] == [1, 2]
    with pytest.raises(KeyError):
        with m.transaction(conn):
            conn.execute("INSERT INTO t VALUES (3)")
            with m.transaction(conn):
                conn.execute("INSERT INTO t VALUES (4)")
            raise KeyError("o externo falha")
    assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 2


# ---------- ex02 ----------
@pytest.fixture
def repo(load_exercise):
    m = load_exercise("ex02_task_repository")
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    repository = m.TaskRepository(conn)
    repository.create_schema()
    repository.m = m
    return repository


def test_task_repository_crud(repo):
    a = repo.add("estudar")
    b = repo.add("treinar")
    assert (a.id, a.title, a.done) == (1, "estudar", False) and b.id == 2
    assert repo.get(1) == a and repo.get(99) is None
    assert repo.complete(1) is True and repo.complete(1) is False and repo.complete(99) is False
    assert repo.get(1).done is True and isinstance(repo.get(1).done, bool)
    assert [t.title for t in repo.list()] == ["estudar", "treinar"]
    assert [t.title for t in repo.list(done=True)] == ["estudar"] and [t.title for t in repo.list(done=False)] == ["treinar"]
    assert repo.delete(2) is True and repo.delete(2) is False


def test_task_repository_validation_and_stats(repo):
    assert repo.stats() == {"total": 0, "done": 0, "pending": 0}
    repo.add("a")
    repo.add("b")
    repo.complete(1)
    assert repo.stats() == {"total": 2, "done": 1, "pending": 1}
    for bad in ("a", "   ", ""):
        with pytest.raises(ValueError):
            repo.add(bad)
    assert repo.stats()["total"] == 2                                        # falhas não deixaram resíduo
    assert repo.add("c").title == "c"                                         # a conexão continua utilizável
    assert "'; DROP TABLE task; --" in [t.title for t in [repo.add("'; DROP TABLE task; --")]]


# ---------- ex03 ----------
def test_bulk_insert_counts_and_batches(load_exercise):
    bulk_insert = load_exercise("ex03_bulk_insert").bulk_insert
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (a INTEGER, b TEXT)")
    assert bulk_insert(conn, "t", ["a", "b"], ((i, str(i)) for i in range(2500)), batch_size=1000) == 2500
    assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 2500
    assert bulk_insert(conn, "t", ["a", "b"], []) == 0


def test_bulk_insert_is_atomic_and_validates(load_exercise):
    bulk_insert = load_exercise("ex03_bulk_insert").bulk_insert
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (a INTEGER PRIMARY KEY, b TEXT NOT NULL)")
    rows = [(i, "x") for i in range(10)] + [(5, "duplicado")]
    with pytest.raises(sqlite3.IntegrityError):
        bulk_insert(conn, "t", ["a", "b"], rows, batch_size=4)
    assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0              # NADA ficou
    for table, columns in (("t; DROP TABLE t", ["a"]), ("t", ["a, b"]), ("1t", ["a"]), ("t", [])):
        with pytest.raises(ValueError):
            bulk_insert(conn, table, columns, [(1,)])
    with pytest.raises(ValueError):
        bulk_insert(conn, "t", ["a"], [(1,)], batch_size=0)
    assert conn.execute("SELECT name FROM sqlite_master").fetchone()[0] == "t"


# ---------- ex04 ----------
@pytest.fixture
def product_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE product (id INTEGER PRIMARY KEY, name TEXT, price REAL, category TEXT)")
    conn.executemany("INSERT INTO product (name, price, category) VALUES (?, ?, ?)", [
        ("caneta azul", 2.5, "papelaria"), ("caneta_preta", 3.0, "papelaria"), ("100% algodao", 40.0, "roupas"),
        ("mochila", 120.0, "bolsas"), ("caderno", 18.9, "papelaria")])
    return conn


def run_query(conn, build, **kwargs):
    sql, params = build(**kwargs)
    return [r[1] for r in conn.execute(sql, params)]


def test_product_query_filters_and_order(load_exercise, product_db):
    build = load_exercise("ex04_product_query").build_product_query
    assert run_query(product_db, build) == ["100% algodao", "caderno", "caneta azul", "caneta_preta", "mochila"]
    assert run_query(product_db, build, category="papelaria", order_by="price", descending=True) == ["caderno", "caneta_preta", "caneta azul"]
    assert run_query(product_db, build, min_price=3, max_price=40) == ["100% algodao", "caderno", "caneta_preta"]
    assert run_query(product_db, build, limit=2, offset=1) == ["caderno", "caneta azul"]
    assert run_query(product_db, build, name_contains="CANETA") == ["caneta azul", "caneta_preta"]


def test_product_query_is_injection_safe(load_exercise, product_db):
    build = load_exercise("ex04_product_query").build_product_query
    assert run_query(product_db, build, name_contains="%") == ["100% algodao"]               # % literal
    assert run_query(product_db, build, name_contains="_") == ["caneta_preta"]               # _ literal
    evil = "'; DROP TABLE product; --"
    sql, params = build(name_contains=evil, category=evil)
    assert "DROP" not in sql and evil not in sql and params.count("%" + evil.replace("_", "\\_") + "%") <= 1
    assert run_query(product_db, build, name_contains=evil) == []
    assert product_db.execute("SELECT COUNT(*) FROM product").fetchone()[0] == 5
    for kwargs in ({"order_by": "price; DROP TABLE product"}, {"order_by": "nome"}, {"limit": 0}, {"limit": 201}, {"offset": -1}):
        with pytest.raises(ValueError):
            build(**kwargs)
    assert build()[0].count("?") == len(build()[1])


# ---------- ex05 ----------
def test_uses_index(load_exercise):
    m = load_exercise("ex05_indexes")
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE u (id INTEGER PRIMARY KEY, email TEXT, age INTEGER)")
    conn.executemany("INSERT INTO u (email, age) VALUES (?, ?)", [(f"a{i}@x", i) for i in range(100)])
    assert m.uses_index(conn, "SELECT * FROM u WHERE email = ?", ("a1@x",)) is False
    assert m.uses_index(conn, "SELECT * FROM u WHERE id = ?", (5,)) is True
    conn.execute("CREATE INDEX ix ON u (email)")
    assert m.uses_index(conn, "SELECT * FROM u WHERE email = ?", ("a1@x",)) is True
    assert m.uses_index(conn, "SELECT * FROM u WHERE age = 3") is False


def test_ensure_index(load_exercise):
    m = load_exercise("ex05_indexes")
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE u (id INTEGER PRIMARY KEY, email TEXT)")
    assert m.ensure_index(conn, "u", "email", unique=True) is True
    assert m.ensure_index(conn, "u", "email") is False
    assert conn.execute("SELECT name FROM sqlite_master WHERE type = 'index' AND name = 'ix_u_email'").fetchone()
    conn.execute("INSERT INTO u (email) VALUES ('a')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO u (email) VALUES ('a')")
    for args in (("u", "nao_existe"), ("tabela_x", "id"), ("u; DROP TABLE u", "email"), ("u", "email) --")):
        with pytest.raises(ValueError):
            m.ensure_index(conn, *args)


# ---------- ex06 ----------
MIGRATIONS = [
    "CREATE TABLE person (id INTEGER PRIMARY KEY, name TEXT NOT NULL);",
    "ALTER TABLE person ADD COLUMN email TEXT; CREATE INDEX ix_person_email ON person (email);",
    "CREATE TABLE note (id INTEGER PRIMARY KEY, person_id INTEGER REFERENCES person(id), body TEXT);",
]


def test_apply_migrations_from_zero_and_idempotent(load_exercise):
    apply = load_exercise("ex06_migrations").apply_migrations
    conn = sqlite3.connect(":memory:")
    assert apply(conn, MIGRATIONS) == 3
    assert [r[1] for r in conn.execute("PRAGMA table_info(person)")] == ["id", "name", "email"]
    assert apply(conn, MIGRATIONS) == 3                                       # nada a fazer
    assert apply(sqlite3.connect(":memory:"), []) == 0


def test_apply_migrations_incremental(load_exercise):
    apply = load_exercise("ex06_migrations").apply_migrations
    conn = sqlite3.connect(":memory:")
    assert apply(conn, MIGRATIONS[:1]) == 1
    conn.execute("INSERT INTO person (name) VALUES ('ana')")
    conn.commit()
    assert apply(conn, MIGRATIONS) == 3
    assert conn.execute("SELECT name, email FROM person").fetchone() == ("ana", None)


def test_apply_migrations_failure_rolls_back_only_that_one(load_exercise):
    apply = load_exercise("ex06_migrations").apply_migrations
    conn = sqlite3.connect(":memory:")
    broken = MIGRATIONS[:2] + ["CREATE TABLE ok_before (x); CREATE TABLE person (x);", "CREATE TABLE never (x);"]
    with pytest.raises(sqlite3.OperationalError):
        apply(conn, broken)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 2
    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "ok_before" not in names and "never" not in names and "person" in names
    with pytest.raises(RuntimeError):
        apply(conn, MIGRATIONS[:1])                                           # banco mais novo que a lista
