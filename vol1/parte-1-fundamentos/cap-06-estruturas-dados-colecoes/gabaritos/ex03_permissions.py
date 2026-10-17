"""Gabarito do exercício 3."""


def audit(granted: set[str], used: set[str]) -> dict[str, set[str]]:
    return {
        "unused": granted - used,    # diferença
        "missing": used - granted,   # diferença no sentido oposto
        "active": granted & used,    # interseção
    }
