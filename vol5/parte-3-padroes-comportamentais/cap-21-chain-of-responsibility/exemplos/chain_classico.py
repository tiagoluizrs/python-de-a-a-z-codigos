"""Chain of Responsibility, forma clássica (GoF): o pedido passa por uma CADEIA de manipuladores até que um deles o resolva."""
import ast
import inspect
import textwrap
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    amount: float
    description: str


# --- 1. o problema: quem decide o quê, em um if/elif que conhece TODOS os níveis ---
def approve_naive(expense):
    if expense.amount <= 1_000:
        return f"líder aprovou {expense.description}"
    elif expense.amount <= 10_000:
        return f"gerente aprovou {expense.description}"
    elif expense.amount <= 100_000:
        return f"diretor aprovou {expense.description}"
    return f"recusado: {expense.description} passa de 100.000"


print("if/elif:", approve_naive(Expense(5_000, "servidor")), "| um nível novo (ex.: 'vice-presidente') edita esta função")


# --- 2. a forma clássica: cada manipulador conhece o PRÓXIMO e decide se resolve ou repassa ---
class Handler(ABC):
    def __init__(self):
        self._next = None

    def set_next(self, handler):
        self._next = handler
        return handler                                          # devolver o próximo permite encadear: a.set_next(b).set_next(c)

    def handle(self, expense):
        if self.can_handle(expense):
            return self.process(expense)
        if self._next is not None:
            return self._next.handle(expense)                   # repassa
        return None                                             # fim da cadeia sem ninguém para resolver

    @abstractmethod
    def can_handle(self, expense) -> bool: ...

    @abstractmethod
    def process(self, expense) -> str: ...


class Approver(Handler):
    def __init__(self, role, limit):
        super().__init__()
        self.role, self.limit = role, limit

    def can_handle(self, expense):
        return expense.amount <= self.limit

    def process(self, expense):
        return f"{self.role} aprovou {expense.description}"


lead = Approver("líder", 1_000)
lead.set_next(Approver("gerente", 10_000)).set_next(Approver("diretor", 100_000))
for expense in (Expense(300, "livro"), Expense(5_000, "servidor"), Expense(50_000, "licenças"), Expense(500_000, "prédio")):
    print(f"  {expense.amount:>9,.0f}: {lead.handle(expense)}")

# acrescentar um nível NÃO edita os existentes: só se monta a cadeia de outro jeito
vp = Approver("vice-presidente", 1_000_000)
chain = Approver("líder", 1_000)
chain.set_next(Approver("gerente", 10_000)).set_next(Approver("diretor", 100_000)).set_next(vp)
print("\ncom o 4º nível (sem editar nada):", chain.handle(Expense(500_000, "prédio")))


# --- 3. as armadilhas ---
print("\n(a) pedido que ninguém resolve (fim da cadeia):", lead.handle(Expense(5_000_000, "estádio")), "(devolve None: quem chama precisa tratar)")

loop_a, loop_b = Approver("a", 0), Approver("b", 0)
loop_a.set_next(loop_b)
loop_b.set_next(loop_a)                                          # um ciclo na cadeia
try:
    loop_a.handle(Expense(1, "x"))
except RecursionError:
    print("(b) uma cadeia com ciclo: RecursionError (cada repasse empilha uma chamada)")


def build(n):
    head = Approver("h0", -1)
    current = head
    for i in range(1, n):
        current = current.set_next(Approver(f"h{i}", -1))
    current.limit = 10
    return head


try:
    build(2_000).handle(Expense(1, "x"))
except RecursionError:
    print("(c) uma cadeia com 2.000 manipuladores estoura a pilha: a cadeia clássica é RECURSIVA e o Python limita a recursão em ~1.000")

# --- 4. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nif/elif:", measure([approve_naive]), "| Handler + Approver:", measure([Handler, Approver]))


def best(fn, n=200_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


big = Expense(50_000, "licenças")
print(f"aprovar um pedido que desce 3 níveis: if/elif {best(lambda: approve_naive(big)):4.0f} ns | cadeia de objetos {best(lambda: lead.handle(big)):4.0f} ns")
