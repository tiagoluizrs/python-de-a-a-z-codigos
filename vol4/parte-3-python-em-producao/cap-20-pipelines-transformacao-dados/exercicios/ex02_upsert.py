"""Exercício 2: cargas idempotentes no SQLite: upsert protegido contra dados fora de ordem e sobrescrita de partição."""
import sqlite3


def make_db() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.execute("create table sales (order_id integer primary key, day text not null, total real not null, updated_at text not null)")
    return db


def upsert(db: sqlite3.Connection, rows: list[dict]) -> dict:
    """Carrega ``rows`` (dicts com ``order_id``, ``day``, ``total`` e ``updated_at`` em ISO) com ``INSERT ... ON CONFLICT(order_id)
    DO UPDATE`` e devolve ``{"inserted": a, "updated": b, "ignored": c}``:

    * ``order_id`` novo: ``inserted``;
    * ``order_id`` que já existe e a linha nova tem ``updated_at`` ESTRITAMENTE MAIOR que a gravada: ``updated`` (os campos mudam);
    * ``order_id`` que já existe com ``updated_at`` igual ou menor (dado repetido ou fora de ordem): ``ignored`` (nada muda);
    * se o MESMO ``order_id`` aparece mais de uma vez em ``rows``, valem as regras acima na ordem em que aparecem;
    * tudo em UMA transação (se algo falhar no meio, nada fica gravado: ``total`` ``None`` levanta ``sqlite3.IntegrityError``).
    Dica: compare ``db.total_changes`` antes e depois de cada linha, ou consulte a linha antes."""
    raise NotImplementedError


def replace_partition(db: sqlite3.Connection, day: str, rows: list[dict]) -> int:
    """Sobrescreve a PARTIÇÃO de um dia: apaga TODAS as linhas de ``sales`` com ``day == day`` e insere ``rows`` (que devem ser
    todas desse dia: se alguma tiver outro ``day``, levante ``ValueError`` ANTES de tocar no banco), tudo em UMA transação (se a
    inserção falhar, as linhas antigas voltam). Devolve quantas linhas o dia tem DEPOIS. Dias diferentes não são afetados."""
    raise NotImplementedError


def totals_by_day(db: sqlite3.Connection) -> dict[str, tuple[int, float]]:
    """``{dia: (quantidade de linhas, soma de total)}`` em ordem de dia (a soma arredondada a 2 casas)."""
    raise NotImplementedError
