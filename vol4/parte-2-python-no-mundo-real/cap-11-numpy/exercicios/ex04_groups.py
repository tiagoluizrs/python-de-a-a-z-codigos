"""Exercício 4: agrupar e agregar sem laço e sem pandas (bincount e ufunc.at)."""
import numpy as np


def group_sum(keys, values, n_groups):
    """``keys``: inteiros de ``0`` a ``n_groups - 1``, um por item de ``values``. Devolve um array de ``float64`` com
    a soma de cada grupo (grupo vazio = ``0.0``). Dica: ``np.bincount(..., weights=...)``."""
    raise NotImplementedError


def group_mean(keys, values, n_groups):
    """Média por grupo; grupo vazio = ``nan`` (sem warnings do NumPy)."""
    raise NotImplementedError


def group_max(keys, values, n_groups):
    """Máximo por grupo; grupo vazio = ``-inf``. Dica: ``np.maximum.at`` (ou ordenar e usar ``reduceat``)."""
    raise NotImplementedError


def top_k_per_group(keys, values, n_groups, k):
    """Para cada grupo, os ``k`` MAIORES valores em ordem decrescente: lista (uma por grupo) de arrays com até ``k``
    itens. Aqui um laço sobre os GRUPOS é aceitável; sobre os itens, não."""
    raise NotImplementedError
