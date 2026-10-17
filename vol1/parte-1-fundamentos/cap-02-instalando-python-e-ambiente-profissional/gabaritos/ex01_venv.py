"""Gabarito do exercício 1."""
import sys


def is_in_virtualenv() -> bool:
    # Dentro de um venv, sys.prefix aponta para o venv e
    # sys.base_prefix continua apontando para o Python original
    return sys.prefix != sys.base_prefix
