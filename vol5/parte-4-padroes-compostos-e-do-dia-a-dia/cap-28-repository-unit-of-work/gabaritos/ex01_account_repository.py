"""Gabarito do exercício 1."""
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass

SCHEMA = """CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY, owner TEXT NOT NULL, balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0))"""


@dataclass(frozen=True)
class Account:
    id: str
    owner: str
    balance_cents: int

    def __post_init__(self):
        if not self.id:
            raise ValueError("id vazio")
        if self.balance_cents < 0:
            raise ValueError("saldo negativo")


class AccountRepository(ABC):
    @abstractmethod
    def add(self, account): ...

    @abstractmethod
    def get(self, account_id): ...

    @abstractmethod
    def save(self, account): ...

    @abstractmethod
    def delete(self, account_id): ...

    @abstractmethod
    def list_all(self): ...

    @abstractmethod
    def with_balance_at_least(self, cents): ...

    @abstractmethod
    def count(self): ...


def _missing(account_id):
    return KeyError(f"conta inexistente: {account_id}")


class InMemoryAccountRepository(AccountRepository):
    def __init__(self, accounts=()):
        self._accounts = {}
        for account in accounts:
            self.add(account)

    def add(self, account):
        if account.id in self._accounts:
            raise ValueError(f"conta já existe: {account.id}")
        self._accounts[account.id] = account

    def get(self, account_id):
        try:
            return self._accounts[account_id]
        except KeyError:
            raise _missing(account_id) from None

    def save(self, account):
        self.get(account.id)
        self._accounts[account.id] = account

    def delete(self, account_id):
        self.get(account_id)
        del self._accounts[account_id]

    def list_all(self):
        return sorted(self._accounts.values(), key=lambda a: a.id)

    def with_balance_at_least(self, cents):
        return sorted((a for a in self._accounts.values() if a.balance_cents >= cents), key=lambda a: (-a.balance_cents, a.id))

    def count(self):
        return len(self._accounts)


class SqliteAccountRepository(AccountRepository):
    COLUMNS = "id, owner, balance_cents"

    def __init__(self, conn):
        self.conn = conn
        conn.execute(SCHEMA)

    def add(self, account):
        try:
            self.conn.execute("INSERT INTO accounts (id, owner, balance_cents) VALUES (?, ?, ?)", (account.id, account.owner, account.balance_cents))
        except sqlite3.IntegrityError:
            raise ValueError(f"conta já existe: {account.id}") from None

    def get(self, account_id):
        row = self.conn.execute(f"SELECT {self.COLUMNS} FROM accounts WHERE id = ?", (account_id,)).fetchone()
        if row is None:
            raise _missing(account_id)
        return Account(*row)

    def save(self, account):
        cursor = self.conn.execute("UPDATE accounts SET owner = ?, balance_cents = ? WHERE id = ?", (account.owner, account.balance_cents, account.id))
        if cursor.rowcount == 0:
            raise _missing(account.id)

    def delete(self, account_id):
        cursor = self.conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        if cursor.rowcount == 0:
            raise _missing(account_id)

    def list_all(self):
        return [Account(*row) for row in self.conn.execute(f"SELECT {self.COLUMNS} FROM accounts ORDER BY id")]

    def with_balance_at_least(self, cents):
        rows = self.conn.execute(f"SELECT {self.COLUMNS} FROM accounts WHERE balance_cents >= ? ORDER BY balance_cents DESC, id", (cents,))
        return [Account(*row) for row in rows]

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
