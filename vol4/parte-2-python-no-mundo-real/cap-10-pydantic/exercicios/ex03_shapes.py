"""Exercício 3: união discriminada e campos calculados."""
from pydantic import BaseModel  # noqa: F401


class Circle(BaseModel):
    """``kind`` literal ``"circle"``, ``radius`` > 0; ``area`` calculada (``round(3.14159 * r**2, 2)``)."""


class Rect(BaseModel):
    """``kind`` literal ``"rect"``, ``width`` > 0, ``height`` > 0; ``area`` calculada."""


class Square(BaseModel):
    """``kind`` literal ``"square"``, ``side`` > 0; ``area`` calculada."""


def parse_shapes(items):
    """Valida uma lista de dicionários com ``TypeAdapter`` e uma união DISCRIMINADA por ``kind`` (``Field(discriminator=...)``).
    Devolve a lista de objetos. Um ``kind`` desconhecido deve resultar em ``ValidationError`` com ``type == "union_tag_invalid"``.
    ``area`` NÃO é campo de entrada: se vier no dicionário, é ignorada (campos extras ignorados) e recalculada."""
    raise NotImplementedError


def total_area(items):
    """Soma das áreas (``round(..., 2)``) de ``parse_shapes(items)``; lista vazia dá ``0.0``."""
    raise NotImplementedError
