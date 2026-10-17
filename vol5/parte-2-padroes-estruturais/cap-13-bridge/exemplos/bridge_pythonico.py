"""Bridge em Python: composição, um Protocol (ou só uma função) como "implementação", e as pontes que a biblioteca padrão já tem."""
import io
import json
import logging
import posixpath
import ntpath
import time
from pathlib import PurePosixPath, PureWindowsPath
from typing import Callable, Protocol


# --- 1. a implementação como Protocol: qualquer objeto com deliver() serve, sem herança ---
class Channel(Protocol):
    def deliver(self, to: str, text: str) -> str: ...


class Email:
    def deliver(self, to, text):
        return f"EMAIL para {to}: {text}"


class Console:
    def deliver(self, to, text):
        return f"CONSOLE {to}: {text}"


# --- 2. a abstração como UMA classe: o que varia é um dado (o formato), não uma subclasse ---
class Message:
    def __init__(self, channel: Channel, template: str = "{body}"):
        self.channel, self.template = channel, template

    def send(self, to, body):
        return self.channel.deliver(to, self.template.format(body=body))


alert = Message(Email(), "[ALERTA] {body}")
report = Message(Console(), "Relatório -- {body}")
print("classe única + dado:", alert.send("ana", "disco cheio"), "|", report.send("ops", "tudo certo"))
print("uma classe `Message` e dois ou três templates substituem a hierarquia inteira de abstrações: a variação cabia em um STRING")


# --- 3. quando a abstração PRECISA de comportamento: uma subclasse só para ela, ainda sem combinar com o canal ---
class Reminder(Message):
    def send(self, to, body):
        return super().send(to, body.capitalize() + " (não esqueça!)")


print(Reminder(Email()).send("ana", "pagar a conta"))

# --- 4. a implementação como FUNÇÃO: o Bridge mais enxuto ---
class Exporter:
    def __init__(self, write: Callable[[str], None]):
        self.write = write                                    # a ponte é um callable

    def export(self, rows):
        for row in rows:
            self.write(",".join(map(str, row)))


collected = []
Exporter(collected.append).export([(1, "a"), (2, "b")])
buffer = io.StringIO()
Exporter(lambda line: buffer.write(line + "\n")).export([(3, "c")])
print("\nfunção como implementação:", collected, "|", repr(buffer.getvalue()), "(trocar o destino é trocar um argumento)")

# --- 5. a biblioteca padrão já tem pontes ---
# (a) logging: Logger (abstração: nível, nome, mensagem) x Handler (implementação: onde escrever)
logger = logging.getLogger("demo")
logger.setLevel(logging.INFO)
logger.propagate = False
stream = io.StringIO()
handler = logging.StreamHandler(stream)
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
logger.addHandler(handler)
logger.info("pedido %d criado", 42)
print("\nlogging: o MESMO Logger, outro Handler -> escreveria em arquivo, rede ou memória:", repr(stream.getvalue()))

# (b) io.TextIOWrapper: a abstração de TEXTO sobre qualquer buffer de bytes
raw = io.BytesIO()
text = io.TextIOWrapper(raw, encoding="utf-8")
text.write("olá")
text.flush()
print("io.TextIOWrapper: texto sobre BytesIO ->", raw.getvalue(), "(o mesmo código de texto serve a arquivo, socket ou memória)")

# (c) json.dump(obj, fp): o serializador (abstração) x o destino (qualquer objeto com write)
sink = io.StringIO()
json.dump({"a": 1}, sink)
print("json.dump(obj, fp): serializador x destino:", sink.getvalue())

# (d) pathlib: PurePath (abstração) x o "sabor" do sistema (posixpath ou ntpath, a implementação)
posix, windows = PurePosixPath("a/b"), PureWindowsPath("a/b")
print("pathlib: a mesma abstração, duas implementações ->", posix, "|", windows, "| separador:", repr(posixpath.sep), repr(ntpath.sep))
flavour_attr = next((n for n in ("parser", "_flavour") if hasattr(PurePosixPath, n)), None)
print("  implementação guardada em PurePosixPath.%s:" % flavour_attr, getattr(PurePosixPath, flavour_attr).__name__ if flavour_attr else "?")

# --- 6. o custo da ponte: uma chamada a mais ---
def best(fn, n=300_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


email = Email()
msg = Message(email)
print(f"\nchamar a implementação direto: {best(lambda: email.deliver('a', 'b')):4.0f} ns | pela ponte (Message.send): {best(lambda: msg.send('a', 'b')):4.0f} ns")
print("a ponte custa uma chamada e a formatação; o ganho é de estrutura: m + n partes em vez de m x n")
