"""Exercício 1: property para validar e para calcular."""


class Temperature:
    """Temperatura guardada em Celsius (``_celsius``).

    * ``Temperature(celsius)`` (valida pelo setter);
    * property ``celsius`` com setter que levanta ``ValueError`` abaixo de
      -273.15;
    * property ``fahrenheit`` com getter E setter (grava em Celsius);
    * property ``kelvin`` SOMENTE LEITURA (atribuir levanta
      ``AttributeError``);
    * ``celsius`` tem docstring ``"Temperatura em Celsius."``;
    * ``repr`` no formato ``Temperature(celsius=21.5)``.
    """

    def __init__(self, celsius):
        raise NotImplementedError
