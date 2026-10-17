"""Exercício 1: ANOTE estas funções para passar no ``mypy --strict``.

O corpo de cada função já está pronto e correto: o seu trabalho é escrever as
anotações (parâmetros e retorno). Pense em genéricos (``def f[T](...)``),
``Sequence``/``Iterable``/``Mapping`` em vez de ``list``/``dict`` nos parâmetros,
``Callable``, ``| None``, ``Literal``.

A correção roda ``mypy --strict`` neste arquivo e também verifica, em um arquivo
de uso, que os tipos devolvidos são os esperados (``first([1, 2])`` deve ser
``int | None``; ``apply_twice(str.upper, "a")`` deve ser ``str``; etc.).
"""


def first(items):
    return items[0] if items else None


def apply_twice(func, value):
    return func(func(value))


def count_words(text, lowercase=True):
    words = text.lower().split() if lowercase else text.split()
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


def safe_div(a, b):
    return None if b == 0 else a / b


def pairs(keys, values):
    return list(zip(keys, values, strict=True))


def log_level(name):
    """``name`` só pode ser um destes textos: "debug", "info", "warning"."""
    return {"debug": 10, "info": 20, "warning": 30}[name]
