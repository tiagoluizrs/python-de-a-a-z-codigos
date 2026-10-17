"""Exercício 3: __new__ para devolver instâncias existentes."""


class Color:
    """Cor imutável e COMPARTILHADA.

    * ``Color("red")`` devolve SEMPRE a mesma instância para o mesmo nome
      (``Color("red") is Color("red")``), e nomes diferentes dão instâncias
      diferentes;
    * o nome é normalizado em minúsculas (``Color("RED") is Color("red")``);
    * ``Color.count()`` (classmethod) diz quantas cores distintas existem;
    * nome vazio levanta ``ValueError``;
    * ``__init__`` NÃO deve reexecutar trabalho inútil: o nome é gravado
      uma vez só;
    * ``repr`` no formato ``Color('red')``.
    """

    def __new__(cls, name):
        raise NotImplementedError
