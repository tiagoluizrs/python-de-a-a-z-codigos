"""Procurar segredos acidentais em texto: padrões conhecidos e atribuições suspeitas."""
import re

SAMPLE = """
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
password = "hunter2hunter2"
api_key = os.environ["API_KEY"]
token = "changeme"
-----BEGIN RSA PRIVATE KEY-----
jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dBjftJeZ4CVPmB92K27uhbUJU1p1r_wW1gFWFOEjXk"
normal = "texto qualquer sem segredo"
"""

PATTERNS = {
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private-key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    "assignment": re.compile(r"(?i)\b(password|secret|token|api[_-]?key)\s*[=:]\s*[\"']([^\"']{8,})[\"']"),
}
PLACEHOLDERS = ("changeme", "your-", "<", "${", "example", "xxx")

for number, line in enumerate(SAMPLE.splitlines(), 1):
    for kind, pattern in PATTERNS.items():
        match = pattern.search(line)
        if not match:
            continue
        if kind == "assignment" and any(p in match.group(2).lower() for p in PLACEHOLDERS):
            continue
        text = match.group(2) if kind == "assignment" else match.group(0)
        print(f"linha {number}: {kind:<15} {text[:4]}...{text[-3:]}")
