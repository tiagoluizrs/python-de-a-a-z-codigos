"""Injeção de Dependência em Python: funções e partial, Protocol, um contêiner com auto-wiring (ao estilo dos frameworks) e contextvars para o contexto de uma requisição."""
import contextvars
import functools
import inspect
import time
from contextlib import contextmanager
from datetime import datetime
from functools import partial
from typing import Protocol, get_type_hints, runtime_checkable

FIXED = datetime(2026, 1, 1, 12, 0)


# --- 1. a dependência pode ser uma FUNÇÃO: sem classes, sem interfaces ---
def place_order(customer, total_cents, *, save, send, now):
    order = {"customer": customer, "total": total_cents, "at": now()}
    save(order)
    send(customer, "pedido recebido")
    return order


saved, sent = [], []
place = partial(place_order, save=saved.append, send=lambda to, subject: sent.append((to, subject)), now=lambda: FIXED)       # a "raiz de composição" é um partial
order = place("ana@x.com", 10_00)
print("funções + partial:", order, saved == [order], sent, "| o teste passa funções de uma linha; nenhuma classe de dublê")


def make_place_order(save, send, now):                                       # a mesma ideia com uma closure (Capítulo 2 do Volume 2)
    def place(customer, total_cents):
        order = {"customer": customer, "total": total_cents, "at": now()}
        save(order)
        send(customer, "pedido recebido")
        return order
    return place


print("closure:", make_place_order(saved.append, lambda *a: None, lambda: FIXED)("bia@x.com", 5_00)["customer"])


# --- 2. o Protocol: o contrato sem herança ---
@runtime_checkable
class Mailer(Protocol):
    def send(self, to: str, subject: str) -> None: ...


class RecordingMailer:                                                        # NÃO herda de Mailer: basta ter o método (tipagem estrutural)
    def __init__(self):
        self.sent = []

    def send(self, to, subject):
        self.sent.append((to, subject))


class NoMailer:
    pass


print("\nProtocol:", isinstance(RecordingMailer(), Mailer), isinstance(NoMailer(), Mailer), "| o verificador de tipos (mypy, pyright) confere o contrato; o dublê não precisa herdar de nada")


# --- 3. um contêiner de injeção com auto-wiring (o que os frameworks fazem) ---
@functools.cache
def plan(factory):
    """A análise da assinatura (nomes, tipos e padrões) é CARA: faz-se uma vez por fábrica e fica em cache."""
    hints = get_type_hints(factory.__init__ if isinstance(factory, type) else factory)
    return tuple((name, hints.get(name), param.default is not inspect.Parameter.empty) for name, param in inspect.signature(factory).parameters.items())


class Container:
    def __init__(self):
        self._providers, self._singletons, self._overrides = {}, {}, {}

    def register(self, key, factory=None, *, lifetime="singleton"):
        self._providers[key] = (factory or key, lifetime)

    def resolve(self, key, _chain=()):
        if key in self._overrides:
            return self._overrides[key]
        names = " -> ".join(k.__name__ for k in (*_chain, key))
        if key in _chain:
            raise RuntimeError(f"dependência circular: {names}")
        if key not in self._providers:
            raise LookupError(f"não registrado: {key.__name__}" + (f" (cadeia: {names})" if _chain else ""))
        factory, lifetime = self._providers[key]
        if lifetime == "singleton" and key in self._singletons:
            return self._singletons[key]
        kwargs = {}
        for name, hint, has_default in plan(factory):
            if hint is not None and (hint in self._providers or hint in self._overrides):
                kwargs[name] = self.resolve(hint, (*_chain, key))
            elif has_default:
                continue                                                      # tem valor padrão (retries=3): o contêiner o deixa em paz
            elif hint is not None:
                raise LookupError(f"não registrado: {getattr(hint, '__name__', hint)} (cadeia: {names} -> {getattr(hint, '__name__', hint)})")
            else:
                raise TypeError(f"parâmetro sem tipo: {key.__name__}.{name}")
        instance = factory(**kwargs)
        if lifetime == "singleton":
            self._singletons[key] = instance
        return instance

    @contextmanager
    def override(self, key, instance):
        self._overrides[key] = instance
        self._singletons.clear()                                              # um singleton já montado guardaria a dependência ANTIGA: o grafo é refeito
        try:
            yield instance
        finally:
            del self._overrides[key]
            self._singletons.clear()                                          # ...e refeito de novo ao sair, para não vazar o dublê


class Clock:
    def __call__(self):
        return FIXED


class SmtpMailer:
    def send(self, to: str, subject: str) -> None:
        raise ConnectionError("sem rede")


class Orders:
    def __init__(self):
        self.saved = []

    def save(self, order):
        self.saved.append(order)


class OrderService:
    def __init__(self, orders: Orders, mailer: Mailer, clock: Clock, retries: int = 3):         # 'retries' tem padrão: o contêiner o deixa em paz
        self.orders, self.mailer, self.clock, self.retries = orders, mailer, clock, retries

    def place(self, customer, total_cents):
        order = {"customer": customer, "total": total_cents, "at": self.clock()}
        self.orders.save(order)
        self.mailer.send(customer, "pedido recebido")
        return order


class Billing:
    def __init__(self, service: OrderService, orders: Orders):
        self.service, self.orders = service, orders


container = Container()
container.register(Clock)
container.register(Orders)
container.register(Mailer, SmtpMailer)
container.register(OrderService)
container.register(Billing, lifetime="transient")
billing = container.resolve(Billing)
print("\ncontêiner: Billing montado sozinho ->", type(billing.service.mailer).__name__, "| o mesmo Orders compartilhado (singleton):", billing.orders is billing.service.orders, "| retries ficou no padrão:", billing.service.retries)
print("transient cria um novo a cada pedido:", container.resolve(Billing) is not billing, "| singleton reaproveita:", container.resolve(OrderService) is billing.service)

recorder = RecordingMailer()
with container.override(Mailer, recorder):                                    # no teste, UM Mailer é trocado e o resto do grafo continua o mesmo
    container.resolve(Billing).service.place("ana@x.com", 10_00)
print("override para o teste:", recorder.sent, "| fora do with, volta ao SmtpMailer:", type(container.resolve(Billing).service.mailer).__name__)

def _missing():
    c = Container()
    c.register(OrderService)
    c.register(Orders)
    c.register(Clock)
    c.resolve(OrderService)


class A:
    def __init__(self, b: "B"):
        self.b = b


class B:
    def __init__(self, a: A):
        self.a = a


def _cycle():
    c = Container()
    c.register(A)
    c.register(B)
    c.resolve(A)


for label, build in (("falta registrar o Mailer", _missing), ("dependência circular", _cycle)):
    try:
        build()
    except (LookupError, RuntimeError) as error:
        print(f"  {label}: {error}")

# --- 4. o contexto de uma requisição: contextvars (dependência "ambiente") ---
request_id = contextvars.ContextVar("request_id")


@contextmanager
def request_scope(value):
    token = request_id.set(value)
    try:
        yield
    finally:
        request_id.reset(token)


def log(message):
    return f"[{request_id.get('-')}] {message}"                               # nenhum parâmetro 'request_id' atravessando 10 funções


with request_scope("req-42"):
    inside = log("cobrando")
print("\ncontextvars:", inside, "|", log("fora da requisição"), "(ótimo para o que atravessa TUDO, como o id da requisição; ruim para dependências de negócio, que ficam invisíveis)")


# --- 5. o custo ---
def best(fn, n=20_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


manual = lambda: OrderService(Orders(), SmtpMailer(), Clock())
fresh = Container()
for key, factory in ((Clock, None), (Orders, None), (Mailer, SmtpMailer)):
    fresh.register(key, factory, lifetime="transient")
fresh.register(OrderService, lifetime="transient")
fresh.register(Billing, lifetime="transient")
shared = Container()
for key, factory in ((Clock, None), (Orders, None), (Mailer, SmtpMailer), (OrderService, None), (Billing, None)):
    shared.register(key, factory)
shared.resolve(Billing)
print(f"montar OrderService | à mão {best(manual):6.2f} µs | contêiner (transient, plano em cache) {best(lambda: fresh.resolve(OrderService)):6.2f} µs | singleton já pronto {best(lambda: shared.resolve(Billing)):5.2f} µs")
print(f"analisar a assinatura de OrderService | sem cache {best(lambda: plan.__wrapped__(OrderService), 2_000):6.1f} µs | com cache {best(lambda: plan(OrderService)):5.2f} µs (get_type_hints + inspect.signature são os custos escondidos de um contêiner)")
