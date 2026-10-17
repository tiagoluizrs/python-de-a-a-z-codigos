"""Gabarito do exercício 1."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Glyph:
    char: str
    font: str
    size: float

    def __post_init__(self):
        if len(self.char) != 1:
            raise ValueError("char deve ter um caractere")
        if not self.font:
            raise ValueError("font vazia")
        if self.size <= 0:
            raise ValueError("size inválido")


class GlyphFactory:
    def __init__(self):
        self._pool = {}
        self.hits = 0
        self.misses = 0

    def get(self, char, font, size):
        key = (char, font, size)
        glyph = self._pool.get(key)
        if glyph is not None:
            self.hits += 1
            return glyph
        glyph = Glyph(char, font, size)
        self._pool[key] = glyph
        self.misses += 1
        return glyph

    @property
    def count(self):
        return len(self._pool)

    def clear(self):
        self._pool.clear()


class Document:
    def __init__(self, factory):
        self._factory = factory
        self._items = []

    def add_text(self, text, font, size, x=0, y=0, advance=1.0):
        for i, char in enumerate(text):
            self._items.append((self._factory.get(char, font, size), x + i * advance, y))

    def render(self):
        return [f"{glyph.char}@{px:g},{py:g}" for glyph, px, py in self._items]

    def stats(self):
        return {"characters": len(self._items), "glyphs": len({id(glyph) for glyph, _, _ in self._items})}

    def text(self):
        return "".join(glyph.char for glyph, _, _ in self._items)
