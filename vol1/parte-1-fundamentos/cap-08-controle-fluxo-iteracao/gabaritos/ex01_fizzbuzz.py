"""Gabarito do exercício 1."""


def fizzbuzz(n: int, rules=((3, "Fizz"), (5, "Buzz"))) -> list[str]:
    if n < 0:
        raise ValueError("n must be >= 0")
    # validamos TODAS as regras antes do laço principal: falhar cedo
    for divisor, _ in rules:
        if divisor < 1:
            raise ValueError("divisors must be >= 1")
    result = []
    for number in range(1, n + 1):
        # concatena o texto de cada regra que se aplica
        text = "".join(word for divisor, word in rules
                       if number % divisor == 0)
        # string vazia é falsa: nenhuma regra se aplicou
        result.append(text or str(number))
    return result
