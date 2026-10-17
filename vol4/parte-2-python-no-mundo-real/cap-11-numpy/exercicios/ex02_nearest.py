"""Exercício 2: distâncias entre todos os pares de pontos e o vizinho mais próximo, sem laços."""
import numpy as np


def pairwise_distances(points):
    """``points`` tem forma ``(n, d)``. Devolve a matriz ``(n, n)`` de distâncias euclidianas
    (``out[i, j]`` = distância do ponto i ao j). Use broadcasting; nada de ``for``."""
    raise NotImplementedError


def nearest_neighbor(points):
    """Para cada ponto, o ÍNDICE do ponto mais próximo OUTRO que ele mesmo (forma ``(n,)``, ``int``).
    Em empate, vale o menor índice. Com menos de 2 pontos, levante ``ValueError``."""
    raise NotImplementedError
