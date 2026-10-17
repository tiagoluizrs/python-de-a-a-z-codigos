"""Gabarito do exercício 5."""


def line_issues(source, max_length=88):
    if not source:
        return []
    findings = []
    lines = source.split("\n")
    ends_with_newline = source.endswith("\n")
    if ends_with_newline:
        lines = lines[:-1]
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped and line[: len(line) - len(line.lstrip())].startswith("\t"):
            findings.append((number, "W191"))
        if stripped and line != line.rstrip():
            findings.append((number, "W291"))
        if not stripped and line:
            findings.append((number, "W293"))
        if len(line) > max_length:
            findings.append((number, "E501"))
    trailing = 0
    for line in reversed(lines):
        if line.strip():
            break
        trailing += 1
    if trailing and ends_with_newline and trailing < len(lines) + 1:
        if trailing == len(lines):
            findings.append((1, "W391"))
        else:
            findings.append((len(lines) - trailing + 1, "W391"))
    if not ends_with_newline:
        findings.append((len(lines), "W292"))
    return sorted(findings)
