"""Gabarito do exercício 4."""
import re


def _check(m, n):
    if m < 0 or n < 0:
        raise ValueError("contagem negativa")


def explosion_count(m, n):
    _check(m, n)
    return m * n


def bridge_count(m, n, bases=2):
    _check(m, n)
    return m + n + bases


def savings(m, n):
    return explosion_count(m, n) - bridge_count(m, n)


def worthwhile_pairs(max_side=10):
    return [(m, n) for m in range(1, max_side + 1) for n in range(m, max_side + 1) if savings(m, n) > 0]


def split_camel(name):
    return re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*", name)


def cartesian_candidates(names):
    suffixes_by_prefix: dict[str, set] = {}
    for name in set(names):
        words = split_camel(name)
        if len(words) == 2:
            suffixes_by_prefix.setdefault(words[0], set()).add(words[1])
    groups: dict[frozenset, list] = {}
    for prefix, suffixes in suffixes_by_prefix.items():
        groups.setdefault(frozenset(suffixes), []).append(prefix)
    result = [(tuple(sorted(prefixes)), tuple(sorted(suffixes))) for suffixes, prefixes in groups.items() if len(prefixes) >= 2 and len(suffixes) >= 2]
    return sorted(result)
