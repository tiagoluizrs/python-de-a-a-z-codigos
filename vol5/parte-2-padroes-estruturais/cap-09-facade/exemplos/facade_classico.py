"""Facade, forma clássica (GoF): UMA porta de entrada simples para um subsistema com várias partes e uma ordem de uso."""
import ast
import inspect
import textwrap
import time
import zlib
from dataclasses import dataclass


# --- 1. o subsistema: quatro serviços que precisam ser chamados na ordem certa, com desfazer ---
class OutOfStock(Exception):
    pass


class PaymentFailed(Exception):
    pass


class Inventory:
    def __init__(self, stock):
        self.stock, self.reserved = dict(stock), {}

    def reserve(self, sku, qty):
        if self.stock.get(sku, 0) < qty:
            raise OutOfStock(sku)
        self.stock[sku] -= qty
        token = f"res-{len(self.reserved) + 1}"
        self.reserved[token] = (sku, qty)
        return token

    def release(self, token):
        sku, qty = self.reserved.pop(token)
        self.stock[sku] += qty


class Payments:
    def __init__(self):
        self.log = []

    def charge(self, card, cents):
        if card.startswith("0000"):
            raise PaymentFailed("cartão recusado")
        self.log.append(("charge", card, cents))
        return f"pay-{len(self.log)}"


class Shipping:
    def schedule(self, address, sku, qty):
        return f"TRK-{zlib.crc32(f'{address}|{sku}|{qty}'.encode()) % 10000:04d}"


class Notifications:
    def __init__(self):
        self.sent = []

    def send(self, to, text):
        self.sent.append((to, text))


PRICES = {"lapis": 150, "caderno": 1200}


# --- 2. o cliente SEM facade: conhece quatro serviços, a ordem e o desfazer ---
def place_order_manual(inventory, payments, shipping, notifications, sku, qty, card, address, email):
    token = inventory.reserve(sku, qty)
    try:
        payment = payments.charge(card, PRICES[sku] * qty)
    except PaymentFailed:
        inventory.release(token)                              # o desfazer: quem esquece deixa o estoque "preso"
        raise
    tracking = shipping.schedule(address, sku, qty)
    notifications.send(email, f"pedido {payment} enviado: {tracking}")
    return tracking


# --- 3. a facade: o subsistema continua igual; ganha uma porta de entrada ---
@dataclass(frozen=True)
class OrderResult:
    payment_id: str
    tracking: str


class OrderFacade:
    def __init__(self, inventory, payments, shipping, notifications):
        self._inventory, self._payments, self._shipping, self._notifications = inventory, payments, shipping, notifications

    def place_order(self, sku, qty, card, address, email) -> OrderResult:
        token = self._inventory.reserve(sku, qty)
        try:
            payment = self._payments.charge(card, PRICES[sku] * qty)
        except PaymentFailed:
            self._inventory.release(token)
            raise
        tracking = self._shipping.schedule(address, sku, qty)
        self._notifications.send(email, f"pedido {payment} enviado: {tracking}")
        return OrderResult(payment, tracking)


def build():
    return Inventory({"lapis": 10, "caderno": 2}), Payments(), Shipping(), Notifications()


inventory, payments, shipping, notifications = build()
print("cliente sem facade:", place_order_manual(inventory, payments, shipping, notifications, "lapis", 3, "4111-1111", "Rua A, 1", "ana@x.com"))

inventory, payments, shipping, notifications = build()
facade = OrderFacade(inventory, payments, shipping, notifications)
result = facade.place_order("lapis", 3, "4111-1111", "Rua A, 1", "ana@x.com")
print("com facade:", result, "| estoque:", inventory.stock, "| e-mails enviados:", len(notifications.sent))

# o caminho de falha, escondido atrás da mesma porta
try:
    facade.place_order("lapis", 2, "0000-0000", "Rua A, 1", "ana@x.com")
except PaymentFailed as error:
    print("pagamento recusado:", error, "| estoque restaurado:", inventory.stock["lapis"], "(o desfazer mora na facade, não em cada cliente)")
try:
    facade.place_order("caderno", 5, "4111-1111", "Rua A, 1", "ana@x.com")
except OutOfStock as error:
    print("sem estoque:", error)


# --- 4. o que a facade tira do cliente: contar o que ele precisa conhecer ---
def coupling(fn):
    """As operações do subsistema que a função conhece: as chamadas distintas `objeto.método(...)` e as exceções que ela trata."""
    func = ast.parse(textwrap.dedent(inspect.getsource(fn))).body[0]
    calls = {f"{n.func.value.id}.{n.func.attr}" for n in ast.walk(func)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)}
    errors = {n.type.id for n in ast.walk(func) if isinstance(n, ast.ExceptHandler) and isinstance(n.type, ast.Name)}
    return sorted(calls | errors)


def client_with_facade(facade, email):
    return facade.place_order("lapis", 3, "4111-1111", "Rua A, 1", email)


print("\no que o cliente SEM facade precisa conhecer:", coupling(place_order_manual))
print("o que o cliente COM facade precisa conhecer:", coupling(client_with_facade))


# --- 5. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nOrderFacade + OrderResult:", measure([OrderFacade, OrderResult]))


def best(fn, n=100_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


def manual():
    i, p, s, nt = build()
    place_order_manual(i, p, s, nt, "lapis", 1, "4111", "x", "a@b")


def with_facade():
    OrderFacade(*build()).place_order("lapis", 1, "4111", "x", "a@b")


print(f"fluxo manual {best(manual):6.0f} ns | pela facade {best(with_facade):6.0f} ns (inclui criar o subsistema nos dois; a diferença é uma chamada)")
