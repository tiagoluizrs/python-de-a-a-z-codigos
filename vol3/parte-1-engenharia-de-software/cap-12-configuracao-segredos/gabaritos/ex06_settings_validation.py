"""Gabarito do exercício 6."""


class ConfigError(Exception):
    def __init__(self, problems):
        super().__init__("configuração inválida: " + "; ".join(problems))
        self.problems = problems


def validate_settings(settings, schema):
    problems, result = [], {}
    for name, rules in schema.items():
        if name not in settings:
            if "default" in rules:
                result[name] = rules["default"]
            elif rules.get("required", False):
                problems.append(f"{name}: obrigatório")
            continue
        value = settings[name]
        expected = rules.get("type")
        if expected is not None:
            wrong = not isinstance(value, expected) or (expected is int and isinstance(value, bool))
            if expected is float and isinstance(value, int) and not isinstance(value, bool):
                wrong = False
            if wrong:
                problems.append(f"{name}: esperado {expected.__name__}, recebido {type(value).__name__}")
                continue
        if "min" in rules and value < rules["min"]:
            problems.append(f"{name}: menor que {rules['min']}")
        if "max" in rules and value > rules["max"]:
            problems.append(f"{name}: maior que {rules['max']}")
        if "choices" in rules and value not in rules["choices"]:
            problems.append(f"{name}: valor fora de {list(rules['choices'])}")
        result[name] = value
    problems += [f"{name}: chave desconhecida" for name in sorted(set(settings) - set(schema))]
    if problems:
        raise ConfigError(problems)
    return result


def describe(settings, secret_keys=()):
    return ", ".join(f"{key}={'***' if key in secret_keys else value}" for key, value in sorted(settings.items()))
