"""Adapter em Python: a duck typing dispensa muita coisa; o que sobra são funções, Protocols e delegação."""
import asyncio
import contextlib
import io
import operator
import time
from dataclasses import dataclass
from typing import Protocol


# --- 1. a duck typing: se os NOMES já combinam, não precisa de adaptador nenhum ---
class Duck:
    def speak(self):
        return "quack"


class Robot:
    def speak(self):
        return "bip"


print("duck typing:", [x.speak() for x in (Duck(), Robot())], "(sem interface comum, sem herança: basta ter o método)")


# --- 2. o alvo como Protocol (tipagem estrutural): documenta o que o cliente espera, sem obrigar herança ---
@dataclass(frozen=True)
class Receipt:
    ok: bool
    reference: str


class PaymentGateway(Protocol):
    def charge(self, amount_cents: int, currency: str, token: str) -> Receipt: ...


class LegacyBank:
    def make_payment(self, card_number, value, curr_code):
        return (0, f"LB-{card_number[-3:]}") if curr_code in (986, 840) else (99, "")


# --- 3. o adaptador mais curto: uma FUNÇÃO (quando o alvo tem uma operação só) ---
def charge_via_legacy(bank: LegacyBank):
    numeric = {"BRL": 986, "USD": 840}

    def charge(amount_cents, currency, token):
        status, reference = bank.make_payment(token, amount_cents / 100, numeric.get(currency, 0))
        return Receipt(status == 0, reference)

    return charge


charge = charge_via_legacy(LegacyBank())
print("\nadaptador-função:", charge(1990, "BRL", "tok_123"), charge(1990, "EUR", "tok_123"))
print("o cliente recebe um callable (Callable[[int, str, str], Receipt]) em vez de um objeto com charge(): menos cerimônia, mesmo contrato")


# --- 4. a delegação genérica: __getattr__ repassa tudo e renomeia só o que precisa ---
class Renamed:
    """Envolve um objeto e expõe alguns atributos/métodos com OUTROS nomes; o resto passa direto."""

    def __init__(self, obj, mapping):
        object.__setattr__(self, "_obj", obj)
        object.__setattr__(self, "_mapping", dict(mapping))                  # {nome_novo: nome_antigo}

    def __getattr__(self, name):
        return getattr(self._obj, self._mapping.get(name, name))

    def __setattr__(self, name, value):
        setattr(self._obj, self._mapping.get(name, name), value)


class OldCounter:
    def __init__(self):
        self.n = 0

    def incr(self):
        self.n += 1
        return self.n


modern = Renamed(OldCounter(), {"increment": "incr", "value": "n"})
modern.increment()
modern.increment()
print("\ndelegação com renomeação: value =", modern.value, "| increment() devolveu", modern.increment())


# --- 5. a biblioteca padrão está cheia de adaptadores ---
raw = io.BytesIO("olá, mundo\n".encode("utf-8"))
text = io.TextIOWrapper(raw, encoding="utf-8")                                # adapta um fluxo de BYTES a um fluxo de TEXTO
print("\nTextIOWrapper adapta bytes a texto:", text.readline().strip())


class Resource:                                                               # só tem close(), não é um gerenciador de contexto
    def close(self):
        print("  Resource.close() chamado")


with contextlib.closing(Resource()) as r:                                    # closing() adapta 'tem close()' para 'serve ao with'
    pass
print("contextlib.closing adapta um objeto com close() ao protocolo do with")

people = [("Ana", 31), ("Bia", 25)]
print("operator.itemgetter adapta uma operação ao formato que o sorted() espera (key):", sorted(people, key=operator.itemgetter(1)))


def read_blocks():
    f = io.BytesIO(b"abcdefgh")
    return list(iter(lambda: f.read(3), b""))                                 # iter(callable, sentinela) adapta uma função repetida a um iterador


print("iter(callable, sentinela):", read_blocks())


def slow_sync(x):
    time.sleep(0.01)
    return x * 2


async def main():
    return await asyncio.gather(*(asyncio.to_thread(slow_sync, i) for i in range(4)))


print("asyncio.to_thread adapta uma função síncrona ao mundo async:", asyncio.run(main()))


# --- 6. o custo ---
def best(fn, n=300_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


bank = LegacyBank()
counter = OldCounter()
modern = Renamed(counter, {"increment": "incr"})
print("\ncusto de chamar:")
for label, fn in [("método direto (counter.incr())", counter.incr), ("adaptador-função (charge(...))", lambda: charge(1990, "BRL", "tok_123")),
                  ("legado direto (make_payment)", lambda: bank.make_payment("tok_123", 19.9, 986)), ("delegação por __getattr__ (modern.increment())", lambda: modern.increment())]:
    print(f"  {label:<46} {best(fn):6.0f} ns")
print("a delegação por __getattr__ custa algumas vezes o método direto (a busca falha na instância e cai no método especial); o adaptador-função custa mais")
print("porque CONVERTE os dados (divisão, dicionário, tupla, criação do Receipt): o custo de um adaptador é, sobretudo, o da conversão que ele faz")
