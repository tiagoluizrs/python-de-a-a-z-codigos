"""Argumentos preguiçosos x f-strings, e o custo de um log desligado."""
import io
import logging
import timeit

log = logging.getLogger("lazy")
log.addHandler(logging.NullHandler())
log.setLevel(logging.WARNING)


class Costly:
    calls = 0

    def __str__(self):
        Costly.calls += 1
        return "valor"


log.debug("a %s", Costly())
print("__str__ chamado com %s e nível desligado:", Costly.calls)
log.debug(f"a {Costly()}")
print("__str__ chamado com f-string e nível desligado:", Costly.calls)
log.setLevel(logging.DEBUG)
log.debug("a %s", Costly())
print("__str__ chamado com %s e nível ligado:", Costly.calls)

# Para dados caros de calcular, proteja com isEnabledFor
def expensive():
    expensive.calls += 1
    return "resumo"


expensive.calls = 0
log.setLevel(logging.WARNING)
log.debug("estado: %s", expensive())                       # expensive() roda mesmo assim!
if log.isEnabledFor(logging.DEBUG):
    log.debug("estado: %s", expensive())
print("expensive() chamado:", expensive.calls, "vez (só a primeira, desprotegida)")

# Custos medidos
log.setLevel(logging.WARNING)
n = 500_000
cases = [
    ("debug desligado, args", lambda: log.debug("v %s", 1)),
    ("debug desligado, f-string", lambda: log.debug(f"v {1}")),
    ("isEnabledFor(DEBUG)", lambda: log.isEnabledFor(logging.DEBUG)),
]
print("ns por chamada:")
for label, fn in cases:
    print(f"  {label:<28}{min(timeit.repeat(fn, number=n, repeat=3)) / n * 1e9:8.1f}")

# E quando o nível está ligado?
m = 50_000
root = logging.getLogger("cost.on")
root.setLevel(logging.INFO)
root.propagate = False
fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
results = []
for label, handler in [("NullHandler", logging.NullHandler()), ("StringIO + formato", logging.StreamHandler(io.StringIO()))]:
    handler.setFormatter(fmt)
    root.handlers = [handler]
    results.append((label, min(timeit.repeat(lambda: root.info("v %s", 1), number=m, repeat=3)) / m * 1e6))
print("info ligado (us por chamada):")
for label, microseconds in results:
    print(f"  {label:<22}{microseconds:8.1f}")
