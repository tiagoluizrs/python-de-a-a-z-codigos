"""Exercício 4: um tipo Result para falhas esperadas."""


class Ok:
    """Sucesso com ``value``. Imutável (``__slots__`` ou dataclass congelada).

    * ``is_ok`` e ``is_err``: propriedades booleanas;
    * ``unwrap()``: o valor; ``unwrap_or(default)``: o valor;
    * ``map(f)``: ``Ok(f(value))``; ``and_then(f)``: ``f(value)`` (``f`` devolve um Result);
    * ``map_err(f)``: ele mesmo;
    * igualdade por valor (``Ok(1) == Ok(1)``); ``repr``: ``Ok(1)``."""

    def __init__(self, value):
        raise NotImplementedError


class Err:
    """Falha com ``error``. Mesma interface:

    * ``unwrap()`` levanta ``RuntimeError(f"unwrap em Err: {error!r}")``;
      ``unwrap_or(default)`` devolve ``default``;
    * ``map(f)`` e ``and_then(f)``: ele mesmo (a falha se propaga);
    * ``map_err(f)``: ``Err(f(error))``; ``repr``: ``Err('x')``."""

    def __init__(self, error):
        raise NotImplementedError


def try_call(func, *args, catch=(Exception,), **kwargs):
    """``Ok(func(*args, **kwargs))`` ou ``Err(exceção)`` se levantar alguma das
    classes em ``catch``; outras exceções propagam."""
    raise NotImplementedError


def collect(results):
    """Lista de Results -> ``Ok([valores])`` se TODOS forem ``Ok``; senão, o
    PRIMEIRO ``Err``. Lista vazia: ``Ok([])``."""
    raise NotImplementedError
