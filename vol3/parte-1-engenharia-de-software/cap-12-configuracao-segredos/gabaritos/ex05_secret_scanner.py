"""Gabarito do exercício 5."""
import re

PATTERNS = {
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private-key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
}
ASSIGNMENT = re.compile(r"(?i)\b(?:password|secret|token|api[_-]?key)\s*[=:]\s*[\"']([^\"']{8,})[\"']")
PLACEHOLDERS = ("changeme", "your-", "<", "${", "example")


def mask(value):
    if len(value) >= 8:
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    return "*" * len(value)


def scan_text(text):
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for kind, pattern in PATTERNS.items():
            match = pattern.search(line)
            if match:
                findings.append({"line": number, "kind": kind, "match": mask(match.group(0))})
        match = ASSIGNMENT.search(line)
        if match and not any(p in match.group(1).lower() for p in PLACEHOLDERS):
            findings.append({"line": number, "kind": "assignment", "match": mask(match.group(1))})
    return findings
