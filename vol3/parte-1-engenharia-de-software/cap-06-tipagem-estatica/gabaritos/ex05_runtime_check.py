"""Gabarito do exercício 5."""
import inspect
import types
import typing
from typing import Any, Literal, get_args, get_origin, get_type_hints


def conforms(value: Any, hint: Any) -> bool:
    if hint is Any:
        return True
    if hint is None or hint is type(None):
        return value is None
    origin, args = get_origin(hint), get_args(hint)
    if origin is None:
        if hint is bool:
            return isinstance(value, bool)
        if hint is int:
            return isinstance(value, int) and not isinstance(value, bool)
        if hint is float:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        return isinstance(value, hint)
    if origin is typing.Union or origin is types.UnionType:
        return any(conforms(value, arg) for arg in args)
    if origin is Literal:
        return any(value == arg and type(value) is type(arg) for arg in args)
    if origin in (list, set, frozenset):
        return isinstance(value, origin) and all(conforms(item, args[0]) for item in value)
    if origin is dict:
        return isinstance(value, dict) and all(conforms(k, args[0]) and conforms(v, args[1]) for k, v in value.items())
    if origin is tuple:
        if not isinstance(value, tuple):
            return False
        if len(args) == 2 and args[1] is Ellipsis:
            return all(conforms(item, args[0]) for item in value)
        return len(value) == len(args) and all(conforms(item, arg) for item, arg in zip(value, args))
    return isinstance(value, origin)


def check_call(func, *args, **kwargs):
    hints = get_type_hints(func)
    bound = inspect.signature(func).bind(*args, **kwargs)
    for name, value in bound.arguments.items():
        if name in hints and not conforms(value, hints[name]):
            raise TypeError(f"{name}: {value!r} não é {hints[name]}")
    result = func(*args, **kwargs)
    if "return" in hints and not conforms(result, hints["return"]):
        raise TypeError(f"retorno: {result!r} não é {hints['return']}")
    return result
