"""Gabarito do exercício 5."""
import re


def parse_changelog(text):
    releases, release, section = [], None, None
    for line in text.splitlines():
        header = re.match(r"^##\s+\[([^\]]+)\](?:\s*-\s*(\d{4}-\d{2}-\d{2}))?", line)
        if header:
            release = {"version": header.group(1), "date": header.group(2), "sections": {}}
            releases.append(release)
            section = None
            continue
        sec = re.match(r"^###\s+(.+?)\s*$", line)
        if sec and release is not None:
            section = sec.group(1)
            release["sections"][section] = []
            continue
        item = re.match(r"^-\s+(.*\S)\s*$", line)
        if item and release is not None and section is not None:
            release["sections"][section].append(item.group(1))
    return releases


def next_version(current, sections):
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", current)
    if not match:
        raise ValueError(f"versão inválida: {current!r}")
    major, minor, patch = map(int, match.groups())
    items = [item for values in sections.values() for item in values]
    if any(item.startswith("BREAKING") for item in items) or sections.get("Removed"):
        return f"{major + 1}.0.0"
    if sections.get("Added"):
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"
