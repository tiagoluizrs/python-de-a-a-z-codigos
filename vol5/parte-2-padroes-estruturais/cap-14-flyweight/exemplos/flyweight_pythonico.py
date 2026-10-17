"""Flyweight em Python: __slots__, dataclass(slots=True), interning, functools.cache e WeakValueDictionary."""
import functools
import gc
import sys
import time
import tracemalloc
import weakref
from collections import namedtuple
from dataclasses import dataclass


def memory_of(build):
    tracemalloc.start()
    before = tracemalloc.get_traced_memory()[0]
    result = build()
    used = tracemalloc.get_traced_memory()[0] - before
    tracemalloc.stop()
    return used, result


# --- 1. o custo de UM objeto: a instância com __dict__ contra __slots__, dataclass(slots=True), namedtuple e tupla ---
class WithDict:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


class WithSlots:
    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


@dataclass(slots=True)
class DataSlots:
    x: float
    y: float
    z: float


Named = namedtuple("Named", "x y z")

N = 100_000
variants = [("classe comum (__dict__)", WithDict), ("__slots__", WithSlots), ("@dataclass(slots=True)", DataSlots), ("namedtuple", Named), ("tupla", lambda x, y, z: (x, y, z))]
print(f"{N:,} objetos com três floats:")
base = None
for label, make in variants:
    used, objs = memory_of(lambda: [make(i * 1.5, i * 2.5, i * 3.5) for i in range(N)])
    base = base or used
    print(f"  {label:<26} {used / N:6.0f} bytes por objeto ({used / base:4.2f} da classe comum)")
    del objs

d, s = WithDict(1, 2, 3), WithSlots(1, 2, 3)
print("\ninstância com __dict__:", sys.getsizeof(d), "bytes + o dict de atributos:", sys.getsizeof(d.__dict__), "| com __slots__:", sys.getsizeof(s), "bytes e nenhum __dict__ (hasattr: %s)" % hasattr(s, "__dict__"))
try:
    s.w = 4
except AttributeError as error:
    print("o preço do __slots__: atributos novos são recusados ->", error)

# --- 2. o flyweight por fábrica: functools.cache devolve o MESMO objeto para os mesmos argumentos ---
@dataclass(frozen=True, slots=True)
class Color:
    r: int
    g: int
    b: int


@functools.cache
def color(r, g, b):
    return Color(r, g, b)


print("\nfunctools.cache como fábrica de flyweights: color(1, 2, 3) is color(1, 2, 3) ->", color(1, 2, 3) is color(1, 2, 3))
print("estatísticas do cache:", color.cache_info())

# --- 3. interning: textos iguais compartilhando UM objeto ---
words = ["verde" + str(i % 10) for i in range(200_000)]           # 200 mil textos criados dinamicamente: 10 valores distintos
distinct_ids = len({id(w) for w in words})
interned = [sys.intern(w) for w in words]
print(f"\n{len(words):,} textos com 10 valores distintos: {distinct_ids:,} objetos distintos sem intern; {len({id(w) for w in interned})} com sys.intern")
used_plain, _p = memory_of(lambda: ["verde" + str(i % 10) for i in range(50_000)])
used_interned, _i = memory_of(lambda: [sys.intern("verde" + str(i % 10)) for i in range(50_000)])
print(f"memória de 50.000 desses textos: sem intern {used_plain / 1e6:.2f} MB | com sys.intern {used_interned / 1e6:.2f} MB")
print("os literais do código e os nomes de atributo já são internados pelo Python; os textos que vêm de arquivos, JSON e bancos NÃO: aí o intern ajuda")
small_a, small_b, big_a, big_b = int("100"), int("100"), int("5000"), int("5000")
print("inteiros pequenos (-5 a 1024 no 3.15; até 256 antes) são flyweights nativos: int(\"100\") is int(\"100\") ->", small_a is small_b, "| int(\"5000\") is int(\"5000\") ->", big_a is big_b)

# --- 4. o pool que NÃO vaza: WeakValueDictionary solta o flyweight quando ninguém mais o usa ---
class Glyph:
    def __init__(self, char):
        self.char = char


pool = weakref.WeakValueDictionary()


def glyph(char):
    obj = pool.get(char)
    if obj is None:
        obj = pool[char] = Glyph(char)
    return obj


a1, a2 = glyph("a"), glyph("a")
print("\nWeakValueDictionary: mesmo objeto para o mesmo caractere:", a1 is a2, "| no pool:", len(pool))
del a1, a2
gc.collect()
print("depois de ninguém mais usar o glifo 'a', o pool o esqueceu:", len(pool), "(um dict comum guardaria para sempre)")

leaky = {}
for i in range(1000):
    leaky[i] = Glyph(str(i))
print("um dict comum como pool cresce sem parar:", len(leaky), "glifos guardados mesmo sem uso: é o vazamento clássico do Flyweight com cache sem limite")

# --- 5. o custo de tempo: a fábrica paga uma busca por hash a cada obtenção ---
def best(fn, n=500_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


print("\ncusto de obter um objeto de cor:")
plain_slots = WithSlots
for label, fn in [("Color congelado novo", lambda: Color(1, 2, 3)), ("classe __slots__ nova", lambda: plain_slots(1, 2, 3)), ("functools.cache (acerto)", lambda: color(1, 2, 3))]:
    print(f"  {label:<26} {best(fn):5.0f} ns")
print("o flyweight troca CRIAÇÃO por BUSCA: aqui a busca (~90 ns) vence a criação de um dataclass congelado (~335 ns) e supera até uma classe simples com __slots__ (~145 ns);")
print("o ganho principal é MEMÓRIA (um objeto compartilhado em vez de milhares), e ele cresce com o TAMANHO do estado repetido")
