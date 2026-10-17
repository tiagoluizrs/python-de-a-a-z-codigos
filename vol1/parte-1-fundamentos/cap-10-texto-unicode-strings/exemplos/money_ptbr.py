"""Números e dinheiro no estilo brasileiro: locale e alternativa manual."""
import locale
from decimal import ROUND_HALF_UP, Decimal

amount = 1234567.891

# o truque clássico: formata em estilo americano e troca os símbolos
us = f"{amount:,.2f}"
print(us, us.translate(str.maketrans(",.", ".,")))


# alternativa manual, explícita e independente do sistema
def format_brl(value, symbol=True):
    cents = Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    sign = "-" if cents < 0 else ""
    whole, frac = f"{abs(cents):.2f}".split(".")
    groups = f"{int(whole):,}".replace(",", ".")
    return f"{sign}{'R$ ' if symbol else ''}{groups},{frac}"


print(format_brl(amount), format_brl(-0.5), format_brl(0.005),
      format_brl("1999.90", symbol=False))

# arredondar: float e round() surpreendem (banker's rounding + binário)
print(round(0.125, 2), round(0.135, 2), round(2.675, 2),
      f"{2.675:.2f}", f"{0.125:.2f}")
print(Decimal("2.675").quantize(Decimal("0.01"), ROUND_HALF_UP))
print(0.1 + 0.2, Decimal("0.1") + Decimal("0.2"))

# locale: correto, mas global ao processo e dependente do SO
for name in ("pt_BR.UTF-8", "Portuguese_Brazil.1252"):
    try:
        print("setlocale:", locale.setlocale(locale.LC_ALL, name))
        break
    except locale.Error:
        pass
print(locale.format_string("%.2f", amount, grouping=True))
print(locale.currency(amount, grouping=True))
print(locale.currency(-1234.5, grouping=True, symbol=False))
print(locale.localeconv()["decimal_point"],
      locale.localeconv()["mon_thousands_sep"])
print(locale.atof("1.234,56"))
print(f"{1234567:n}|{amount:.9n}")      # o tipo 'n' usa o locale atual
locale.setlocale(locale.LC_ALL, "C")
print(f"{amount:,.2f}")                # a f-string com ',' ignora o locale
print(f"{1234567:n}")
