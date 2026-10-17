"""Gabarito 3: FizzBuzz com match de tuplas."""


def fizzbuzz(n: int) -> str:
    # Casamos o PAR de restos; "_" ignora o resto que não importa.
    match n % 3, n % 5:
        case 0, 0:
            return "FizzBuzz"
        case 0, _:
            return "Fizz"
        case _, 0:
            return "Buzz"
        case _:
            return str(n)
