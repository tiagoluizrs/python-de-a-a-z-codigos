"""Template Method em Python: funções que recebem os passos, gerenciadores de contexto, e os "templates" da biblioteca padrão (ABCs, ganchos)."""
import ast
import csv
import datetime
import inspect
import io
import json
import textwrap
import unittest
from collections.abc import MutableSet, Sequence
from contextlib import contextmanager


# --- 1. o roteiro como FUNÇÃO: os passos variáveis são argumentos ---
def run_import(raw, parse, *, validate=None, transform=None, before=None, after=None):
    if before:
        before()
    rows, errors = [], []
    for i, row in enumerate(parse(raw)):
        try:
            if validate:
                validate(row)
        except ValueError as error:
            errors.append((i, str(error)))
            continue
        rows.append(transform(row) if transform else row)
    if after:
        after(rows, errors)
    return rows, errors


def require_name(row):
    if not row["name"]:
        raise ValueError("nome vazio")


def normalize(row):
    row["name"] = row["name"].strip().title()
    return row


def parse_csv(raw):
    return csv.DictReader(io.StringIO(raw))


audit = []
print("função com passos:", run_import("name,age\nana,3\n,5\n", parse_csv, validate=require_name, transform=normalize,
                                       before=lambda: audit.append("início"), after=lambda rows, errors: audit.append(f"fim: {len(rows)}/{len(errors)}")), audit)
print("outro formato = outra função de parse:", run_import('[{"name": " bia "}]', json.loads, validate=require_name, transform=normalize))
print("sem herança, sem @abstractmethod, sem super(): os passos são argumentos e os opcionais têm padrão None")

# --- 2. o template de abrir/fechar: o gerenciador de contexto (o passo variável é o CORPO do with) ---
@contextmanager
def timed(label, sink, clock):
    start = clock()
    try:
        yield                                                  # <- aqui entra o passo variável, escrito por quem usa o with
    finally:
        sink.append((label, round(clock() - start, 3)))


ticks = iter([0.0, 1.5, 10.0, 10.25])
sink = []
with timed("carregar", sink, lambda: next(ticks)):
    pass
try:
    with timed("falha", sink, lambda: next(ticks)):
        raise RuntimeError("erro no meio")
except RuntimeError:
    pass
print("\ngerenciador de contexto: o esqueleto (medir, mesmo com erro) fica no @contextmanager; o corpo muda a cada uso ->", sink)

# --- 3. a biblioteca padrão é cheia de templates: as ABCs de collections.abc (métodos mixin) ---
class Countdown(Sequence):
    """Só __getitem__ e __len__: a ABC já oferece __iter__, __contains__, __reversed__, index e count."""

    def __init__(self, start):
        self.start = start

    def __len__(self):
        return self.start + 1

    def __getitem__(self, i):
        if isinstance(i, slice):
            return [self[j] for j in range(*i.indices(len(self)))]
        if not 0 <= i < len(self):
            raise IndexError(i)
        return self.start - i


c = Countdown(4)
print("\nSequence a partir de 2 métodos:", list(c), "| 2 in c:", 2 in c, "| reversed:", list(reversed(c)), "| index(1):", c.index(1), "| count(3):", c.count(3), "| c[1:3]:", c[1:3])


class OrderedSet(MutableSet):
    def __init__(self, items=()):
        self._d = dict.fromkeys(items)

    def __contains__(self, item):
        return item in self._d

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def add(self, item):
        self._d[item] = None

    def discard(self, item):
        self._d.pop(item, None)

    def __repr__(self):
        return f"OrderedSet({list(self._d)})"


a, b = OrderedSet([3, 1, 2]), OrderedSet([2, 5])
print("MutableSet a partir de 5 métodos:", a | b, "|", a & b, "|", a - b, "| isdisjoint:", a.isdisjoint({9}), "| a <= a|b:", a <= (a | b))

# --- 4. os ganchos (hooks) da biblioteca padrão: json.JSONEncoder.default, unittest.setUp/tearDown ---
class DateEncoder(json.JSONEncoder):
    def default(self, o):                                      # o gancho: só é chamado para o que o JSON não conhece
        if isinstance(o, datetime.date):
            return o.isoformat()
        return super().default(o)


print("\njson.JSONEncoder.default (um gancho):", json.dumps({"quando": datetime.date(2026, 10, 15)}, cls=DateEncoder))

events = []


class Demo(unittest.TestCase):
    def setUp(self):
        events.append("setUp")

    def tearDown(self):
        events.append("tearDown")

    def test_a(self):
        events.append("test_a")

    def test_b(self):
        events.append("test_b")


unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(Demo))
print("unittest.TestCase: o esqueleto (setUp -> teste -> tearDown) é da base; você escreve só os testes:", events)


# --- 5. o custo de código ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nrun_import (função com passos):", measure([run_import]), "| mais parse_csv e as regras:", measure([run_import, require_name, normalize, parse_csv]))
