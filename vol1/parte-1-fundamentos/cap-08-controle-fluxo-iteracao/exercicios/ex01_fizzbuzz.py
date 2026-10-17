"""Exercício 1: FizzBuzz robusto e configurável."""


def fizzbuzz(n: int, rules=((3, "Fizz"), (5, "Buzz"))) -> list[str]:
    """Devolva os textos de 1 até ``n`` (inclusive).

    Para cada número, concatene o texto de TODAS as regras cujo
    divisor divide o número, na ordem das regras. Se nenhuma regra
    se aplicar, use ``str(número)``.

    Exemplos:
        ``fizzbuzz(15)[-1] == "FizzBuzz"``
        ``fizzbuzz(4, ((2, "A"), (4, "B"))) == ["1", "A", "3", "AB"]``

    Lance ``ValueError`` se ``n < 0`` ou se algum divisor for ``< 1``.
    ``n == 0`` devolve lista vazia.
    """
    raise NotImplementedError
