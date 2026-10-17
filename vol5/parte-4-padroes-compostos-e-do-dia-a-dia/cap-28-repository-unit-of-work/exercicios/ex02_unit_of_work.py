"""Exercício 2: a Unit of Work: "tudo ou nada" sobre sqlite e sobre memória, e uma transferência que não conhece nenhum dos dois."""
import sqlite3
from dataclasses import dataclass, replace

SCHEMA = """CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY, owner TEXT NOT NULL, balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0))"""


# ---- (Pronto, NÃO edite.) O domínio e os repositórios ----
@dataclass(frozen=True)
class Account:
    id: str
    owner: str
    balance_cents: int


class InsufficientFunds(Exception):
    pass


class InMemoryAccountRepository:
    def __init__(self, accounts: dict):
        self._accounts = accounts                           # um dicionário id -> Account (o "banco" desta unidade de trabalho)

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


# ---- Implemente a partir daqui ----
class SqliteUnitOfWork:
    """``SqliteUnitOfWork(path)``: um gerenciador de contexto sobre um arquivo sqlite.

    * ``__enter__``: abre uma conexão NOVA (``sqlite3.connect(path)``), cria ``self.conn`` e ``self.accounts`` (um ``SqliteAccountRepository``) e devolve ``self``;
    * ``commit()``: confirma (``conn.commit()``); fora de um ``with``: ``RuntimeError("unit of work não iniciada")``;
    * ``__exit__``: DESFAZ tudo o que não foi confirmado (``rollback``), FECHA a conexão, põe ``self.conn = None`` (assim ``commit()`` depois do ``with`` também é um ``RuntimeError``) e
      devolve ``False`` (a exceção, se houver, continua subindo);
    * sair do ``with`` sem ``commit()`` descarta as mudanças; o mesmo objeto pode ser usado em vários ``with`` (uma conexão nova a cada um)."""

    def __init__(self, path: str):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


class InMemoryUnitOfWork:
    """``InMemoryUnitOfWork(store)``: ``store`` é um dicionário ``id -> Account`` (o "banco" que sobrevive entre os ``with``).

    * ``__enter__``: trabalha em uma CÓPIA do ``store`` (``self.accounts`` é um ``InMemoryAccountRepository`` sobre a cópia) e devolve ``self``;
    * ``commit()``: o conteúdo da cópia substitui o do ``store`` (``store.clear()`` e ``store.update(...)``); fora de um ``with``: ``RuntimeError("unit of work não iniciada")``;
    * ``__exit__``: descarta a cópia e devolve ``False``; sair sem ``commit()`` não muda o ``store``."""

    def __init__(self, store: dict):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


def transfer(uow_factory, src_id: str, dst_id: str, amount_cents: int) -> tuple[int, int]:
    """Move ``amount_cents`` da conta ``src_id`` para ``dst_id`` com ``uow_factory()`` (uma função sem argumentos que devolve uma Unit of Work).

    * ANTES de abrir a unidade: ``amount_cents`` precisa ser um ``int`` ``> 0`` (``bool`` NÃO vale): ``ValueError("valor inválido")``; ``src_id == dst_id``: ``ValueError("contas iguais")``;
    * dentro de ``with uow_factory() as uow``: lê as duas contas (``KeyError`` se alguma não existe), ``InsufficientFunds(f"saldo insuficiente em {src_id}")`` se o saldo da origem é
      menor que o valor, grava a origem debitada e DEPOIS o destino creditado (``dataclasses.replace``), chama ``uow.commit()`` e devolve ``(novo_saldo_origem, novo_saldo_destino)``;
    * qualquer falha antes do ``commit`` deixa TUDO como estava (a Unit of Work cuida disso; a função não tem ``try``/``rollback``)."""
    raise NotImplementedError
