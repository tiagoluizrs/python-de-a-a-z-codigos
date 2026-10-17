"""Estado por thread: threading.local e contextvars."""
import contextvars
import sys
import threading

local = threading.local()
local.user = "principal"
seen = []


def read_local():
    seen.append(getattr(local, "user", "(nada)"))
    local.user = threading.current_thread().name
    seen.append(local.user)


t = threading.Thread(target=read_local, name="filha")
t.start()
t.join()
print("threading.local: a filha começa sem o valor e o dela não afeta a principal:", seen, "| principal:", local.user)

# contextvars
request_id = contextvars.ContextVar("request_id", default="-")
request_id.set("req-1")
out = {}


def show(label):
    out[label] = request_id.get()


for label, kwargs in (("padrão", {}), ("context=copy_context()", {"context": contextvars.copy_context()}), ("context=Context() vazio", {"context": contextvars.Context()})):
    thread = threading.Thread(target=show, args=(label,), **kwargs)
    thread.start()
    thread.join()
print("contextvars em uma thread nova:", out)
print("sys.flags.thread_inherit_context =", sys.flags.thread_inherit_context, "(0 no build com GIL; 1 por padrão no build sem GIL)")

# Padrão útil: um recurso por thread (conexão, sessão) em um pool
import concurrent.futures as cf

resources = threading.local()
created = []


def get_connection():
    if not hasattr(resources, "conn"):
        resources.conn = f"conexão-{threading.current_thread().name}"
        created.append(resources.conn)
    return resources.conn


with cf.ThreadPoolExecutor(max_workers=3, thread_name_prefix="pool") as pool:
    list(pool.map(lambda _: get_connection(), range(30)))
print("30 tarefas, 3 threads -> conexões criadas:", len(created))
