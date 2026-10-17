"""Exercício 2: primos até n com o crivo de Eratóstenes."""


def primes_up_to(n: int) -> list[int]:
    """Devolva todos os primos ``<= n``, em ordem crescente.

    Use o crivo: uma lista de booleanos ``is_prime``; para cada
    ``p`` primo com ``p * p <= n``, marque como não primos os
    múltiplos de ``p`` a partir de ``p * p`` (``range`` com passo).

    Exemplos: ``primes_up_to(10) == [2, 3, 5, 7]``,
    ``primes_up_to(1) == []``. Deve calcular ``n = 100_000``
    em bem menos de um segundo.
    """
    raise NotImplementedError
