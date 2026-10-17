"""Null Object, forma clássica (GoF): um objeto que "não faz nada" no lugar do None, para o chamador nunca precisar perguntar."""
import ast
import inspect
import textwrap
import time
from abc import ABC, abstractmethod

# --- 1. o problema: o None que obriga todo chamador a lembrar ---
USERS = {1: {"name": "Ana", "email": "ana@x.com", "discount": 10}}


def find_user(user_id):
    return USERS.get(user_id)                               # None se não existe


def greet_naive(user_id):
    user = find_user(user_id)
    return f"Olá, {user['name']}!"


try:
    greet_naive(2)
except TypeError as error:
    print("o chamador esqueceu o None:", error)


def greet(user_id):
    user = find_user(user_id)
    if user is None:
        return "Olá, visitante!"
    return f"Olá, {user['name']}!"


def email(user_id):
    user = find_user(user_id)
    if user is None:
        return None
    return user["email"]


def price(user_id, cents):
    user = find_user(user_id)
    if user is None:
        return cents
    return cents * (100 - user["discount"]) // 100


print("com guardas:", greet(1), "|", greet(2), "|", email(2), "|", price(2, 1000), "| 3 funções, 3 'if user is None': cada chamador novo precisa lembrar (e o esquecimento só aparece em produção)")


# --- 2. o Null Object: a ausência também é um Customer ---
class Customer(ABC):
    is_null = False

    @abstractmethod
    def greeting(self): ...

    @abstractmethod
    def price(self, cents): ...

    @abstractmethod
    def add_points(self, points): ...


class RealCustomer(Customer):
    def __init__(self, name, discount_pct):
        self.name, self.discount_pct, self.points = name, discount_pct, 0

    def greeting(self):
        return f"Olá, {self.name}!"

    def price(self, cents):
        return cents * (100 - self.discount_pct) // 100

    def add_points(self, points):
        self.points += points


class NullCustomer(Customer):
    """Sem estado e sem efeito: faz o comportamento SEGURO para a ausência."""

    is_null = True
    name = "visitante"
    points = 0

    def greeting(self):
        return "Olá, visitante! Cadastre-se para ganhar descontos."

    def price(self, cents):
        return cents

    def add_points(self, points):
        pass


NULL_CUSTOMER = NullCustomer()
CUSTOMERS = {1: RealCustomer("Ana", 10)}


def find_customer(customer_id):
    return CUSTOMERS.get(customer_id, NULL_CUSTOMER)        # nunca devolve None


def checkout(customer_id, cents):
    customer = find_customer(customer_id)                   # nenhum 'if None' daqui para baixo
    total = customer.price(cents)
    customer.add_points(total // 100)
    return f"{customer.greeting()} Total: R$ {total / 100:.2f}"


print("\ncliente real:     ", checkout(1, 1000))
print("cliente ausente:  ", checkout(99, 1000))
print("pontos da Ana:", CUSTOMERS[1].points, "| pontos do visitante:", NULL_CUSTOMER.points, "(add_points do Null ignorou)")


# --- 3. o colaborador opcional: o logger que não loga ---
class NullLogger:
    def info(self, *args, **kwargs):
        pass

    error = warning = info


class Service:
    def __init__(self, logger=None):
        self.logger = NullLogger() if logger is None else logger          # 'is None', e não 'or' (veja a pegadinha abaixo)

    def run(self):
        self.logger.info("começou")                         # sem 'if self.logger:' em lugar nenhum
        return 42


class BufferLogger:
    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(message)

    def __len__(self):
        return len(self.messages)                           # um logger "vazio" é FALSO


quiet, spy = Service(), Service(BufferLogger())
quiet.run()
spy.run()
print("\nService sem logger:", quiet.run(), "| com logger:", spy.logger.messages)
empty = BufferLogger()
print("'logger or NullLogger()' descartou um logger vazio (porque ele é falso):", (empty or NullLogger()) is not empty, "| use 'is None'")


# --- 4. a armadilha: o Null Object que ESCONDE um erro ---
class Account:
    def __init__(self):
        self.balance = 0

    def deposit(self, cents):
        self.balance += cents


class NullAccount:
    def deposit(self, cents):
        pass                                                # o dinheiro some e ninguém é avisado


ACCOUNTS = {"A1": Account()}


def find_account(account_id):
    return ACCOUNTS.get(account_id, NullAccount())          # um id digitado errado vira... nada


find_account("A-1 (digitado errado)").deposit(10_000)
print("\ndepositar R$ 100 em uma conta que não existe: nenhum erro; saldo da A1:", ACCOUNTS["A1"].balance, "| o dinheiro sumiu: onde 'não fazer nada' é errado, levante um erro (KeyError), não use Null Object")


# --- 5. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\ncom guardas (3 funções):", measure([greet, email, price]), "| Null Object (Customer + Real + Null + checkout):", measure([Customer, RealCustomer, NullCustomer, checkout]))


def best(fn, n=1_000_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


logger_none, null_logger = None, NullLogger()


def guarded():
    if logger_none is not None:
        logger_none.info("x")


def null_call():
    null_logger.info("x")


print(f"registrar com a guarda 'if logger is not None' (logger ausente): {best(guarded):4.0f} ns | chamar o NullLogger: {best(null_call):4.0f} ns")
