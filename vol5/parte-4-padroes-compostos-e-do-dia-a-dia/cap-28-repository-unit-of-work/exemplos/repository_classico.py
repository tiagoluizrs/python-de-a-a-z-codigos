"""Repository e Unit of Work, forma clássica: esconder ONDE os dados vivem atrás de uma coleção e agrupar várias mudanças em UMA transação."""
import ast
import inspect
import sqlite3
import tempfile
import textwrap
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from pathlib import Path

SCHEMA = """CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY, owner TEXT NOT NULL, balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0))"""


@dataclass(frozen=True)
class Account:
    id: str
    owner: str
    balance_cents: int

    def __post_init__(self):
        if self.balance_cents < 0:
            raise ValueError("saldo negativo")


class InsufficientFunds(Exception):
    pass


def make_db(path):
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA)
    conn.executemany("INSERT INTO accounts VALUES (?, ?, ?)", [("A", "Ana", 100_00), ("B", "Bia", 100_00)])
    conn.commit()
    conn.close()


def total_in_db(path):
    conn = sqlite3.connect(path)
    try:
        return conn.execute("SELECT SUM(balance_cents) FROM accounts").fetchone()[0]
    finally:
        conn.close()


tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
DB = str(Path(tmp.name) / "bank.db")
make_db(DB)


# --- 1. o problema: SQL dentro da regra de negócio, e commits "para garantir" ---
def transfer_naive(path, src, dst, amount, crash=False):
    conn = sqlite3.connect(path)
    conn.execute(f"UPDATE accounts SET balance_cents = balance_cents - {amount} WHERE id = '{src}'")     # SQL colado em texto
    conn.commit()                                                                                         # "para garantir"
    if crash:
        raise ConnectionError("a rede caiu no meio")
    conn.execute(f"UPDATE accounts SET balance_cents = balance_cents + {amount} WHERE id = '{dst}'")
    conn.commit()
    conn.close()


before = total_in_db(DB)
try:
    transfer_naive(DB, "A", "B", 50_00, crash=True)
except ConnectionError:
    pass
print(f"transferência ingênua com falha no meio: total antes {before / 100:.2f} | depois {total_in_db(DB) / 100:.2f} | R$ 50,00 sumiram (debitou, não creditou)")
reset = sqlite3.connect(DB)
reset.execute("UPDATE accounts SET balance_cents = 10000")                  # volta ao saldo inicial para o próximo experimento
reset.commit()
reset.close()


# --- 2. o Repository: uma COLEÇÃO de contas; a regra de negócio não sabe de SQL ---
class AccountRepository(ABC):
    @abstractmethod
    def add(self, account): ...

    @abstractmethod
    def get(self, account_id): ...

    @abstractmethod
    def save(self, account): ...


class InMemoryAccountRepository(AccountRepository):
    def __init__(self, accounts=()):
        self._accounts = {a.id: a for a in accounts}

    def add(self, account):
        self._accounts[account.id] = account

    def get(self, account_id):
        try:
            return self._accounts[account_id]
        except KeyError:
            raise KeyError(f"conta inexistente: {account_id}") from None

    def save(self, account):
        self.get(account.id)
        self._accounts[account.id] = account


class SqliteAccountRepository(AccountRepository):
    def __init__(self, conn):
        self.conn = conn                                    # o repositório NÃO dá commit: isso é papel da Unit of Work

    def add(self, account):
        self.conn.execute("INSERT INTO accounts VALUES (?, ?, ?)", (account.id, account.owner, account.balance_cents))

    def get(self, account_id):
        row = self.conn.execute("SELECT id, owner, balance_cents FROM accounts WHERE id = ?", (account_id,)).fetchone()
        if row is None:
            raise KeyError(f"conta inexistente: {account_id}")
        return Account(*row)

    def save(self, account):
        self.get(account.id)
        self.conn.execute("UPDATE accounts SET owner = ?, balance_cents = ? WHERE id = ?", (account.owner, account.balance_cents, account.id))


def transfer(repo, src_id, dst_id, amount):
    """A regra de negócio: sem uma linha de SQL, funciona com QUALQUER repositório."""
    src, dst = repo.get(src_id), repo.get(dst_id)
    if src.balance_cents < amount:
        raise InsufficientFunds(f"saldo insuficiente em {src_id}")
    repo.save(replace(src, balance_cents=src.balance_cents - amount))
    repo.save(replace(dst, balance_cents=dst.balance_cents + amount))


fake = InMemoryAccountRepository([Account("A", "Ana", 100_00), Account("B", "Bia", 100_00)])
transfer(fake, "A", "B", 30_00)
print("\nregra de negócio com repositório em memória (sem banco, sem arquivo):", fake.get("A").balance_cents, fake.get("B").balance_cents)
try:
    transfer(fake, "A", "B", 999_00)
except InsufficientFunds as error:
    print("  regra recusa:", error)


class FlakyRepository(InMemoryAccountRepository):
    """Falha na SEGUNDA gravação: o repositório sozinho não garante a atomicidade."""

    def __init__(self, accounts):
        super().__init__(accounts)
        self.saves = 0

    def save(self, account):
        self.saves += 1
        if self.saves == 2:
            raise ConnectionError("falhou na segunda gravação")
        super().save(account)


flaky = FlakyRepository([Account("A", "Ana", 100_00), Account("B", "Bia", 100_00)])
try:
    transfer(flaky, "A", "B", 40_00)
except ConnectionError:
    pass
print("repositório sozinho, falha na segunda gravação:", flaky.get("A").balance_cents + flaky.get("B").balance_cents, "centavos no total (eram 20000): faltam 4000; é para isso que existe a Unit of Work")


# --- 3. a Unit of Work: tudo ou nada ---
class SqliteUnitOfWork:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.accounts = SqliteAccountRepository(self.conn)
        return self

    def commit(self):
        self.conn.commit()

    def __exit__(self, exc_type, exc, tb):
        self.conn.rollback()                                # o que não foi confirmado (commit) é DESFEITO, com ou sem exceção
        self.conn.close()
        return False                                        # a exceção continua subindo


class InMemoryUnitOfWork:
    def __init__(self, store):
        self.store = store                                  # o "banco": um dicionário compartilhado

    def __enter__(self):
        self._working = dict(self.store)                    # trabalha em uma CÓPIA
        self.accounts = InMemoryAccountRepository(self._working.values())
        return self

    def commit(self):
        self.store.clear()
        self.store.update(self.accounts._accounts)          # confirma: a cópia vira o banco

    def __exit__(self, exc_type, exc, tb):
        return False                                        # sem commit, a cópia é simplesmente descartada


def transfer_uow(uow_factory, src_id, dst_id, amount, crash=False):
    with uow_factory() as uow:
        transfer(uow.accounts, src_id, dst_id, amount)
        if crash:
            raise ConnectionError("a rede caiu antes do commit")
        uow.commit()


try:
    transfer_uow(lambda: SqliteUnitOfWork(DB), "A", "B", 40_00, crash=True)
except ConnectionError:
    pass
print(f"\nUnit of Work (sqlite), falha antes do commit: total {total_in_db(DB) / 100:.2f} (rollback: nada mudou)")
transfer_uow(lambda: SqliteUnitOfWork(DB), "A", "B", 40_00)
conn = sqlite3.connect(DB)
print("Unit of Work, sucesso:", conn.execute("SELECT id, balance_cents FROM accounts ORDER BY id").fetchall())
conn.close()

store = {a.id: a for a in (Account("A", "Ana", 100_00), Account("B", "Bia", 100_00))}
try:
    transfer_uow(lambda: InMemoryUnitOfWork(store), "A", "B", 40_00, crash=True)
except ConnectionError:
    pass
print("mesma função, Unit of Work em memória, falha antes do commit:", {k: v.balance_cents for k, v in store.items()}, "(intacto)")
transfer_uow(lambda: InMemoryUnitOfWork(store), "A", "B", 40_00)
print("e com sucesso:", {k: v.balance_cents for k, v in store.items()})

# --- 4. a injeção de SQL: parâmetros, nunca texto colado ---
memory = sqlite3.connect(":memory:")
memory.execute(SCHEMA)
memory.executemany("INSERT INTO accounts VALUES (?, ?, ?)", [("A", "Ana", 1), ("B", "Bia", 2)])
hostile = "x' OR '1'='1"
leaky = memory.execute(f"SELECT id FROM accounts WHERE id = '{hostile}'").fetchall()
safe = memory.execute("SELECT id FROM accounts WHERE id = ?", (hostile,)).fetchall()
print("\nid hostil", repr(hostile), "| SQL em texto devolve:", leaky, "(TODAS as contas) | com parâmetro:", safe)


# --- 5. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\ningênuo:", measure([transfer_naive]), "| Repository + Unit of Work (3 classes de repositório + 2 UoW + transfer + transfer_uow):",
      measure([AccountRepository, InMemoryAccountRepository, SqliteAccountRepository, transfer, SqliteUnitOfWork, InMemoryUnitOfWork, transfer_uow]))

ROWS = 300


def insert_commit_each(path):
    conn = sqlite3.connect(path)
    for i in range(ROWS):
        conn.execute("INSERT INTO accounts VALUES (?, ?, ?)", (f"R{i}", "x", 1))
        conn.commit()
    conn.close()


def insert_one_transaction(path):
    conn = sqlite3.connect(path)
    conn.executemany("INSERT INTO accounts VALUES (?, ?, ?)", [(f"T{i}", "x", 1) for i in range(ROWS)])
    conn.commit()
    conn.close()


def timed(fn, *args):
    start = time.perf_counter()
    fn(*args)
    return (time.perf_counter() - start) * 1000


print(f"inserir {ROWS} linhas em arquivo: um commit por linha {timed(insert_commit_each, DB):7.1f} ms | uma transação só {timed(insert_one_transaction, DB):6.1f} ms")
conn = sqlite3.connect(DB)
repo = SqliteAccountRepository(conn)
mem = InMemoryAccountRepository(Account(f"R{i}", "x", 1) for i in range(ROWS))


def best(fn, n=2_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


print(f"get(): sqlite (arquivo) {best(lambda: repo.get('R10')):6.1f} µs | em memória {best(lambda: mem.get('R10')):6.2f} µs")
conn.close()
tmp.cleanup()
