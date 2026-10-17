import threading
import time

import pymysql
import pytest


# ---------- ex01 (sem servidor) ----------
def test_parse_url_full(load_exercise):
    parse = load_exercise("ex01_parse_url").parse_mysql_url
    assert parse("mysql://app:p%40ss%3Aw@db.local:3307/loja?charset=utf8mb4&connect_timeout=5") == {
        "user": "app", "password": "p@ss:w", "host": "db.local", "port": 3307, "database": "loja",
        "charset": "utf8mb4", "connect_timeout": 5}


def test_parse_url_defaults_and_schemes(load_exercise):
    parse = load_exercise("ex01_parse_url").parse_mysql_url
    result = parse("mariadb+x://u@h/db".replace("mariadb+x", "mysql+pymysql"))
    assert result == {"user": "u", "password": "", "host": "h", "port": 3306, "database": "db", "charset": "utf8mb4"}
    assert parse("mariadb://u:p@h/db?charset=latin1")["charset"] == "latin1"
    for bad in ("postgresql://u:p@h/db", "mysql://h/db", "mysql://u:p@/db", "mysql://u:p@h", "mysql://u:p@h/"):
        with pytest.raises(ValueError):
            parse(bad)


# ---------- ex02 ----------
@pytest.fixture
def products(load_exercise, db):
    m = load_exercise("ex02_product_repository")
    conn = db.connect(autocommit=False)
    repo = m.ProductRepository(conn)
    repo.create_schema()
    yield repo
    conn.close()


def test_product_add_get_and_duplicates(products):
    p = products.add("A-1", "caneta", 10)
    assert p["id"] == 1 and p["sku"] == "A-1" and p["stock"] == 10
    assert products.get(1) == p and products.get(99) is None
    with pytest.raises(ValueError):
        products.add("A-1", "outra")
    assert products.add("a-1", "minúscula")["id"] >= 2                 # SKU é sensível a maiúsculas; a conexão segue boa


def test_product_add_stock(products):
    products.add("S", "x", 5)
    products.add_stock("S", 3)
    products.add_stock("S", -8)
    assert products.get(1)["stock"] == 0
    with pytest.raises(ValueError):
        products.add_stock("S", -1)
    with pytest.raises(KeyError):
        products.add_stock("NAO-EXISTE", 1)
    assert products.get(1)["stock"] == 0


def test_product_upsert(products):
    assert products.upsert("U", "primeiro", 5) is True
    assert products.upsert("U", "segundo", 7) is False
    row = products.get(1)
    assert row["name"] == "segundo" and row["stock"] == 12


# ---------- ex03 ----------
def test_quote_identifier(load_exercise):
    quote = load_exercise("ex03_bulk_insert").quote_identifier
    assert quote("tabela") == "`tabela`" and quote("a`b") == "`a``b`" and quote("order") == "`order`"
    for bad in ("", "a\x00b", "x" * 65):
        with pytest.raises(ValueError):
            quote(bad)


def test_bulk_insert(load_exercise, db):
    m = load_exercise("ex03_bulk_insert")
    with db.connect(autocommit=False) as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE TABLE `order` (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(10) NOT NULL, qty INT)")
        assert m.bulk_insert(conn, "order", ["name", "qty"], ((f"n{i}", i) for i in range(2500)), batch_size=1000) == 2500
        assert m.bulk_insert(conn, "order", ["name", "qty"], []) == 0
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS n FROM `order`")
            assert cursor.fetchone()["n"] == 2500
        rows = [("ok", 1)] * 5 + [(None, 2)] + [("ok", 1)] * 5
        with pytest.raises(pymysql.err.IntegrityError):
            m.bulk_insert(conn, "order", ["name", "qty"], rows, batch_size=4)
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS n FROM `order`")
            assert cursor.fetchone()["n"] == 2500                          # a carga falha NÃO deixou resíduo
        with pytest.raises(ValueError):
            m.bulk_insert(conn, "order", [], [(1,)])
        with pytest.raises(ValueError):
            m.bulk_insert(conn, "order", ["name"], [("a",)], batch_size=0)


# ---------- ex04 ----------
def test_run_with_retry_logic(load_exercise):
    m = load_exercise("ex04_retry_transaction")
    calls, sleeps = [], []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise pymysql.err.OperationalError(1213, "Deadlock found when trying to get lock")
        return "ok"

    assert m.run_with_retry(flaky, attempts=3, delay=0.1, sleep=sleeps.append) == "ok" and sleeps == [0.1, 0.2]
    calls.clear()

    def always():
        calls.append(1)
        raise pymysql.err.OperationalError(1205, "Lock wait timeout exceeded")

    with pytest.raises(pymysql.err.OperationalError):
        m.run_with_retry(always, attempts=2, sleep=lambda s: None)
    assert len(calls) == 2
    calls.clear()

    def other():
        calls.append(1)
        raise pymysql.err.OperationalError(2003, "Can\'t connect")

    with pytest.raises(pymysql.err.OperationalError):
        m.run_with_retry(other, attempts=5, sleep=lambda s: None)
    assert len(calls) == 1
    with pytest.raises(ValueError):
        m.run_with_retry(other, attempts=0)


@pytest.fixture
def accounts(db):
    with db.connect(autocommit=True) as conn, conn.cursor() as cursor:
        cursor.execute("CREATE TABLE account (id INT PRIMARY KEY, balance INT NOT NULL) ENGINE=InnoDB")
        cursor.execute("INSERT INTO account VALUES (1, 100), (2, 100), (3, 0)")
    return db


def balances(db):
    with db.connect(autocommit=True) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT id, balance FROM account")
        return {r["id"]: r["balance"] for r in cursor.fetchall()}


def test_transfer_validations(load_exercise, accounts):
    transfer = load_exercise("ex04_retry_transaction").transfer
    with accounts.connect(autocommit=False) as conn:
        transfer(conn, 1, 2, 30)
        for args in ((1, 1, 5), (1, 2, 0), (1, 2, -1), (1, 99, 5), (3, 1, 1), (2, 1, 10_000)):
            with pytest.raises(ValueError):
                transfer(conn, *args)
    assert balances(accounts) == {1: 70, 2: 130, 3: 0}


def test_transfer_concurrent_opposite_directions(load_exercise, accounts):
    m = load_exercise("ex04_retry_transaction")
    errors = []

    def loop(source, target):
        try:
            with accounts.connect(autocommit=False) as conn:
                for _ in range(30):
                    m.run_with_retry(lambda: m.transfer(conn, source, target, 1), attempts=5)
        except Exception as error:
            errors.append(error)

    threads = [threading.Thread(target=loop, args=args) for args in ((1, 2), (2, 1), (1, 2), (2, 1))]
    for t in threads:
        t.start()
    for t in threads:
        t.join(60)
    assert not errors, errors
    assert sum(balances(accounts).values()) == 200 and balances(accounts)[1] == 100


# ---------- ex05 ----------
def test_audit_charsets(load_exercise, db):
    m = load_exercise("ex05_audit_charsets")
    with db.connect(autocommit=True) as conn, conn.cursor() as cursor:
        cursor.execute("CREATE TABLE good (a VARCHAR(5), n INT) CHARACTER SET utf8mb4")
        cursor.execute("CREATE TABLE legacy (a VARCHAR(5), b TEXT, n INT) CHARACTER SET latin1")
        cursor.execute("CREATE TABLE mixed (x VARCHAR(5) CHARACTER SET utf8mb3, y VARCHAR(5)) CHARACTER SET utf8mb4")
        findings = m.audit_charsets(conn, db.database)
        assert [(t, c) for t, c, _ in findings] == [("legacy", "a"), ("legacy", "b"), ("mixed", "x")]
        assert {cs for _, _, cs in findings} <= {"latin1", "utf8", "utf8mb3"}
        assert m.audit_charsets(conn, "schema_que_nao_existe") == []
        statements = m.fix_statements(findings)
        assert statements == ["ALTER TABLE `legacy` CONVERT TO CHARACTER SET utf8mb4", "ALTER TABLE `mixed` CONVERT TO CHARACTER SET utf8mb4"]
        for statement in statements:
            cursor.execute(statement)
        assert m.audit_charsets(conn, db.database) == []


def test_fix_statements_pure(load_exercise):
    fix = load_exercise("ex05_audit_charsets").fix_statements
    assert fix([]) == []
    assert fix([("a`b", "c", "latin1")]) == ["ALTER TABLE `a``b` CONVERT TO CHARACTER SET utf8mb4"]


# ---------- ex06 ----------
def test_ensure_column(load_exercise, db):
    m = load_exercise("ex06_ensure_column")
    with db.connect(autocommit=False) as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE TABLE person (id INT PRIMARY KEY)")
        assert m.column_exists(conn, "person", "id") is True and m.column_exists(conn, "person", "email") is False
        assert m.ensure_column(conn, "person", "email", "VARCHAR(80) NULL") is True
        assert m.ensure_column(conn, "person", "email", "VARCHAR(80) NULL") is False
        assert m.column_exists(conn, "person", "email") is True
        for args in (("person", "x; DROP TABLE person", "INT"), ("pe`rson", "x", "INT"), ("person", "1x", "INT")):
            with pytest.raises(ValueError):
                m.ensure_column(conn, *args)
        assert m.column_exists(conn, "person", "id") is True
