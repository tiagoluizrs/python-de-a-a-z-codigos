"""Exercício 4: chaves compostas e __setitem__."""


class Grid:
    """Grade ``rows`` x ``cols`` de números, inicialmente zero.

    * ``g[r, c]`` lê e ``g[r, c] = v`` escreve (tupla como chave);
    * ``g[r]`` devolve uma CÓPIA da linha (lista);
    * posição fora da grade levanta ``IndexError`` (inclusive índices
      negativos que passem do tamanho; índices negativos válidos funcionam);
    * ``len(g)`` é o número de linhas;
    * ``v in g`` diz se algum célula vale ``v``;
    * ``g == outro`` compara o conteúdo (``NotImplemented`` para outros tipos).
    """

    def __init__(self, rows, cols):
        raise NotImplementedError
