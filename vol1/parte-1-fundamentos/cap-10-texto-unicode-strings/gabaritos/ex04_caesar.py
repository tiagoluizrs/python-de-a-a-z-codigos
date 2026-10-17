"""Gabarito do exercício 4."""
import string


def caesar(text: str, shift: int) -> str:
    shift %= 26                      # % do Python é sempre >= 0 aqui
    lower, upper = string.ascii_lowercase, string.ascii_uppercase
    # a tabela é montada uma vez; translate trabalha em C, caractere a
    # caractere, e deixa intactos os que não estão na tabela
    table = str.maketrans(
        lower + upper,
        lower[shift:] + lower[:shift] + upper[shift:] + upper[:shift],
    )
    return text.translate(table)
