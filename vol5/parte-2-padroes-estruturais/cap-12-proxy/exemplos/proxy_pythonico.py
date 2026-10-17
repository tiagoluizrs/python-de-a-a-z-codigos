"""Proxy em Python: __getattr__ para delegar, property e descritores para controlar atributos, e weakref.proxy da biblioteca padrão."""
import functools
import gc
import time
import weakref


# --- 1. o proxy genérico: __getattr__ repassa TUDO, sem repetir método por método ---
class LazyProxy:
    def __init__(self, factory):
        object.__setattr__(self, "_factory", factory)
        object.__setattr__(self, "_target", None)

    def _load(self):
        if self._target is None:
            print("    [carregando o objeto real]")
            object.__setattr__(self, "_target", self._factory())
        return self._target

    def __getattr__(self, name):                                # só é chamado para nomes que a instância NÃO tem
        return getattr(self._load(), name)

    def __setattr__(self, name, value):
        setattr(self._load(), name, value)


class Report:
    def __init__(self):
        self.rows = [1, 2, 3]

    def total(self):
        return sum(self.rows)

    def __len__(self):
        return len(self.rows)


proxy = LazyProxy(Report)
print("o proxy existe, o objeto real não:", proxy._target)
print("primeiro uso:", proxy.total())
print("segundo uso:", proxy.total(), "(sem recarregar)")

# --- 2. a pegadinha: os MÉTODOS ESPECIAIS não passam pelo __getattr__ (o Python os procura no TIPO, não na instância) ---
for label, action in [("len(proxy)", lambda: len(proxy)), ("proxy.rows[0]", lambda: proxy.rows[0]), ("proxy[0]", lambda: proxy[0]), ("bool(proxy)", lambda: bool(proxy))]:
    try:
        print(f"  {label:<14} ->", action())
    except TypeError as error:
        print(f"  {label:<14} -> TypeError:", error)
print("proxy.rows[0] funciona (é um atributo normal); len(proxy) e proxy[0] falham: o __getattr__ não é consultado para __len__ e __getitem__")


# --- 3. a correção: declarar os métodos especiais que importam (e o __class__ para o isinstance) ---
class FullProxy(LazyProxy):
    def __len__(self):
        return len(self._load())

    def __iter__(self):
        return iter(self._load())

    def __getitem__(self, key):
        return self._load()[key]

    def __contains__(self, item):
        return item in self._load()

    def __repr__(self):
        return f"FullProxy({'<não carregado>' if self._target is None else repr(self._target)})"

    @property
    def __class__(self):                                        # faz isinstance(proxy, list) funcionar
        return type(self._load())


lst = FullProxy(lambda: [10, 20, 30])
print("\ncom os métodos especiais declarados: len =", len(lst), "| lst[1] =", lst[1], "| 20 in lst:", 20 in lst, "| list(lst) =", list(lst))
print("isinstance(lst, list):", isinstance(lst, list), "(por causa do __class__)  | type(lst).__name__:", type(lst).__name__, "(o tipo real continua FullProxy)")

# --- 4. a biblioteca padrão: weakref.proxy (um proxy que NÃO mantém o objeto vivo) ---
class Holder:
    def hello(self):
        return "olá"


obj = Holder()
ref = weakref.proxy(obj)
print("\nweakref.proxy:", ref.hello(), "| tipo:", type(ref).__name__)
del obj
gc.collect()
try:
    ref.hello()
except ReferenceError as error:
    print("depois de apagar o objeto, o proxy fraco avisa:", error)


# --- 5. controlar ATRIBUTOS: property (um proxy de um atributo) e descritores ---
class Account:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):                                          # só leitura: o "proxy de proteção" de um atributo
        return self._balance


acc = Account(100)
try:
    acc.balance = 5
except AttributeError as error:
    print("\nproperty sem setter protege o atributo:", error)


class lazy:
    """Descritor SEM dados (só __get__): calcula na primeira leitura e guarda no __dict__ da instância; as próximas leituras nem passam por aqui."""

    def __init__(self, fn):
        self.fn, self.name = fn, fn.__name__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        value = self.fn(obj)
        obj.__dict__[self.name] = value                         # a instância passa a ter o atributo: acesso direto daqui em diante
        return value


class Data:
    loads = 0

    @lazy
    def rows(self):
        Data.loads += 1
        return list(range(1000))

    @functools.cached_property                                   # a mesma ideia, na biblioteca padrão
    def total(self):
        return sum(self.rows)


d = Data()
print("antes de usar, 'rows' em __dict__?", "rows" in d.__dict__, "| depois:", (d.rows is d.rows, "rows" in d.__dict__), "| cargas:", Data.loads, "| total:", d.total)


# --- 6. o custo ---
def best(fn, n=500_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


class Plain:
    def __init__(self):
        self.x = 1


class Prop:
    @property
    def x(self):
        return 1


plain, prop = Plain(), Prop()
px = LazyProxy(Plain)
px.x
dd = Data()
dd.rows
dd.total
print("\ncusto de ler um atributo:")
for label, fn in [("atributo normal (obj.x)", lambda: plain.x), ("property", lambda: prop.x), ("proxy com __getattr__", lambda: px.x),
                  ("descritor lazy (depois da 1ª leitura)", lambda: dd.rows), ("cached_property (depois da 1ª leitura)", lambda: dd.total)]:
    print(f"  {label:<40} {best(fn):6.0f} ns")
print("o proxy por __getattr__ paga uma busca que falha + uma chamada a cada leitura; o descritor que guarda no __dict__ deixa de ser consultado: vira atributo normal")
