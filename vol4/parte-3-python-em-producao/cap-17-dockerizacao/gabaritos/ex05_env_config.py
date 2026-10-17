"""Gabarito do exercício 5."""

_TRUE, _FALSE = {"1", "true", "yes", "on"}, {"0", "false", "no", "off"}


class ConfigError(Exception):
    def __init__(self, problems):
        self.problems = problems
        super().__init__("; ".join(problems))


def _convert(name, text, kind):
    if kind is bool:
        low = text.strip().lower()
        if low in _TRUE:
            return True
        if low in _FALSE:
            return False
        raise ValueError
    return kind(text)


def load_config(env, spec):
    values, problems = {}, []
    for name, options in spec.items():
        kind = options.get("type", str)
        file_key = name + "_FILE"
        if name in env and file_key in env:
            problems.append(f"{name}: defina {name} ou {file_key}, não os dois")
            continue
        if name in env:
            raw = env[name]
        elif file_key in env:
            raw = options["read_file"](env[file_key]).rstrip("\r\n")
        elif "default" in options:
            values[name] = options["default"]
            continue
        else:
            problems.append(f"{name}: obrigatória")
            continue
        try:
            values[name] = _convert(name, raw, kind)
        except ValueError:
            problems.append(f"{name}: valor inválido {raw!r} para {kind.__name__}")
    if problems:
        raise ConfigError(problems)
    return values


def describe(config, spec):
    return "\n".join(f"{name}={'***' if spec[name].get('secret') else config[name]}" for name in spec)
