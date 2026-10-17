"""strftime/strptime: diretivas, erros, locale e custo."""
import datetime as dt
import timeit

moment = dt.datetime(2026, 10, 12, 9, 30, 15, 123456, tzinfo=dt.UTC)

directives = "%Y %m %d %H %M %S %f %j %a %A %b %B %p %y %z %Z %u %w"
for directive in directives.split():
    print(f"{directive:3}", moment.strftime(directive))

print(moment.strftime("%d/%m/%Y %H:%M"), "|", f"{moment:%d/%m/%Y}")

parse = dt.datetime.strptime
print(parse("12/10/2026 09:30", "%d/%m/%Y %H:%M"))
print(parse("2026-10-12T09:30:15Z", "%Y-%m-%dT%H:%M:%S%z"))
print(repr(parse("2026-10-12", "%Y-%m-%d").tzinfo))

cases = [
    ("12/10/2026", "%Y-%m-%d"),
    ("2026-10-12 extra", "%Y-%m-%d"),
    ("31/02/2026", "%d/%m/%Y"),
    ("Out 12 2026", "%b %d %Y"),
    ("02/29", "%m/%d"),
]
for text, fmt in cases:
    try:
        parse(text, fmt)
    except ValueError as error:
        print(f"{text!r} {fmt!r}: {str(error)[:60]}")

# Ano de dois dígitos: 69-99 -> 1969-1999, 00-68 -> 2000-2068.
print(parse("69", "%y").year, parse("68", "%y").year)

# Custo (medido; varia conforme a máquina).
runs = 100_000
text = "2026-10-12 09:30:15"
candidates = {
    "strptime": lambda: parse(text, "%Y-%m-%d %H:%M:%S"),
    "fromisoformat": lambda: dt.datetime.fromisoformat(text),
    "strftime": lambda: moment.strftime("%Y-%m-%d %H:%M:%S"),
    "isoformat": lambda: moment.isoformat(),
}
for name, func in candidates.items():
    ns = timeit.timeit(func, number=runs) / runs * 1e9
    print(f"{name:14} {ns:8.0f} ns")
