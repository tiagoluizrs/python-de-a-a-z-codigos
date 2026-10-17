"""sub com função: dd/mm/aaaa para ISO, preservando datas inválidas."""
import re
from datetime import date

DATE_BR = re.compile(r"\b(?P<d>\d{2})/(?P<m>\d{2})/(?P<y>\d{4})\b")


def to_iso(m: re.Match) -> str:
    try:
        return date(int(m["y"]), int(m["m"]), int(m["d"])).isoformat()
    except ValueError:
        return m[0]       # 31/02/2026 não existe: deixa como está


text = "Pago em 12/10/2026, vence 31/02/2026 e 05/11/2026."
print(DATE_BR.sub(to_iso, text))
print(DATE_BR.sub(r"\g<y>-\g<m>-\g<d>", text))   # sem validar
