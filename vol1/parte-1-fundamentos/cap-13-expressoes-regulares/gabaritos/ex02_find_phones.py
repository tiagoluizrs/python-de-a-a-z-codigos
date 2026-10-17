"""Gabarito 2: telefones em texto livre."""
import re

PHONE = re.compile(
    r"""
    (?<!\d)                       # não começa no meio de um número
    (?:\+?55\s?)?
    \(?(?P<ddd>[1-9]\d)\)?\s?
    (?P<prefix>9\d{4}|[2-5]\d{3})
    -?(?P<suffix>\d{4})
    (?!\d)                        # nem termina no meio de outro
    """,
    re.VERBOSE,
)


def find_phones(text: str) -> list[str]:
    return [
        f"+55{m['ddd']}{m['prefix']}{m['suffix']}"
        for m in PHONE.finditer(text)
    ]
