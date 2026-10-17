"""Exercício 1: detector de ciclos."""


def has_cycle(obj) -> bool:
    """Devolva True se ``obj`` participa de, ou alcança, um ciclo de referências.

    Percorra listas, tuplas, conjuntos (``set``/``frozenset``), dicionários
    (chaves e valores) e atributos de instâncias (``vars(obj)``).
    Objetos atômicos (int, str, float, bool, None, bytes) não têm filhos.

    Dica: compartilhar NÃO é ciclo. ``[x, x]`` não tem ciclo;
    ``x = []; x.append(x)`` tem. Use uma busca em profundidade guardando
    os ``id`` do caminho atual (os ancestrais) e, à parte, os ids já
    totalmente explorados, para não repetir trabalho.

    >>> a = []; a.append(a); has_cycle(a)
    True
    >>> shared = [1]; has_cycle([shared, shared])
    False
    """
    raise NotImplementedError
