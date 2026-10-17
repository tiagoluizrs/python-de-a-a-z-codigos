"""Exercício 1: limpar uma planilha de pedidos e separar o que foi rejeitado (e por quê)."""
import pandas as pd


def clean_orders(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """``raw`` tem as colunas ``Order ID``, ``Customer``, ``Date``, ``Amount``, ``Status`` (todas texto).

    Devolve ``(clean, rejected)``:

    * ``clean`` tem as colunas ``order_id`` (``Int64``), ``customer`` (``Nome Em Title Case``, sem espaços nas pontas),
      ``date`` (``datetime64``), ``amount`` (``float64``) e ``status`` (minúsculas), na ordem original das linhas, com
      índice ``0..n-1`` e SEM duplicatas (linhas idênticas: fica a primeira);
    * a data vem em ``AAAA-MM-DD`` ou ``DD/MM/AAAA``; o valor pode ter ``R$``, ponto de milhar e vírgula decimal
      (``"R$ 1.250,50"`` vale ``1250.5``);
    * ``rejected`` guarda as linhas que não puderam ser limpas (id, cliente, data ou valor ausentes/inválidos, ou valor
      menor ou igual a zero), com as colunas ORIGINAIS de ``raw`` mais ``reason``: os nomes das colunas problemáticas
      separados por vírgula, na ordem ``order_id,customer,date,amount`` (ex.: ``"customer,date"``).
      Linhas duplicadas já descartadas não entram em ``rejected``."""
    raise NotImplementedError
