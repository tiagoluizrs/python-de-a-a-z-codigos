"""Gabarito do exercício 3."""
import re

_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def dependency_names(dependencies: list[str]) -> list[str]:
    names = []
    for requirement in dependencies:
        match = _NAME.match(requirement.strip())
        if match:
            names.append(match.group().lower())
    return names
