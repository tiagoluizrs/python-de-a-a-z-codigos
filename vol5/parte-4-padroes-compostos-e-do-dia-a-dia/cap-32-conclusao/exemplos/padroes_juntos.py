"""Os padrões trabalhando juntos: um gerador de relatórios que usa OITO padrões do volume, cada um onde se paga, e o que isso custa em relação a um laço simples."""
import functools
import json
import time
from dataclasses import dataclass
from datetime import datetime

FIXED = datetime(2026, 1, 1, 12, 0)


@dataclass(frozen=True)
class Sale:
    id: int
    customer: str
    country: str
    amount_cents: int
    vip: bool = False


SALES = [
    Sale(1, "Ana", "BR", 12_000, vip=True),
    Sale(2, "Bia", "BR", 4_500),
    Sale(3, "Caio", "PT", 30_000),
    Sale(4, "Duda", "US", 9_900, vip=True),
    Sale(5, "Edu", "BR", 25_000),
    Sale(6, "Fabi", "PT", 800),
]


# 1) Repository (Capítulo 28): os dados atrás de uma coleção; o serviço não sabe de onde vêm
class InMemorySales:
    def __init__(self, sales):
        self._sales = list(sales)

    def all(self):
        return list(self._sales)


# 2) Specification (Capítulo 29): as regras de filtro são objetos que se combinam
class Spec:
    def __init__(self, fn, description):
        self.fn, self.description = fn, description

    def __call__(self, sale):
        return bool(self.fn(sale))

    def __and__(self, other):
        return Spec(lambda s: self(s) and other(s), f"({self.description} e {other.description})")

    def __or__(self, other):
        return Spec(lambda s: self(s) or other(s), f"({self.description} ou {other.description})")

    def __invert__(self):
        return Spec(lambda s: not self(s), f"não {self.description}")

    def __repr__(self):
        return self.description


from_br = Spec(lambda s: s.country == "BR", "do BR")
big = Spec(lambda s: s.amount_cents >= 10_000, "valor >= 100,00")
is_vip = Spec(lambda s: s.vip, "VIP")

# 3) Strategy (Capítulo 15): a ordenação é uma função escolhida pelo nome
ORDERINGS = {"id": lambda s: s.id, "amount": lambda s: -s.amount_cents, "customer": lambda s: s.customer}


# 4) Registry (Capítulo 30): os formatos se cadastram sozinhos, com um decorador
class Registry:
    def __init__(self, kind):
        self.kind, self._items = kind, {}

    def register(self, name):
        def decorator(fn):
            if name in self._items:
                raise ValueError(f"{self.kind} já registrado: {name}")
            self._items[name] = fn
            return fn
        return decorator

    def get(self, name):
        try:
            return self._items[name]
        except KeyError:
            raise KeyError(f"{self.kind} desconhecido: {name!r}; disponíveis: {', '.join(sorted(self._items))}") from None


formats = Registry("formato")


@formats.register("csv")
def to_csv(rows):
    return "\n".join(["id,cliente,valor"] + [f"{s.id},{s.customer},{s.amount_cents / 100:.2f}" for s in rows])


@formats.register("json")
def to_json(rows):
    return json.dumps([{"id": s.id, "cliente": s.customer, "valor": s.amount_cents / 100} for s in rows], ensure_ascii=False)


@formats.register("text")
def to_text(rows):
    return "; ".join(f"{s.customer} R$ {s.amount_cents / 100:.2f}" for s in rows)


# 5) Decorator (Capítulo 10): medir o tempo sem mexer na função
def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        try:
            return fn(*args, **kwargs)
        finally:
            wrapper.last_ns = time.perf_counter_ns() - start
    wrapper.last_ns = 0
    return wrapper


# 6) Observer (Capítulo 16): uma lista de funções avisada a cada linha
class Signal:
    def __init__(self):
        self._handlers = []

    def connect(self, fn):
        self._handlers.append(fn)
        return fn

    def emit(self, *args):
        for handler in list(self._handlers):
            handler(*args)


# 7) Null Object (Capítulo 27): o logger que não loga, como padrão inofensivo
class NullLogger:
    def info(self, message):
        pass

    error = info


NULL_LOGGER = NullLogger()


# 8) Injeção de Dependência (Capítulo 31): o serviço RECEBE tudo; quem monta é a raiz de composição
class ReportService:
    def __init__(self, repo, formats, clock, logger=None, progress=None):
        self.repo, self.formats, self.clock = repo, formats, clock
        self.logger = NULL_LOGGER if logger is None else logger
        self.progress = Signal() if progress is None else progress

    @timed
    def generate(self, fmt, *, where=None, order_by="id"):
        render = self.formats.get(fmt)                                   # o catálogo de formatos (Registry), com a mensagem das opções
        rows = [s for s in self.repo.all() if where is None or where(s)]
        rows.sort(key=ORDERINGS[order_by])
        for i, _ in enumerate(rows, 1):
            self.progress.emit(i, len(rows))
        self.logger.info(f"gerado {fmt}: {len(rows)} linhas")
        return {"format": fmt, "count": len(rows), "content": render(rows), "at": self.clock().isoformat()}


class RecordingLogger:
    def __init__(self):
        self.lines = []

    def info(self, message):
        self.lines.append(message)

    error = info


def build_service(env):                                                   # a raiz de composição: o ÚNICO lugar que escolhe os concretos
    if env == "test":
        return ReportService(InMemorySales(SALES), formats, lambda: FIXED, RecordingLogger())
    if env == "prod":
        return ReportService(InMemorySales(SALES), formats, datetime.now)
    raise ValueError(f"ambiente desconhecido: {env!r}")


service = build_service("test")
events = []
service.progress.connect(lambda i, n: events.append(f"{i}/{n}"))
rule = from_br & big & ~is_vip
result = service.generate("csv", where=rule, order_by="amount")
print("regra:", rule)
print("csv:", result["content"].replace("\n", " | "), "|", result["count"], "linhas |", result["at"])
print("progresso (Observer):", events, "| log (Null Object trocado por um gravador no teste):", service.logger.lines)
print("json:", service.generate("json", where=from_br | is_vip, order_by="customer")["content"][:70], "...")
try:
    service.generate("xml")
except KeyError as error:
    print("formato inválido:", error.args[0])
print(f"tempo do último generate (Decorator): {service.generate.last_ns / 1000:.1f} µs")
print("o serviço de produção, sem logger nem observadores (os padrões opcionais ficaram nulos):", build_service("prod").generate("text", where=big)["content"])

# --- o custo da composição, em relação a um laço direto ---
BIG = SALES * 1_667                                                       # ~10.000 vendas


def plain(sales):
    rows = sorted((s for s in sales if s.country == "BR" and s.amount_cents >= 10_000 and not s.vip), key=lambda s: -s.amount_cents)
    return "\n".join(["id,cliente,valor"] + [f"{s.id},{s.customer},{s.amount_cents / 100:.2f}" for s in rows])


big_service = ReportService(InMemorySales(BIG), formats, lambda: FIXED)


def ms(fn, n=20):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1000


simple = lambda s: s.country == "BR" and s.amount_cents >= 10_000 and not s.vip           # a mesma regra, como um predicado simples
composed = ms(lambda: big_service.generate("csv", where=rule, order_by="amount"))
light = ms(lambda: big_service.generate("csv", where=simple, order_by="amount"))
direct = ms(lambda: plain(BIG))
print(f"\n{len(BIG)} vendas | laço direto {direct:5.2f} ms | composição com a regra como Specification {composed:5.2f} ms ({composed / direct:.1f}x) | com um predicado simples no lugar da Specification {light:5.2f} ms ({light / direct:.1f}x)")
print("quase todo o custo extra está em UMA peça (a regra como árvore de objetos, Capítulo 29); Repository, Registry, Strategy, Decorator, Observer, Null Object e DI juntos custam pouco. Moral: escolha cada padrão pelo que ele compra, e meça o que ele cobra")
