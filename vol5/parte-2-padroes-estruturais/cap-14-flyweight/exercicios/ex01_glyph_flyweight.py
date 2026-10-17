"""Exercício 1: o Flyweight clássico: um editor de texto em que cada caractere é um objeto leve que COMPARTILHA o seu glifo."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Glyph:
    """O FLYWEIGHT (estado intrínseco, imutável): ``char`` (exatamente um caractere), ``font`` (texto não vazio) e ``size`` (número ``> 0``).
    Complete a validação em ``__post_init__``: ``char`` com comprimento diferente de 1: ``ValueError("char deve ter um caractere")``; ``font`` vazia:
    ``ValueError("font vazia")``; ``size <= 0``: ``ValueError("size inválido")``."""

    char: str
    font: str
    size: float

    def __post_init__(self):
        raise NotImplementedError


class GlyphFactory:
    """A fábrica: ``get(char, font, size)`` devolve SEMPRE o mesmo objeto ``Glyph`` para os mesmos três valores (compare com ``is``); os valores são validados
    pelo próprio ``Glyph`` (a fábrica só guarda os que deram certo: um erro não deixa nada no pool).

    * ``count`` (propriedade): quantos glifos distintos o pool tem;
    * ``clear()``: esvazia o pool (os glifos que já estão nos documentos continuam existindo, mas ``get`` passa a criar objetos novos);
    * ``hits`` e ``misses``: quantas chamadas a ``get`` acharam (``hits``) ou criaram (``misses``) um glifo."""

    def __init__(self):
        raise NotImplementedError

    def get(self, char: str, font: str, size: float) -> Glyph:
        raise NotImplementedError

    @property
    def count(self) -> int:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError


class Document:
    """O contexto: guarda, para cada caractere, SÓ o estado extrínseco: ``(glifo, x, y)`` (uma tupla). ``Document(factory)``.

    * ``add_text(text, font, size, x=0, y=0, advance=1.0)``: acrescenta um caractere por posição, com ``x`` crescendo ``advance`` a cada caractere (o primeiro em
      ``x``); espaços e quebras de linha TAMBÉM entram (cada um é um glifo); ``text`` vazio não faz nada. Os glifos vêm da fábrica;
    * ``render()``: a lista de textos ``f"{char}@{x:g},{y:g}"`` na ordem em que foram acrescentados;
    * ``stats()``: ``{"characters": total_de_caracteres, "glyphs": glifos_distintos_NESTE_documento}`` (distintos por identidade, ``id``);
    * ``text()``: os caracteres juntos, como uma string."""

    def __init__(self, factory: GlyphFactory):
        raise NotImplementedError

    def add_text(self, text: str, font: str, size: float, x: float = 0, y: float = 0, advance: float = 1.0) -> None:
        raise NotImplementedError

    def render(self) -> list[str]:
        raise NotImplementedError

    def stats(self) -> dict:
        raise NotImplementedError

    def text(self) -> str:
        raise NotImplementedError
