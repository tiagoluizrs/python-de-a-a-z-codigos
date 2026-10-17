"""Command em Python: um callable (functools.partial), um par (fazer, desfazer), ExitStack como pilha de desfazer e comandos como DADOS."""
import ast
import functools
import inspect
import json
import queue
import textwrap
import threading
import time
from contextlib import ExitStack


# --- 1. o comando mais simples: um callable com os argumentos já ligados ---
results = []
commands = [functools.partial(results.append, "a"), functools.partial(print, "executando", "um", "comando", sep=" ")]
commands.append(lambda: results.append("c"))
for command in commands:
    command()
print("\nfila de callables (partial e lambda), executados depois:", results)

# --- 2. com desfazer: um PAR de funções (fazer, desfazer), sem classe ---
def make_insert(doc, pos, text):
    def do():
        doc["text"] = doc["text"][:pos] + text + doc["text"][pos:]

    def undo():
        doc["text"] = doc["text"][:pos] + doc["text"][pos + len(text):]

    return do, undo


def make_delete(doc, start, end):
    removed = []

    def do():
        removed.append(doc["text"][start:end])                      # o que foi removido fica na closure
        doc["text"] = doc["text"][:start] + doc["text"][end:]

    def undo():
        doc["text"] = doc["text"][:start] + removed.pop() + doc["text"][start:]

    return do, undo


def macro(*pairs):                                                  # o comando composto: um par que agrupa pares
    def do():
        for pair in pairs:
            pair[0]()

    def undo():
        for pair in reversed(pairs):                                # desfaz na ordem INVERSA
            pair[1]()

    return do, undo


class History:
    def __init__(self):
        self.done, self.undone = [], []

    def run(self, pair):
        pair[0]()
        self.done.append(pair)
        self.undone.clear()

    def undo(self):
        if self.done:
            pair = self.done.pop()
            pair[1]()
            self.undone.append(pair)

    def redo(self):
        if self.undone:
            pair = self.undone.pop()
            pair[0]()
            self.done.append(pair)


doc, history = {"text": "olá"}, History()
history.run(make_insert(doc, 3, ", mundo"))
history.run(make_delete(doc, 0, 1))
print("\npar (fazer, desfazer):", repr(doc["text"]), end=" -> ")
history.undo()
history.undo()
print("desfeito duas vezes:", repr(doc["text"]), end=" -> ")
history.redo()
print("refeito:", repr(doc["text"]))
doc2, history2 = {"text": "abc"}, History()
history2.run(macro(make_insert(doc2, 3, "d"), make_insert(doc2, 4, "e"), make_delete(doc2, 0, 1)))
print("macro:", repr(doc2["text"]), end=" -> ")
history2.undo()
print("desfeita de uma vez:", repr(doc2["text"]))
print("sem interface Command, sem classe por ação: cada comando é uma função que devolve duas funções")

# --- 3. a pilha de desfazer da biblioteca padrão: contextlib.ExitStack ---
state = {"files": []}


def create(name):
    state["files"].append(name)
    return lambda: state["files"].remove(name)                     # o "desfazer"


try:
    with ExitStack() as stack:
        for name in ("a.txt", "b.txt", "c.txt"):
            stack.callback(create(name))                            # registra o desfazer de cada passo, na ordem
        # esperaria o final para "confirmar"; aqui o passo seguinte falha:
        raise RuntimeError("falhou no quarto passo")
except RuntimeError:
    pass
print("\nExitStack: os 'desfazer' rodam na ORDEM INVERSA quando algo falha ->", state["files"], "(todos desfeitos)")

with ExitStack() as stack:
    for name in ("a.txt", "b.txt"):
        stack.callback(create(name))
    stack.pop_all()                                                 # "confirmar": remove os desfazer da pilha, nada é desfeito
print("com pop_all() (confirmar), os desfazer são descartados:", state["files"], "| a transação ficou")

# --- 4. a fila de comandos: guardar agora, executar depois (e em outra thread) ---
jobs: queue.Queue = queue.Queue()
output = []


def worker():
    while True:
        job = jobs.get()
        if job is None:
            break
        job()


thread = threading.Thread(target=worker)
thread.start()
for i in range(3):
    jobs.put(functools.partial(output.append, i * i))
jobs.put(None)
thread.join()
print("\nfila de comandos processada por outra thread:", output)

# --- 5. comandos como DADOS: gravar, enviar e reproduzir (o germe do event sourcing) ---
HANDLERS = {}


def handler(name):
    def register(fn):
        HANDLERS[name] = fn
        return fn
    return register


@handler("deposit")
def deposit(balance, amount):
    return balance + amount


@handler("withdraw")
def withdraw(balance, amount):
    if amount > balance:
        raise ValueError("saldo insuficiente")
    return balance - amount


def replay(balance, log):
    for command in log:
        balance = HANDLERS[command["name"]](balance, **command["args"])
    return balance


log = [{"name": "deposit", "args": {"amount": 100}}, {"name": "withdraw", "args": {"amount": 30}}, {"name": "deposit", "args": {"amount": 5}}]
text = json.dumps(log)
print("\ncomandos como dados, serializados:", text[:70] + "...")
print("reproduzidos a partir do JSON, saldo final:", replay(0, json.loads(text)), "| e em qualquer momento do passado:", replay(0, log[:2]))
print("um callable não vai para o disco nem para a rede; um dict com o NOME do comando e os argumentos, sim")


# --- 6. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nmake_insert + make_delete + macro + History:", measure([make_insert, make_delete, macro, History]), "(contra 46 linhas e 5 classes do clássico)")


def best(fn, n=300_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


sink = []
partial = functools.partial(sink.append, 1)
direct = sink.append
print(f"\nchamar uma ação: direto {best(lambda: direct(1)):4.0f} ns | via functools.partial {best(partial):4.0f} ns")
sink.clear()
