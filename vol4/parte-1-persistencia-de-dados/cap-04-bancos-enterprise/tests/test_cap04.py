import re
import sqlite3

import pytest

ALL = ("sqlite", "postgresql", "mysql", "mariadb", "oracle", "mssql")


# ---------- ex01 ----------
def test_paginate_each_dialect(load_exercise):
    paginate = load_exercise("ex01_paginate").paginate
    for dialect in ("sqlite", "postgresql", "mysql", "mariadb"):
        assert paginate(dialect, "SELECT * FROM t ORDER BY id;", 10, 20) == "SELECT * FROM t ORDER BY id LIMIT 10 OFFSET 20"
        assert paginate(dialect, "SELECT * FROM t", 5) == "SELECT * FROM t LIMIT 5 OFFSET 0"
    for dialect in ("oracle", "mssql"):
        assert paginate(dialect, "SELECT * FROM t order  by id ; ", 10, 20) == "SELECT * FROM t order  by id OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY"


def test_paginate_validation(load_exercise):
    paginate = load_exercise("ex01_paginate").paginate
    for dialect in ("oracle", "mssql"):
        with pytest.raises(ValueError):
            paginate(dialect, "SELECT * FROM t", 5)
    for args in (("sqlite", "SELECT 1", 0), ("sqlite", "SELECT 1", 5, -1), ("sqlite", "SELECT 1", "5"), ("db2", "SELECT 1", 5)):
        with pytest.raises(ValueError):
            paginate(*args)


@pytest.fixture
def paged(backend, load_exercise):
    """A paginação gerada deve FUNCIONAR no banco real."""
    paginate = load_exercise("ex01_paginate").paginate
    b = backend
    b.execute(f"CREATE TABLE {b.table} (id INT PRIMARY KEY, name VARCHAR(20))")
    for i in range(1, 21):
        b.execute(f"INSERT INTO {b.table} (id, name) VALUES (?, ?)", (i, f"n{i}"))
    b.commit()
    return b, paginate


def test_paginate_runs_on_real_database(paged):
    b, paginate = paged
    sql = paginate(b.dialect, f"SELECT id FROM {b.table} ORDER BY id", 4, 8)
    assert [r[0] for r in b.query(sql)] == [9, 10, 11, 12]


# ---------- ex02 ----------
def test_quote_ident(load_exercise):
    q = load_exercise("ex02_quote_ident").quote_ident
    assert q("sqlite", 'a"b') == '"a""b"' and q("postgresql", "x") == '"x"' and q("oracle", "ORDER") == '"ORDER"'
    assert q("mysql", "a`b") == "`a``b`" and q("mariadb", "x") == "`x`"
    assert q("mssql", "a]b") == "[a]]b]" and q("mssql", "order") == "[order]"
    for bad in ("", "a\x00b", "x" * 129):
        with pytest.raises(ValueError):
            q("sqlite", bad)
    with pytest.raises(ValueError):
        q("db2", "x")


def test_quote_ident_hostile_name_stays_one_identifier(load_exercise):
    q = load_exercise("ex02_quote_ident").quote_ident
    conn = sqlite3.connect(":memory:")
    hostile = 'a"; DROP TABLE t; --'
    conn.execute("CREATE TABLE t (x)")
    conn.execute(f"CREATE TABLE {q('sqlite', hostile)} (v)")
    assert {r[0] for r in conn.execute("SELECT name FROM sqlite_master")} == {"t", hostile}


# ---------- ex03 ----------
def test_convert_placeholders(load_exercise):
    c = load_exercise("ex03_placeholders").convert_placeholders
    sql = "SELECT * FROM t WHERE a = ? AND b = ?"
    assert c("sqlite", sql) == sql and c("mssql", sql) == sql
    for dialect in ("postgresql", "mysql", "mariadb"):
        assert c(dialect, sql) == "SELECT * FROM t WHERE a = %s AND b = %s"
    assert c("oracle", sql) == "SELECT * FROM t WHERE a = :1 AND b = :2"


def test_convert_placeholders_literals_and_percent(load_exercise):
    c = load_exercise("ex03_placeholders").convert_placeholders
    sql = "SELECT 'quem?' AS q, 'it''s ?' AS r, x FROM t WHERE a = ? AND n LIKE '%a'"
    assert c("oracle", sql) == "SELECT 'quem?' AS q, 'it''s ?' AS r, x FROM t WHERE a = :1 AND n LIKE '%a'"
    assert c("postgresql", sql) == "SELECT 'quem?' AS q, 'it''s ?' AS r, x FROM t WHERE a = %s AND n LIKE '%%a'"
    with pytest.raises(ValueError):
        c("db2", "SELECT 1")


# ---------- ex04 ----------
def test_upsert_shapes(load_exercise):
    up = load_exercise("ex04_upsert").upsert_sql
    assert "ON CONFLICT" in up("sqlite", "t", "id", ["a"]) and "excluded" in up("postgresql", "t", "id", ["a"])
    assert "ON DUPLICATE KEY UPDATE" in up("mysql", "t", "id", ["a"]) and "VALUES(" in up("mariadb", "t", "id", ["a"])
    oracle, mssql = up("oracle", "t", "id", ["a", "b"]), up("mssql", "t", "id", ["a", "b"])
    assert oracle.startswith("MERGE INTO") and "dual" in oracle and not oracle.rstrip().endswith(";")
    assert mssql.startswith("MERGE") and mssql.rstrip().endswith(";")
    assert up("sqlite", "t", "id", ["a", "b"]).count("?") == 3 and oracle.count("?") == 3
    for args in (("sqlite", "t", "id", []), ("db2", "t", "id", ["a"])):
        with pytest.raises(ValueError):
            up(*args)


def test_upsert_works_on_every_available_database(backend, load_exercise):
    upsert_sql = load_exercise("ex04_upsert").upsert_sql
    b = backend
    qty_type = "NUMBER(10)" if b.dialect == "oracle" else "INT"
    name_type = "VARCHAR2(50)" if b.dialect == "oracle" else "VARCHAR(50)"
    b.execute(f"CREATE TABLE {b.table} (id INT PRIMARY KEY, name {name_type}, qty {qty_type})")
    sql = upsert_sql(b.dialect, b.table, "id", ["name", "qty"])
    b.execute(sql, (1, "caneta", 5))
    b.execute(sql, (2, "lápis", 7))
    b.execute(sql, (1, "caneta azul", 9))                                   # atualiza
    b.commit()
    rows = sorted((r[0], r[1], r[2]) for r in b.query(f"SELECT id, name, qty FROM {b.table}"))
    assert rows == [(1, "caneta azul", 9), (2, "lápis", 7)]


# ---------- ex05 ----------
def test_choose_arraysize(load_exercise):
    choose = load_exercise("ex05_fetching").choose_arraysize
    assert choose(100) == 10_000 and choose(1_000) == 1_000 and choose(1_000_000) == 10 and choose(50_000) == 20
    assert choose(100, target_batch_bytes=10_000, minimum=5, maximum=50) == 50
    for args in ((0,), (-1,), (10, 1000, 20, 10)):
        with pytest.raises(ValueError):
            choose(*args)


def test_fetch_in_batches(load_exercise):
    fetch = load_exercise("ex05_fetching").fetch_in_batches
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (x INTEGER)")
    conn.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(25)])
    batches = list(fetch(conn.execute("SELECT x FROM t ORDER BY x"), 10))
    assert [len(b) for b in batches] == [10, 10, 5] and [r[0] for b in batches for r in b] == list(range(25))
    assert list(fetch(conn.execute("SELECT x FROM t WHERE x < 0"), 10)) == []
    generator = fetch(conn.execute("SELECT x FROM t"), 7)
    assert next(generator) and hasattr(generator, "__next__")                 # é preguiçoso
    with pytest.raises(ValueError):
        list(fetch(conn.execute("SELECT 1"), 0))


# ---------- ex06 ----------
@pytest.mark.parametrize("dialect, code, expected", [
    ("postgresql", "23505", "duplicate"), ("postgresql", "40P01", "deadlock"), ("postgresql", "40001", "deadlock"),
    ("postgresql", "57014", "timeout"), ("postgresql", "08006", "connection"), ("postgresql", "42P01", "other"),
    ("mysql", 1062, "duplicate"), ("mariadb", 1213, "deadlock"), ("mysql", 1205, "timeout"), ("mysql", 2013, "connection"), ("mysql", 1146, "other"),
    ("oracle", 1, "duplicate"), ("oracle", 60, "deadlock"), ("oracle", 3113, "connection"), ("oracle", 942, "other"),
    ("mssql", 2627, "duplicate"), ("mssql", 2601, "duplicate"), ("mssql", 1205, "deadlock"), ("mssql", -2, "timeout"), ("mssql", 208, "other"),
    ("sqlite", "UNIQUE constraint failed: t.x", "duplicate"), ("sqlite", "database is locked", "timeout"), ("sqlite", "no such table", "other"),
])
def test_classify_error(load_exercise, dialect, code, expected):
    assert load_exercise("ex06_classify_errors").classify_error(dialect, code) == expected


def test_retryable_and_validation(load_exercise):
    m = load_exercise("ex06_classify_errors")
    assert [m.is_retryable(c) for c in m.CATEGORIES] == [False, True, True, True, False]
    with pytest.raises(ValueError):
        m.is_retryable("outra")
    with pytest.raises(ValueError):
        m.classify_error("db2", 1)
