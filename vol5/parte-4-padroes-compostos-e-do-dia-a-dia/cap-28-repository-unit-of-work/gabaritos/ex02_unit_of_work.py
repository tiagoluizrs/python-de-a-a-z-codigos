"""Gabarito do exercício 2."""
import sqlite3
from dataclasses import dataclass, replace

SCHEMA = """CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY, owner TEXT NOT NULL, balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0))"""


@dataclass(frozen=True)
class Account:
    id: str
    owner: str
    balance_cents: int


class InsufficientFunds(Exception):
    pass


class InMemoryAccountRepository:
    def __init__(self, accounts):
        self._accounts = accounts

    def add(self, account):
        if account.id in self._accounts:
            raise ValueError(f"conta já existe: {account.id}")
        self._accounts[account.id] = account

    def get(self, account_id):
        try:
            return self._accounts[account_id]
        except KeyError:
            raise KeyError(f"conta inexistente: {account_id}") from None

    def save(self, account):
        self.get(account.id)
        self._accounts[account.id] = account


class SqliteAccountRepository:
    def __init__(self, conn):
        self.conn = conn
        conn.execute(SCHEMA)

    def add(self, account):
        try:
            self.conn.execute("INSERT INTO accounts VALUES (?, ?, ?)", (account.id, account.owner, account.balance_cents))
        except sqlite3.IntegrityError:
            raise ValueError(f"conta já existe: {account.id}") from None

    def get(self, account_id):
        row = self.conn.execute("SELECT id, owner, balance_cents FROM accounts WHERE id = ?", (account_id,)).fetchone()
        if row is None:
            raise KeyError(f"conta inexistente: {account_id}")
        return Account(*row)

    def save(self, account):
        self.get(account.id)
        self.conn.execute("UPDATE accounts SET owner = ?, balance_cents = ? WHERE id = ?", (account.owner, account.balance_cents, account.id))


class SqliteUnitOfWork:
    def __init__(self, path):
        self.path = path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.accounts = SqliteAccountRepository(self.conn)
        return self

    def commit(self):
        if self.conn is None:
            raise RuntimeError("unit of work não iniciada")
        self.conn.commit()

    def __exit__(self, exc_type, exc, tb):
        self.conn.rollback()
        self.conn.close()
        self.conn = None
        return False


class InMemoryUnitOfWork:
    def __init__(self, store):
        self.store = store
        self._working = None

    def __enter__(self):
        self._working = dict(self.store)
        self.accounts = InMemoryAccountRepository(self._working)
        return self

    def commit(self):
        if self._working is None:
            raise RuntimeError("unit of work não iniciada")
        self.store.clear()
        self.store.update(self._working)

    def __exit__(self, exc_type, exc, tb):
        self._working = None
        return False


def transfer(uow_factory, src_id, dst_id, amount_cents):
    if not isinstance(amount_cents, int) or isinstance(amount_cents, bool) or amount_cents <= 0:
        raise ValueError("valor inválido")
    if src_id == dst_id:
        raise ValueError("contas iguais")
    with uow_factory() as uow:
        src, dst = uow.accounts.get(src_id), uow.accounts.get(dst_id)
        if src.balance_cents < amount_cents:
            raise InsufficientFunds(f"saldo insuficiente em {src_id}")
        src = replace(src, balance_cents=src.balance_cents - amount_cents)
        dst = replace(dst, balance_cents=dst.balance_cents + amount_cents)
        uow.accounts.save(src)
        uow.accounts.save(dst)
        uow.commit()
        return src.balance_cents, dst.balance_cents
