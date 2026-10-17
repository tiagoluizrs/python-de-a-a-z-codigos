"""Gabarito do exercício 2."""
import numpy as np


def pairwise_distances(points):
    pts = np.asarray(points, dtype=np.float64)
    diff = pts[:, None, :] - pts[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=-1))


def nearest_neighbor(points):
    pts = np.asarray(points, dtype=np.float64)
    if len(pts) < 2:
        raise ValueError("são necessários ao menos 2 pontos")
    dist = pairwise_distances(pts)
    np.fill_diagonal(dist, np.inf)                  # um ponto não é vizinho de si mesmo
    return dist.argmin(axis=1)                      # argmin devolve o PRIMEIRO mínimo: empate -> menor índice
