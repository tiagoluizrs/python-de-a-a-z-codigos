"""Gabarito do exercício 2."""
import re


def _to_regex(pattern: str) -> re.Pattern:
    out, i = "", 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif c == "*":
            out += "[^/]*"
            i += 1
        elif c == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(c)
            i += 1
    return re.compile(f"^{out}(?:/.*)?$")                         # casar o diretório ignora tudo dentro dele


def is_ignored(path, patterns):
    ignored = False
    for raw in patterns:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        negate = line.startswith("!")
        if negate:
            line = line[1:].strip()
        line = line.strip("/") if line not in ("/",) else line
        if _to_regex(line).match(path):
            ignored = not negate
    return ignored


def build_context(paths, patterns):
    return [p for p in paths if not is_ignored(p, patterns)]
