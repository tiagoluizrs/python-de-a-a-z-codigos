"""State em Python: Enum + tabela de transições (dados), match, e a validação do grafo de estados."""
import ast
import inspect
import textwrap
import time
from enum import Enum
from collections import deque


class InvalidTransition(Exception):
    pass


# --- 1. o estado como Enum e as transições como DADOS: uma tabela (estado, evento) -> próximo estado ---
class Status(Enum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


TRANSITIONS = {
    (Status.NEW, "pay"): Status.PAID,
    (Status.NEW, "cancel"): Status.CANCELLED,
    (Status.PAID, "ship"): Status.SHIPPED,
    (Status.PAID, "cancel"): Status.CANCELLED,
    (Status.SHIPPED, "deliver"): Status.DELIVERED,
}


class Order:
    def __init__(self):
        self.status = Status.NEW
        self.history = [self.status]

    def fire(self, event):
        try:
            self.status = TRANSITIONS[(self.status, event)]
        except KeyError:
            raise InvalidTransition(f"{event} não permitido em {self.status.value}") from None
        self.history.append(self.status)
        return self.status

    def allowed(self):                                         # a tabela responde "o que posso fazer agora?" de graça
        return sorted(event for (state, event) in TRANSITIONS if state is self.status)


order = Order()
for event in ("pay", "ship"):
    order.fire(event)
print("tabela:", " -> ".join(s.value for s in order.history), "| permitido agora:", order.allowed())
try:
    order.fire("cancel")
except InvalidTransition as error:
    print("transição inválida:", error)
print("acrescentar um estado ou uma transição é UMA linha na tabela; o código do Order não muda")

# --- 2. match: quando as regras têm lógica (guardas) e não cabem em uma tabela ---
def door(state, event):
    match (state, event):
        case ("closed", "open"):
            return "open"
        case ("open", "close"):
            return "closed"
        case ("closed", "lock"):
            return "locked"
        case ("locked", "unlock"):
            return "closed"
        case (_, e) if e in ("open", "close", "lock", "unlock"):
            raise InvalidTransition(f"{e} não permitido em {state}")
        case _:
            raise ValueError(f"evento desconhecido: {event}")


print("\nmatch:", door("closed", "lock"), door("locked", "unlock"), end=" | ")
try:
    door("locked", "open")
except InvalidTransition as error:
    print(error)

# --- 3. o truque do __class__: o objeto MUDA de classe quando muda de estado (State clássico, sem contexto separado) ---
class Draft:
    def publish(self):
        self.__class__ = Published
        return "publicado"

    def edit(self, text):
        self.text = text
        return "editado"


class Published:
    def publish(self):
        raise InvalidTransition("já publicado")

    def edit(self, text):
        raise InvalidTransition("publicado não se edita")


post = Draft()
print("\n__class__ como estado:", post.edit("v1"), post.publish(), type(post).__name__, end=" | ")
try:
    post.edit("v2")
except InvalidTransition as error:
    print(error)
print("funciona, mas esconde a mudança de classe de quem lê o código: prefira o Enum e a tabela, a menos que cada estado tenha MUITO comportamento")

# --- 4. validar o grafo de estados: inalcançáveis e terminais ---
def analyze(transitions, initial):
    states = {s for s, _ in transitions} | set(transitions.values())
    graph = {s: set() for s in states}
    for (s, _), target in transitions.items():
        graph[s].add(target)
    seen, queue = {initial}, deque([initial])
    while queue:
        for nxt in graph[queue.popleft()]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    unreachable = sorted(s.value for s in states - seen)
    terminal = sorted(s.value for s in states if not graph[s])
    return unreachable, terminal


unreachable, terminal = analyze(TRANSITIONS, Status.NEW)
print("\nanálise do grafo: inalcançáveis:", unreachable, "| terminais:", terminal)
broken = dict(TRANSITIONS)
broken[(Status.DELIVERED, "return")] = Status.NEW
del broken[(Status.NEW, "pay")]
print("tabela com defeito (sem 'pay' em NEW): inalcançáveis:", analyze(broken, Status.NEW)[0], "<- a tabela se verifica com poucas linhas; os if/elif espalhados, não")


# --- 5. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(x) for x in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nOrder com Enum e tabela:", measure([Order]), "| a tabela tem", len(TRANSITIONS), "linhas de dados (contra 43 linhas e 7 classes do State clássico)")


def best(fn, n=100_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


def cycle():
    x = Order()
    x.fire("pay")
    x.fire("ship")
    x.fire("deliver")


print(f"ciclo new->paid->shipped->delivered com tabela: {best(cycle):5.0f} ns")
