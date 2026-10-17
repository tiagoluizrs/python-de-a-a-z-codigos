"""Exercício 4: uma série diária completa e indicadores de tendência."""
import pandas as pd


def daily_revenue(orders: pd.DataFrame, start=None, end=None) -> pd.Series:
    """Receita por DIA (``date`` é ``datetime64`` com hora; ``total`` é a receita; ignore ``status``).

    A Series tem índice diário (``freq="D"``, hora zerada) do primeiro ao último dia de ``orders`` (ou de ``start`` a
    ``end``, se forem dados) e ``0.0`` nos dias sem pedido. Nome da Series: ``"revenue"``."""
    raise NotImplementedError


def add_trend(series: pd.Series, window: int = 7) -> pd.DataFrame:
    """Devolve um DataFrame com as colunas ``revenue`` (a série), ``ma`` (média móvel de ``window`` dias; os primeiros
    ``window - 1`` valores ficam ``NaN``), ``change`` (``revenue`` menos o dia anterior) e ``growth`` (variação
    percentual em relação ao dia anterior; ``NaN`` quando o dia anterior foi ``0`` ou não existe; nunca ``inf``)."""
    raise NotImplementedError


def best_weekday(series: pd.Series) -> str:
    """Nome em inglês (``"Monday"`` ...) do dia da semana com maior MÉDIA diária de receita."""
    raise NotImplementedError
