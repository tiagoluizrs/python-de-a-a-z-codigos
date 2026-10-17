"""asyncio.run/Runner, loop_factory e o que muda no 3.15."""
import asyncio
import inspect
import sys
import warnings


async def loop_name():
    return type(asyncio.get_running_loop()).__name__


async def sample():
    pass


print("laço padrão no", sys.platform, ":", asyncio.run(loop_name()))

# loop_factory: o jeito atual de escolher o tipo de laço (substitui as "políticas")
factory = asyncio.SelectorEventLoop
print("asyncio.run(..., loop_factory=SelectorEventLoop) ->", asyncio.run(loop_name(), loop_factory=factory))

# Runner: vários asyncio.run no MESMO laço (compartilham estado e contexto)
with asyncio.Runner(debug=False) as runner:
    first = runner.run(loop_name())
    second = runner.run(loop_name())
    print("Runner reutiliza o laço:", first == second)

# Obsoleto no 3.15 (remoção no 3.16)
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    asyncio.iscoroutinefunction(sample)
    asyncio.set_event_loop_policy(None)
print("avisos de depreciação:")
for warning in caught:
    print("  -", str(warning.message)[:78])
print("use inspect.iscoroutinefunction:", inspect.iscoroutinefunction(sample), "| e asyncio.run(..., loop_factory=...)")
