"""Exercício 3: percorrendo a cadeia de causas."""


def describe_chain(error):
    """Liste a cadeia de ``error`` da exceção mais externa até a causa raiz.

    Cada item é ``"NomeDoTipo: mensagem"``. Siga ``__cause__`` quando existir;
    senão siga ``__context__``, EXCETO se ``__suppress_context__`` for True
    (``raise ... from None`` esconde o contexto). Pare quando não houver mais.
    """
    raise NotImplementedError
