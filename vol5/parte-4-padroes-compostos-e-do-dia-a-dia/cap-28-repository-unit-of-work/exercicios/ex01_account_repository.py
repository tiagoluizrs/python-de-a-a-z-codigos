"""Exercício 1: o Repository: duas implementações (memória e sqlite) com o MESMO contrato; os testes rodam o mesmo roteiro nas duas."""
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass

SCHEMA = """CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY, owner TEXT NOT NULL, balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0))"""


@dataclass(frozen=True)
class Account:
    """(Pronto, NÃO edite.) Uma conta. ``id`` vazio: ``ValueError("id vazio")``; ``balance_cents`` negativo: ``ValueError("saldo negativo")``."""

    id: str
    owner: str
    balance_cents: int

    def __post_init__(self):
        if not self.id:
            raise ValueError("id vazio")
        if self.balance_cents < 0:
            raise ValueError("saldo negativo")


class AccountRepository(ABC):
    """(Pronto, NÃO edite.) O contrato: uma COLEÇÃO de contas que não revela onde elas vivem."""

    @abstractmethod
    def add(self, account: Account) -> None: ...

    @abstractmethod
    def get(self, account_id: str) -> Account: ...

    @abstractmethod
    def save(self, account: Account) -> None: ...

    @abstractmethod
    def delete(self, account_id: str) -> None: ...

    @abstractmethod
    def list_all(self) -> list[Account]: ...

    @abstractmethod
    def with_balance_at_least(self, cents: int) -> list[Account]: ...

    @abstractmethod
    def count(self) -> int: ...


class InMemoryAccountRepository(AccountRepository):
    """Guarda as contas em um dicionário. ``InMemoryAccountRepository(accounts=())``: as contas iniciais entram por ``add`` (id repetido sobe o erro do ``add``).

    O CONTRATO (igual ao do sqlite):

    * ``add(account)``: id repetido: ``ValueError(f"conta já existe: {id}")``;
    * ``get(id)``: a conta, ou ``KeyError(f"conta inexistente: {id}")``;
    * ``save(account)``: troca a conta de mesmo ``id`` (``owner`` e saldo); conta que não existe: o mesmo ``KeyError`` do ``get``;
    * ``delete(id)``: apaga; conta que não existe: o mesmo ``KeyError``;
    * ``list_all()``: todas, ordenadas por ``id``; ``with_balance_at_least(cents)``: as de saldo ``>= cents``, ordenadas por saldo DECRESCENTE e, no empate, por ``id``;
    * ``count()``: quantas contas existem."""

    def __init__(self, accounts=()):
        raise NotImplementedError

    def add(self, account: Account) -> None:
        raise NotImplementedError

    def get(self, account_id: str) -> Account:
        raise NotImplementedError

    def save(self, account: Account) -> None:
        raise NotImplementedError

    def delete(self, account_id: str) -> None:
        raise NotImplementedError

    def list_all(self) -> list[Account]:
        raise NotImplementedError

    def with_balance_at_least(self, cents: int) -> list[Account]:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError


class SqliteAccountRepository(AccountRepository):
    """O mesmo contrato, sobre uma conexão ``sqlite3``. ``SqliteAccountRepository(conn)`` executa ``SCHEMA`` (``CREATE TABLE IF NOT EXISTS``) e guarda a conexão.

    * TODO valor que vem de fora entra como PARÂMETRO (``?``), nunca colado no texto do SQL (um ``id`` como ``"x'; DROP TABLE accounts; --"`` é só um ``id`` esquisito);
    * o repositório NÃO dá ``commit`` (nem ``rollback``): confirmar é papel da Unit of Work (outra conexão não enxerga as mudanças até alguém chamar ``conn.commit()``);
    * ``add``: o ``sqlite3.IntegrityError`` de chave repetida vira ``ValueError(f"conta já existe: {id}")``;
    * ``save``/``delete``: se nenhuma linha foi afetada (``cursor.rowcount == 0``), ``KeyError(f"conta inexistente: {id}")``;
    * os métodos de leitura devolvem objetos ``Account`` (não tuplas), nas mesmas ordens do repositório em memória."""

    def __init__(self, conn: sqlite3.Connection):
        raise NotImplementedError

    def add(self, account: Account) -> None:
        raise NotImplementedError

    def get(self, account_id: str) -> Account:
        raise NotImplementedError

    def save(self, account: Account) -> None:
        raise NotImplementedError

    def delete(self, account_id: str) -> None:
        raise NotImplementedError

    def list_all(self) -> list[Account]:
        raise NotImplementedError

    def with_balance_at_least(self, cents: int) -> list[Account]:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError
