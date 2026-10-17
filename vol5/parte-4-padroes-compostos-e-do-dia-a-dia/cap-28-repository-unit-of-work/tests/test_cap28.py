import sqlite3
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01: o MESMO contrato nas duas implementações ----------
@pytest.fixture(params=["memória", "sqlite"])
def repo_env(request, load_exercise):
    m = load_exercise("ex01_account_repository")

    def make():
        if request.param == "memória":
            return m.InMemoryAccountRepository()
        return m.SqliteAccountRepository(sqlite3.connect(":memory:"))

    return m, make


def test_add_get_save_delete(repo_env):
    m, make = repo_env
    repo = make()
    ana = m.Account("A", "Ana", 100_00)
    assert repo.count() == 0
    repo.add(ana)
    assert repo.get("A") == ana and isinstance(repo.get("A"), m.Account) and repo.count() == 1
    repo.save(replace(ana, owner="Ana Maria", balance_cents=5_00))
    assert repo.get("A") == m.Account("A", "Ana Maria", 5_00)
    repo.delete("A")
    assert repo.count() == 0
    with pytest.raises(KeyError, match="conta inexistente: A"):
        repo.get("A")


def test_errors(repo_env):
    m, make = repo_env
    repo = make()
    repo.add(m.Account("A", "Ana", 1))
    with pytest.raises(ValueError, match="conta já existe: A"):
        repo.add(m.Account("A", "Outra", 2))
    assert repo.get("A").owner == "Ana" and repo.count() == 1
    for call in (lambda: repo.get("Z"), lambda: repo.save(m.Account("Z", "x", 1)), lambda: repo.delete("Z")):
        with pytest.raises(KeyError, match="conta inexistente: Z"):
            call()
    with pytest.raises(ValueError, match="id vazio"):
        m.Account("", "x", 1)
    with pytest.raises(ValueError, match="saldo negativo"):
        m.Account("A", "x", -1)


def test_listing_orders(repo_env):
    m, make = repo_env
    repo = make()
    for account in (m.Account("C", "c", 300), m.Account("A", "a", 100), m.Account("B", "b", 300), m.Account("D", "d", 50)):
        repo.add(account)
    assert [a.id for a in repo.list_all()] == ["A", "B", "C", "D"]
    assert [a.id for a in repo.with_balance_at_least(100)] == ["B", "C", "A"]
    assert [a.id for a in repo.with_balance_at_least(0)] == ["B", "C", "A", "D"]
    assert repo.with_balance_at_least(301) == [] and all(isinstance(a, m.Account) for a in repo.list_all())


def test_hostile_ids_and_unicode(repo_env):
    m, make = repo_env
    repo = make()
    hostile = "x'; DROP TABLE accounts; --"
    repo.add(m.Account(hostile, "José 日本 O'Brien", 7))
    repo.add(m.Account("normal", "n", 1))
    assert repo.get(hostile) == m.Account(hostile, "José 日本 O'Brien", 7)
    assert repo.count() == 2 and [a.id for a in repo.list_all()] == ["normal", hostile]
    repo.delete(hostile)
    assert repo.count() == 1 and repo.get("normal").owner == "n"
    with pytest.raises(KeyError):
        repo.get("x' OR '1'='1")


def test_in_memory_initial_accounts(load_exercise):
    m = load_exercise("ex01_account_repository")
    repo = m.InMemoryAccountRepository([m.Account("A", "a", 1), m.Account("B", "b", 2)])
    assert repo.count() == 2 and repo.get("B").balance_cents == 2
    with pytest.raises(ValueError, match="conta já existe: A"):
        m.InMemoryAccountRepository([m.Account("A", "a", 1), m.Account("A", "dup", 2)])


def test_sqlite_repository_never_commits(load_exercise, tmp_path):
    m = load_exercise("ex01_account_repository")
    path = str(tmp_path / "bank.db")
    conn, other = sqlite3.connect(path), sqlite3.connect(path)
    repo = m.SqliteAccountRepository(conn)
    repo.add(m.Account("A", "Ana", 1))
    assert repo.count() == 1
    assert other.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0          # ninguém mais enxerga: não houve commit
    conn.rollback()
    assert repo.count() == 0
    repo.add(m.Account("B", "Bia", 2))
    conn.commit()
    assert other.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 1
    m.SqliteAccountRepository(conn)                                                   # o esquema é idempotente
    assert repo.count() == 1
    conn.close()
    other.close()


# ---------- ex02 ----------
@pytest.fixture(params=["memória", "sqlite"])
def world(request, load_exercise, tmp_path):
    m = load_exercise("ex02_unit_of_work")
    seed = [m.Account("A", "Ana", 100_00), m.Account("B", "Bia", 50_00)]
    if request.param == "memória":
        store = {a.id: a for a in seed}

        def factory():
            return m.InMemoryUnitOfWork(store)

        def balances():
            return {k: v.balance_cents for k, v in store.items()}

        target = m.InMemoryAccountRepository
    else:
        path = str(tmp_path / "bank.db")
        conn = sqlite3.connect(path)
        repo = m.SqliteAccountRepository(conn)
        for account in seed:
            repo.add(account)
        conn.commit()
        conn.close()

        def factory():
            return m.SqliteUnitOfWork(path)

        def balances():
            check = sqlite3.connect(path)
            try:
                return dict(check.execute("SELECT id, balance_cents FROM accounts ORDER BY id").fetchall())
            finally:
                check.close()

        target = m.SqliteAccountRepository
    return m, factory, balances, target


def test_transfer_success(world):
    m, factory, balances, _ = world
    assert m.transfer(factory, "A", "B", 30_00) == (70_00, 80_00)
    assert balances() == {"A": 70_00, "B": 80_00}
    assert m.transfer(factory, "B", "A", 80_00) == (0, 150_00) and balances() == {"A": 150_00, "B": 0}


def test_transfer_refusals_change_nothing(world):
    m, factory, balances, _ = world
    with pytest.raises(m.InsufficientFunds, match="saldo insuficiente em B"):
        m.transfer(factory, "B", "A", 50_01)
    with pytest.raises(KeyError, match="conta inexistente: Z"):
        m.transfer(factory, "A", "Z", 10)
    with pytest.raises(KeyError, match="conta inexistente: Z"):
        m.transfer(factory, "Z", "A", 10)
    assert balances() == {"A": 100_00, "B": 50_00}


def test_transfer_validates_before_opening_the_unit(world):
    m, factory, balances, _ = world
    calls = []

    def counting():
        calls.append(1)
        return factory()

    for bad in (0, -5, True, 1.5, "10"):
        with pytest.raises(ValueError, match="valor inválido"):
            m.transfer(counting, "A", "B", bad)
    with pytest.raises(ValueError, match="contas iguais"):
        m.transfer(counting, "A", "A", 10)
    assert calls == [] and balances() == {"A": 100_00, "B": 50_00}


def test_failure_between_the_two_saves_rolls_everything_back(world, monkeypatch):
    m, factory, balances, target = world
    original, count = target.save, []

    def flaky(self, account):
        count.append(1)
        if len(count) == 2:
            raise ConnectionError("a rede caiu na segunda gravação")
        return original(self, account)

    monkeypatch.setattr(target, "save", flaky)
    with pytest.raises(ConnectionError):
        m.transfer(factory, "A", "B", 40_00)
    assert len(count) == 2 and balances() == {"A": 100_00, "B": 50_00}


def test_without_commit_nothing_is_written(world):
    m, factory, balances, _ = world
    with factory() as uow:
        uow.accounts.save(replace(uow.accounts.get("A"), balance_cents=1))
        assert uow.accounts.get("A").balance_cents == 1               # dentro da unidade a mudança é visível...
    assert balances()["A"] == 100_00                                  # ...e ao sair sem commit, desfeita
    with pytest.raises(RuntimeError, match="boom"):
        with factory() as uow:
            uow.accounts.save(replace(uow.accounts.get("A"), balance_cents=2))
            uow.commit()
            raise RuntimeError("boom")                                # o commit já tinha acontecido: vale
    assert balances()["A"] == 2


def test_commit_outside_a_with(world):
    m, factory, _, _ = world
    uow = factory()
    with pytest.raises(RuntimeError, match="unit of work não iniciada"):
        uow.commit()
    with uow:
        pass
    with pytest.raises(RuntimeError, match="unit of work não iniciada"):
        uow.commit()
    with uow:                                                         # o mesmo objeto serve de novo
        uow.commit()


def test_sqlite_unit_closes_its_connection(load_exercise, tmp_path):
    m = load_exercise("ex02_unit_of_work")
    uow = m.SqliteUnitOfWork(str(tmp_path / "bank.db"))
    with uow as inside:
        assert inside is uow
        conn = uow.conn
        conn.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
    assert uow.conn is None


def test_in_memory_unit_works_on_a_copy(load_exercise):
    m = load_exercise("ex02_unit_of_work")
    store = {"A": m.Account("A", "Ana", 10)}
    with m.InMemoryUnitOfWork(store) as uow:
        uow.accounts.save(m.Account("A", "Ana", 99))
        uow.accounts.add(m.Account("B", "Bia", 1))
        assert store["A"].balance_cents == 10 and "B" not in store          # o store só muda no commit
        uow.commit()
    assert store["A"].balance_cents == 99 and store["B"].balance_cents == 1


# ---------- ex03 ----------
SCHEMA3 = """CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT UNIQUE);
CREATE TABLE books (id INTEGER PRIMARY KEY, author_id INTEGER, title TEXT);"""


def library(n_authors, books_per=2):
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA3)
    for i in range(n_authors, 0, -1):                                       # inseridos em ordem DECRESCENTE de nome
        conn.execute("INSERT INTO authors VALUES (?, ?)", (i, f"autor {i:04d}"))
        for k in range(books_per):
            conn.execute("INSERT INTO books (author_id, title) VALUES (?, ?)", (i, f"livro {i:04d}-{books_per - k}"))
    conn.commit()
    return conn


def test_query_counter(load_exercise):
    m = load_exercise("ex03_n_plus_one")
    conn = library(2)
    with m.QueryCounter(conn) as q:
        conn.execute("SELECT 1")
        conn.execute("   select 2  ")
        conn.execute("INSERT INTO authors VALUES (99, 'novo')")
        conn.execute("UPDATE authors SET name = 'x' WHERE id = 99")
    assert q.count == 2 and len(q.statements) == 2 and all(s.lstrip().upper().startswith("SELECT") for s in q.statements)
    conn.execute("SELECT 3")
    assert q.count == 2                                                       # o contador parou ao sair do with
    with pytest.raises(RuntimeError):
        with m.QueryCounter(conn) as q2:
            conn.execute("SELECT 1")
            raise RuntimeError("boom")
    assert q2.count == 1
    conn.execute("SELECT 4")
    assert q2.count == 1
    with m.QueryCounter(conn) as q3:
        pass
    assert q3.count == 0


def test_the_three_loaders_agree(load_exercise):
    m = load_exercise("ex03_n_plus_one")
    conn = library(5, books_per=3)
    conn.execute("INSERT INTO authors VALUES (100, 'autor sem livros')")
    conn.commit()
    expected = {f"autor {i:04d}": [f"livro {i:04d}-1", f"livro {i:04d}-2", f"livro {i:04d}-3"] for i in range(1, 6)}
    expected["autor sem livros"] = []
    for loader in (m.titles_naive, m.titles_in, m.titles_join):
        result = loader(conn)
        assert result == expected and list(result) == sorted(expected)
        assert all(titles == sorted(titles) for titles in result.values())


@pytest.mark.parametrize("n, naive, in_, join", [(0, 1, 1, 1), (3, 4, 2, 1), (500, 501, 2, 1), (501, 502, 3, 1), (1200, 1201, 4, 1)])
def test_query_counts(load_exercise, n, naive, in_, join):
    m = load_exercise("ex03_n_plus_one")
    conn = library(n, books_per=1)
    counts = {}
    results = {}
    for name, loader in (("naive", m.titles_naive), ("in", m.titles_in), ("join", m.titles_join)):
        with m.QueryCounter(conn) as q:
            results[name] = loader(conn)
        counts[name] = q.count
    assert counts == {"naive": naive, "in": in_, "join": join}
    assert results["naive"] == results["in"] == results["join"] and len(results["join"]) == n


# ---------- ex04 ----------
def items_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT NOT NULL, qty INTEGER NOT NULL)")
    conn.executemany("INSERT INTO items VALUES (?, ?, ?)", [(1, "caneta", 10), (2, "lápis", 20), (3, "borracha", 5)])
    conn.commit()
    return conn


def spy(conn):
    log = []
    conn.set_trace_callback(log.append)
    return log


def kind(log, prefix):
    return [s for s in log if s.startswith(prefix)]


def db_row(conn, item_id):
    return conn.execute("SELECT name, qty FROM items WHERE id = ?", (item_id,)).fetchone()


def test_identity_map(load_exercise):
    m = load_exercise("ex04_session_tracking")
    conn = items_conn()
    log = spy(conn)
    s = m.Session(conn)
    a = s.get(1)
    assert a == m.Item(1, "caneta", 10) and s.get(1) is a and s.get(1) is a
    assert len(kind(log, "SELECT")) == 1
    s.get(2)
    assert len(kind(log, "SELECT")) == 2
    with pytest.raises(KeyError, match="item inexistente: 99"):
        s.get(99)


def test_commit_writes_only_what_changed(load_exercise):
    m = load_exercise("ex04_session_tracking")
    conn = items_conn()
    s = m.Session(conn)
    a, b, c = s.get(1), s.get(2), s.get(3)
    assert s.dirty() == []
    a.qty -= 3
    assert s.dirty() == [1]
    log = spy(conn)
    s.commit()
    assert len(kind(log, "UPDATE")) == 1 and "caneta" in kind(log, "UPDATE")[0] and not kind(log, "INSERT") and not kind(log, "DELETE")
    assert db_row(conn, 1) == ("caneta", 7) and db_row(conn, 2) == ("lápis", 20) and s.dirty() == []
    log.clear()
    s.commit()
    assert not kind(log, "UPDATE")
    b.name = "lápis 2B"
    c.qty = 6
    assert s.dirty() == [2, 3]
    s.commit()
    assert len(kind(log, "UPDATE")) == 2 and db_row(conn, 2) == ("lápis 2B", 20) and db_row(conn, 3) == ("borracha", 6)


def test_change_and_revert_is_not_dirty(load_exercise):
    m = load_exercise("ex04_session_tracking")
    conn = items_conn()
    s = m.Session(conn)
    a = s.get(1)
    a.qty = 99
    assert s.dirty() == [1]
    a.qty = 10
    log = spy(conn)
    assert s.dirty() == []
    s.commit()
    assert not kind(log, "UPDATE")
    s.get(2).qty = 21                                                        # só o item carregado e mexido é gravado
    s.commit()
    assert len(kind(log, "UPDATE")) == 1 and db_row(conn, 1) == ("caneta", 10) and db_row(conn, 3) == ("borracha", 5)


def test_add_new_items(load_exercise):
    m = load_exercise("ex04_session_tracking")
    conn = items_conn()
    s = m.Session(conn)
    new = m.Item(10, "régua", 3)
    s.add(new)
    log = spy(conn)
    assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 3     # nada foi gravado ainda
    s.commit()
    assert len(kind(log, "INSERT")) == 1 and conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 4
    log.clear()
    assert s.get(10) is new and not kind(log, "SELECT")
    new.qty = 4
    assert s.dirty() == [10]
    s.commit()
    assert db_row(conn, 10) == ("régua", 4)
    with pytest.raises(ValueError, match="item já existe: 1"):
        s.add(m.Item(1, "outra", 1))                                          # existe no banco
    with pytest.raises(ValueError, match="item já existe: 10"):
        s.add(m.Item(10, "outra", 1))                                         # existe na sessão
    other = m.Session(conn)
    other.add(m.Item(11, "x", 1))
    with pytest.raises(ValueError, match="item já existe: 11"):
        other.add(m.Item(11, "y", 1))


def test_delete_items(load_exercise):
    m = load_exercise("ex04_session_tracking")
    conn = items_conn()
    s = m.Session(conn)
    a = s.get(1)
    s.delete(a)
    with pytest.raises(KeyError, match="item inexistente: 1"):
        s.get(1)
    assert db_row(conn, 1) == ("caneta", 10)                                  # ainda não foi apagado
    log = spy(conn)
    s.commit()
    assert len(kind(log, "DELETE")) == 1 and db_row(conn, 1) is None
    with pytest.raises(KeyError):
        s.get(1)
    with pytest.raises(ValueError, match="item não gerenciado"):
        s.delete(m.Item(2, "lápis", 20))                                      # igual, mas NÃO é o objeto da sessão
    s.get(2).qty = 0
    s.delete(s.get(2))
    log.clear()
    s.commit()
    assert not kind(log, "UPDATE") and len(kind(log, "DELETE")) == 1           # mudar e depois apagar: só o DELETE


def test_new_then_deleted_never_touches_the_database(load_exercise):
    m = load_exercise("ex04_session_tracking")
    conn = items_conn()
    s = m.Session(conn)
    new = m.Item(10, "régua", 3)
    s.add(new)
    s.delete(new)
    log = spy(conn)
    s.commit()
    assert not kind(log, "INSERT") and not kind(log, "DELETE") and db_row(conn, 10) is None


def test_commit_order_insert_update_delete(load_exercise):
    m = load_exercise("ex04_session_tracking")
    conn = items_conn()
    s = m.Session(conn)
    s.get(1).qty = 11
    s.delete(s.get(3))
    s.add(m.Item(10, "régua", 3))
    log = spy(conn)
    s.commit()
    writes = [x.split()[0] for x in log if x.split()[0] in ("INSERT", "UPDATE", "DELETE")]
    assert writes == ["INSERT", "UPDATE", "DELETE"]
    assert db_row(conn, 1) == ("caneta", 11) and db_row(conn, 3) is None and db_row(conn, 10) == ("régua", 3)


def test_rollback_forgets_everything(load_exercise):
    m = load_exercise("ex04_session_tracking")
    conn = items_conn()
    s = m.Session(conn)
    old = s.get(1)
    old.qty = 99
    s.add(m.Item(10, "régua", 3))
    s.delete(s.get(2))
    s.rollback()
    assert s.dirty() == [] and db_row(conn, 1) == ("caneta", 10) and db_row(conn, 10) is None
    fresh = s.get(1)
    assert fresh is not old and fresh.qty == 10 and old.qty == 99               # o objeto antigo ficou "solto"
    assert s.get(2).name == "lápis"
    log = spy(conn)
    s.commit()
    assert not kind(log, "UPDATE") and not kind(log, "INSERT") and not kind(log, "DELETE")


def test_context_manager(load_exercise):
    m = load_exercise("ex04_session_tracking")
    conn = items_conn()
    with m.Session(conn) as s:
        assert isinstance(s, m.Session)
        s.get(1).qty = 99
        s.commit()
    assert db_row(conn, 1) == ("caneta", 99)
    with m.Session(conn) as s:
        s.get(2).qty = 77                                                       # sem commit: descartado
        s.add(m.Item(10, "régua", 3))
    assert db_row(conn, 2) == ("lápis", 20) and db_row(conn, 10) is None
    log = spy(conn)
    with pytest.raises(RuntimeError, match="boom"):
        with m.Session(conn) as s:
            s.get(3).qty = 0
            raise RuntimeError("boom")
    assert not kind(log, "UPDATE") and db_row(conn, 3) == ("borracha", 5)
    assert s.dirty() == []                                                      # a saída por exceção fez rollback


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["repository_classico", "repository_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
