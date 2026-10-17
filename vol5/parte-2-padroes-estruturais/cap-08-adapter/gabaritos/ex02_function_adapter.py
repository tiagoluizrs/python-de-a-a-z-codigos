"""Gabarito do exercício 2."""
import functools
import inspect


def adapt(fn, *, rename=None, defaults=None, convert_args=None, convert_result=None):
    rename, defaults, convert_args = dict(rename or {}), dict(defaults or {}), dict(convert_args or {})
    signature = inspect.signature(fn)
    params = signature.parameters
    for name in list(rename.values()) + list(defaults) + list(convert_args):
        if name not in params:
            raise ValueError(f"parâmetro inexistente: {name}")

    @functools.wraps(fn)
    def adapted(*args, **kwargs):
        translated = {}
        for key, value in kwargs.items():
            old = rename.get(key, key)
            if old in translated or (key in rename and old in kwargs):
                raise TypeError(f"argumento repetido: {old}")
            translated[old] = value
        given = set(signature.bind_partial(*args).arguments) | set(translated)
        for name, value in defaults.items():
            if name not in given:
                translated[name] = value
        if convert_args:
            bound = signature.bind_partial(*args, **translated)
            for name, function in convert_args.items():
                if name in bound.arguments:
                    bound.arguments[name] = function(bound.arguments[name])
            result = fn(*bound.args, **bound.kwargs)
        else:
            result = fn(*args, **translated)
        return convert_result(result) if convert_result else result

    return adapted
