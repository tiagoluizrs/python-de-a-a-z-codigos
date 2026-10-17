"""Exercício 3: ``flatten`` recursivo com ``yield from``.

``flatten(items)`` entrega, em ordem, os itens folha de uma estrutura
aninhada de listas, tuplas, conjuntos... qualquer iterável, EXCETO
``str`` e ``bytes`` (tratados como folhas, senão a recursão não acaba).

Implemente também ``depth_of(items)``: profundidade máxima de
aninhamento (``[]`` e ``[1]`` têm profundidade 1; ``[[1]]``, 2;
uma folha pura, como ``5``, 0).

Dicas:
* Use ``collections.abc.Iterable`` para testar se algo é iterável.
* ``yield from flatten(item)`` delega ao subgerador.

Exemplo: ``list(flatten([1, [2, (3, "ab")], 4])) == [1, 2, 3, "ab", 4]``
"""


def flatten(items):
    raise NotImplementedError


def depth_of(items):
    raise NotImplementedError
