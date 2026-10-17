"""Gabarito 6: sub com função e validação de calendário."""
import re
from datetime import date

DATE_BR = re.compile(r"(?<!\d)(\d{2})/(\d{2})/(\d{4})(?!\d)")


def dates_to_iso(text: str) -> str:
    def convert(m: re.Match) -> str:
        day, month, year = map(int, m.groups())
        try:
            return date(year, month, day).isoformat()
        except ValueError:      # dia 31 de fevereiro etc.
            return m[0]

    return DATE_BR.sub(convert, text)
