"""Exercício 2: construtores alternativos com ``@classmethod`` (o factory method mais comum do Python)."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Temperature:
    """Guarda a temperatura em graus Celsius. Abaixo do zero absoluto (-273.15 °C): ``ValueError("abaixo do zero absoluto")``, em QUALQUER
    caminho de criação (use ``__post_init__``)."""

    celsius: float

    @classmethod
    def from_fahrenheit(cls, f: float) -> "Temperature":
        """``(f - 32) * 5 / 9``. Devolve uma instância de ``cls`` (subclasses recebem a subclasse)."""
        raise NotImplementedError

    @classmethod
    def from_kelvin(cls, k: float) -> "Temperature":
        """``k - 273.15``."""
        raise NotImplementedError

    @classmethod
    def parse(cls, text: str) -> "Temperature":
        """Lê ``"21.5C"``, ``"70 F"``, ``"300k"`` (número com sinal e ponto decimal opcionais, espaços opcionais, uma letra C/F/K em qualquer caixa)
        e usa o construtor certo. Texto que não casa: ``ValueError(f"temperatura inválida: {text!r}")``."""
        raise NotImplementedError

    @property
    def fahrenheit(self) -> float:
        raise NotImplementedError

    @property
    def kelvin(self) -> float:
        raise NotImplementedError

    def __post_init__(self):
        raise NotImplementedError


class RoomTemperature(Temperature):
    """Uma subclasse sem nada novo: serve para provar que os construtores alternativos respeitam ``cls``."""
