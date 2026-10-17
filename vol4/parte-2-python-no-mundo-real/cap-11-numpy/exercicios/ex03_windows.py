"""Exercício 3: janelas deslizantes (média móvel e máximo móvel)."""
import numpy as np


def moving_average(x, window):
    """Média móvel em modo ``valid``: ``len(x) - window + 1`` valores, o primeiro é a média de ``x[:window]``.

    * use ``np.cumsum`` (diferença de somas acumuladas), não um laço;
    * ``window < 1`` ou maior que ``len(x)`` levanta ``ValueError``;
    * devolve ``float64``."""
    raise NotImplementedError


def rolling_max(x, window):
    """Máximo móvel, mesmas regras de tamanho e de erro. Use ``sliding_window_view`` (uma view, sem copiar)."""
    raise NotImplementedError


def exceed_count(x, window, limit):
    """Quantas janelas têm média MAIOR que ``limit`` (um ``int`` do Python)."""
    raise NotImplementedError
