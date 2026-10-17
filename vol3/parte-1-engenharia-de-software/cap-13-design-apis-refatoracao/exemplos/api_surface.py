"""A superfície pública de um módulo: o que você promete manter."""
import inspect
import types

module = types.ModuleType("mylib")
module.__dict__["__name__"] = "mylib"
exec("""
__all__ = ["connect", "Client"]

def connect(url, *, timeout=10):
    \"\"\"Abre uma conexão.\"\"\"

def _helper():
    pass

class Client:
    def __init__(self, url):
        pass

    def get(self, path):
        pass

    def _internal(self):
        pass

def not_exported():
    pass
""", module.__dict__)

print("__all__ (a promessa):", module.__all__)
print("o que `from mylib import *` traz:", [n for n in module.__all__])
print("público por convenção (sem _):", sorted(n for n in vars(module) if not n.startswith("_") and callable(vars(module)[n])))
print("\nassinaturas prometidas:")
for name in module.__all__:
    print(f"  {name}{inspect.signature(getattr(module, name))}")
print("regra: o que está em __all__ (e documentado) é API; todo o resto pode mudar sem aviso")
