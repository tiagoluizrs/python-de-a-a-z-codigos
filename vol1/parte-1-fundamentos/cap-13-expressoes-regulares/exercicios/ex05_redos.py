"""Exercício 5: consertar um padrão vulnerável a ReDoS."""
import re

# Aceita texto formado por palavras separadas por no máximo um
# espaço em branco (e opcionalmente um espaço no fim). Vulnerável:
# com "a" * 30 + "!" o Python leva minutos.
VULNERABLE = re.compile(r"^(\w+\s?)*$")


def build_safe_pattern() -> re.Pattern:
    """Devolva um padrão compilado que aceita EXATAMENTE as mesmas
    strings que ``VULNERABLE`` (use ``search`` para comparar), mas sem
    backtracking exponencial.

    Dica: a ambiguidade nasce de ``\\w+`` dentro de um ``*``: a mesma
    sequência de letras pode ser repartida em vários ``\\w+``. Torne a
    divisão única exigindo que o separador seja obrigatório entre as
    repetições. Cuidado com a string vazia.
    """
    raise NotImplementedError
