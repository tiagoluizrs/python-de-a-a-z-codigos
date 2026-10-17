import sqlite3

import pytest


def row(order_id, customer_id, name="Ana", city="Recife", total=10):
    return {"order_id": order_id, "customer_id": customer_id, "customer_name": name, "customer_city": city, "total": total}


# ---------- ex01 ----------
def test_split_customers(load_exercise):
    split = load_exercise("ex01_normalize").split_customers
    customers, orders = split([row(1, 1), row(2, 1, total=20), row(3, 2, "Bia", "Natal", 5)])
    assert customers == {1: {"name": "Ana", "city": "Recife"}, 2: {"name": "Bia", "city": "Natal"}}
    assert orders == [{"id": 1, "customer_id": 1, "total": 10}, {"id": 2, "customer_id": 1, "total": 20}, {"id": 3, "customer_id": 2, "total": 5}]
    assert split([]) == ({}, [])


def test_split_customers_detects_inconsistencies(load_exercise):
    split = load_exercise("ex01_normalize").split_customers
    with pytest.raises(ValueError, match="clientes inconsistentes: 1, 7"):
        split([row(1, 7, "Z", "A"), row(2, 1), row(3, 1, city="Olinda"), row(4, 7, "Z", "B"), row(5, 3)])
    with pytest.raises(ValueError, match="pedido duplicado: 2"):
        split([row(1, 1), row(2, 1), row(2, 3)])


# ---------- ex02 ----------
def test_schema_smells_finds_problems(load_exercise):
    smells = load_exercise("ex02_schema_smells").schema_smells
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE customer (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customer(id), total REAL, note TEXT);
        CREATE TABLE log_entry (message TEXT, at TEXT);
        CREATE TABLE ok_table (id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES customer(id), price NUMERIC);
        CREATE INDEX ix_ok_owner ON ok_table (owner_id);
    """)
    assert smells(conn) == [
        ("coluna_nula_na_pk_unica", "customer", "email"),
        ("dinheiro_em_float", "orders", "total"),
        ("fk_sem_indice", "orders", "customer_id"),
        ("sem_chave_primaria", "log_entry", None),
    ]


def test_schema_smells_clean_database(load_exercise):
    smells = load_exercise("ex02_schema_smells").schema_smells
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE customer (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customer(id), total NUMERIC NOT NULL);
        CREATE INDEX ix_orders_customer ON orders (customer_id);
        CREATE TABLE tag (customer_id INTEGER NOT NULL REFERENCES customer(id), tag TEXT NOT NULL, PRIMARY KEY (customer_id, tag));
    """)
    assert smells(conn) == [] and smells(sqlite3.connect(":memory:")) == []


# ---------- ex03 ----------
def test_redundant_indexes(load_exercise):
    redundant = load_exercise("ex03_redundant_indexes").redundant_indexes
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE t (id INTEGER PRIMARY KEY, a INT, b INT, c INT, email TEXT UNIQUE);
        CREATE INDEX ix_a ON t (a);
        CREATE INDEX ix_ab ON t (a, b);
        CREATE INDEX ix_abc ON t (a, b, c);
        CREATE INDEX ix_b ON t (b);
        CREATE INDEX ix_c1 ON t (c);
        CREATE INDEX ix_c2 ON t (c);
        CREATE UNIQUE INDEX uq_a ON t (a);
        CREATE INDEX ix_partial ON t (a) WHERE b > 1;
    """)
    assert redundant(conn) == [("t", "ix_a", "ix_ab"), ("t", "ix_ab", "ix_abc"), ("t", "ix_c2", "ix_c1")]


def test_redundant_indexes_none(load_exercise):
    redundant = load_exercise("ex03_redundant_indexes").redundant_indexes
    conn = sqlite3.connect(":memory:")
    conn.executescript("CREATE TABLE t (id INTEGER PRIMARY KEY, a INT, b INT); CREATE INDEX ix_a ON t (a); CREATE INDEX ix_b ON t (b);")
    assert redundant(conn) == []


# ---------- ex04 ----------
@pytest.fixture
def shop():
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE customer (id INTEGER PRIMARY KEY, name TEXT, city TEXT);
        CREATE TABLE sale (id INTEGER PRIMARY KEY, customer_id INTEGER, amount INTEGER);
        CREATE INDEX ix_sale_customer ON sale (customer_id);
    """)
    return conn


def test_plan_report(load_exercise, shop):
    report = load_exercise("ex04_plan_report").plan_report
    full = report(shop, "SELECT * FROM customer WHERE city = ?", ("x",))
    assert full == {"scans": ["customer"], "searches": [], "temp_btree": False, "uses_index": False}
    by_id = report(shop, "SELECT * FROM customer WHERE id = ?", (1,))
    assert by_id["searches"] == [("customer", "PRIMARY KEY")] and by_id["scans"] == [] and by_id["uses_index"] is True
    by_index = report(shop, "SELECT * FROM sale WHERE customer_id = ?", (1,))
    assert by_index["searches"] == [("sale", "ix_sale_customer")]
    grouped = report(shop, "SELECT city, COUNT(*) FROM customer GROUP BY city")
    assert grouped["temp_btree"] is True and grouped["scans"] == ["customer"]
    joined = report(shop, "SELECT * FROM customer c JOIN sale s ON s.customer_id = c.id")
    assert len(joined["scans"]) == 1 and joined["uses_index"] is True                    # varre UMA tabela e busca na outra


def test_assert_uses_index(load_exercise, shop):
    assert_uses_index = load_exercise("ex04_plan_report").assert_uses_index
    assert assert_uses_index(shop, "SELECT * FROM sale WHERE customer_id = ?", (1,)) is None
    with pytest.raises(AssertionError, match="customer"):
        assert_uses_index(shop, "SELECT * FROM customer WHERE city = 'x'")
    assert assert_uses_index(shop, "SELECT * FROM customer c JOIN sale s ON s.customer_id = c.id", table="sale") is None
    with pytest.raises(AssertionError):
        assert_uses_index(shop, "SELECT * FROM sale WHERE amount > 1", table="sale")


# ---------- ex05 ----------
@pytest.fixture
def people():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE p (id INTEGER PRIMARY KEY, age INTEGER, name TEXT)")
    conn.executemany("INSERT INTO p (age, name) VALUES (?, ?)", [(20 + (i % 4), f"n{i}") for i in range(1, 23)])    # muitos empates em age
    return conn


def test_keyset_pagination_with_ties(load_exercise, people):
    keyset = load_exercise("ex05_keyset_pagination").keyset_page
    expected = [tuple(r) for r in people.execute("SELECT id, age, name FROM p ORDER BY age, id")]
    seen, after, pages = [], None, 0
    while True:
        rows, after = keyset(people, "p", ["age", "id"], after, limit=5, columns="id, age, name")
        seen += rows
        pages += 1
        if after is None:
            break
    assert seen == expected and pages == 5 and len(seen) == len(set(seen))              # sem repetir e sem pular


def test_keyset_edges_and_validation(load_exercise, people):
    keyset = load_exercise("ex05_keyset_pagination").keyset_page
    rows, nxt = keyset(people, "p", ["id"], limit=22)
    assert len(rows) == 22 and nxt is None                                              # exatamente o que cabe
    rows, nxt = keyset(people, "p", ["id"], limit=21)
    assert len(rows) == 21 and nxt == (21,)
    assert keyset(people, "p", ["id"], after=(22,), limit=5) == ([], None)
    for kwargs in ({"order_columns": []}, {"order_columns": ["id; DROP TABLE p"]}, {"limit": 0}, {"limit": 1001}, {"table": "p; --"},
                   {"columns": "name", "order_columns": ["id"]}, {"after": (1, 2)}):
        args = {"table": "p", "order_columns": ["id"], **kwargs}
        with pytest.raises(ValueError):
            keyset(people, **args)
    assert people.execute("SELECT COUNT(*) FROM p").fetchone()[0] == 22


# ---------- ex06 ----------
@pytest.fixture
def users(load_exercise):
    conn = sqlite3.connect(":memory:")
    repo = load_exercise("ex06_soft_delete").SoftDeleteUsers(conn)
    repo.create_schema()
    repo.create_schema()                                                                 # idempotente
    return repo


def test_soft_delete_unique_among_active(users):
    a = users.add("ana@x.com", "Ana")
    with pytest.raises(ValueError):
        users.add("ANA@x.com", "Outra Ana")
    assert users.delete(a, "2026-10-01T00:00:00") is True and users.delete(a, "2026-10-02T00:00:00") is False
    b = users.add("ana@x.com", "Ana Nova")                                              # o e-mail ficou livre
    assert b != a and users.active_emails() == ["ana@x.com"]
    assert users.delete(999, "2026-10-01") is False


def test_soft_delete_restore_and_purge(users):
    a = users.add("ana@x.com", "Ana")
    users.delete(a, "2026-01-01T00:00:00")
    b = users.add("ANA@x.com", "Ana 2")
    with pytest.raises(ValueError):
        users.restore(a)                                                                 # conflito com o ativo
    users.delete(b, "2026-06-01T00:00:00")
    assert users.restore(a) is True and users.restore(a) is False and users.active_emails() == ["ana@x.com"]
    c = users.add("bia@x.com", "Bia")
    users.delete(c, "2026-03-01T00:00:00")
    assert users.purge("2026-02-01T00:00:00") == 0
    assert users.purge("2026-12-31T00:00:00") == 2                                      # b e c; o ativo (a) fica
    assert users.active_emails() == ["ana@x.com"]
    assert users.restore(999) is False
