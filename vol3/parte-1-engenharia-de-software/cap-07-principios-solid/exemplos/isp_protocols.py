"""I: Segregação de Interface. Ninguém deve ser forçado a depender de métodos que não usa. Em Python: Protocols pequenos e parâmetros estreitos."""
import inspect
import time
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import Protocol, runtime_checkable


# --- 1. a interface gorda: uma ABC com tudo, e a implementação simples paga por métodos que não faz ---
class Machine(ABC):
    @abstractmethod
    def print_doc(self, doc): ...

    @abstractmethod
    def scan(self): ...

    @abstractmethod
    def fax(self, doc, number): ...


class SimplePrinter(Machine):
    def print_doc(self, doc):
        return f"imprimiu {doc}"

    def scan(self):
        raise NotImplementedError("esta impressora não escaneia")      # obrigada a implementar o que não tem (e viola Liskov)

    def fax(self, doc, number):
        raise NotImplementedError("esta impressora não envia fax")


# --- 2. interfaces pequenas, por PAPEL (Protocol: tipagem estrutural, sem herança) ---
class Printer(Protocol):
    def print_doc(self, doc: str) -> str: ...


class Scanner(Protocol):
    def scan(self) -> str: ...


class SimplePrinter2:                                                   # não herda de nada: só tem o que faz
    def print_doc(self, doc):
        return f"imprimiu {doc}"


class OfficeCenter:
    def print_doc(self, doc):
        return f"imprimiu {doc}"

    def scan(self):
        return "imagem"


def print_report(printer: Printer, text: str) -> str:                   # depende só do papel de que precisa
    return printer.print_doc(text)


def digitize(scanner: Scanner) -> str:
    return scanner.scan()


print("papéis separados:", print_report(SimplePrinter2(), "relatório"), "|", print_report(OfficeCenter(), "relatório"), "|", digitize(OfficeCenter()))
try:
    SimplePrinter().scan()
except NotImplementedError as error:
    print("interface gorda: SimplePrinter().scan() ->", error)


# --- 3. o custo para QUEM TESTA: o dublê de uma interface gorda tem que implementar tudo ---
class FatRepository(Protocol):
    def get(self, id): ...
    def list(self): ...
    def add(self, item): ...
    def update(self, item): ...
    def delete(self, id): ...
    def count(self): ...
    def search(self, text): ...
    def export_csv(self, path): ...


class ThinReader(Protocol):
    def get(self, id): ...


def methods_to_fake(protocol: type) -> int:
    return sum(1 for name, member in inspect.getmembers(protocol) if not name.startswith("_") and callable(member))


def show_user(repo: ThinReader, user_id):                              # só LÊ um usuário: só precisa de get
    return f"usuário {repo.get(user_id)['name']}"


class FakeReader:
    def get(self, id):
        return {"id": id, "name": "Ana"}


print(f"\nfunção que só lê um item: o dublê precisa de {methods_to_fake(ThinReader)} método (ThinReader) em vez de {methods_to_fake(FatRepository)} (FatRepository)")
print("  teste:", show_user(FakeReader(), 7), "(o dublê tem 3 linhas)")


# --- 4. o parâmetro mais estreito que serve: Iterable, Sequence, Mapping em vez de list e dict ---
def total_wide(items: list[float]) -> float:                            # promete mais do que precisa: só aceita list
    return sum(items)


def total_narrow(items: Iterable[float]) -> float:                      # só PRECISA de iteração: aceita lista, tupla, gerador, arquivo...
    return sum(items)


def median(items: Sequence[float]) -> float:                            # precisa de ÍNDICE e len: Sequence (não Iterable)
    ordered = sorted(items)
    n = len(ordered)
    return ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2


gen = (x * 1.5 for x in range(4))
print("\nIterable aceita um gerador:", total_narrow(gen), "| list não:", end=" ")
try:
    len(x for x in range(3))
except TypeError as error:
    print("(len de um gerador ->", str(error)[:35], ")")
print("  median(tupla):", median((3.0, 1.0, 2.0)), "| a anotação diz exatamente o que a função exige do argumento")

# --- 5. Protocol em runtime: não é de graça ---
@runtime_checkable
class Closable(Protocol):
    def close(self): ...


class Res:
    def close(self):
        pass


class Base:
    def close(self):
        pass


class Derived(Base):
    pass


N = 200_000


def best(fn):
    start = time.perf_counter()
    for _ in range(N):
        fn()
    return (time.perf_counter() - start) / N * 1e9


r, d = Res(), Derived()
print(f"\nisinstance(r, ClasseNormal) {best(lambda: isinstance(d, Base)):7.0f} ns | isinstance(r, Protocol runtime_checkable) {best(lambda: isinstance(r, Closable)):7.0f} ns | hasattr(r, 'close') {best(lambda: hasattr(r, 'close')):6.0f} ns")
print("o Protocol é de TIPAGEM (verificada pelo mypy); isinstance contra ele existe (com @runtime_checkable), mas custa ~8 vezes mais que contra uma classe: não o use em laços quentes")

# --- 6. a biblioteca padrão é uma aula de ISP ---
print("\nprotocolos de UM método na biblioteca padrão: Sized (__len__), Iterable (__iter__), Hashable (__hash__), SupportsInt (__int__), ContextManager...")
