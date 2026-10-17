"""Gabarito do exercício 1."""
import re

SECTIONS = {"Args", "Returns", "Raises", "Example", "Examples"}


def _indent(line):
    return len(line) - len(line.lstrip())


def _entries(lines):
    entries, name, parts = {}, None, []
    base = min((_indent(l) for l in lines if l.strip()), default=0)
    for line in lines:
        if not line.strip():
            continue
        if _indent(line) == base:
            if name is not None:
                entries[name] = " ".join(parts)
            head, _, rest = line.strip().partition(":")
            name, parts = head.strip(), ([rest.strip()] if rest.strip() else [])
        else:
            parts.append(line.strip())
    if name is not None:
        entries[name] = " ".join(parts)
    return entries


def parse_google_docstring(text):
    lines = text.splitlines()
    result = {"summary": lines[0].strip() if lines else "", "description": "", "args": {}, "arg_types": {}, "returns": "", "raises": {}, "example": ""}
    sections, current, buffer = {}, None, []
    description = []
    for line in lines[1:]:
        title = line.strip()[:-1] if line.strip().endswith(":") and not line.startswith(" ") else None
        if title in SECTIONS:
            if current:
                sections[current] = buffer
            current, buffer = title, []
            continue
        (buffer if current else description).append(line)
    if current:
        sections[current] = buffer
    result["description"] = "\n".join(description).strip("\n").strip()
    raw_args = _entries(sections.get("Args", []))
    for key, value in raw_args.items():
        match = re.match(r"(\S+)\s*\((.+)\)$", key)
        if match:
            result["args"][match.group(1)] = value
            result["arg_types"][match.group(1)] = match.group(2)
        else:
            result["args"][key] = value
    result["returns"] = " ".join(l.strip() for l in sections.get("Returns", []) if l.strip())
    result["raises"] = _entries(sections.get("Raises", []))
    example_lines = sections.get("Example", sections.get("Examples", []))
    base = min((_indent(l) for l in example_lines if l.strip()), default=0)
    result["example"] = "\n".join(l[base:] if l.strip() else "" for l in example_lines).strip("\n")
    return result
