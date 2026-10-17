"""Ciclos: o contador de referências não basta; entra o módulo gc."""
import gc
import weakref


class Node:
    def __init__(self, name: str) -> None:
        self.name = name
        self.peer = None


def make_cycle(name: str) -> weakref.ref:
    a, b = Node(name + "-a"), Node(name + "-b")
    a.peer, b.peer = b, a
    return weakref.ref(a)       # observa sem manter vivo


def make_chain(name: str) -> weakref.ref:
    a, b = Node(name + "-a"), Node(name + "-b")
    a.peer = b                  # sem volta: não há ciclo
    return weakref.ref(a)


gc.collect()                    # começa de um estado limpo
gc.disable()                    # para o coletor não interferir na demo

chain = make_chain("chain")
print("cadeia sem ciclo, depois do retorno:", chain() is None)

cycle = make_cycle("cycle")
print("ciclo, depois do retorno           :", cycle() is None)
print("gc.collect() devolveu              :", gc.collect())
print("ciclo, depois do gc.collect()      :", cycle() is None)

# Gerações, limiares e contadores
print("\nlimiares (g0, g1, g2):", gc.get_threshold())
print("contadores atuais    :", gc.get_count())
before = gc.get_count()[0]
keep = [Node(str(i)) for i in range(100)]   # 100+ rastreados vivos
print("alocações líquidas   :", gc.get_count()[0] - before)
gc.collect(0)
print("após collect(0)      :", gc.get_count())

# Quem é rastreado?
print("\nint rastreado?   ", gc.is_tracked(1))
print("str rastreada?   ", gc.is_tracked("abc"))
print("lista rastreada? ", gc.is_tracked([1]))
print("tupla de ints?   ", gc.is_tracked((1, 2)))
print("tupla com lista? ", gc.is_tracked(([], 2)))
print("Node rastreado?  ", gc.is_tracked(Node("n")))

# Estatísticas por geração
for gen, stats in enumerate(gc.get_stats()):
    print(f"geração {gen}: coletas={stats['collections']} "
          f"coletados={stats['collected']}")

# Referentes e referrers
target = Node("alvo")
holder = {"node": target}
print("\nreferentes de target :", [type(r).__name__
      for r in gc.get_referents(target)])
print("referrers de target  :", [type(r).__name__
      for r in gc.get_referrers(target) if r is holder])
gc.enable()
