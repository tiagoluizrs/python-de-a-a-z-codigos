"""Núcleo funcional, casca imperativa: a decisão é uma função pura; o efeito (gravar, enviar) fica na borda."""
import json
import random
import tempfile
import time
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


# ---------- o núcleo: dados imutáveis e funções puras ----------
@dataclass(frozen=True)
class Account:
    id: str
    balance: Decimal = Decimal("0")
    frozen: bool = False


@dataclass(frozen=True)
class Deposit:
    amount: Decimal


@dataclass(frozen=True)
class Withdraw:
    amount: Decimal


@dataclass(frozen=True)
class Freeze:
    pass


# eventos: fatos que aconteceram
@dataclass(frozen=True)
class Deposited:
    amount: Decimal


@dataclass(frozen=True)
class Withdrawn:
    amount: Decimal


@dataclass(frozen=True)
class Rejected:
    reason: str


@dataclass(frozen=True)
class Frozen:
    pass


def decide(state: Account, command) -> list:
    """(estado, comando) -> eventos. PURA: sem relógio, sem banco, sem sorteio, sem print. Decide o que acontece."""
    match command:
        case Deposit(amount) if amount <= 0:
            return [Rejected("valor deve ser positivo")]
        case Deposit(amount):
            return [Rejected("conta congelada")] if state.frozen else [Deposited(amount)]
        case Withdraw(amount) if amount <= 0:
            return [Rejected("valor deve ser positivo")]
        case Withdraw(amount) if state.frozen:
            return [Rejected("conta congelada")]
        case Withdraw(amount) if amount > state.balance:
            return [Rejected("saldo insuficiente")]
        case Withdraw(amount):
            return [Withdrawn(amount)]
        case Freeze():
            return [Frozen()]
    raise TypeError(f"comando desconhecido: {command!r}")


def evolve(state: Account, event) -> Account:
    """(estado, evento) -> novo estado. PURA. Aplicar eventos NUNCA falha e nunca decide: só registra o que já aconteceu."""
    match event:
        case Deposited(amount):
            return Account(state.id, state.balance + amount, state.frozen)
        case Withdrawn(amount):
            return Account(state.id, state.balance - amount, state.frozen)
        case Frozen():
            return Account(state.id, state.balance, True)
        case Rejected():
            return state
    raise TypeError(f"evento desconhecido: {event!r}")


def replay(events, initial: Account) -> Account:
    state = initial
    for event in events:
        state = evolve(state, event)
    return state


# ---------- a casca: o único lugar com efeito colateral ----------
class Shell:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.state = Account("acc-1")

    def handle(self, command) -> list:
        events = decide(self.state, command)                        # 1) pensa (puro)
        with self.log_path.open("a", encoding="utf-8") as log:       # 2) grava (efeito)
            for event in events:
                log.write(json.dumps({"type": type(event).__name__, **{k: str(v) for k, v in vars(event).items()}}) + "\n")
        for event in events:                                         # 3) atualiza a memória (puro)
            self.state = evolve(self.state, event)
        return events


# 1. testar a decisão não precisa de nada: valores entram, valores saem
state = Account("a", Decimal("100"))
print("decide:")
for command in (Withdraw(Decimal("30")), Withdraw(Decimal("500")), Deposit(Decimal("-1")), Freeze()):
    print(f"  {command!r:<48} -> {decide(state, command)}")
print("conta congelada rejeita depósito:", decide(Account("a", frozen=True), Deposit(Decimal("5"))))

# 2. determinismo: a mesma entrada sempre dá a mesma saída (o que torna o teste e o replay possíveis)
assert all(decide(state, Withdraw(Decimal("30"))) == [Withdrawn(Decimal("30"))] for _ in range(1000))
print("\n1.000 chamadas iguais deram exatamente o mesmo resultado")

# 3. o estado É o histórico: reconstruir pelos eventos
rng = random.Random(42)
commands = [rng.choice([Deposit(Decimal(rng.randint(1, 200))), Withdraw(Decimal(rng.randint(1, 300)))]) for _ in range(100_000)]
current, events = Account("acc-1"), []
start = time.perf_counter()
for command in commands:
    new_events = decide(current, command)
    events += new_events
    for event in new_events:
        current = evolve(current, event)
t_run = time.perf_counter() - start
start = time.perf_counter()
rebuilt = replay(events, Account("acc-1"))
t_replay = time.perf_counter() - start
accepted = sum(not isinstance(e, Rejected) for e in events)
print(f"{len(commands):,} comandos: {accepted:,} aceitos e {len(events) - accepted:,} rejeitados | decidir+aplicar {t_run * 1e3:.0f} ms ({t_run / len(commands) * 1e6:.1f} µs por comando)")
print(f"replay do histórico inteiro ({len(events):,} eventos): {t_replay * 1e3:.0f} ms | mesmo estado? {rebuilt == current} | saldo final {rebuilt.balance}")

# 4. uma invariante testada em MASSA, sem banco: o saldo nunca fica negativo
balance, minimum = Decimal("0"), Decimal("0")
for event in events:
    balance = balance + event.amount if isinstance(event, Deposited) else balance - event.amount if isinstance(event, Withdrawn) else balance
    minimum = min(minimum, balance)
print(f"invariante em {len(events):,} eventos: menor saldo visto = {minimum} (nunca negativo: {minimum >= 0})")

# 5. a casca: gravar em disco custa muito mais que pensar
shell = Shell(Path(tempfile.mkdtemp(prefix="core-")) / "events.log")
start = time.perf_counter()
for command in commands[:2000]:
    shell.handle(command)
t_shell = (time.perf_counter() - start) / 2000 * 1e6
print(f"\ncasca (decide + grava no log + atualiza): {t_shell:.0f} µs por comando, contra {t_run / len(commands) * 1e6:.1f} µs só de pensar: o efeito é o que custa")
print("linhas no log:", sum(1 for _ in shell.log_path.open(encoding="utf-8")), "| estado em memória:", shell.state.balance)
