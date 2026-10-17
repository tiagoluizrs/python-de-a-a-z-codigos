"""Gabarito do exercício 2."""

TRUE = {"true", "1", "yes", "on"}
FALSE = {"false", "0", "no", "off"}


def _convert(text, template, variable):
    try:
        if isinstance(template, bool):
            lowered = text.strip().lower()
            if lowered in TRUE:
                return True
            if lowered in FALSE:
                return False
            raise ValueError(lowered)
        if isinstance(template, int):
            return int(text)
        if isinstance(template, float):
            return float(text)
        if isinstance(template, list):
            return [item.strip() for item in text.split(",") if item.strip()]
        return text
    except ValueError:
        raise ValueError(f"{variable}: valor inválido {text!r}") from None


def load_settings(defaults, file_data=None, environ=None, cli=None, prefix="APP_"):
    settings = dict(defaults)
    sources = {key: "default" for key in defaults}
    for key, value in (file_data or {}).items():
        if key not in defaults:
            raise KeyError(key)
        settings[key], sources[key] = value, "file"
    for variable, text in (environ or {}).items():
        if not variable.startswith(prefix):
            continue
        key = variable[len(prefix):].lower()
        if key in defaults:
            settings[key], sources[key] = _convert(text, defaults[key], variable), "env"
    for key, value in (cli or {}).items():
        if key not in defaults:
            raise KeyError(key)
        if value is not None:
            settings[key], sources[key] = value, "cli"
    return settings, sources
