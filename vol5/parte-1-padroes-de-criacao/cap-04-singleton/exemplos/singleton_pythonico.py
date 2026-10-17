"""Singleton em Python: o módulo, a função com cache e o estado compartilhado, e o que fazer quando você só quer UMA coisa."""
import ast
import functools
import inspect
import sys
import textwrap
import threading
import time

# --- 1. o módulo é o singleton: carregado uma vez, guardado em sys.modules ---
print("primeiro import:")
import app_settings                                       # noqa: E402

print("segundo import (nada é impresso):")
import app_settings as again                              # noqa: E402

app_settings.configure(region="sa-east-1")
print("  mesmo objeto:", app_settings is again, "| estado compartilhado:", again.VALUES, "| 'app_settings' in sys.modules:", "app_settings" in sys.modules)


# --- 2. um objeto único e criado sob demanda: uma função com functools.cache ---
class Settings:
    def __init__(self):
        time.sleep(0.01)                                  # uma criação cara (ler um arquivo, falar com um serviço)
        self.values = {"timeout": 5}


@functools.cache
def get_settings() -> Settings:
    return Settings()


print("\nfunção com cache:", get_settings() is get_settings(), "| a 1ª chamada cria; as outras devolvem a mesma instância")
get_settings.cache_clear()
print("nos testes, cache_clear() recomeça do zero:", get_settings.cache_info())


# --- 3. a pegadinha: functools.cache NÃO impede duas threads de criarem ao mesmo tempo ---
creations = []


class Heavy:
    def __init__(self):
        creations.append(threading.get_ident())
        time.sleep(0.02)


@functools.cache
def get_heavy():
    return Heavy()


def hammer(fn, threads=8):
    barrier = threading.Barrier(threads)
    found = []

    def work():
        barrier.wait()
        found.append(fn())

    workers = [threading.Thread(target=work) for _ in range(threads)]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    return found


found = hammer(get_heavy)
print(f"\nfunctools.cache com 8 threads simultâneas: {len(creations)} criações (a documentação avisa: a função pode rodar mais de uma vez)")
print("  instâncias distintas devolvidas:", len({id(x) for x in found}), "(o cache guarda uma, mas várias threads já tinham criado a sua)")

_lock = threading.Lock()
_instance = None
created = []


def get_once():
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                created.append(1)
                time.sleep(0.02)
                _instance = object()
    return _instance


found = hammer(get_once)
print(f"com uma trava: {len(created)} criação, {len({id(x) for x in found})} instância: use a trava quando a criação for cara ou tiver efeito colateral")


# --- 4. o estado compartilhado (Borg / monostate): várias instâncias, UM estado ---
class Borg:
    _shared: dict = {}

    def __init__(self):
        self.__dict__ = self._shared


x, y = Borg(), Borg()
x.color = "azul"
print("\nBorg: instâncias diferentes?", x is not y, "| estado compartilhado?", y.color, "| é um singleton? Não: é um estado único (e continua global)")

# --- 5. o melhor singleton: nenhum. Receber a dependência por parâmetro ---
def charge(settings, amount):
    return round(amount * (1 + settings["fee"]), 2)


print("\nsem global nenhum:", charge({"fee": 0.1}, 100.0), "| o teste passa o que quiser; a raiz de composição cria UMA configuração e a entrega adiante")


# --- 6. o custo de ler o valor ---
def best(fn, n=500_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


class NewSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class Plain:
    pass


plain = Plain()
get_settings()
print("\ncusto de obter a instância única:")
for label, fn in [("variável de módulo (app_settings.TIMEOUT)", lambda: app_settings.TIMEOUT), ("função com cache (get_settings())", get_settings),
                  ("classe com __new__ (NewSingleton())", NewSingleton), ("criar uma instância nova (Plain())", Plain)]:
    print(f"  {label:<44} {best(fn):6.0f} ns")


# --- 7. o que custa escrever ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


class LockedNew:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance


print("\nclasse com __new__ e trava (modelo clássico):", measure([LockedNew]), "| módulo: 0 linhas de mecanismo | função com cache:", measure([get_settings]))
sys.modules.pop("app_settings", None)
