"""Exercício 4: o padrão Outbox transacional com SQLite."""
import sqlite3

SCHEMA = """
create table orders (id integer primary key, total integer not null);
create table outbox (id integer primary key autoincrement, topic text not null, body text not null, published integer not null default 0);
"""


def make_db() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.executescript(SCHEMA)
    return db


def place_order(db: sqlite3.Connection, order_id: int, total: int) -> None:
    """Grava o pedido E a linha de outbox (``topic="order_created"``, ``body=str(order_id)``) na MESMA transação: se qualquer uma
    falhar (pedido duplicado, total negativo -> ``ValueError``), NENHUMA fica gravada. ``total < 0`` levanta ``ValueError`` ANTES de
    tocar no banco; pedido repetido levanta ``sqlite3.IntegrityError`` e não deixa linha de outbox órfã."""
    raise NotImplementedError


def pending(db: sqlite3.Connection) -> int:
    """Quantas linhas de outbox ainda não foram publicadas."""
    raise NotImplementedError


def relay(db: sqlite3.Connection, publish, batch: int = 100) -> dict:
    """Publica até ``batch`` linhas pendentes, na ORDEM do ``id``, chamando ``publish(topic, body)`` e marcando cada uma
    como publicada SÓ DEPOIS de ``publish`` voltar sem exceção.

    * se ``publish`` levantar ``ConnectionError``, essa linha continua pendente e as seguintes TAMBÉM não são tentadas nesta
      rodada (para preservar a ordem): pare ali;
    * devolva ``{"sent": n, "failed": 0 ou 1, "pending": restantes}``."""
    raise NotImplementedError


def drain(db: sqlite3.Connection, publish, max_rounds: int = 50) -> int:
    """Roda ``relay`` até não haver pendentes (ou ``max_rounds`` rodadas) e devolve quantas rodadas fez."""
    raise NotImplementedError
