"""Tokenizador com finditer e grupos nomeados (lastgroup)."""
import re

TOKEN = re.compile(
    r"""
    (?P<NUMBER>\d+(?:\.\d+)?)
  | (?P<IDENT>[A-Za-z_]\w*)
  | (?P<OP>[-+*/^=])
  | (?P<LPAREN>\()
  | (?P<RPAREN>\))
  | (?P<SKIP>\s+)
  | (?P<ERROR>.)
    """,
    re.VERBOSE,
)


def tokenize(source: str):
    for m in TOKEN.finditer(source):
        kind = m.lastgroup
        if kind == "SKIP":
            continue
        if kind == "ERROR":
            raise ValueError(f"unexpected {m[0]!r} at {m.start()}")
        yield kind, m[0]


print(list(tokenize("rate = (price + 2.5) * qty")))
try:
    list(tokenize("a $ b"))
except ValueError as exc:
    print("erro:", exc)

# Ordem importa: a primeira alternativa que casa vence
print(re.findall(r"\d|\d+\.\d+", "3.14"))
print(re.findall(r"\d+\.\d+|\d", "3.14"))
