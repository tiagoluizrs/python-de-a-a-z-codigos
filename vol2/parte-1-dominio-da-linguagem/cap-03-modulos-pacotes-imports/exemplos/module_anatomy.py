"""O que e um modulo: um objeto com um namespace."""
import math
import types

print(type(math))                      # <class 'module'>
print(math.__name__, math.__doc__[:40])
print(math.__spec__.origin)            # 'built-in' ou caminho

import colorsys
print(colorsys.__file__.rsplit("\\", 1)[-1])
print(sorted(k for k in vars(colorsys) if k.startswith("__")))
print(colorsys.__dict__["rgb_to_hsv"] is colorsys.rgb_to_hsv)

# Um modulo e so um objeto: da para criar um na mao.
virtual = types.ModuleType("virtual", "Modulo criado em memoria.")
virtual.answer = 42
exec("def double(x): return x * 2", virtual.__dict__)
print(virtual.double(virtual.answer), virtual.__doc__)
print(virtual.__file__ if hasattr(virtual, "__file__") else "sem __file__")

# Atributos do modulo que esta rodando agora
print(__name__)                        # '__main__'
print(__doc__.splitlines()[0])
print(__package__, __spec__)           # None None (rodou como script)
