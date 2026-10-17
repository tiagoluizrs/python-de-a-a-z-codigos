"""Gabarito do exercício 6."""
import numpy as np

WEIGHTS = np.array([0.299, 0.587, 0.114])


def to_gray(img):
    arr = np.asarray(img)
    if arr.ndim == 2:
        return arr.copy()
    return (arr @ WEIGHTS).astype(np.uint8)


def brighten(img, delta):
    return np.clip(np.asarray(img, dtype=np.int16) + delta, 0, 255).astype(np.uint8)


def center_crop(img, height, width):
    h, w = img.shape[:2]
    if height > h or width > w:
        raise ValueError("recorte maior que a imagem")
    top, left = (h - height) // 2, (w - width) // 2
    return img[top:top + height, left:left + width]


def histogram(gray):
    return np.bincount(np.asarray(gray).ravel(), minlength=256)


def threshold(gray, level):
    return np.asarray(gray) >= level
