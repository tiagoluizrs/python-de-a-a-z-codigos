"""Gabarito do exercício 2."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Temperature:
    celsius: float

    def __post_init__(self):
        if self.celsius < -273.15:
            raise ValueError("abaixo do zero absoluto")

    @classmethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    @classmethod
    def from_kelvin(cls, k):
        return cls(k - 273.15)

    @classmethod
    def parse(cls, text):
        m = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*([cCfFkK])\s*", text)
        if not m:
            raise ValueError(f"temperatura inválida: {text!r}")
        value, unit = float(m.group(1)), m.group(2).lower()
        return {"c": cls, "f": cls.from_fahrenheit, "k": cls.from_kelvin}[unit](value)

    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    @property
    def kelvin(self):
        return self.celsius + 273.15


class RoomTemperature(Temperature):
    pass
