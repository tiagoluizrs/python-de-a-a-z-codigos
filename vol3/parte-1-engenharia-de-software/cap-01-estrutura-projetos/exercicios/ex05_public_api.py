"""Exercício 5: a API pública de um módulo."""


def public_names(module):
    """Nomes públicos de ``module`` (``types.ModuleType``), ORDENADOS.

    Se o módulo define ``__all__``, é ele (a lista, ordenada). Senão: nomes que
    não começam com ``_`` e que NÃO são módulos importados (ignore valores que
    sejam ``types.ModuleType``)."""
    raise NotImplementedError


def broken_exports(module):
    """Nomes listados em ``__all__`` que NÃO existem no módulo (ordenados).
    Módulo sem ``__all__`` devolve ``[]``."""
    raise NotImplementedError


def star_import_names(module):
    """O que ``from module import *`` traria: igual a ``public_names``, mas
    sem os nomes que não existem (use ``broken_exports``)."""
    raise NotImplementedError
