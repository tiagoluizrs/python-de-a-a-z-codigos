"""Gabarito do exercício 1."""
import numpy as np


def standardize(data, axis=0):
    arr = np.asarray(data, dtype=np.float64)
    mean = arr.mean(axis=axis, keepdims=True)
    std = arr.std(axis=axis, keepdims=True)
    safe = np.where(std == 0, 1.0, std)             # evita dividir por zero; o numerador já é 0 nessas colunas
    return (arr - mean) / safe


def minmax_scale(data, low=0.0, high=1.0):
    arr = np.asarray(data, dtype=np.float64)
    lo = arr.min(axis=0, keepdims=True)
    span = arr.max(axis=0, keepdims=True) - lo
    unit = (arr - lo) / np.where(span == 0, 1.0, span)
    return low + unit * (high - low)
