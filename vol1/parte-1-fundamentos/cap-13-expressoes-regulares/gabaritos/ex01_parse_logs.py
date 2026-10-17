"""Gabarito 1: logs com grupos nomeados."""
import re

LOG = re.compile(
    r"""
    ^(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})
    \s+\[(?P<level>[A-Z]+)\]
    \s+(?P<message>.*)$
    """,
    re.VERBOSE | re.MULTILINE,
)


def parse_logs(text: str) -> list[dict[str, str]]:
    # MULTILINE faz ^ e $ valerem por linha; groupdict já dá o dict
    return [m.groupdict() for m in LOG.finditer(text)]
