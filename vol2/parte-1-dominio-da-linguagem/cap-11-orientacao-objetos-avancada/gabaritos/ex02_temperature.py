"""Gabarito do exercício 2."""


class Temperature:
    def __init__(self, kelvin):
        if kelvin < 0:
            raise ValueError("abaixo do zero absoluto")
        self.kelvin = kelvin

    @classmethod
    def from_celsius(cls, celsius):
        return cls(celsius + 273.15)             # cls: respeita subclasses

    @classmethod
    def from_fahrenheit(cls, fahrenheit):
        return cls.from_celsius((fahrenheit - 32) * 5 / 9)

    def celsius(self):
        return self.kelvin - 273.15

    def fahrenheit(self):
        return self.celsius() * 9 / 5 + 32

    def __repr__(self):
        return f"{type(self).__name__}({self.kelvin:.2f})"
