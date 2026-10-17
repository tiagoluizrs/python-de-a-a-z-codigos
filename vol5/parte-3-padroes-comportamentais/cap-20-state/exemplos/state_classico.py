"""State, forma clássica (GoF): o comportamento de um objeto muda conforme o seu ESTADO, e cada estado é uma classe."""
import ast
import inspect
import textwrap
import time
from abc import ABC


class InvalidTransition(Exception):
    pass


# --- 1. o problema: um campo `status` e um if/elif em CADA operação ---
class OrderNaive:
    def __init__(self):
        self.status = "new"

    def pay(self):
        if self.status == "new":
            self.status = "paid"
        else:
            raise InvalidTransition(f"pay não permitido em {self.status}")

    def ship(self):
        if self.status == "paid":
            self.status = "shipped"
        else:
            raise InvalidTransition(f"ship não permitido em {self.status}")

    def deliver(self):
        if self.status == "shipped":
            self.status = "delivered"
        else:
            raise InvalidTransition(f"deliver não permitido em {self.status}")

    def cancel(self):
        if self.status in ("new", "paid"):
            self.status = "cancelled"
        else:
            raise InvalidTransition(f"cancel não permitido em {self.status}")


order = OrderNaive()
order.pay()
order.ship()
try:
    order.cancel()
except InvalidTransition as error:
    print("com if/elif:", error, "| 4 operações x 5 estados espalhados em 4 métodos; um estado novo edita TODOS")


# --- 2. a forma clássica: uma classe por estado; cada uma decide o que cada operação faz e qual é o PRÓXIMO estado ---
class State(ABC):
    name = "?"

    def pay(self, order):
        self._deny("pay")

    def ship(self, order):
        self._deny("ship")

    def deliver(self, order):
        self._deny("deliver")

    def cancel(self, order):
        self._deny("cancel")

    def _deny(self, event):
        raise InvalidTransition(f"{event} não permitido em {self.name}")


class New(State):
    name = "new"

    def pay(self, order):
        order.state = Paid()

    def cancel(self, order):
        order.state = Cancelled()


class Paid(State):
    name = "paid"

    def ship(self, order):
        order.state = Shipped()

    def cancel(self, order):
        order.state = Cancelled()


class Shipped(State):
    name = "shipped"

    def deliver(self, order):
        order.state = Delivered()


class Delivered(State):
    name = "delivered"


class Cancelled(State):
    name = "cancelled"


class Order:                                                  # o CONTEXTO: só delega ao estado atual
    def __init__(self):
        self.state: State = New()

    def pay(self):
        self.state.pay(self)

    def ship(self):
        self.state.ship(self)

    def deliver(self):
        self.state.deliver(self)

    def cancel(self):
        self.state.cancel(self)


o = Order()
steps = [o.state.name]
for action in (o.pay, o.ship, o.deliver):
    action()
    steps.append(o.state.name)
print("\nState clássico:", " -> ".join(steps))
for bad in (o.cancel, o.pay):
    try:
        bad()
    except InvalidTransition as error:
        print("  transição inválida:", error)

# acrescentar um estado novo (ex.: "returned" depois de entregue) toca em UMA classe (Delivered) e cria outra; o contexto e os outros estados não mudam
class Returned(State):
    name = "returned"


class DeliveredWithReturn(Delivered):
    def cancel(self, order):
        order.state = Returned()


o.state = DeliveredWithReturn()
o.cancel()
print("estado novo sem editar os existentes (só uma subclasse):", o.state.name)


# --- 3. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(x) for x in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nif/elif (OrderNaive):", measure([OrderNaive]))
print("State (State + 5 estados + Order):", measure([State, New, Paid, Shipped, Delivered, Cancelled, Order]))


def best(fn, n=100_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


def cycle_state():
    x = Order()
    x.pay()
    x.ship()
    x.deliver()


def cycle_naive():
    x = OrderNaive()
    x.pay()
    x.ship()
    x.deliver()


print(f"\nciclo new->paid->shipped->delivered: if/elif {best(cycle_naive):5.0f} ns | State {best(cycle_state):5.0f} ns")
