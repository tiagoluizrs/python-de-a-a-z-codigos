"""Exercício 1: uma tabela de hash de endereçamento aberto."""


class LinearProbingTable:
    """Implemente um dicionário simples com sondagem linear.

    Regras:

    * comece com ``slots = 8`` posições (atributo público ``slots``);
    * a posição inicial de uma chave é ``hash(key) % slots``; em caso de
      colisão, avance de 1 em 1 (circularmente) até achar a chave ou
      uma posição vazia;
    * ao remover, deixe uma LÁPIDE (um marcador) para não quebrar a
      sondagem das outras chaves;
    * quando ``len(self) + lápides`` passar de 2/3 de ``slots``, dobre
      ``slots`` e reinsira só os itens vivos (a rehash descarta lápides);
    * ``__getitem__`` e ``__delitem__`` levantam ``KeyError`` se a chave
      não existe.

    Métodos: ``__setitem__``, ``__getitem__``, ``__delitem__``,
    ``__contains__``, ``__len__`` e ``__iter__`` (chaves, em qualquer
    ordem).
    """

    def __init__(self):
        raise NotImplementedError
