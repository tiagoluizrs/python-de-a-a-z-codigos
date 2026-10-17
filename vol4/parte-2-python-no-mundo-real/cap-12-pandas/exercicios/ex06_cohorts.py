"""Exercício 6: análise de coortes (quantos clientes continuam comprando mês após mês)."""
import pandas as pd


def first_purchase_month(orders: pd.DataFrame) -> pd.Series:
    """``orders`` tem ``customer_id`` e ``date`` (``datetime64``). Devolve uma Series indexada por ``customer_id``
    (ordenada pelo id), com o PRIMEIRO mês de compra de cada cliente como ``Period`` mensal (``"M"``). Nome: ``"cohort"``."""
    raise NotImplementedError


def retention_counts(orders: pd.DataFrame) -> pd.DataFrame:
    """Matriz de coortes: LINHAS = mês da primeira compra (``Period``, em ordem), COLUNAS = meses desde a primeira
    compra (``0, 1, 2, ...``, inteiros), VALORES = quantos clientes DISTINTOS da coorte compraram naquele mês
    (``int``; células sem ninguém = ``0``). A coluna ``0`` é o tamanho da coorte. Nome do índice: ``cohort``;
    nome do cabeçalho das colunas: ``months_since``."""
    raise NotImplementedError


def retention_rate(orders: pd.DataFrame) -> pd.DataFrame:
    """A mesma matriz dividida pela coluna ``0`` (cada linha), em fração entre 0 e 1 (``float``), arredondada para
    4 casas. A coluna ``0`` vale ``1.0``."""
    raise NotImplementedError
