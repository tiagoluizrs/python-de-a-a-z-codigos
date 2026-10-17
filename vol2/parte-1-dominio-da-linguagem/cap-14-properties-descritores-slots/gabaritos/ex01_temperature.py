"""Gabarito do exercício 1."""


class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius                       # passa pelo setter

    @property
    def celsius(self):
        """Temperatura em Celsius."""
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("abaixo do zero absoluto")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9          # reaproveita a validação

    @property
    def kelvin(self):                                # sem setter: somente leitura
        return self._celsius + 273.15

    def __repr__(self):
        return f"Temperature(celsius={self._celsius!r})"
