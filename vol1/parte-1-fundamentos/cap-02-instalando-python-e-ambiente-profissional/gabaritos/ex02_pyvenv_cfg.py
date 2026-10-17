"""Gabarito do exercício 2."""


def parse_pyvenv_cfg(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        # partition divide só no PRIMEIRO '=', preservando '=' no valor
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result
