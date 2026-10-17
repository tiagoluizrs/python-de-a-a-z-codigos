"""Gabarito do exercício 4."""
import re

NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def parse_dotenv(text, environ=None):
    environ = environ or {}
    result = {}

    def expand(value):
        return VAR.sub(lambda m: result.get(m.group(1), environ.get(m.group(1), "")), value)

    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ValueError(f"linha {number}: faltou '='")
        key, _, rest = line.partition("=")
        key, rest = key.strip(), rest.strip()
        if not NAME.match(key):
            raise ValueError(f"linha {number}: nome inválido {key!r}")
        if rest[:1] == '"':
            end = 1
            while end < len(rest) and not (rest[end] == '"' and rest[end - 1] != "\\"):
                end += 1
            body = rest[1:end]
            value = expand(body.replace("\\n", "\n").replace('\\"', '"'))
        elif rest[:1] == "'":
            end = rest.find("'", 1)
            value = rest[1:end if end != -1 else None]
        else:
            comment = rest.find(" #")
            if comment != -1:
                rest = rest[:comment]
            value = expand(rest.strip())
        result[key] = value
    return result
