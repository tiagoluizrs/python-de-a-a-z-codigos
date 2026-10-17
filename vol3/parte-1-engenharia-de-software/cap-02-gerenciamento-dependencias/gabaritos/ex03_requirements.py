"""Gabarito do exercício 3."""
import re

NAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")
LINE = re.compile(r"^\s*(?P<name>[^\s\[<>=!~;]+)\s*(?:\[(?P<extras>[^\]]*)\])?\s*(?P<spec>[^;]*?)\s*(?:;\s*(?P<marker>.+?))?\s*$")


def normalize_name(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_requirement(line):
    text = line.split("#", 1)[0].strip()
    if not text:
        raise ValueError("linha vazia")
    match = LINE.match(text)
    if not match or not NAME.match(match["name"]):
        raise ValueError(f"requisito inválido: {line!r}")
    if match["spec"] and not re.match(r"^[~=<>!]", match["spec"]):
        raise ValueError(f"requisito inválido: {line!r}")
    extras = sorted(e.strip() for e in (match["extras"] or "").split(",") if e.strip())
    return {"name": normalize_name(match["name"]), "extras": extras,
            "specifier": re.sub(r"\s+", "", match["spec"]), "marker": match["marker"]}


def parse_requirements(text):
    result = []
    for number, line in enumerate(text.splitlines(), 1):
        clean = line.split("#", 1)[0].strip()
        if not clean or clean.startswith("-"):
            continue
        try:
            result.append(parse_requirement(clean))
        except ValueError as error:
            raise ValueError(f"linha {number}: {error}") from None
    return result
