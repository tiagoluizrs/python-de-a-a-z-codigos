"""Exercício 2: relatórios de vendas com groupby, resample e ranking."""
import pandas as pd


def product_report(orders: pd.DataFrame) -> pd.DataFrame:
    """``orders`` tem ``order_id``, ``product``, ``qty``, ``total`` e ``status``. Considere SÓ ``status == "paid"``.

    Devolve um DataFrame com ``product`` como ÍNDICE e as colunas ``orders`` (quantidade de pedidos), ``units``
    (soma de ``qty``), ``revenue`` (soma de ``total``) e ``share`` (fração da receita total, somando 1.0), ordenado
    da MAIOR para a menor receita (desempate pelo nome do produto). Use ``agg`` com nomes, sem ``apply``."""
    raise NotImplementedError


def monthly_revenue(orders: pd.DataFrame) -> pd.Series:
    """Receita de pedidos ``paid`` por MÊS (``date`` é ``datetime64``): Series com índice de início de mês
    (``freq="MS"``), incluindo meses SEM vendas com ``0.0`` entre o primeiro e o último mês, ``float64``."""
    raise NotImplementedError


def top_customers(orders: pd.DataFrame, n: int) -> pd.DataFrame:
    """Os ``n`` clientes com maior receita (pedidos ``paid``): colunas ``customer_id``, ``revenue``, ``orders``,
    ordenadas por receita decrescente (desempate: menor ``customer_id``) e com índice ``0..n-1``."""
    raise NotImplementedError
