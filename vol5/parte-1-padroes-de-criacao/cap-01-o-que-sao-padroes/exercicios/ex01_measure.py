"""Exercício 1: medir a cerimônia de um padrão lendo o código com ``ast``."""
import ast
import textwrap


def measure(source: str) -> dict:
    """Analisa ``source`` (use ``textwrap.dedent``) e devolve um dict com:

    * ``lines``: linhas de código (não vazias e que não começam com ``#``; docstrings contam como código);
    * ``classes``: quantas ``class`` (inclusive aninhadas);
    * ``functions``: quantas ``def``, ``async def`` e ``lambda`` (métodos contam);
    * ``abstract``: quantas classes são abstratas: herdam de ``ABC`` (``ABC`` ou ``abc.ABC``) OU têm um método decorado com ``abstractmethod``
      (``@abstractmethod`` ou ``@abc.abstractmethod``);
    * ``depth``: a profundidade da maior cadeia de herança ENTRE as classes definidas em ``source`` (uma classe sem base definida em
      ``source`` vale 1; uma que herda de uma classe definida em ``source`` vale 1 + a profundidade da base; bases de fora, como ``ABC`` ou ``dict``,
      não contam); sem classes: 0."""
    raise NotImplementedError


def ceremony_ratio(classic: str, pythonic: str) -> float:
    """Quantas vezes o código clássico é maior que o pythônico, em ``lines`` (``round(..., 1)``). ``pythonic`` sem linhas: ``ValueError``."""
    raise NotImplementedError
