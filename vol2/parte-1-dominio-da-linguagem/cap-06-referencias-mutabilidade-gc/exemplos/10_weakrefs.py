"""Referências fracas: observar sem manter vivo."""
import gc
import weakref
from weakref import WeakSet, WeakValueDictionary


class Image:
    def __init__(self, path: str) -> None:
        self.path = path
        self.pixels = bytearray(1000)

    def __repr__(self) -> str:
        return f"Image({self.path!r})"


# 1) weakref.ref e o callback
img = Image("a.png")
ref = weakref.ref(img, lambda r: print("  callback: objeto morreu"))
print("ref():", ref())
del img
print("ref() depois do del:", ref())

# 2) Nem todo tipo aceita referência fraca
for value in (Image("x"), [1], {1}, "text", 42, (1, 2)):
    try:
        weakref.ref(value)
        print(f"{type(value).__name__:<6} aceita weakref")
    except TypeError as exc:
        print(f"{type(value).__name__:<6} -> {exc}")


# 3) Cache que não prende memória: WeakValueDictionary
_loads = 0
cache: WeakValueDictionary[str, Image] = WeakValueDictionary()


def load(path: str) -> Image:
    global _loads
    obj = cache.get(path)
    if obj is None:
        _loads += 1
        obj = Image(path)
        cache[path] = obj
    return obj


first = load("logo.png")
second = load("logo.png")
print("\nmesma instância:", first is second, "| cargas:", _loads)
print("no cache:", len(cache))
del first, second
print("no cache após soltar os nomes:", len(cache))
load("logo.png")                       # recarrega: o cache esvaziou
print("cargas:", _loads)

# 4) Observadores em WeakSet: sem cancelar inscrição manualmente
class Listener:
    def __init__(self, name: str) -> None:
        self.name = name

    def notify(self, event: str) -> None:
        print(f"  {self.name} recebeu {event}")


listeners: WeakSet[Listener] = WeakSet()
one, two = Listener("um"), Listener("dois")
listeners.update((one, two))
for item in sorted(listeners, key=lambda x: x.name):
    item.notify("e1")
del two
gc.collect()
print("inscritos agora:", len(listeners))

# 5) Método vinculado: use WeakMethod
class Owner:
    def hello(self) -> str:
        return "olá"


owner = Owner()
wm = weakref.WeakMethod(owner.hello)
print("\nWeakMethod:", wm()())
del owner
print("depois do del:", wm())
broken = weakref.ref(Owner().hello)     # o método vinculado morre já
print("weakref.ref de método vinculado:", broken())
