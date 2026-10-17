"""Mediator em Python: um objeto simples com métodos e callbacks; regras como dados; e os mediadores da biblioteca padrão (Queue, o laço de eventos)."""
import asyncio
import queue
import threading
import time
import weakref


# --- 1. a sala de bate-papo: o mediador é um objeto comum, e os "colegas" são só funções de entrega ---
class ChatRoom:
    def __init__(self):
        self._members = {}            # nome -> função de entrega
        self._muted = set()           # (quem silenciou, quem foi silenciado)
        self.history = []

    def join(self, name, deliver):
        self._members[name] = deliver

    def mute(self, by, who):
        self._muted.add((by, who))

    def send(self, sender, text, to=None):
        self.history.append((sender, to, text))
        targets = [to] if to else [n for n in self._members if n != sender]
        delivered = 0
        for name in targets:
            if (name, sender) in self._muted:                     # a regra de coordenação mora AQUI, não em cada usuário
                continue
            self._members[name](sender, text, bool(to))
            delivered += 1
        return delivered


inbox = {"ana": [], "bia": [], "caio": []}
room = ChatRoom()
for name, box in inbox.items():
    room.join(name, lambda sender, text, private, box=box: box.append((sender, text, private)))
room.mute("caio", "ana")                                          # caio não quer ouvir a ana
print("entregues a todos:", room.send("ana", "olá, pessoal"), "| bia recebeu:", inbox["bia"], "| caio (silenciou a ana):", inbox["caio"])
print("mensagem privada:", room.send("bia", "só para a ana", to="ana"), "| ana recebeu:", inbox["ana"])
print("os usuários só conhecem a sala (uma função de entrega cada); n usuários = n ligações, e não n x (n-1) conversas diretas")
print("combinações possíveis de comunicação direta com 10 usuários:", 10 * 9, "| com mediador:", 10)

# --- 2. as regras como DADOS: o mediador reativo (campos derivados) ---
class Form:
    """Valores derivados recalculados quando uma dependência muda: o mediador é a tabela de regras, não um if/elif."""

    def __init__(self, **initial):
        self.values = dict(initial)
        self.rules = []                                            # (nome_derivado, função, dependências)
        self.recomputed = []

    def derive(self, name, fn, *deps):
        self.rules.append((name, fn, deps))
        self._recompute(name)

    def _recompute(self, name):
        for rule_name, fn, deps in self.rules:
            if rule_name == name:
                self.values[name] = fn(*(self.values[d] for d in deps))
                self.recomputed.append(name)

    def set(self, key, value):
        if self.values.get(key) == value:                          # a guarda: só reage se MUDOU (evita o laço infinito)
            return
        self.values[key] = value
        self._propagate(key)

    def _propagate(self, key):
        for name, _, deps in self.rules:
            if key in deps:
                before = self.values.get(name)
                self._recompute(name)
                if self.values[name] != before:                    # propaga em CASCATA: um derivado pode ser dependência de outro
                    self._propagate(name)


form = Form(agree=False, email="")
form.derive("email_ok", lambda email: "@" in email, "email")
form.derive("can_submit", lambda agree, ok: agree and ok, "agree", "email_ok")
form.recomputed.clear()
form.set("agree", True)
form.set("email", "ana@x.com")
form.set("email", "ana@x.com")                                     # igual: nada é recalculado
print("\nregras como dados:", form.values, "| recalculados:", form.recomputed, "(só o que dependia do que mudou; o set repetido não fez nada)")

# --- 3. o mediador da biblioteca padrão: queue.Queue entre threads (produtor e consumidor não se conhecem) ---
mailbox: queue.Queue = queue.Queue()
received = []


def consumer():
    while (item := mailbox.get()) is not None:
        received.append(item)


worker = threading.Thread(target=consumer)
worker.start()
for i in range(3):
    mailbox.put(f"mensagem {i}")                                   # o produtor não sabe QUEM consome, nem em qual thread
mailbox.put(None)
worker.join()
print("\nqueue.Queue como mediador entre threads:", received)


async def producer(q):
    for i in range(3):
        await q.put(i * i)
    await q.put(None)


async def consume(q):
    out = []
    while (item := await q.get()) is not None:
        out.append(item)
    return out


async def main():
    q = asyncio.Queue()
    _, result = await asyncio.gather(producer(q), consume(q))
    return result


print("asyncio.Queue entre tarefas:", asyncio.run(main()), "| e o próprio laço de eventos do asyncio é o mediador que coordena todas as tarefas")

# --- 4. o vazamento do mediador: ele guarda os colegas e os colegas guardam o mediador (um ciclo) ---
class Colleague:
    def __init__(self, mediator):
        self.mediator = mediator


class Hub:
    def __init__(self):
        self.members = []


hub = Hub()
strong = Colleague(hub)
hub.members.append(strong)
ref = weakref.ref(strong)
del strong
print("\ncolega guardado pelo mediador ainda vivo após apagar a referência:", ref() is not None, "(use WeakSet/weakref no mediador se os colegas têm vida curta)")


# --- 5. o custo ---
def best(fn, n=100_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


big = ChatRoom()
for i in range(10):
    big.join(f"u{i}", lambda *a: None)
print(f"\nenviar uma mensagem a 9 destinatários: {best(lambda: big.send('u0', 'oi')):5.0f} ns (~{best(lambda: big.send('u0', 'oi')) / 9:.0f} ns por entrega)")
