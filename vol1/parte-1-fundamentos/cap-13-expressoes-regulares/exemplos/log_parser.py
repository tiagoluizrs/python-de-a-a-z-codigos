"""Extrair campos de logs com grupos nomeados e VERBOSE."""
import re

LOG = re.compile(
    r"""
    ^(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})  # data e hora
    \s+\[(?P<level>[A-Z]+)\]                         # nível
    \s+(?P<message>.*)$                              # resto da linha
    """,
    re.VERBOSE | re.MULTILINE,
)

SAMPLE = """\
2026-10-12 14:03:22 [INFO] server started on port 8000
garbage line without structure
2026-10-12 14:03:25 [ERROR] db: connection lost (retry 1/3)
2026-10-12T14:03:30 [WARNING] disk at 91%
"""

for m in LOG.finditer(SAMPLE):
    print(m.groupdict())
