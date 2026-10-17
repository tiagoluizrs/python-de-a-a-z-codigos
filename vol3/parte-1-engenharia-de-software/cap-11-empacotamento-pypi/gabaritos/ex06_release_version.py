"""Gabarito do exercício 6."""
import re

FINAL = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
PRE = re.compile(r"^(\d+\.\d+\.\d+)(?:(a|b|rc)(\d+))?$")
ORDER = {"a": 0, "b": 1, "rc": 2}


def bump(version, part):
    match = FINAL.match(version)
    if not match:
        raise ValueError(f"versão final inválida: {version!r}")
    major, minor, patch = map(int, match.groups())
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"parte inválida: {part!r}")


def to_prerelease(version, kind):
    if kind not in ORDER:
        raise ValueError(f"tipo inválido: {kind!r}")
    match = PRE.match(version)
    if not match:
        raise ValueError(f"versão inválida: {version!r}")
    base, current, number = match.groups()
    if current is None:
        return f"{base}{kind}1"
    if ORDER[kind] < ORDER[current]:
        raise ValueError("não se volta a um tipo anterior")
    if kind == current:
        return f"{base}{kind}{int(number) + 1}"
    return f"{base}{kind}1"


def finalize(version):
    match = PRE.match(version)
    if not match:
        raise ValueError(f"versão inválida: {version!r}")
    return match.group(1)
