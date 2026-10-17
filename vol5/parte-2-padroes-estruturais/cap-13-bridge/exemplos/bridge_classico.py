"""Bridge, forma clássica (GoF): separar uma ABSTRAÇÃO da sua IMPLEMENTAÇÃO para que as duas variem de forma independente."""
from abc import ABC, abstractmethod


# --- 1. o problema: duas dimensões de variação em UMA hierarquia de herança ---
class EmailAlert:                       # tipo de mensagem x canal: cada combinação é uma classe
    def send(self, to, body):
        return f"EMAIL para {to}: [ALERTA] {body.upper()}"


class SmsAlert:
    def send(self, to, body):
        return f"SMS para {to}: [ALERTA] {body.upper()}"


class EmailReport:
    def send(self, to, body):
        return f"EMAIL para {to}: Relatório -- {body}"


class SmsReport:
    def send(self, to, body):
        return f"SMS para {to}: Relatório -- {body}"


print("herança por combinação:", EmailAlert().send("ana", "disco cheio"))
print("2 tipos x 2 canais = 4 classes; mais um canal (Slack) = +2; mais um tipo (Lembrete) = +3; 3 tipos x 4 canais = 12 classes")


# --- 2. o Bridge: duas hierarquias independentes, ligadas por COMPOSIÇÃO (a "ponte") ---
class Channel(ABC):                     # a IMPLEMENTAÇÃO: como entregar
    @abstractmethod
    def deliver(self, to: str, text: str) -> str: ...


class Email(Channel):
    def deliver(self, to, text):
        return f"EMAIL para {to}: {text}"


class Sms(Channel):
    def deliver(self, to, text):
        return f"SMS para {to}: {text}"


class Slack(Channel):
    def deliver(self, to, text):
        return f"SLACK #{to}: {text}"


class Message(ABC):                     # a ABSTRAÇÃO: o que dizer. Guarda a ponte para um Channel
    def __init__(self, channel: Channel):
        self._channel = channel

    @abstractmethod
    def format(self, body: str) -> str: ...

    def send(self, to, body):
        return self._channel.deliver(to, self.format(body))          # a ponte: delega a entrega


class Alert(Message):
    def format(self, body):
        return f"[ALERTA] {body.upper()}"


class Report(Message):
    def format(self, body):
        return f"Relatório -- {body}"


class Reminder(Message):
    def format(self, body):
        return f"Lembrete: {body}"


channels = [Email(), Sms(), Slack()]
messages = [Alert, Report, Reminder]
print("\nbridge: qualquer mensagem com qualquer canal, escolhidos na hora:")
for cls in messages:
    print(" ", cls(channels[0]).send("ana", "backup concluído"), "|", cls(channels[2]).send("ops", "backup concluído"))

# --- 3. a contagem: m x n contra m + n ---
print("\nclasses necessárias, por número de tipos de mensagem (m) e de canais (n):")
print("  m  n | herança por combinação (m x n) | bridge (m + n + 2 bases)")
for m_, n_ in [(2, 2), (3, 3), (3, 4), (5, 5), (10, 6)]:
    print(f"  {m_:>2} {n_:>2} | {m_ * n_:>30} | {m_ + n_ + 2:>24}")

# --- 4. a ponte permite TROCAR a implementação em tempo de execução ---
alert = Alert(Email())
print("\ntroca de canal em tempo de execução:", alert.send("ana", "falha no deploy"), "->", end=" ")
alert._channel = Sms()                                                 # a abstração não muda; a implementação sim
print(alert.send("ana", "falha no deploy"))

# --- 5. e novas abstrações e implementações entram SEM tocar nas existentes ---
class Fax(Channel):
    def deliver(self, to, text):
        return f"FAX para {to}: {text}"


class Urgent(Alert):
    def format(self, body):
        return super().format(body) + " !!!"


print("canal novo + tipo novo, nenhuma classe antiga editada:", Urgent(Fax()).send("ana", "incêndio"))
