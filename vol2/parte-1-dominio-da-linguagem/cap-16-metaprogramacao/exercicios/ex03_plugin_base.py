"""Exercício 3: __init_subclass__ com argumentos de classe."""


class Exporter:
    """Classe base de exportadores.

    Cada subclasse deve:

    * ser declarada com ``class Csv(Exporter, fmt="csv")`` (``fmt`` é
      obrigatório; sem ele, ``TypeError``);
    * definir um método ``export`` (senão, ``TypeError``);
    * não repetir ``fmt`` de outra subclasse (``ValueError``).

    Classmethod ``Exporter.for_format(fmt)`` devolve uma INSTÂNCIA da
    subclasse registrada (``KeyError`` se o formato não existir) e
    ``Exporter.formats()`` devolve a lista ordenada dos formatos.
    Subclasses de subclasses (``class Fancy(Csv, fmt="fancy-csv")``) também
    registram.
    """
