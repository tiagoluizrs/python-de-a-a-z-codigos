"""Exercício 1: novas colunas com expressões (sem laço, sem apply)."""
import polars as pl


def add_features(df: pl.DataFrame) -> pl.DataFrame:
    """``df`` tem ``qty`` (Int64), ``unit_price`` (Float64), ``date`` (Datetime) e ``status`` (String).
    Devolve um DataFrame NOVO com TODAS as colunas originais (mesma ordem) mais, nesta ordem:

    * ``total``: ``qty * unit_price`` (Float64);
    * ``tier``: ``"alto"`` se ``total >= 1000``, ``"médio"`` se ``total >= 100``, senão ``"baixo"`` (String);
    * ``weekday``: nome do dia da semana em inglês (``"Monday"``...; use ``dt.to_string("%A")``);
    * ``is_weekend``: ``True`` em sábado e domingo (Boolean);
    * ``month``: o primeiro dia do mês da data, como ``Date`` (``dt.truncate("1mo").dt.date()``);
    * ``paid_total``: ``total`` se ``status == "paid"``, senão ``0.0`` (Float64).

    O argumento não pode ser alterado."""
    raise NotImplementedError


def tier_counts(df: pl.DataFrame) -> dict[str, int]:
    """Quantas linhas há em cada ``tier`` (considere ``add_features(df)``); só as faixas que existem, em um dict
    ordenado por contagem decrescente (desempate pelo nome da faixa)."""
    raise NotImplementedError
