"""Exercício 3: o capstone: um gerador de relatórios que COMPÕE seis padrões do volume (Repository, Specification, Registry, Strategy, Observer e Null Object) por Injeção de Dependência."""
import json
from dataclasses import dataclass
from datetime import datetime

FIXED = datetime(2026, 1, 1, 12, 0)


# ---- (Pronto, NÃO edite.) As peças dos capítulos anteriores ----
@dataclass(frozen=True)
class Sale:
    id: int
    customer: str
    country: str
    amount_cents: int
    vip: bool = False


class InMemorySales:                                            # Repository (Capítulo 28)
    def __init__(self, sales):
        self._sales = list(sales)
        self.reads = 0

    def all(self):
        self.reads += 1
        return list(self._sales)


class Spec:                                                     # Specification (Capítulo 29)
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


class Registry:                                                 # Registry (Capítulo 30)
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


ORDERINGS = {"id": lambda s: s.id, "amount": lambda s: -s.amount_cents, "customer": lambda s: s.customer}      # Strategy (Capítulo 15)


class Signal:                                                   # Observer (Capítulo 16)
    def __init__(self):
        self._handlers = []

    def connect(self, fn):
        self._handlers.append(fn)
        return fn

    def emit(self, *args):
        for handler in list(self._handlers):
            handler(*args)


class NullLogger:                                               # Null Object (Capítulo 27)
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


# ---- Implemente a partir daqui ----
formats = Registry("formato")


def to_csv(rows):
    """Registre com ``@formats.register("csv")``. O texto: a linha ``"id,cliente,valor"`` e, para cada venda, ``f"{id},{customer},{amount_cents / 100:.2f}"``, tudo unido por ``"\\n"``."""
    raise NotImplementedError


def to_json(rows):
    """Registre como ``"json"``. ``json.dumps`` (com ``ensure_ascii=False``) de uma lista de dicionários ``{"id": id, "cliente": customer, "valor": amount_cents / 100}``."""
    raise NotImplementedError


def to_text(rows):
    """Registre como ``"text"``. ``"; ".join(f"{customer} R$ {amount_cents / 100:.2f}")`` (``""`` se não há vendas)."""
    raise NotImplementedError


class ReportService:
    """``ReportService(repo, formats, clock, logger=None, progress=None)``: RECEBE tudo; ``logger`` ``None`` vira ``NULL_LOGGER`` e ``progress`` ``None`` vira um ``Signal()`` novo (use ``is None``).

    ``generate(fmt, *, where=None, order_by="id")``:

    * PRIMEIRO ``formats.get(fmt)`` (formato desconhecido: o ``KeyError`` do registro, ANTES de ler o repositório: ``repo.reads`` não muda);
    * ``order_by`` fora de ``ORDERINGS``: ``ValueError(f"ordenação desconhecida: {order_by!r}; disponíveis: amount, customer, id")`` (também ANTES de ler o repositório);
    * as vendas de ``repo.all()`` que satisfazem ``where`` (um ``Spec`` ou qualquer função; ``None`` não filtra), ordenadas com ``key=ORDERINGS[order_by]``;
    * ``progress.emit(i, total)`` para cada venda mantida (``i`` de 1), na ordem do relatório;
    * ``logger.info(f"gerado {fmt}: {n} linhas")`` depois de renderizar; se a renderização levantar uma exceção: ``logger.error(f"falhou {fmt}: {NomeDoTipoDoErro}")`` e a exceção sobe;
    * devolve ``{"format": fmt, "count": n, "content": texto, "at": clock().isoformat()}``."""

    def __init__(self, repo, formats, clock, logger=None, progress=None):
        raise NotImplementedError

    def generate(self, fmt, *, where=None, order_by="id") -> dict:
        raise NotImplementedError


def build_service(env: str, sales) -> ReportService:
    """A raiz de composição: ``"test"``: ``InMemorySales(sales)``, o registro ``formats``, ``lambda: FIXED`` e um ``RecordingLogger()``; ``"prod"``: ``InMemorySales(sales)``, ``formats``,
    ``datetime.now`` e SEM logger (nem observador); outro ambiente: ``ValueError(f"ambiente desconhecido: {env!r}")``."""
    raise NotImplementedError
