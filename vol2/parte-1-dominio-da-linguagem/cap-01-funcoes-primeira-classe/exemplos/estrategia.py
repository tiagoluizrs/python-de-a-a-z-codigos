"""Estratégia, callback, comando e tabela de despacho com funções."""
from collections.abc import Callable
from dataclasses import dataclass


# Estratégia: a política é só um parâmetro callable
def no_discount(total: float) -> float:
    return total


def black_friday(total: float) -> float:
    return total * 0.7


def loyalty(total: float) -> float:
    return total - min(total * 0.1, 20)


@dataclass
class Order:
    total: float
    pricing: Callable[[float], float] = no_discount

    def final(self) -> float:
        return self.pricing(self.total)


print(Order(100).final(), Order(100, black_friday).final(),
      Order(300, loyalty).final())

# Tabela de despacho
COMMANDS: dict[str, Callable[[list[str]], str]] = {}


def command(name):
    def register(fn):
        COMMANDS[name] = fn
        return fn
    return register


@command("echo")
def echo(args):
    return " ".join(args)


@command("count")
def count(args):
    return str(len(args))


def run(line: str) -> str:
    name, *args = line.split()
    handler = COMMANDS.get(name)
    if handler is None:
        return f"unknown command: {name}"
    return handler(args)


print(run("echo a b"), run("count a b c"), run("nope"))


# Callback: quem chama decide o que fazer a cada evento
def download(chunks, on_progress):
    done = 0
    for c in chunks:
        done += len(c)
        on_progress(done)


log = []
download(["ab", "cde", "f"], log.append)
print(log)


# Comando com desfazer: pares de funções
history = []


def do(action, undo):
    action()
    history.append(undo)


items = []
do(lambda: items.append("x"), items.pop)
do(lambda: items.append("y"), items.pop)
print(items)
while history:
    history.pop()()
print(items)
