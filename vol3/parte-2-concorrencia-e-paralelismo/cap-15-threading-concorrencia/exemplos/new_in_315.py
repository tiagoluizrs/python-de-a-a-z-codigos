"""Novidades do 3.15 em threading: iteradores compartilhados entre threads."""
import threading
import warnings

# Um gerador compartilhado entre threads, sem proteção, é um erro (ValueError: generator already executing)
def numbers():
    for i in range(2000):
        yield i


shared = numbers()
errors = []


def eat_unsafe():
    try:
        for _ in shared:
            pass
    except ValueError as error:
        errors.append(str(error))


threads = [threading.Thread(target=eat_unsafe) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("gerador compartilhado sem proteção -> erros:", set(errors) or "nenhum desta vez (depende do agendamento)")

# serialize_iterator: um acesso por vez, sem perder itens
collected = []
safe = threading.serialize_iterator(numbers())
lock = threading.Lock()


def eat_safe():
    for item in safe:
        with lock:
            collected.append(item)


threads = [threading.Thread(target=eat_safe) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("serialize_iterator: itens consumidos =", len(collected), "| sem repetição:", len(set(collected)) == 2000)


# concurrent_tee: várias threads leem O MESMO fluxo, cada uma com a sua cópia
tees = threading.concurrent_tee(iter(range(5)), 3)
print("concurrent_tee(…, 3) devolve", len(tees), "iteradores independentes:", [list(t) for t in tees])

# Nomes antigos (camelCase) obsoletos
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    event = threading.Event()
    event.isSet()
    threading.currentThread()
    threading.activeCount()
print("avisos de depreciação:", sorted({str(w.message).split(" ")[0] for w in caught if issubclass(w.category, DeprecationWarning)}))
print("use: event.is_set(), threading.current_thread(), threading.active_count(), thread.daemon, thread.name")
