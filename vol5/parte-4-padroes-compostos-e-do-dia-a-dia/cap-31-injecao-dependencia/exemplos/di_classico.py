"""Injeção de Dependência, forma clássica: o código RECEBE o que precisa (em vez de criar ou procurar), e UM lugar (a raiz de composição) monta tudo."""
import ast
import inspect
import textwrap
import time
from datetime import datetime

FIXED = datetime(2026, 1, 1, 12, 0)


# --- 1. o problema: as dependências são criadas POR DENTRO ---
class SmtpMailer:
    def send(self, to, subject):
        raise ConnectionError("sem rede: smtp.empresa.com:25")                # (de mentira) um servidor de e-mail de verdade


class SqlOrders:
    def __init__(self):
        self.rows = []

    def save(self, order):
        self.rows.append(order)


class NaiveOrderService:
    def place(self, customer, total_cents):
        repo, mailer = SqlOrders(), SmtpMailer()                              # cria o banco e o servidor de e-mail DENTRO do método
        order = {"customer": customer, "total": total_cents, "at": datetime.now()}
        repo.save(order)
        mailer.send(customer, "pedido recebido")
        return order


try:
    NaiveOrderService().place("ana@x.com", 10_00)
except ConnectionError as error:
    print("testar o serviço ingênuo:", error, "| para testar a regra do pedido é preciso ter rede (ou remendar o módulo por dentro), e o relógio (datetime.now) nunca é o mesmo")


# --- 2. a injeção pelo construtor: o serviço DECLARA o que precisa ---
class OrderService:
    def __init__(self, repo, mailer, clock):
        self.repo, self.mailer, self.clock = repo, mailer, clock

    def place(self, customer, total_cents):
        order = {"customer": customer, "total": total_cents, "at": self.clock()}
        self.repo.save(order)
        self.mailer.send(customer, "pedido recebido")
        return order


class InMemoryOrders:
    def __init__(self):
        self.saved = []

    def save(self, order):
        self.saved.append(order)


class RecordingMailer:
    def __init__(self):
        self.sent = []

    def send(self, to, subject):
        self.sent.append((to, subject))


class NullMailer:
    def send(self, to, subject):
        pass


repo, mailer = InMemoryOrders(), RecordingMailer()
service = OrderService(repo, mailer, lambda: FIXED)                           # o teste escolhe: um banco em memória, um e-mail que anota, um relógio parado
order = service.place("ana@x.com", 10_00)
print("\ncom injeção:", order, "|", mailer.sent, "(testado sem rede, sem banco e com a data fixa; nenhum remendo)")


# --- 3. a raiz de composição: UM lugar escolhe os concretos ---
def build_service(env):
    if env == "test":
        return OrderService(InMemoryOrders(), RecordingMailer(), lambda: FIXED)
    if env == "dry-run":
        return OrderService(SqlOrders(), NullMailer(), datetime.now)          # o Null Object do Capítulo 27: grava, mas não envia
    if env == "prod":
        return OrderService(SqlOrders(), SmtpMailer(), datetime.now)
    raise ValueError(f"ambiente desconhecido: {env!r}")


for env in ("test", "dry-run", "prod"):
    svc = build_service(env)
    print(f"  {env:8} -> repo={type(svc.repo).__name__}, mailer={type(svc.mailer).__name__}")
print("a escolha do concreto acontece em UM lugar (o 'main'); o resto do código só recebe, e nunca pergunta 'em que ambiente estou?'")


# --- 4. o anti-padrão: o Service Locator ---
class Locator:
    _services = {}

    @classmethod
    def register(cls, name, service):
        cls._services[name] = service

    @classmethod
    def get(cls, name):
        return cls._services[name]


class LocatorOrderService:
    def place(self, customer, total_cents):
        repo = Locator.get("repo")                                            # a dependência está ESCONDIDA dentro do método
        repo.save({"customer": customer, "total": total_cents})


forgotten = LocatorOrderService()                                             # constrói sem problema...
try:
    forgotten.place("ana@x.com", 10_00)
except KeyError as error:
    print("\nService Locator: construiu e só falhou ao USAR, com KeyError", error, end=" | ")
try:
    OrderService()
except TypeError as error:
    print("injeção: falha ao CONSTRUIR:", error)


# --- 5. a armadilha: o valor padrão que cria o concreto ---
class LazyDefaultService:
    def __init__(self, mailer=None):
        self.mailer = mailer or SmtpMailer()                                  # esquecer o parâmetro no teste = um e-mail de verdade


try:
    LazyDefaultService().mailer.send("ana@x.com", "oi")
except ConnectionError:
    print("\nparâmetro opcional que cria o concreto: o teste que esqueceu de passar o 'mailer' tentou falar com o SMTP de verdade | um parâmetro OBRIGATÓRIO (ou um padrão inofensivo, como o NullMailer) não deixa isso acontecer")


# --- 6. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\ndependências criadas por dentro:", measure([NaiveOrderService]), "| com injeção (serviço + raiz de composição):", measure([OrderService, build_service]))


def best(fn, n=200_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


r, m, c = InMemoryOrders(), NullMailer(), lambda: FIXED
ready = OrderService(r, m, c)
print(f"construir o serviço injetado: {best(lambda: OrderService(r, m, c)):4.0f} ns | place() com injeção: {best(lambda: ready.place('a', 100)):4.0f} ns | (guardar o serviço pronto e reusá-lo, em vez de remontar a cada pedido, é o normal)")
