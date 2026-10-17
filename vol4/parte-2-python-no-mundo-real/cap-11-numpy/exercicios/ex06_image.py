"""Exercício 6: uma imagem é um array ``uint8`` (cuidado com o estouro)."""
import numpy as np


def to_gray(img):
    """``img``: ``(h, w, 3)`` ``uint8`` em RGB. Devolve ``(h, w)`` ``uint8`` com ``0.299 R + 0.587 G + 0.114 B``
    (trunque ao converter para ``uint8``). Uma matriz 2D (já cinza) volta como cópia."""
    raise NotImplementedError


def brighten(img, delta):
    """Soma ``delta`` (pode ser negativo) a cada pixel SEM dar a volta: o resultado fica em ``[0, 255]``
    (``clip``) e continua ``uint8``. O array original não muda."""
    raise NotImplementedError


def center_crop(img, height, width):
    """Recorte central ``height x width``. Devolve uma VIEW (sem copiar). Se o recorte for maior que a imagem,
    levante ``ValueError``."""
    raise NotImplementedError


def histogram(gray):
    """Vetor de 256 posições com a contagem de cada nível de cinza (``int``). Use ``np.bincount`` com ``minlength``."""
    raise NotImplementedError


def threshold(gray, level):
    """Máscara booleana ``(h, w)``: ``True`` onde o pixel é ``>= level``."""
    raise NotImplementedError
