"""Exercício 4: dispatcher por tipo com singledispatch."""
import functools


@functools.singledispatch
def describe(value):
    """Descreva ``value`` em texto.

    Regras (registre uma implementação por tipo):

    * qualquer outro tipo: ``"object:<NomeDoTipo>"``
    * ``int``: ``"int:<valor>"`` (``bool`` herda de ``int``, mas
      deve devolver ``"bool:<valor>"``)
    * ``str``: ``"str:<tamanho>"``
    * ``list`` e ``tuple``: ``"seq[<itens descritos, separados por
      vírgula, sem espaço>]"`` (descreva cada item recursivamente)
    * ``dict``: ``"map:<n chaves>"``
    * ``None``: ``"none"`` (dica: ``type(None)``)

    >>> describe([1, "ab"])
    'seq[int:1,str:2]'
    """
    raise NotImplementedError
