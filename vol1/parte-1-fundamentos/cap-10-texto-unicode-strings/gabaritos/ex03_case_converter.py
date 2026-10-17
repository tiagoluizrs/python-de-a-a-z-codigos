"""Gabarito do exercício 3."""


def to_snake(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            prev = name[i - 1]
            nxt = name[i + 1] if i + 1 < len(name) else ""
            # nova palavra: depois de minúscula/dígito, ou no último
            # maiúsculo de uma sigla seguido de minúscula (HTTPServer)
            if prev.islower() or prev.isdigit() or (
                    prev.isupper() and nxt.islower()):
                out.append("_")
        out.append(ch.lower())
    return "".join(out)


def to_camel(name: str, pascal: bool = False) -> str:
    # split("_") deixa pedaços vazios onde havia "_" repetido: filtramos
    parts = [p for p in name.split("_") if p]
    if not parts:
        return ""
    head = parts[0].capitalize() if pascal else parts[0]
    return head + "".join(p.capitalize() for p in parts[1:])
