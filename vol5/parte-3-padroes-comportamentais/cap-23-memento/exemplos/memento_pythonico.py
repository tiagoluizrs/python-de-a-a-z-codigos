"""Memento em Python: o estado imutável É o memento; compartilhamento estrutural; transações com rollback; histórico limitado; comandos inversos."""
import copy
import json
import time
import tracemalloc
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, replace


# --- 1. o estado imutável: não precisa de classe Memento ---
@dataclass(frozen=True)
class State:
    text: str = ""
    cursor: int = 0


class Editor:
    def __init__(self):
        self.state = State()
        self._past, self._future = [], []

    def apply(self, new_state):
        self._past.append(self.state)                       # o "memento" é o próprio estado: ninguém consegue alterá-lo
        self._future.clear()
        self.state = new_state

    def type(self, chars):
        s = self.state
        self.apply(replace(s, text=s.text[: s.cursor] + chars + s.text[s.cursor:], cursor=s.cursor + len(chars)))

    def undo(self):
        if self._past:
            self._future.append(self.state)
            self.state = self._past.pop()

    def redo(self):
        if self._future:
            self._past.append(self.state)
            self.state = self._future.pop()


ed = Editor()
ed.type("olá")
ed.type(", mundo")
ed.undo()
print("estado imutável:", ed.state, "| desfeito uma vez; refazer ->", end=" ")
ed.redo()
print(ed.state.text)
try:
    ed.state.text = "hack"                                  # type: ignore[misc]
except Exception as error:
    print("ninguém altera um estado guardado:", type(error).__name__)

# --- 2. compartilhamento estrutural: o documento como tupla de linhas ---
LINES, VERSIONS = 5_000, 40


def memory_of(build):
    tracemalloc.start()
    keep = build()
    size = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return size, keep


def make_lines():
    return [[f"palavra{j}" for j in range(8)] for _ in range(LINES)]      # cada linha é uma lista (mutável) de palavras


def deep_snapshots(n=VERSIONS):
    lines, snaps = make_lines(), []
    for i in range(n):
        snaps.append(copy.deepcopy(lines))                  # copia TODAS as listas a cada versão (as strings, imutáveis, o deepcopy já compartilha)
        lines[i][0] = "EDITADA"
    return snaps


def shared_snapshots(n=VERSIONS):
    doc, snaps = tuple(tuple(line) for line in make_lines()), []
    for i in range(n):
        snaps.append(doc)                                   # só uma referência
        doc = doc[:i] + (("EDITADA",) + doc[i][1:],) + doc[i + 1:]     # versão nova: só a linha editada é um objeto novo
    return snaps


big_deep, _ = memory_of(deep_snapshots)
big_shared, snaps = memory_of(shared_snapshots)
print(f"\n{VERSIONS} versões de um documento de {LINES} linhas | deepcopy de tudo: {big_deep / 1e6:6.1f} MB | tuplas imutáveis compartilhando linhas: {big_shared / 1e6:6.1f} MB ({big_deep / big_shared:.0f}x menos)")
print("a linha 50 é o MESMO objeto nas versões 0 e 1:", snaps[0][50] is snaps[1][50], "| a linha 0 mudou entre elas:", snaps[0][0] is not snaps[1][0])
print("(cada versão ainda paga o vetor de ponteiros da tupla externa; só estruturas persistentes de verdade, em árvore, fazem isso em O(log n))")


# --- 3. a transação: rollback automático com um gerenciador de contexto ---
class Inventory:
    def __init__(self, **stock):
        self.stock = dict(stock)

    @contextmanager
    def transaction(self):
        snapshot = copy.deepcopy(self.stock)                # o memento fica na variável local: ninguém de fora o vê
        try:
            yield self
        except BaseException:
            self.stock = snapshot                           # rollback
            raise


inv = Inventory(maçã=5, pera=2)
try:
    with inv.transaction():
        inv.stock["maçã"] -= 3
        inv.stock["pera"] -= 9                              # inválido
        if inv.stock["pera"] < 0:
            raise ValueError("estoque negativo")
except ValueError as error:
    print("\ntransação falhou:", error, "| estoque restaurado:", inv.stock)
with inv.transaction():
    inv.stock["maçã"] -= 3
print("transação ok:", inv.stock)

# --- 4. o histórico limitado: deque(maxlen) ---
history: deque[State] = deque(maxlen=3)
for i in range(6):
    history.append(State(text=f"v{i}"))
print("\nhistórico limitado a 3:", [s.text for s in history], "(os mais antigos caem sozinhos)")


# --- 5. o snapshot ou o comando inverso: o custo em memória ---
def snapshot_history(n=200):
    data, snaps = list(range(5_000)), []
    for i in range(n):
        snaps.append(list(data))                            # uma cópia inteira por edição
        data[i] = -1
    return snaps


def inverse_history(n=200):
    data, undo = list(range(5_000)), []
    for i in range(n):
        undo.append((i, data[i]))                           # só o que mudou: (posição, valor antigo)
        data[i] = -1
    return undo


snap_mem, _ = memory_of(snapshot_history)
inv_mem, _ = memory_of(inverse_history)
print(f"200 edições em uma lista de 5.000 itens | um snapshot por edição: {snap_mem / 1e6:5.1f} MB | só o comando inverso (posição, valor): {inv_mem / 1e6:5.3f} MB ({snap_mem / inv_mem:.0f}x menos)")


# --- 6. o memento que vai para o disco: JSON e versão ---
def dump(state):
    return json.dumps({"version": 1, "text": state.text, "cursor": state.cursor})


def load(raw):
    data = json.loads(raw)
    if data.get("version") != 1:
        raise ValueError(f"versão {data.get('version')} não suportada")
    return State(data["text"], data["cursor"])


raw = dump(State("olá", 3))
print("\nmemento em JSON:", raw, "->", load(raw), "| um memento persistido precisa de uma VERSÃO: o formato muda, os arquivos antigos continuam")


# --- 7. o custo por salvar ---
def best(fn, n=20_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


data = {"text": "x" * 200, "cursor": 5, "marks": list(range(20))}
frozen = State("x" * 200, 5)
print(f"\nsalvar o estado: referência a um estado imutável {best(lambda: frozen):4.0f} ns | copy.copy {best(lambda: copy.copy(data)):5.0f} ns | json ida e volta {best(lambda: json.loads(json.dumps(data))):5.0f} ns | deepcopy {best(lambda: copy.deepcopy(data)):5.0f} ns")
