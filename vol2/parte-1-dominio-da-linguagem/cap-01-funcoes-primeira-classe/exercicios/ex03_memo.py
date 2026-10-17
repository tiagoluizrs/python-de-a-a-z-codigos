"""Exercício 3: memoização manual com dict e comparação."""


def memoize(func):
    """Devolva uma função que memoriza os resultados de ``func``.

    Regras:

    * a chave do cache é a tupla de argumentos posicionais (aceite só
      argumentos posicionais hasheáveis);
    * a função devolvida tem os atributos ``cache`` (o dict),
      ``hits`` e ``misses`` (inteiros) atualizados a cada chamada.

    Lembre-se: funções aceitam atributos próprios.

    >>> square = memoize(lambda n: n * n)
    >>> square(4), square(4)
    (16, 16)
    >>> square.hits, square.misses
    (1, 1)
    """
    raise NotImplementedError


def count_calls_fib(n):
    """Fibonacci recursivo memoizado SEM decorador e SEM lru_cache.

    Devolva uma tupla ``(valor, chamadas)`` com ``chamadas`` igual ao
    número de execuções do corpo da função de fibonacci. Com um dict
    de memo, para n=30 o resultado deve ser 59 chamadas, contra
    2 692 537 do fibonacci ingênuo.
    """
    raise NotImplementedError
