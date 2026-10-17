"""Exercício 6: comparar a API pública de duas versões de um módulo."""


def public_api(module):
    """``{nome: assinatura_texto}`` do que o módulo promete: se há ``__all__``, só
    esses nomes; senão, os nomes sem ``_`` inicial que sejam funções ou classes
    DEFINIDAS no módulo (``obj.__module__ == module.__name__``). A assinatura é
    ``str(inspect.signature(obj))`` (para classes, a do construtor; se não houver
    assinatura obtível, ``"(...)"``). Nomes de ``__all__`` ausentes do módulo são ignorados."""
    raise NotImplementedError


def diff_api(old, new):
    """Compara dois resultados de ``public_api``. Devolve ``{"removed": [nomes],
    "added": [nomes], "changed": [nomes cuja assinatura mudou]}``, cada lista em
    ordem alfabética."""
    raise NotImplementedError


def required_bump(diff):
    """Salto SemVer mínimo para a mudança: ``"major"`` se houver ``removed`` ou
    ``changed``; senão ``"minor"`` se houver ``added``; senão ``"patch"``."""
    raise NotImplementedError
