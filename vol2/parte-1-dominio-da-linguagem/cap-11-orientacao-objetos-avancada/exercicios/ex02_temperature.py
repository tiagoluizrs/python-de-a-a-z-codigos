"""Exercício 2: construtores alternativos que respeitam subclasses."""


class Temperature:
    """Temperatura guardada em Kelvin.

    * ``Temperature(kelvin)`` (não pode ser negativa: ``ValueError``);
    * construtores alternativos (classmethods): ``from_celsius(c)`` e
      ``from_fahrenheit(f)``;
    * propriedades-métodos simples: ``celsius()`` e ``fahrenheit()``;
    * os classmethods devem criar ``cls(...)``, para que subclasses recebam
      instâncias da SUBCLASSE;
    * ``repr`` no formato ``Temperature(300.15)`` usando o nome da classe
      real (``type(self).__name__``).
    """

    def __init__(self, kelvin):
        raise NotImplementedError
