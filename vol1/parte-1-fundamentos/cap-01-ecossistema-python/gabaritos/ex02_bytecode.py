"""Gabarito do exercício 2."""
import dis


def count_instructions(func) -> int:
    # get_instructions devolve um iterador; sum(1 for ...) conta sem criar lista
    return sum(1 for _ in dis.get_instructions(func))
