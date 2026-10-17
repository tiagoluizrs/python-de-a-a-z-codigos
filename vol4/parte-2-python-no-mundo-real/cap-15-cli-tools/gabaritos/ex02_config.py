"""Gabarito do exercício 2."""


def resolve(name, flags, env, file_values, defaults, convert=str, prefix="APP_"):
    if flags.get(name) is not None:
        return flags[name], "flag"
    key = prefix + name.upper()
    if key in env:
        try:
            return convert(env[key]), "env"
        except ValueError:
            raise ValueError(f"{key}: valor inválido {env[key]!r}") from None
    if name in file_values:
        return file_values[name], "arquivo"
    if name in defaults:
        return defaults[name], "padrão"
    raise KeyError(name)


def resolve_all(names, flags, env, file_values, defaults, converters=None):
    converters = converters or {}
    values, origins = {}, {}
    for name in names:
        values[name], origins[name] = resolve(name, flags, env, file_values, defaults, converters.get(name, str))
    return values, origins
