"""Seis padrões do GoF que o Python já traz na linguagem: você os usa todo dia sem chamá-los pelo nome."""
import copy
import functools
import sys
from dataclasses import dataclass, replace

# --- Singleton: o módulo ---
import config_demo                       # noqa: E402 (um módulo deste mesmo diretório, importado UMA vez)
import config_demo as again              # noqa: E402

print("Singleton: o módulo é carregado uma vez e guardado em sys.modules:", config_demo is again, "| 'config_demo' in sys.modules:", "config_demo" in sys.modules)


# --- Prototype: copy e dataclasses.replace ---
@dataclass
class Settings:
    host: str
    tags: list


base = Settings("localhost", ["a"])
clone = copy.deepcopy(base)
clone.tags.append("b")
variant = replace(base, host="prod")
print("\nPrototype: deepcopy não compartilha a lista ->", base.tags, clone.tags, "| replace cria uma variante ->", variant.host)


# --- Decorator: a sintaxe @ e functools.wraps ---
def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return fn(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


@timed
def add(a, b):
    """Soma."""
    return a + b


add(1, 2), add(3, 4)
print("\nDecorator: @timed embrulha a função sem tocá-la:", add.calls, "chamadas | nome e documentação preservados:", add.__name__, add.__doc__)


# --- Strategy: a função é a estratégia ---
operations = {"soma": lambda a, b: a + b, "produto": lambda a, b: a * b}
print("\nStrategy: trocar o algoritmo é trocar a chave:", {k: f(3, 4) for k, f in operations.items()})


# --- Command: um callable com argumentos já ligados ---
command = functools.partial(print, "Command: um callable guardado e executado depois ->", sep=" ")
queue = [command, functools.partial(add, 10, 20)]
results = [c() for c in queue]
print("  resultados:", results)


# --- Iterator: o protocolo de iteração e os geradores ---
def countdown(n):
    while n:
        yield n
        n -= 1


print("\nIterator: um gerador é um iterador em 3 linhas:", list(countdown(3)), "| for, list, sum, in... falam o mesmo protocolo")

print("\nnenhum desses seis exigiu uma classe abstrata, uma fábrica ou uma hierarquia: o mecanismo do padrão ESTÁ na linguagem")
print("padrões do GoF que 'sumiram': ao ler 'Singleton' em um livro de Java, pense em 'módulo'; em 'Strategy' ou 'Command', pense em 'função'")
sys.modules.pop("config_demo", None)
