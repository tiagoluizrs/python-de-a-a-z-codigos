"""Exercício 2: verificar especificadores de versão."""


def release(text):
    """``"1.2.3"`` -> ``(1, 2, 3)`` (já pronta; só versões numéricas)."""
    return tuple(int(part) for part in text.split("."))


def _pad(a, b):
    size = max(len(a), len(b))
    return a + (0,) * (size - len(a)), b + (0,) * (size - len(b))


def satisfies(version, specifier):
    """``True`` se ``version`` (``"2.7.3"``, só números e pontos) satisfaz
    ``specifier``: cláusulas separadas por vírgula, todas devem valer.

    Operadores: ``==``, ``!=``, ``>=``, ``<=``, ``>``, ``<``; ``==2.*`` (e
    ``!=2.*``) casam pelo prefixo; ``~=2.2`` é ``>=2.2,==2.*`` e ``~=2.2.1``
    é ``>=2.2.1,==2.2.*`` (todos os componentes menos o último fixados).
    Zeros finais não contam (``1.0 == 1``). Especificador vazio aceita tudo.
    Cláusula inválida levanta ``ValueError``. Espaços ao redor são ignorados.
    """
    raise NotImplementedError
