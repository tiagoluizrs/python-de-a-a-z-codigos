"""lazy import (PEP 810, novo no Python 3.15)."""
import sys
import types

lazy import colorsys
lazy from fractions import Fraction

# Cuidado: ler o NOME (proxy = colorsys) ja materializa o import.
# globals() devolve o proxy sem materializar.
print(type(globals()["colorsys"]).__name__, globals()["colorsys"])
print(type(globals()["colorsys"]) is types.LazyImportType)
print("colorsys carregado?", "colorsys" in sys.modules)
print("registrado como pendente?", "colorsys" in sys.lazy_modules)

# Primeiro uso: o import acontece agora
print(colorsys.rgb_to_hsv(0, 0, 1))
print(type(globals()["colorsys"]).__name__)
print("colorsys carregado?", "colorsys" in sys.modules)

# 'from' tem um proxy por nome; so o usado e materializado
print(type(globals()["Fraction"]).__name__)
print(Fraction(3, 6))
print(type(globals()["Fraction"]).__name__)

# Modulo inexistente: o erro so aparece no primeiro uso
lazy import module_that_does_not_exist
print("importou sem erro")
try:
    module_that_does_not_exist
except ImportError as exc:
    print(type(exc).__name__, "|", exc)
    print("causa:", exc.__cause__)

print("modo global:", sys.get_lazy_imports())
