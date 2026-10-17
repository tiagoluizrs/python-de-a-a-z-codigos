"""Controles de lazy import: __lazy_modules__, filtro e modo global."""
import subprocess
import sys

# 1. __lazy_modules__: torna lazy um import comum (ponte de migracao;
#    em versoes anteriores ao 3.15 a lista e simplesmente ignorada)
__lazy_modules__ = ["colorsys"]
import colorsys
print("lista:", type(globals()["colorsys"]).__name__)


# 2. Filtro: decide, a cada 'lazy import', se ele fica lazy (True)
def keep_lazy(importer, name, fromlist):
    return name != "fractions"


sys.set_lazy_imports_filter(keep_lazy)
lazy import fractions
lazy import decimal
print("filtro:", type(globals()["fractions"]).__name__,
      type(globals()["decimal"]).__name__)
sys.set_lazy_imports_filter(None)

# 3. Modo global: 'all' deixa lazy todo import de nivel de modulo
code = ("import sys, colorsys; print(sys.get_lazy_imports(), "
        "type(globals()['colorsys']).__name__)")
for flags in ([], ["-X", "lazy_imports=all"]):
    out = subprocess.run([sys.executable, *flags, "-c", code],
                         capture_output=True, text=True)
    print(flags or "[padrao]", out.stdout.strip())
