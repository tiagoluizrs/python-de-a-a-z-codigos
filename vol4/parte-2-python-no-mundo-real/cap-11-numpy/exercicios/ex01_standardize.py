"""Exercício 1: padronizar colunas sem laço (broadcasting e keepdims)."""
import numpy as np


def standardize(data, axis=0):
    """Z-score: ``(x - média) / desvio`` ao longo de ``axis`` (padrão: cada COLUNA).

    * devolve um array NOVO de ``float64``; o ``data`` recebido não pode ser alterado (aceite listas e ``int``);
    * onde o desvio for zero (coluna constante) o resultado é ``0.0``, nunca ``nan`` nem ``inf``;
    * desvio populacional (``ddof=0``, o padrão do NumPy)."""
    raise NotImplementedError


def minmax_scale(data, low=0.0, high=1.0):
    """Reescala CADA COLUNA para o intervalo ``[low, high]``; coluna constante vira ``low``.
    Devolve um array novo de ``float64``."""
    raise NotImplementedError
