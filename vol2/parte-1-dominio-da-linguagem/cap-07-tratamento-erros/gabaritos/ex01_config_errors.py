"""Gabarito do exercício 1."""


class ConfigError(Exception):
    """Base de todos os erros desta biblioteca."""


class InvalidValueError(ConfigError):
    def __init__(self, line_no, key, raw):
        super().__init__(line_no, key, raw)        # args completos (bom para pickle)
        self.line_no, self.key, self.raw = line_no, key, raw

    def __str__(self):
        return f"linha {self.line_no}: valor inválido para {self.key!r}: {self.raw!r}"


class MissingSeparatorError(ConfigError):
    def __init__(self, line_no, line):
        super().__init__(line_no, line)
        self.line_no, self.line = line_no, line

    def __str__(self):
        return f"linha {self.line_no}: falta '=' em {self.line!r}"


def parse_settings(lines):
    settings = {}
    for line_no, line in enumerate(lines, start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        key, separator, raw = text.partition("=")
        if not separator:
            raise MissingSeparatorError(line_no, text)
        key, raw = key.strip(), raw.strip()
        try:
            settings[key] = int(raw)
        except ValueError as error:
            raise InvalidValueError(line_no, key, raw) from error   # encadeia
    return settings
