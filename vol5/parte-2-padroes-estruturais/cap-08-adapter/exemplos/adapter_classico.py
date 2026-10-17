"""Adapter, forma clássica (GoF): fazer uma classe com a interface ERRADA servir a quem espera outra, sem editar nenhuma das duas."""
import ast
import inspect
import textwrap
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


# --- 1. a interface que o NOSSO código espera (o "alvo", Target) ---
@dataclass(frozen=True)
class Receipt:
    ok: bool
    reference: str
    message: str = ""


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount_cents: int, currency: str, token: str) -> Receipt: ...


def checkout(gateway: PaymentGateway, amount_cents: int):
    receipt = gateway.charge(amount_cents, "BRL", "tok_123")
    return f"pago ({receipt.reference})" if receipt.ok else f"recusado: {receipt.message}"


# --- 2. a classe que já existe e NÃO podemos mudar (o "adaptado", Adaptee): biblioteca de terceiros, código legado ---
class LegacyBank:
    CURRENCIES = {986: "BRL", 840: "USD"}

    def make_payment(self, card_number: str, value: float, curr_code: int):
        """Devolve (status, referência): status 0 = aprovado; qualquer outro valor = recusado."""
        if curr_code not in self.CURRENCIES:
            return 99, ""
        if value > 1000:
            return 51, ""                                    # limite excedido
        return 0, f"LB-{card_number[-3:]}-{round(value * 100)}"


bank = LegacyBank()
try:
    checkout(bank, 1990)                                     # type: ignore[arg-type]
except AttributeError as error:
    print("sem adaptador, as interfaces não se encaixam:", error)


# --- 3. o adaptador de OBJETO (composição): implementa o alvo e DELEGA ao adaptado ---
class LegacyBankAdapter(PaymentGateway):
    NUMERIC = {"BRL": 986, "USD": 840}
    MESSAGES = {51: "limite excedido", 99: "moeda inválida"}

    def __init__(self, bank: LegacyBank):
        self._bank = bank

    def charge(self, amount_cents, currency, token):
        status, reference = self._bank.make_payment(token, amount_cents / 100, self.NUMERIC.get(currency, 0))
        if status == 0:
            return Receipt(True, reference)
        return Receipt(False, "", self.MESSAGES.get(status, f"erro {status}"))


adapter = LegacyBankAdapter(bank)
print("\nadaptador de objeto:", checkout(adapter, 1990), "|", checkout(adapter, 250_000))
print("o cliente (checkout) não mudou, o LegacyBank não mudou: só o adaptador conhece os dois lados")


# --- 4. o adaptador de CLASSE (herança múltipla): herda do alvo E do adaptado ---
class LegacyBankClassAdapter(PaymentGateway, LegacyBank):
    def charge(self, amount_cents, currency, token):
        status, reference = self.make_payment(token, amount_cents / 100, {"BRL": 986, "USD": 840}.get(currency, 0))
        return Receipt(status == 0, reference, "" if status == 0 else f"erro {status}")


print("adaptador de classe:", checkout(LegacyBankClassAdapter(), 1990), "| mais curto, mas preso a UMA classe adaptada (não adapta subclasses nem outros objetos)")


# --- 5. por que o adaptador de OBJETO costuma ser melhor: adapta qualquer objeto com a interface do adaptado (inclusive um dublê de teste) ---
class FakeBank:
    def make_payment(self, card_number, value, curr_code):
        return 0, "FAKE-1"


print("o mesmo adaptador com um dublê:", checkout(LegacyBankAdapter(FakeBank()), 100))


# --- 6. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nPaymentGateway + adaptador:", measure([PaymentGateway, LegacyBankAdapter]))


def best(fn, n=300_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


print(f"chamar o legado direto: {best(lambda: bank.make_payment('4111111111111111', 19.9, 986)):5.0f} ns | pelo adaptador: {best(lambda: adapter.charge(1990, 'BRL', '4111111111111111')):5.0f} ns")
print("o adaptador acrescenta uma chamada e a conversão dos dados: centenas de ns, que desaparecem diante de qualquer chamada de rede")
