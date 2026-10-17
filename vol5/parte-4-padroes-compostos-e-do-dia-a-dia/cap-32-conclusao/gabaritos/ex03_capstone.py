"""Gabarito do exercício 3."""
import json
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


class InMemorySales:
    def __init__(self, sales):
        self._sales = list(sales)
        self.reads = 0

    def all(self):
        self.reads += 1
        return list(self._sales)


class Spec:
    def __init__(self, fn, description="?"):
        self.fn, self.description = fn, description

    def __call__(self, item):
        return bool(self.fn(item))

    def __and__(self, other):
        return Spec(lambda i: self(i) and other(i), f"({self.description} e {other.description})")

    def __or__(self, other):
        return Spec(lambda i: self(i) or other(i), f"({self.description} ou {other.description})")

    def __invert__(self):
        return Spec(lambda i: not self(i), f"não {self.description}")


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

    def names(self):
        return sorted(self._items)


ORDERINGS = {"id": lambda s: s.id, "amount": lambda s: -s.amount_cents, "customer": lambda s: s.customer}


class Signal:
    def __init__(self):
        self._handlers = []

    def connect(self, fn):
        self._handlers.append(fn)
        return fn

    def emit(self, *args):
        for handler in list(self._handlers):
            handler(*args)


class NullLogger:
    def info(self, message):
        pass

    error = info


NULL_LOGGER = NullLogger()


class RecordingLogger:
    def __init__(self):
        self.lines = []

    def info(self, message):
        self.lines.append(("info", message))

    def error(self, message):
        self.lines.append(("error", message))


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


class ReportService:
    def __init__(self, repo, formats, clock, logger=None, progress=None):
        self.repo, self.formats, self.clock = repo, formats, clock
        self.logger = NULL_LOGGER if logger is None else logger
        self.progress = Signal() if progress is None else progress

    def generate(self, fmt, *, where=None, order_by="id"):
        render = self.formats.get(fmt)
        if order_by not in ORDERINGS:
            raise ValueError(f"ordenação desconhecida: {order_by!r}; disponíveis: {', '.join(sorted(ORDERINGS))}")
        rows = [s for s in self.repo.all() if where is None or where(s)]
        rows.sort(key=ORDERINGS[order_by])
        for i, _ in enumerate(rows, 1):
            self.progress.emit(i, len(rows))
        try:
            content = render(rows)
        except Exception as error:
            self.logger.error(f"falhou {fmt}: {type(error).__name__}")
            raise
        self.logger.info(f"gerado {fmt}: {len(rows)} linhas")
        return {"format": fmt, "count": len(rows), "content": content, "at": self.clock().isoformat()}


def build_service(env, sales):
    if env == "test":
        return ReportService(InMemorySales(sales), formats, lambda: FIXED, RecordingLogger())
    if env == "prod":
        return ReportService(InMemorySales(sales), formats, datetime.now)
    raise ValueError(f"ambiente desconhecido: {env!r}")
