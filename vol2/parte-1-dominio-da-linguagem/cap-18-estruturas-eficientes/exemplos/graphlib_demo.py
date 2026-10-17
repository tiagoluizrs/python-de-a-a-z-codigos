"""graphlib: ordem topológica e camadas paralelas."""
import graphlib

deps = {"app": {"lib", "log"}, "lib": {"core"}, "log": {"core"}, "core": set()}
print(list(graphlib.TopologicalSorter(deps).static_order()))

# Camadas: tudo que está pronto ao mesmo tempo pode rodar em paralelo
ts = graphlib.TopologicalSorter({"c": {"a", "b"}, "b": {"a"}, "d": {"a"}})
ts.prepare()
layers = []
while ts.is_active():
    ready = ts.get_ready()                         # tupla: nós sem dependências pendentes
    layers.append(sorted(ready))
    ts.done(*ready)                                # marcar como concluídos libera os próximos
print(layers)

# Ciclos
try:
    list(graphlib.TopologicalSorter({"a": {"b"}, "b": {"a"}}).static_order())
except graphlib.CycleError as error:
    print("CycleError:", error.args[0], error.args[1])

# Construção incremental
ts2 = graphlib.TopologicalSorter()
ts2.add("deploy", "test", "build")                 # deploy depende de test e build
ts2.add("test", "build")
print(list(ts2.static_order()))
