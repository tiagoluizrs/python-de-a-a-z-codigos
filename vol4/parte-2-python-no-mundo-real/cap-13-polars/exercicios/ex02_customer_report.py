"""Exercício 2: relatório por cliente com group_by e janelas (over)."""
import polars as pl


def customer_report(orders: pl.DataFrame) -> pl.DataFrame:
    """``orders`` tem ``order_id``, ``customer_id``, ``date`` (Datetime), ``product``, ``total`` (Float64) e ``status``.
    Considere SÓ ``status == "paid"``. Devolve UMA linha por cliente com as colunas, nesta ordem:

    ``customer_id``, ``orders`` (``UInt32``: quantidade), ``revenue`` (soma de ``total``), ``first_order`` e
    ``last_order`` (menor e maior ``date``), ``top_product`` (o produto com MAIOR receita do cliente; empate: ordem
    alfabética).

    Ordene por ``revenue`` decrescente e, em empate, por ``customer_id`` crescente."""
    raise NotImplementedError


def share_within_product(orders: pl.DataFrame) -> pl.DataFrame:
    """Para cada linha de ``orders`` (todas, qualquer status), acrescente ``share``: ``total`` dividido pela soma de
    ``total`` do MESMO produto (uma expressão com ``over``), e ``rank``: a posição da linha entre as do mesmo produto
    por ``total`` decrescente (``rank("ordinal", descending=True)``; empate: a ordem original). Mantém a ordem e as
    colunas originais, com ``share`` e ``rank`` no fim."""
    raise NotImplementedError
