"""Gabarito 3: tokenizador com lastgroup."""
import re

TOKEN = re.compile(
    r"""
    (?P<NUMBER>\d+(?:\.\d+)?)
  | (?P<IDENT>[A-Za-z_]\w*)
  | (?P<OP>[-+*/=])
  | (?P<LPAREN>\()
  | (?P<RPAREN>\))
  | (?P<SKIP>\s+)
  | (?P<ERROR>.)           # rede de segurança: nada passa em silêncio
    """,
    re.VERBOSE | re.DOTALL,
)


def tokenize(source: str) -> list[tuple[str, str]]:
    tokens = []
    for m in TOKEN.finditer(source):
        kind = m.lastgroup
        if kind == "SKIP":
            continue
        if kind == "ERROR":
            raise ValueError(f"unexpected {m[0]!r} at position {m.start()}")
        tokens.append((kind, m[0]))
    return tokens
