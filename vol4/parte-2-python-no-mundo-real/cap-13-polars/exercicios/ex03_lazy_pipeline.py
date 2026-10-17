"""Exercício 3: uma consulta preguiçosa sobre um arquivo Parquet (o plano, não o resultado)."""
from pathlib import Path

import polars as pl


def monthly_revenue_query(path: Path) -> pl.LazyFrame:
    """``path`` é um Parquet com ``order_id``, ``date`` (Datetime), ``product``, ``qty``, ``total`` e ``status``
    (e outras colunas que você NÃO deve precisar ler).

    Devolve um **LazyFrame** (não execute nada! nada de ``collect`` aqui) que:

    * lê o arquivo com ``scan_parquet``;
    * mantém só os pedidos com ``status == "paid"``;
    * agrupa por mês (``month`` = o primeiro dia do mês, como ``Date``) e calcula ``revenue`` (soma de ``total``) e
      ``orders`` (contagem);
    * ordena por ``month`` crescente."""
    raise NotImplementedError


def run(path: Path) -> pl.DataFrame:
    """Executa ``monthly_revenue_query`` e devolve o DataFrame."""
    raise NotImplementedError


def explain_text(path: Path) -> str:
    """O plano OTIMIZADO da consulta, como texto (``explain()``), sem executá-la."""
    raise NotImplementedError
