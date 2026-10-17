"""Repository e Unit of Work em Python: a coleção que parece um dict, o `with conn`, o @contextmanager, o rastreamento de mudanças, o teste de contrato e o N+1."""
import sqlite3
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path

SCHEMA = """CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY, owner TEXT NOT NULL, balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0))"""


@dataclass(frozen=True)
class Account:
    id: str
    owner: str
    balance_cents: int


# --- 1. o repositório que se comporta como uma COLEÇÃO Python ---
class AccountBook:
    def __init__(self, accounts=()):
        self._by_id = {a.id: a for a in accounts}

    def add(self, account):
        if account.id in self._by_id:
            raise ValueError(f"conta já existe: {account.id}")
        self._by_id[account.id] = account

    def __getitem__(self, account_id):
        return self._by_id[account_id]                      # KeyError: o erro que o Python já usa para "chave inexistente"

    def __setitem__(self, account_id, account):
        if account_id not in self._by_id:
            raise KeyError(account_id)
        self._by_id[account_id] = account

    def __contains__(self, account_id):
        return account_id in self._by_id

    def __iter__(self):
        return iter(sorted(self._by_id.values(), key=lambda a: a.id))

    def __len__(self):
        return len(self._by_id)

    def with_balance_at_least(self, cents):                 # a consulta tem NOME DE NEGÓCIO, não é um SQL solto
        return [a for a in self if a.balance_cents >= cents]


book = AccountBook([Account("B", "Bia", 50_00), Account("A", "Ana", 120_00)])
book["B"] = replace(book["B"], balance_cents=60_00)
print("coleção:", [a.id for a in book], "| 'A' in book:", "A" in book, "| len:", len(book), "| rica (>= 100,00):", [a.owner for a in book.with_balance_at_least(100_00)])


# --- 2. a Unit of Work em 8 linhas: um @contextmanager e o `with conn` do sqlite3 ---
class SqliteAccounts:
    def __init__(self, conn):
        self.conn = conn

    def add(self, a):
        self.conn.execute("INSERT INTO accounts VALUES (?, ?, ?)", (a.id, a.owner, a.balance_cents))

    def get(self, account_id):
        row = self.conn.execute("SELECT id, owner, balance_cents FROM accounts WHERE id = ?", (account_id,)).fetchone()
        if row is None:
            raise KeyError(f"conta inexistente: {account_id}")
        return Account(*row)

    def save(self, a):
        self.conn.execute("UPDATE accounts SET owner = ?, balance_cents = ? WHERE id = ?", (a.owner, a.balance_cents, a.id))


@contextmanager
def unit_of_work(path):
    conn = sqlite3.connect(path)
    try:
        with conn:                                          # a conexão É um gerenciador de contexto: commit se o bloco termina, rollback se levanta
            yield SqliteAccounts(conn)
    finally:
        conn.close()


tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
DB = str(Path(tmp.name) / "bank.db")
setup = sqlite3.connect(DB)
setup.execute(SCHEMA)
setup.commit()
setup.close()

with unit_of_work(DB) as accounts:
    accounts.add(Account("A", "Ana", 100_00))
    accounts.add(Account("B", "Bia", 100_00))
try:
    with unit_of_work(DB) as accounts:
        accounts.save(replace(accounts.get("A"), balance_cents=0))
        raise ConnectionError("a rede caiu")
except ConnectionError:
    pass
with unit_of_work(DB) as accounts:
    print("\n@contextmanager + `with conn`: depois de uma falha, A =", accounts.get("A").balance_cents, "(rollback automático; sem 'try/commit/except/rollback' na regra de negócio)")

# --- 3. o rastreamento de mudanças: só grava o que mudou ---
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, qty INTEGER)")
conn.executemany("INSERT INTO items VALUES (?, ?, ?)", [(1, "caneta", 10), (2, "lápis", 20), (3, "borracha", 5)])
conn.commit()


@dataclass
class Item:
    id: int
    name: str
    qty: int


class Session:
    """Um "mapa de identidade" (cada linha vira UM objeto) e um instantâneo de cada objeto lido: o commit grava SÓ as diferenças."""

    def __init__(self, conn):
        self.conn, self._identity, self._snapshots = conn, {}, {}

    def get(self, item_id):
        if item_id in self._identity:
            return self._identity[item_id]                  # já carregado: nenhuma consulta nova, e o MESMO objeto
        row = self.conn.execute("SELECT id, name, qty FROM items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise KeyError(f"item inexistente: {item_id}")
        item = Item(*row)
        self._identity[item_id], self._snapshots[item_id] = item, (item.name, item.qty)
        return item

    def commit(self):
        for item_id, item in self._identity.items():
            if (item.name, item.qty) != self._snapshots[item_id]:
                self.conn.execute("UPDATE items SET name = ?, qty = ? WHERE id = ?", (item.name, item.qty, item_id))
                self._snapshots[item_id] = (item.name, item.qty)
        self.conn.commit()


statements = []
conn.set_trace_callback(statements.append)
session = Session(conn)
a, b, c = session.get(1), session.get(2), session.get(3)
again = session.get(1)
a.qty -= 3                                                  # mexe em UM objeto; não existe `save()` explícito
session.commit()
conn.set_trace_callback(None)
reads = [s for s in statements if s.startswith("SELECT")]
writes = [s for s in statements if s.startswith("UPDATE")]
print(f"\nSession: 4 chamadas de get() -> {len(reads)} SELECT (o 4º veio do mapa de identidade; mesmo objeto: {again is a}) | 1 objeto alterado -> {len(writes)} UPDATE:", writes[0])


# --- 4. o teste de CONTRATO: a mesma verificação para qualquer repositório ---
def check_contract(make_repo):
    repo = make_repo()
    repo.add(Account("A", "Ana", 10_00))
    assert repo.get("A") == Account("A", "Ana", 10_00)
    repo.save(replace(repo.get("A"), balance_cents=99))
    assert repo.get("A").balance_cents == 99
    try:
        repo.get("Z")
    except KeyError as error:
        assert "inexistente" in str(error)
    else:
        raise AssertionError("deveria levantar KeyError")
    return "ok"


class InMemoryAccounts:
    def __init__(self):
        self._d = {}

    def add(self, a):
        self._d[a.id] = a

    def get(self, account_id):
        try:
            return self._d[account_id]
        except KeyError:
            raise KeyError(f"conta inexistente: {account_id}") from None

    def save(self, a):
        self._d[a.id] = a


def make_sqlite():
    conn = sqlite3.connect(":memory:")
    conn.execute(SCHEMA)
    return SqliteAccounts(conn)


print("\nteste de contrato (mesmo roteiro):", {"em memória": check_contract(InMemoryAccounts), "sqlite": check_contract(make_sqlite)}, "| o repositório falso só serve se o teste PROVA que ele se comporta como o de verdade")

# --- 5. o N+1: consultar dentro de um laço ---
db = sqlite3.connect(":memory:")
db.executescript("""
    CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE books (id INTEGER PRIMARY KEY, author_id INTEGER, title TEXT);
    CREATE INDEX books_author ON books (author_id);
""")
db.executemany("INSERT INTO authors VALUES (?, ?)", [(i, f"autor {i:03d}") for i in range(200)])
db.executemany("INSERT INTO books (author_id, title) VALUES (?, ?)", [(i, f"livro {i}-{k}") for i in range(200) for k in range(5)])
db.commit()


def n_plus_one():
    out = {}
    for author_id, name in db.execute("SELECT id, name FROM authors").fetchall():                                  # 1 consulta...
        out[name] = [t for (t,) in db.execute("SELECT title FROM books WHERE author_id = ? ORDER BY title", (author_id,))]   # ...e mais N
    return out


def with_join():
    out = {}
    for name, title in db.execute("SELECT a.name, b.title FROM authors a LEFT JOIN books b ON b.author_id = a.id ORDER BY a.id, b.title"):   # 1 consulta
        out.setdefault(name, []).append(title)
    return out


def count_selects(fn):
    log = []
    db.set_trace_callback(log.append)
    fn()
    db.set_trace_callback(None)
    return sum(1 for s in log if s.startswith("SELECT"))


def ms(fn, n=20):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1000


assert n_plus_one() == with_join()
print(f"\n200 autores com 5 livros cada | N+1: {count_selects(n_plus_one)} consultas, {ms(n_plus_one):5.2f} ms | JOIN: {count_selects(with_join)} consulta, {ms(with_join):5.2f} ms")
print("(em um banco em memória cada consulta é barata; em um banco de rede, cada uma custa uma viagem de ~1 ms: 201 viagens contra 1)")

db.close()
conn.close()
tmp.cleanup()
