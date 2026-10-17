"""Exercício 4: metaclasse Singleton por classe."""


class Singleton(type):
    """Metaclasse: cada classe que a usa tem UMA instância.

    * ``Cls() is Cls()``; o ``__init__`` roda só na primeira vez;
    * classes DIFERENTES (inclusive subclasses) têm instâncias separadas;
    * ``Singleton.reset(cls)`` (método de classe da metaclasse; ou
      ``cls.reset()`` via metaclasse, como preferir, mas o teste usa
      ``Singleton.reset(Cls)``) esquece a instância dessa classe;
    * os argumentos da primeira chamada valem; chamadas seguintes com
      argumentos DIFERENTES levantam ``TypeError``.
    """
