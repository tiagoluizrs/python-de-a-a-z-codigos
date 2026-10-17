"""concurrent.interpreters: interpretadores isolados dentro do mesmo processo."""
import time
from concurrent import interpreters

start = time.perf_counter()
interp = interpreters.create()
print(f"criar um subinterpretador: {(time.perf_counter() - start) * 1e3:.1f} ms (um processo spawn custa dezenas de ms; Cap. 16)")

interp.exec("x = 40 + 2")
print("exec define x NO subinterpretador; no principal existe 'x'?", "x" in globals())
try:
    interp.exec("print(x2)")
except interpreters.ExecutionFailed as error:
    print("erro dentro do subinterpretador volta como", type(error).__name__)

print("call(pow, 2, 10) ->", interp.call(pow, 2, 10), "(funções importáveis passam; o resultado volta)")

# o que pode atravessar a fronteira? só objetos "compartilháveis"
print("is_shareable(1), (\"a\"), ([1]) ->", interpreters.is_shareable(1), interpreters.is_shareable("a"), interpreters.is_shareable([1]))

# filas entre interpretadores
queue = interpreters.create_queue()
interp.prepare_main(queue=queue)                  # injeta o objeto no __main__ do subinterpretador
interp.exec("queue.put('olá do subinterpretador')")
print("recebido pela fila:", queue.get(timeout=5))

queue.put({"a": 1, "b": (2, 3)})
print("dict atravessa a fronteira como CÓPIA:", queue.get())

# cada interpretador tem seus próprios módulos e estado
interp.exec("import sys; sys.my_flag = 'só aqui'")
import sys
print("sys.my_flag no principal?", hasattr(sys, "my_flag"))

print("interpretadores vivos:", len(interpreters.list_all()))
interp.close()
print("depois do close:", len(interpreters.list_all()))
