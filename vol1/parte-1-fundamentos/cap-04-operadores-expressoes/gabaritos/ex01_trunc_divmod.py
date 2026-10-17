"""Gabarito do exercício 1."""


def trunc_divmod(a: int, b: int) -> tuple[int, int]:
    if b == 0:
        raise ZeroDivisionError("division by zero")
    # Com valores absolutos, // e % se comportam como o C
    quotient, remainder = divmod(abs(a), abs(b))
    if (a < 0) != (b < 0):          # sinais diferentes: quociente negativo
        quotient = -quotient
    if a < 0:                       # o resto acompanha o dividendo
        remainder = -remainder
    return quotient, remainder
