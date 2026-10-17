"""Factory Method, forma pythônica: a classe é um objeto, então ela pode ser guardada, passada e chamada."""
import functools
import io
import tempfile
import time
from collections import namedtuple
from dataclasses import dataclass, make_dataclass
from datetime import date
from pathlib import Path


class Email:
    def send(self, to, text):
        return f"email para {to}: {text}"


class Sms:
    def send(self, to, text):
        return f"sms para {to}: {text}"


# --- 1. a fábrica simples: um dicionário de classes (ou de funções) ---
CHANNELS = {"email": Email, "sms": Sms}


def make_notifier(channel: str):
    try:
        return CHANNELS[channel]()
    except KeyError:
        raise ValueError(f"canal desconhecido: {channel!r}; disponíveis: {', '.join(sorted(CHANNELS))}") from None


print(make_notifier("sms").send("ana", "oi"))
try:
    make_notifier("fax")
except ValueError as error:
    print("erro com a lista de opções:", error)

CHANNELS["push"] = type("Push", (), {"send": lambda self, to, text: f"push para {to}: {text}"})   # um canal novo: UMA linha, sem editar make_notifier
print("canal novo registrado:", make_notifier("push").send("ana", "oi"))


# --- 2. passar a CLASSE como parâmetro: o 'factory method' vira um argumento ---
class Alert:
    def __init__(self, notifier_cls=Email):
        self.notifier_cls = notifier_cls                 # a classe é um valor como outro qualquer

    def raise_alert(self, to, text):
        return self.notifier_cls().send(to, f"[ALERTA] {text}")


print("\nclasse como argumento:", Alert(Sms).raise_alert("ana", "disco cheio"))
print("sem criador abstrato, sem subclasse por produto: Alert(Sms) faz o trabalho de SmsAlert")


# --- 3. construtores alternativos: @classmethod (o factory method mais comum da biblioteca padrão) ---
print("\nna biblioteca padrão:")
print("  dict.fromkeys('ab', 0)        ->", dict.fromkeys("ab", 0))
print("  date.fromisoformat('2026-10-13') ->", date.fromisoformat("2026-10-13"))
print("  int.from_bytes(bytes([1, 0]), 'little') ->", int.from_bytes(bytes([1, 0]), "little"))
print("  Path.home() é uma Path?       ->", isinstance(Path.home(), Path))


@dataclass(frozen=True)
class Temperature:
    celsius: float

    @classmethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    @classmethod
    def from_kelvin(cls, k):
        return cls(k - 273.15)


class Room(Temperature):
    pass


t = Room.from_kelvin(300)
print("\nclassmethod usa `cls`: Room.from_kelvin devolve", type(t).__name__, f"({t.celsius:.2f} °C), não Temperature; Temperature.from_fahrenheit(212) ->", Temperature.from_fahrenheit(212))


# --- 4. functools.partial: uma fábrica com valores padrão ---
@dataclass
class Connection:
    host: str
    port: int = 5432
    timeout: float = 5.0


local_db = functools.partial(Connection, "localhost", timeout=1.0)
print("\npartial como fábrica:", local_db(), "|", local_db(port=6543))

# --- 5. a própria biblioteca padrão escolhe a classe pelo argumento: open() ---
with tempfile.TemporaryDirectory() as folder:
    f = Path(folder) / "x.bin"
    f.write_bytes(b"abc")
    with open(f) as a, open(f, "rb") as b:
        print("\nopen(f) ->", type(a).__name__, "| open(f, 'rb') ->", type(b).__name__, "| ambos são fábricas de objetos arquivo")

# --- 6. fábricas de CLASSES: namedtuple e make_dataclass ---
Point = namedtuple("Point", "x y")
Item = make_dataclass("Item", [("name", str), ("price", float)])
print("namedtuple e make_dataclass criam classes em tempo de execução:", Point(1, 2), Item("lápis", 1.5))


# --- 7. o custo: if/elif, dicionário, classe como argumento, construtor direto ---
def make_if(channel):
    if channel == "email":
        return Email()
    elif channel == "sms":
        return Sms()
    raise ValueError(channel)


def best(fn, n=300_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


alert = Alert(Sms)
print("\ncusto de criar um objeto:")
for label, fn in [("construtor direto Sms()", lambda: Sms()), ("if/elif (último ramo)", lambda: make_if("sms")),
                  ("dicionário de classes", lambda: make_notifier("sms")), ("classe guardada (alert.notifier_cls())", lambda: alert.notifier_cls())]:
    print(f"  {label:<38} {best(fn):6.0f} ns")
print("o dicionário custa uma busca por hash a mais que o construtor direto: dezenas de ns; a escolha é de DESIGN, não de velocidade")
