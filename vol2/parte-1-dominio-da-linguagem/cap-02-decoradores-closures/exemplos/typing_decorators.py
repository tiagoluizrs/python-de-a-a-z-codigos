"""Decoradores e tipagem: ParamSpec, TypeVar e a sintaxe do 3.12."""
import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar, reveal_type  # noqa: F401


# Sintaxe moderna (PEP 695, Python 3.12+): parâmetros de tipo
# declarados direto na função. **P é um ParamSpec; R, um TypeVar.
def logged[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@logged
def add(a: int, b: int = 0) -> int:
    return a + b


print(add(1, b=2))
print(type(logged.__type_params__[0]).__name__,
      type(logged.__type_params__[1]).__name__)


# Fábrica de decoradores tipada
def retry[**P, R](times: int) -> Callable[[Callable[P, R]],
                                          Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for _ in range(times - 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    pass
            return func(*args, **kwargs)
        return wrapper
    return decorator


@retry(times=2)
def parse(text: str) -> int:
    return int(text)


print(parse("42"))


# Mudando a assinatura: o wrapper devolve R | None
def or_none[**P, R](func: Callable[P, R]) -> Callable[P, R | None]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return func(*args, **kwargs)
        except Exception:
            return None
    return wrapper


print(or_none(int)("x"), or_none(int)("7"))


# A sintaxe antiga (antes do 3.12) continua válida
P = ParamSpec("P")
R = TypeVar("R")


def legacy(func: Callable[P, R]) -> Callable[P, R]:
    return func


print(legacy(len)("abc"))
