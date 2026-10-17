"""strftime depende do locale do processo (global e frágil)."""
import datetime as dt
import locale

moment = dt.datetime(2026, 10, 12, 9, 30)
fmt = "%A, %d de %B de %Y"
print("padrão     :", moment.strftime(fmt))

# Os nomes dos locales mudam de sistema para sistema.
try:
    for name in ("pt_BR.UTF-8", "pt_BR", "Portuguese_Brazil.1252"):
        try:
            locale.setlocale(locale.LC_TIME, name)
        except locale.Error as error:
            print(f"{name:24} -> locale.Error: {error}")
        else:
            print(f"{name:24} -> {moment.strftime(fmt)}")
            break
finally:
    locale.setlocale(locale.LC_TIME, "C")   # restaura

print("restaurado :", moment.strftime(fmt))
# Em Windows, %#d remove o zero à esquerda; em Linux é %-d.
print("sem zero   :", moment.strftime("%#d"), "(Windows)")
print("portátil   :", moment.day)
