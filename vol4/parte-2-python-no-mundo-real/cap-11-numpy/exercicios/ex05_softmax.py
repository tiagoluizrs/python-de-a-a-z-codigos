"""Exercício 5: softmax estável, one-hot e acurácia (estabilidade numérica e fancy indexing)."""
import numpy as np


def softmax(logits, axis=-1):
    """``exp(x) / sum(exp(x))`` ao longo de ``axis``, SEM estourar com valores grandes (``[1000, 1001]`` tem de
    funcionar) e sem ``nan``. Devolve ``float64`` e não altera o argumento."""
    raise NotImplementedError


def one_hot(labels, n_classes):
    """``labels`` é um vetor de inteiros; devolve uma matriz ``(len(labels), n_classes)`` de ``uint8`` com 1 na
    posição do rótulo. Rótulo fora de ``[0, n_classes)`` levanta ``ValueError``. Sem laço."""
    raise NotImplementedError


def accuracy(logits, labels):
    """Fração (``float``) de linhas em que ``argmax`` dos logits é igual ao rótulo. Sem linhas: ``0.0``."""
    raise NotImplementedError
