"""Exercício 5: composição em vez de herança."""


class BoundedStack:
    """Pilha com capacidade, usando uma lista INTERNA (composição).

    * ``BoundedStack(capacity)``;
    * ``push(item)`` (``OverflowError`` se cheia), ``pop()`` e ``peek()``
      (``IndexError`` se vazia);
    * ``len(stack)``, ``bool(stack)`` (falso se vazia) e ``repr`` no formato
      ``BoundedStack([1, 2], capacity=3)``;
    * iteração do TOPO para a base: ``list(stack)`` -> ``[2, 1]``;
    * NÃO é uma subclasse de ``list`` e não expõe ``append``, ``insert`` etc.;
    * o atributo da lista deve ser "interno" (comece com ``_``).
    """

    def __init__(self, capacity):
        raise NotImplementedError
