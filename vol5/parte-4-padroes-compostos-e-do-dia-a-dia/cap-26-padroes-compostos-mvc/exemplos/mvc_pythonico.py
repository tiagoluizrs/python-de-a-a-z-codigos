"""MVC em Python: o estilo "Elm" (estado imutável + mensagens + update puro + view pura) e o Presenter com ViewModel."""
import copy
import time
import tracemalloc
from dataclasses import dataclass, replace
from functools import reduce


# --- 1. o estado e as mensagens são DADOS imutáveis ---
@dataclass(frozen=True)
class Todo:
    text: str
    done: bool = False


@dataclass(frozen=True)
class State:
    items: tuple[Todo, ...] = ()
    filter: str = "all"                                      # "all" | "open" | "done"


@dataclass(frozen=True)
class Add:
    text: str


@dataclass(frozen=True)
class Toggle:
    index: int


@dataclass(frozen=True)
class Remove:
    index: int


@dataclass(frozen=True)
class SetFilter:
    name: str


Msg = Add | Toggle | Remove | SetFilter


# --- 2. update: uma função PURA (estado antigo + mensagem -> estado novo) ---
def update(state, msg):
    match msg:
        case Add(text):
            return replace(state, items=state.items + (Todo(text),))
        case Toggle(i):
            item = state.items[i]
            return replace(state, items=state.items[:i] + (replace(item, done=not item.done),) + state.items[i + 1:])
        case Remove(i):
            return replace(state, items=state.items[:i] + state.items[i + 1:])
        case SetFilter(name) if name in ("all", "open", "done"):
            return replace(state, filter=name)
        case _:
            raise ValueError(f"mensagem inválida: {msg!r}")


# --- 3. view: outra função PURA (estado -> texto) ---
def view(state):
    shown = [t for t in state.items if state.filter == "all" or (state.filter == "done") == t.done]
    lines = [f"[{'x' if t.done else ' '}] {t.text}" for t in shown]
    return " | ".join(lines) + f"  ({sum(t.done for t in state.items)}/{len(state.items)} feitas)"


# --- 4. o "controlador" é um laço minúsculo: a Store ---
class Store:
    def __init__(self, update, state):
        self.update, self.state = update, state
        self._past, self._future, self._subscribers = [], [], []

    def subscribe(self, fn):
        self._subscribers.append(fn)
        return fn

    def dispatch(self, msg):
        new = self.update(self.state, msg)
        if new == self.state:                                # nada mudou: ninguém é avisado
            return
        self._past.append(self.state)                        # desfazer é GRÁTIS: o estado antigo é imutável e já está aqui
        self._future.clear()
        self.state = new
        for fn in self._subscribers:
            fn(new)

    def undo(self):
        if self._past:
            self._future.append(self.state)
            self.state = self._past.pop()
            for fn in self._subscribers:
                fn(self.state)

    def redo(self):
        if self._future:
            self._past.append(self.state)
            self.state = self._future.pop()
            for fn in self._subscribers:
                fn(self.state)


screen = []
store = Store(update, State())
store.subscribe(lambda state: screen.append(view(state)))
for msg in (Add("leite"), Add("pão"), Toggle(0), SetFilter("open"), Add("café")):
    store.dispatch(msg)
print("tela depois de cada mensagem:")
for line in screen:
    print("  ", line)
store.undo()
store.undo()
print("depois de 2 undo:", screen[-1], "| nenhum código de 'snapshot/restore': a história é a lista de estados")
before = len(screen)
store.dispatch(SetFilter("all"))                             # o filtro já era "all": nada muda
print("mensagem que não muda nada avisa as visões?", len(screen) != before)

# a view e o update são testáveis sem tela, sem entrada e sem mocks:
assert update(State(), Add("x")) == State((Todo("x"),))
assert view(State((Todo("a", True), Todo("b")))) == "[x] a | [ ] b  (1/2 feitas)"
print("\nupdate e view são funções puras: 'assert update(State(), Add(\"x\")) == State((Todo(\"x\"),))' basta como teste")

# viagem no tempo: reproduzir uma sessão é só dobrar as mensagens
session = [Add("a"), Add("b"), Toggle(0), Remove(1), Add("c")]
print("reproduzir a sessão (reduce):", view(reduce(update, session, State())), "| depurar um bug de usuário = pedir as mensagens dele")


# --- 5. o Presenter: a view FICA BURRA, e o que ela mostra é um ViewModel (dados) ---
@dataclass(frozen=True)
class ViewModel:
    rows: tuple[str, ...]
    remaining: str
    can_clear: bool


def present(state):
    open_count = sum(not t.done for t in state.items)
    return ViewModel(
        rows=tuple(f"{'✔' if t.done else '○'} {t.text}" for t in state.items),
        remaining="nada a fazer" if open_count == 0 else f"{open_count} a fazer",
        can_clear=any(t.done for t in state.items),
    )


vm = present(State((Todo("a", True), Todo("b"))))
print("\nViewModel:", vm, "| os testes conferem os DADOS (vm.remaining == '1 a fazer'), não pedaços de texto de uma tela")


# --- 6. o custo ---
def memory_of(build):
    tracemalloc.start()
    keep = build()
    size = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return size, keep


N_ITEMS, N_OPS = 2_000, 100


def classic_history():
    items = [[f"t{i}", False] for i in range(N_ITEMS)]
    history = []
    for i in range(N_OPS):
        history.append([list(item) for item in items])        # o snapshot do Memento (copia cada lista de dentro)
        items[i][1] = True
    return history


def elm_history():
    state = State(tuple(Todo(f"t{i}") for i in range(N_ITEMS)))
    history = []
    for i in range(N_OPS):
        history.append(state)
        state = update(state, Toggle(i))
    return history


classic_mem, _ = memory_of(classic_history)
elm_mem, _ = memory_of(elm_history)
print(f"\n{N_OPS} operações em {N_ITEMS} itens, histórico completo | snapshots do MVC clássico: {classic_mem / 1e6:5.1f} MB | estados imutáveis: {elm_mem / 1e6:5.1f} MB ({classic_mem / elm_mem:.0f}x menos)")


def best(fn, n=5_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


small = Store(update, State((Todo("a"), Todo("b"), Todo("c"))))
small.subscribe(lambda s: None)
print(f"dispatch de um Toggle (3 itens, 1 assinante): {best(lambda: small.dispatch(Toggle(1))):5.2f} µs")
