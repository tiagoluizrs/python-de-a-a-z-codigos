"""Gabarito do exercício 3."""


def predicted_int_size(n: int) -> int:
    bits = abs(n).bit_length()
    digits = max(1, -(-bits // 30))   # divisão com teto
    return 24 + 4 * digits
