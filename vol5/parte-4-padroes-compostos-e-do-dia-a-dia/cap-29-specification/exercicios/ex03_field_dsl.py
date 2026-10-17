"""Exercício 3: um DSL de campos (``F.age >= 18``) que vira uma regra em Python E um trecho de SQL, com a lógica de TRÊS valores do NULL (as duas versões dão o MESMO resultado)."""
import operator

COLUMNS = {"id", "name", "age", "country", "vip", "banned"}               # (Pronto.) a lista de permissão: só estes nomes viram SQL
OPS = {"==": operator.eq, "!=": operator.ne, "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
SQL_OPS = {"==": "=", "!=": "<>"}                                          # os outros operadores têm o mesmo texto em SQL


class Spec3:
    """A base das regras. Uma regra tem ``evaluate(row)``, que devolve ``True``, ``False`` ou ``None`` (DESCONHECIDO), e ``to_sql()``, que devolve ``(clausula, parametros)``.
    ``row`` é um dicionário; coluna ausente ou com ``None`` é DESCONHECIDA.

    * ``a & b``, ``a | b`` e ``~a`` criam ``And(a, b)``, ``Or(a, b)`` e ``Not(a)``;
    * ``spec(row)`` devolve ``True`` só se ``evaluate(row) is True`` (desconhecido NÃO satisfaz, como uma linha com NULL no ``WHERE``)."""

    def __and__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError

    def __invert__(self):
        raise NotImplementedError

    def __call__(self, row) -> bool:
        raise NotImplementedError


class Cmp(Spec3):
    """``Cmp(column, op, value)`` (``op`` é uma chave de ``OPS``).

    * ``value`` ``None``: ``ValueError("use is_null() para comparar com NULL")``;
    * ``evaluate``: ``None`` se ``row.get(column)`` é ``None``; senão o resultado de ``OPS[op](valor_da_linha, value)``;
    * ``to_sql()``: ``(f"{column} {operador_sql} ?", (value,))``, com ``SQL_OPS.get(op, op)``; ``repr``: ``f"{column} {op} {value!r}"``."""

    def __init__(self, column: str, op: str, value):
        raise NotImplementedError


class IsNull(Spec3):
    """``IsNull(column)``: ``evaluate`` é ``True`` se ``row.get(column) is None`` e ``False`` senão (NUNCA ``None``); ``to_sql()``: ``(f"{column} IS NULL", ())``; ``repr``: ``f"{column} é nulo"``."""

    def __init__(self, column: str):
        raise NotImplementedError


class And(Spec3):
    """``And(left, right)``: ``False`` se ALGUM lado é ``False``; senão ``None`` se algum é ``None``; senão ``True``. ``to_sql()``: ``(f"({l} AND {r})", params_l + params_r)``;
    ``repr``: ``f"({left!r} e {right!r})"``."""

    def __init__(self, left: Spec3, right: Spec3):
        raise NotImplementedError


class Or(Spec3):
    """``Or(left, right)``: ``True`` se ALGUM lado é ``True``; senão ``None`` se algum é ``None``; senão ``False``. ``to_sql()``: ``(f"({l} OR {r})", ...)``; ``repr``: ``f"({left!r} ou {right!r})"``."""

    def __init__(self, left: Spec3, right: Spec3):
        raise NotImplementedError


class Not(Spec3):
    """``Not(inner)``: ``None`` se ``inner`` é ``None``; senão o contrário. ``to_sql()``: ``(f"(NOT {sql})", params)``; ``repr``: ``f"não {inner!r}"``."""

    def __init__(self, inner: Spec3):
        raise NotImplementedError


class Field:
    """Uma coluna: ``Field(name)`` (``name`` fora de ``COLUMNS``: ``AttributeError(f"coluna desconhecida: {name}")``).

    * ``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=`` devolvem um ``Cmp`` (e NÃO um ``bool``); o ``Field`` não é "hashable" (``__hash__ = None``), porque o ``==`` mudou de significado;
    * ``isin(values)``: o ``Or`` encadeado (da esquerda para a direita) de ``== v``; sem valores: ``ValueError("isin precisa de pelo menos um valor")``;
    * ``between(low, high)``: ``(campo >= low) & (campo <= high)``;
    * ``is_null()``: um ``IsNull``; ``is_not_null()``: ``~is_null()``."""

    def __init__(self, name: str):
        raise NotImplementedError


class _F:
    """``F.age`` devolve ``Field("age")`` (use ``__getattr__``). Nomes desconhecidos levantam o ``AttributeError`` do ``Field``."""


F = _F()
