"""Gabarito 5: tirar a ambiguidade do padrão."""
import re

VULNERABLE = re.compile(r"^(\w+\s?)*$")


def build_safe_pattern() -> re.Pattern:
    # Original: (\w+\s?)* deixa "aaaa" ser repartido de 2**(n-1)
    # formas. Aqui o separador \s é obrigatório entre palavras, então
    # cada string tem UMA só decomposição. O grupo externo opcional
    # preserva a aceitação da string vazia.
    return re.compile(r"^(?:\w+(?:\s\w+)*\s?)?$")
