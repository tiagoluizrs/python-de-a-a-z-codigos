"""Exercício 6: portar duas funções de pandas para Polars (o raciocínio muda, o resultado não)."""
import polars as pl


def top_n(df: pl.DataFrame, by: str, value: str, n: int) -> pl.DataFrame:
    """As ``n`` linhas de MAIOR ``value`` dentro de cada grupo ``by``, ordenadas por ``by`` crescente e ``value``
    decrescente (empate: a ordem original de ``df``). No pandas seria ``sort_values`` + ``groupby().head(n)``. Mantém
    as colunas originais. Grupos com menos de ``n`` linhas devolvem todas."""
    raise NotImplementedError


def growth_by_group(df: pl.DataFrame, group: str, order: str, value: str) -> pl.DataFrame:
    """Dentro de cada grupo (ordenado por ``order``), acrescente ``growth``: variação percentual de ``value`` em
    relação à linha anterior do MESMO grupo (``(v - anterior) / anterior * 100``). A primeira linha de cada grupo e
    as que seguem um ``0`` ficam ``null`` (nunca ``inf`` nem ``NaN``). O resultado vem ordenado por ``group`` e
    ``order``, com as colunas originais mais ``growth``."""
    raise NotImplementedError


def to_pandas_safely(df: pl.DataFrame):
    """Converte para pandas e devolve ``(pdf, report)``, em que ``report`` é um dict ``{coluna: dtype_do_pandas}``
    (``str``). Se ``df`` tiver coluna com tipo aninhado (``List`` ou ``Struct``), levante ``TypeError`` ANTES de
    converter, com a mensagem ``"colunas aninhadas: [nomes]"``."""
    raise NotImplementedError
