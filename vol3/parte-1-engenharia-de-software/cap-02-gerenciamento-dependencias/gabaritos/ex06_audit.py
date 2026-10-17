"""Gabarito do exercício 6."""
import re


def release(text):
    return tuple(int(part) for part in text.split("."))


def _norm(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def vulnerable(installed, advisories):
    versions = {_norm(name): (name, version) for name, version in installed.items()}
    findings = []
    for advisory in advisories:
        key = _norm(advisory["name"])
        if key in versions and release(versions[key][1]) < release(advisory["below"]):
            findings.append({"id": advisory["id"], "name": advisory["name"],
                             "installed": versions[key][1], "fix": advisory["below"]})
    return sorted(findings, key=lambda f: (f["name"], f["id"]))


def distance(a, b):
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def suspicious(candidates, popular, max_distance=1):
    popular = sorted(p.lower() for p in popular)
    result = []
    for candidate in candidates:
        name = candidate.lower()
        if name in popular:
            continue
        best = min(((distance(name, p), p) for p in popular), default=None)
        if best and best[0] <= max_distance:
            result.append((candidate, best[1]))
    return sorted(result)
