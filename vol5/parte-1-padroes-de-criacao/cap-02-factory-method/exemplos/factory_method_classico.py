"""Factory Method, forma clássica (GoF): o criador define COMO usar o produto e deixa as subclasses decidirem QUAL produto criar."""
import ast
import inspect
import json
import textwrap
import time
from abc import ABC, abstractmethod


# --- 1. o problema: quem usa decide a classe concreta, e a decisão se espalha ---
class EmailNotifier:
    def send(self, to, text):
        return f"email para {to}: {text}"


class SmsNotifier:
    def send(self, to, text):
        return f"sms para {to}: {text}"


def notify_v1(channel, to, text):
    if channel == "email":
        notifier = EmailNotifier()
    elif channel == "sms":
        notifier = SmsNotifier()
    else:
        raise ValueError(channel)
    return notifier.send(to, text)                       # cada canal novo EDITA esta função (e todas as que se parecem com ela)


# --- 2. a forma clássica: o criador abstrato e uma subclasse por produto ---
class Notifier(ABC):
    @abstractmethod
    def send(self, to: str, text: str) -> str: ...


class Email(Notifier):
    def send(self, to, text):
        return f"email para {to}: {text}"


class Sms(Notifier):
    def send(self, to, text):
        return f"sms para {to}: {text}"


class Alert(ABC):
    """O CRIADOR: a regra de negócio (montar a mensagem, enviar) fica aqui; QUAL notificador usar, nas subclasses."""

    @abstractmethod
    def create_notifier(self) -> Notifier:               # o factory method
        ...

    def raise_alert(self, to, level, text):
        notifier = self.create_notifier()
        return notifier.send(to, f"[{level.upper()}] {text}")


class EmailAlert(Alert):
    def create_notifier(self):
        return Email()


class SmsAlert(Alert):
    def create_notifier(self):
        return Sms()


for alert in (EmailAlert(), SmsAlert()):
    print(alert.raise_alert("ana", "warn", "disco cheio"))

print("\nacrescentar o canal 'push': escreve Push + PushAlert; Alert, EmailAlert e SmsAlert não são tocadas (OCP)")


class Push(Notifier):
    def send(self, to, text):
        return f"push para {to}: {text}"


class PushAlert(Alert):
    def create_notifier(self):
        return Push()


print(PushAlert().raise_alert("ana", "info", "nova versão"))


# --- 3. o preço: contar a cerimônia ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nversão com if/elif (sem o padrão):", measure([EmailNotifier, SmsNotifier, notify_v1]))
print("versão com Factory Method clássico:", measure([Notifier, Email, Sms, Alert, EmailAlert, SmsAlert]))


# --- 4. o custo de uma chamada ---
def best(fn, n=200_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


email_alert = EmailAlert()
print(f"\nnotify_v1('email') {best(lambda: notify_v1('email', 'a', 'b')):5.0f} ns | EmailAlert().raise_alert {best(lambda: email_alert.raise_alert('a', 'w', 'b')):5.0f} ns")

# --- 5. onde a forma clássica ainda faz sentido: o criador TEM mais comportamento além de criar (um framework com pontos de extensão) ---
print("\nquando a hierarquia de criadores se paga: o criador tem uma regra complexa em volta da criação (ciclo de vida, validação, registro)")
print("e vários pontos de extensão. Se o criador só devolve o objeto, a subclasse é cerimônia: veja o exemplo seguinte")
