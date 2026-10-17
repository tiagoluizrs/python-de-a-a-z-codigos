"""Exercício 5: inspecionar a assinatura de uma função."""


def signature_report(func):
    """Descreva os parâmetros de ``func`` com ``inspect.signature``.

    Devolva uma lista de tuplas ``(nome, tipo, tem_padrao)``, na ordem
    da assinatura, onde ``tipo`` é o nome do "kind" do parâmetro
    (``"POSITIONAL_ONLY"``, ``"POSITIONAL_OR_KEYWORD"``,
    ``"VAR_POSITIONAL"``, ``"KEYWORD_ONLY"`` ou ``"VAR_KEYWORD"``).

    >>> def f(a, /, b=1, *args, c, **kw): ...
    >>> signature_report(f)[1]
    ('b', 'POSITIONAL_OR_KEYWORD', True)
    """
    raise NotImplementedError
