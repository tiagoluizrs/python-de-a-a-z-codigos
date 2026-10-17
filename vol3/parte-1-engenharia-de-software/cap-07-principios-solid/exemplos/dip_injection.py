"""D: Inversão de Dependência. O código de alto nível (a regra) não depende do de baixo nível (SMTP, relógio, banco): ambos dependem de uma abstração."""
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol


# --- 1. a regra que CRIA o que usa: impossível de testar sem o mundo de fora ---
class ReminderV1:
    def __init__(self):
        import smtplib                                                   # a regra conhece SMTP, o servidor e o relógio
        self.smtplib = smtplib

    def due_reminders(self, reminders):
        now = datetime.now(timezone.utc)                                 # relógio fixo: o teste depende de "agora"
        return [r for r in reminders if r["at"] <= now]

    def run(self, reminders):
        for r in self.due_reminders(reminders):
            try:
                with self.smtplib.SMTP("localhost", 25, timeout=1) as server:      # rede de verdade em cada teste
                    server.sendmail("lembretes@x.com", r["to"], r["text"])
            except OSError:
                pass


# --- 2. a versão invertida: a regra declara o que PRECISA (o papel); quem chama decide o concreto ---
class Sender(Protocol):
    def send(self, to: str, text: str) -> None: ...


@dataclass
class Reminder:
    at: datetime
    to: str
    text: str


class ReminderService:
    def __init__(self, sender: Sender, now: Callable[[], datetime]):    # dependências: um Protocol e UMA FUNÇÃO
        self.sender, self.now = sender, now

    def run(self, reminders: list[Reminder]) -> list[Reminder]:
        due = [r for r in reminders if r.at <= self.now()]
        for r in due:
            self.sender.send(r.to, r.text)
        return due


class SmtpSender:
    def __init__(self, host):
        self.host = host

    def send(self, to, text):
        import smtplib
        with smtplib.SMTP(self.host, timeout=2) as server:
            server.sendmail("lembretes@x.com", to, text)


class FakeSender:
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    def send(self, to, text):
        self.sent.append((to, text))


# --- 3. o teste da versão invertida: determinístico, instantâneo, sem rede e sem relógio de verdade ---
fixed = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)
fake = FakeSender()
service = ReminderService(fake, now=lambda: fixed)
reminders = [Reminder(fixed - timedelta(hours=1), "ana@x.com", "reunião"), Reminder(fixed + timedelta(hours=1), "bia@x.com", "almoço")]
start = time.perf_counter()
due = service.run(reminders)
t_fake = (time.perf_counter() - start) * 1e6
print(f"teste com dublê: {len(due)} vencido, enviado a {fake.sent} em {t_fake:.0f} µs; o relógio é uma função: o 'agora' do teste é 2026-10-13 12:00 SEMPRE")

# --- 4. o teste da versão acoplada: depende da rede e do relógio ---
old = ReminderV1()
past = [{"at": datetime.now(timezone.utc) - timedelta(hours=1), "to": "ana@x.com", "text": "reunião"}]
start = time.perf_counter()
old.run(past)
t_real = (time.perf_counter() - start) * 1e3
print(f"teste da versão acoplada: {t_real:.0f} ms (tenta SMTP em localhost:25; o tempo depende da máquina e do sistema operacional) | {t_real * 1e3 / t_fake:,.0f}x mais lento")

# --- 5. injetar uma FUNÇÃO em vez de um objeto: o jeito mais leve em Python ---
def remind(reminders, send: Callable[[str, str], None], now: Callable[[], datetime]):
    for r in (r for r in reminders if r.at <= now()):
        send(r.to, r.text)


sent = []
remind(reminders, lambda to, text: sent.append((to, text)), lambda: fixed)
print("\nfunção com dependências como parâmetros (callables):", sent, "| sem classe, sem Protocol: bastou assinar os tipos")

# --- 6. a RAIZ DE COMPOSIÇÃO: o único lugar que escolhe o concreto ---
def build_service(env: dict) -> ReminderService:
    sender = SmtpSender(env["SMTP_HOST"]) if env.get("SMTP_HOST") else FakeSender()
    return ReminderService(sender, now=lambda: datetime.now(timezone.utc))


print("composição: SMTP_HOST ausente ->", type(build_service({}).sender).__name__, "| presente ->", type(build_service({"SMTP_HOST": "mail"}).sender).__name__)

# --- 7. DIP NÃO é injeção de dependência (é uma consequência): a ideia é a DIREÇÃO da dependência ---
print("\nDIP = a regra de negócio define a interface (Sender) e a infraestrutura se ADAPTA a ela; DI (injeção) é a técnica de entregar o concreto")
print("o import vai da infraestrutura (SmtpSender) para a regra (Sender), e não o contrário: a seta de dependência foi INVERTIDA")
