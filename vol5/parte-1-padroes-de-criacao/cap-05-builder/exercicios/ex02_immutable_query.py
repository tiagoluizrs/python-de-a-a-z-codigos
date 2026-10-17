"""Exercício 2: um builder IMUTÁVEL de consultas SQL parametrizadas (cada passo devolve uma consulta NOVA)."""
from dataclasses import dataclass, replace

ALLOWED = {"users": {"id", "name", "age", "city"}, "orders": {"id", "user_id", "total", "status"}}


@dataclass(frozen=True)
class Select:
    """``Select("users")`` começa com todas as colunas (``*``). Tabela fora de ``ALLOWED``: ``ValueError(f"tabela desconhecida: {nome}")`` (na
    criação, ``__post_init__``). Campos: ``table``, ``columns=("*",)``, ``conditions=()``, ``params=()``, ``order=()``, ``max_rows=None``,
    ``skip=0``.

    Todos os métodos devolvem um NOVO ``Select`` (use ``dataclasses.replace``) e validam NOMES pela lista de permissão
    (``ValueError(f"coluna desconhecida: {nome}")``); VALORES vão sempre como parâmetros (``?``), nunca no texto do SQL:

    * ``columns_(*names)``: as colunas do SELECT (o sublinhado evita o conflito com o campo);
    * ``where(column, op, value)``: ``op`` em ``= != < <= > >=`` (outro: ``ValueError(f"operador inválido: {op}")``); condição ``"coluna op ?"``;
    * ``where_in(column, values)``: condição ``"coluna IN (?, ?, ?)"`` (um ``?`` por valor); ``values`` vazio: ``ValueError("lista vazia")``;
    * ``order_by(column, descending=False)``: acrescenta ``"coluna ASC"`` ou ``"coluna DESC"``;
    * ``limit(n)`` e ``offset(n)``: inteiros ``>= 0`` (``n < 0``: ``ValueError("valor negativo")``); ``int(n)`` aplicado;
    * ``build()``: devolve ``(sql, params)``. SQL: ``SELECT colunas FROM tabela`` + `` WHERE c1 AND c2`` + `` ORDER BY o1, o2`` + `` LIMIT n`` +
      `` OFFSET n`` (cada parte só se houver; ``OFFSET`` só se ``skip > 0``; um ``OFFSET`` sem ``LIMIT`` usa ``LIMIT -1``)."""

    table: str
    columns: tuple = ("*",)
    conditions: tuple = ()
    params: tuple = ()
    order: tuple = ()
    max_rows: int | None = None
    skip: int = 0

    def __post_init__(self):
        raise NotImplementedError

    def columns_(self, *names: str) -> "Select":
        raise NotImplementedError

    def where(self, column: str, op: str, value) -> "Select":
        raise NotImplementedError

    def where_in(self, column: str, values) -> "Select":
        raise NotImplementedError

    def order_by(self, column: str, descending: bool = False) -> "Select":
        raise NotImplementedError

    def limit(self, n: int) -> "Select":
        raise NotImplementedError

    def offset(self, n: int) -> "Select":
        raise NotImplementedError

    def build(self) -> tuple[str, tuple]:
        raise NotImplementedError
