"""Exercício 4: resultados com ordem DEFINIDA (o group_by e o join não prometem ordem)."""
import polars as pl


def totals_by_key(df: pl.DataFrame) -> pl.DataFrame:
    """``df`` tem ``key`` (String) e ``value`` (Int64). Devolve ``key`` e ``total`` (soma de ``value``),
    SEMPRE ordenado por ``key`` crescente, em qualquer execução."""
    raise NotImplementedError


def first_seen_order(df: pl.DataFrame) -> pl.DataFrame:
    """Os mesmos totais, mas os grupos na ordem da PRIMEIRA aparição de cada ``key`` em ``df``
    (colunas ``key``, ``total``)."""
    raise NotImplementedError


def attach_names(df: pl.DataFrame, names: pl.DataFrame) -> pl.DataFrame:
    """``names`` tem ``key`` e ``name``. Acrescenta ``name`` a ``df`` com um ``left join`` por ``key``, preservando
    a ORDEM das linhas de ``df`` (e levantando ``ValueError`` se ``names`` tiver ``key`` repetida). Atenção: o
    join não promete ordem sozinho."""
    raise NotImplementedError
