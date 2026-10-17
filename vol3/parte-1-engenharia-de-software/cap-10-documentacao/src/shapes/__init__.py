"""Formas geométricas simples, para ilustrar a documentação de código.

O pacote expõe duas formas (:class:`Circle` e :class:`Rectangle`) e funções para
trabalhar com coleções delas.

Example:
    >>> from shapes import Circle, Rectangle, total_area
    >>> round(total_area([Circle(1), Rectangle(2, 3)]), 2)
    9.14
"""
from .geometry import Circle, Rectangle, Shape, largest, total_area

__all__ = ["Circle", "Rectangle", "Shape", "largest", "total_area"]
