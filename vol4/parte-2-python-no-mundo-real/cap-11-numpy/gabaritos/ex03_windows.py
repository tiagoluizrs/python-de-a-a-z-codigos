"""Gabarito do exercício 3."""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def _check(arr, window):
    if window < 1 or window > len(arr):
        raise ValueError(f"janela {window} inválida para {len(arr)} valores")


def moving_average(x, window):
    arr = np.asarray(x, dtype=np.float64)
    _check(arr, window)
    cumulative = np.concatenate(([0.0], np.cumsum(arr)))
    return (cumulative[window:] - cumulative[:-window]) / window


def rolling_max(x, window):
    arr = np.asarray(x)
    _check(arr, window)
    return sliding_window_view(arr, window).max(axis=1)


def exceed_count(x, window, limit):
    return int((moving_average(x, window) > limit).sum())
