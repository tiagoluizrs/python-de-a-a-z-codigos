"""Exercício 1: parâmetros posicionais, nomeados e "restos"."""


def summarize(title, /, *numbers, precision=2, **extras):
    """Resuma uma série de números.

    - ``title``: somente posicional (não pode ser passado por nome).
    - ``*numbers``: zero ou mais números.
    - ``precision``: somente nomeado; casas decimais da média.
    - ``**extras``: pares nome=valor quaisquer, copiados para o resultado.

    Devolva um dicionário com as chaves ``title``, ``count``, ``total``,
    ``mean`` (arredondada com ``precision``; ``None`` se não houver
    números) e, além delas, todos os ``extras``.

    >>> summarize("t", 1, 2, 4, precision=1, unit="kg")
    {'title': 't', 'count': 3, 'total': 7, 'mean': 2.3, 'unit': 'kg'}
    """
    raise NotImplementedError
