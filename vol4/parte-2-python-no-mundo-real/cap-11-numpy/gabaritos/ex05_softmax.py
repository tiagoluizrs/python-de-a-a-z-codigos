"""Gabarito do exercício 5."""
import numpy as np


def softmax(logits, axis=-1):
    arr = np.asarray(logits, dtype=np.float64)
    shifted = arr - arr.max(axis=axis, keepdims=True)        # o maior vira 0: exp() nunca passa de 1
    exp = np.exp(shifted)
    return exp / exp.sum(axis=axis, keepdims=True)


def one_hot(labels, n_classes):
    idx = np.asarray(labels, dtype=np.intp)             # lista vazia vira float64 sem o dtype: não serviria de índice
    if idx.size and (idx.min() < 0 or idx.max() >= n_classes):
        raise ValueError("rótulo fora do intervalo")
    out = np.zeros((len(idx), n_classes), dtype=np.uint8)
    out[np.arange(len(idx)), idx] = 1
    return out


def accuracy(logits, labels):
    arr = np.asarray(logits)
    if len(arr) == 0:
        return 0.0
    return float((arr.argmax(axis=1) == np.asarray(labels)).mean())
