"""sys.monitoring: observar a execução com baixo custo."""
import sys
import timeit

mon = sys.monitoring
TOOL = mon.PROFILER_ID

calls = []


def on_start(code, offset):
    calls.append(code.co_name)


mon.use_tool_id(TOOL, "demo")
mon.register_callback(TOOL, mon.events.PY_START, on_start)
mon.set_events(TOOL, mon.events.PY_START)


def a():
    b()
    b()


def b():
    c()


def c():
    pass


a()
mon.set_events(TOOL, 0)                              # desliga
print(calls)

# Eventos de linha
lines = []


def on_line(code, line):
    if code.co_name == "work":
        lines.append(line)


mon.register_callback(TOOL, mon.events.LINE, on_line)
mon.set_events(TOOL, mon.events.LINE)


def work():
    x = 1
    for i in range(2):
        x += i
    return x


work()
mon.set_events(TOOL, 0)
print(lines)

# DISABLE: o callback pode desligar o evento naquele ponto (custo zero depois)
seen = []


def once(code, offset):
    seen.append(code.co_name)
    return mon.DISABLE


mon.register_callback(TOOL, mon.events.PY_START, once)
mon.set_events(TOOL, mon.events.PY_START)
for _ in range(5):
    c()
mon.set_events(TOOL, 0)
print("c observada:", seen.count("c"), "vez(es) apesar de 5 chamadas")
mon.restart_events()
mon.free_tool_id(TOOL)

# Custo: sem monitoramento x com callback em cada chamada
def loop(n):
    for _ in range(n):
        c()


plain = min(timeit.repeat(lambda: loop(20_000), number=1, repeat=5))
mon.use_tool_id(TOOL, "cost")
mon.register_callback(TOOL, mon.events.PY_START, lambda code, offset: None)
mon.set_events(TOOL, mon.events.PY_START)
traced = min(timeit.repeat(lambda: loop(20_000), number=1, repeat=5))
mon.set_events(TOOL, 0)
mon.free_tool_id(TOOL)
print(f"20 mil chamadas: sem monitor {plain * 1e3:.2f} ms | com callback {traced * 1e3:.2f} ms ({traced / plain:.1f}x)")
