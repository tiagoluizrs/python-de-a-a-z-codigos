"""zoneinfo: banco de dados IANA e o erro no Windows sem tzdata."""
import datetime as dt
import zoneinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

sao_paulo = ZoneInfo("America/Sao_Paulo")
print(repr(sao_paulo), sao_paulo.key)
print("cache:", ZoneInfo("America/Sao_Paulo") is sao_paulo)
print("fusos conhecidos:", len(zoneinfo.available_timezones()))
print("TZPATH:", zoneinfo.TZPATH)

# Chaves erradas: dois erros diferentes.
for key in ("America/Nowhere", "../etc"):
    try:
        ZoneInfo(key)
    except ZoneInfoNotFoundError as error:
        print("NotFound :", error, "| é KeyError:",
              isinstance(error, KeyError))
    except ValueError as error:
        print("ValueError:", error)


def load_zone(key: str) -> ZoneInfo:
    """Carrega um fuso com uma mensagem de erro que ajuda."""
    try:
        return ZoneInfo(key)
    except ZoneInfoNotFoundError as error:
        raise LookupError(
            f"fuso {key!r} não encontrado. Se o nome está certo, o "
            "sistema não tem o banco IANA (comum no Windows): "
            "instale o pacote 'tzdata' (pip install tzdata)."
        ) from error


try:
    load_zone("Mars/Olympus_Mons")
except LookupError as error:
    print(error)

# O offset de um mesmo fuso muda com a data (regra histórica).
for year in (2018, 2019, 2026):
    moment = dt.datetime(year, 1, 15, 12, tzinfo=sao_paulo)
    print(year, moment.utcoffset(), moment.tzname(), moment.dst())
