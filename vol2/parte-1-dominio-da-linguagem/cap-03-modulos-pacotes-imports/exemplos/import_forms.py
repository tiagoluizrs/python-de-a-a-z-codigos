"""As formas de import e o que cada uma vincula."""
import os.path                  # vincula 'os' (nao 'os.path')
import collections.abc as cabc  # vincula 'cabc'
from math import sqrt, pi as PI  # vincula 'sqrt' e 'PI'

print(os.path.basename("a/b.txt"), cabc.Mapping.__name__)
print(sqrt(16), round(PI, 2))
print("math" in globals(), "sqrt" in globals())   # False True

# O modulo math foi carregado mesmo assim:
import sys
print("math" in sys.modules)

# Estrela: traz o que __all__ lista (ou todos os nomes sem '_')
ns: dict = {}
exec("from geometry import *", ns)
print(sorted(k for k in ns if not k.startswith("__")))

ns2: dict = {}
exec("from colorsys import *", ns2)
print(sorted(k for k in ns2 if not k.startswith("__")))
import colorsys
print(colorsys.__all__)
