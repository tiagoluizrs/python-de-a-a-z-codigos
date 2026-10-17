"""Proxy, forma clássica (GoF): um substituto com a MESMA interface do objeto real, que CONTROLA o acesso a ele."""
import time
from abc import ABC, abstractmethod


# --- 1. a interface comum e o objeto real, CARO de criar ---
class Report(ABC):
    @abstractmethod
    def total(self) -> int: ...

    @abstractmethod
    def delete(self) -> str: ...


class RealReport(Report):
    created = 0

    def __init__(self, name):
        RealReport.created += 1
        self.name = name
        self.rows = [i * 2 for i in range(300_000)]              # "carregar do disco": custa tempo e memória

    def total(self):
        return sum(self.rows)

    def delete(self):
        return f"relatório {self.name} apagado"


start = time.perf_counter()
RealReport("teste")
t_real = (time.perf_counter() - start) * 1e3
print(f"criar um RealReport: {t_real:.1f} ms | objetos reais criados até aqui: {RealReport.created}")


# --- 2. o proxy VIRTUAL: parece o objeto, mas só o cria quando alguém usa ---
class LazyReport(Report):
    def __init__(self, name):
        self._name, self._real = name, None

    def _load(self):
        if self._real is None:
            self._real = RealReport(self._name)
        return self._real

    def total(self):
        return self._load().total()

    def delete(self):
        return self._load().delete()


RealReport.created = 0
start = time.perf_counter()
reports = [LazyReport(f"r{i}") for i in range(1000)]             # mil relatórios "abertos"
t_lazy = (time.perf_counter() - start) * 1e3
print(f"\ncriar 1000 proxies virtuais: {t_lazy:.2f} ms | objetos reais criados: {RealReport.created} (nenhum: ninguém usou ainda)")
reports[3].total()
reports[3].total()
print("usar um deles duas vezes: objetos reais criados =", RealReport.created, "(carregou na primeira chamada e reaproveitou)")


# --- 3. o proxy de PROTEÇÃO: controla QUEM pode chamar ---
class ProtectedReport(Report):
    def __init__(self, real: Report, user_roles: set):
        self._real, self._roles = real, user_roles

    def total(self):
        return self._real.total()

    def delete(self):
        if "admin" not in self._roles:
            raise PermissionError("só administradores apagam relatórios")
        return self._real.delete()


small = type("Small", (Report,), {"total": lambda self: 6, "delete": lambda self: "apagado"})()
print("\nproxy de proteção:", ProtectedReport(small, {"viewer"}).total(), "| delete como viewer ->", end=" ")
try:
    ProtectedReport(small, {"viewer"}).delete()
except PermissionError as error:
    print("PermissionError:", error)
print("delete como admin ->", ProtectedReport(small, {"admin"}).delete())


# --- 4. o proxy de CACHE e o de REGISTRO: o mesmo molde, comportamentos diferentes ---
class CachingReport(Report):
    def __init__(self, real: Report):
        self._real, self._total = real, None
        self.hits = 0

    def total(self):
        if self._total is None:
            self._total = self._real.total()
        else:
            self.hits += 1
        return self._total

    def delete(self):
        self._total = None                                       # a escrita invalida o cache
        return self._real.delete()


class LoggingReport(Report):
    def __init__(self, real: Report, log):
        self._real, self._log = real, log

    def total(self):
        self._log.append("total()")
        return self._real.total()

    def delete(self):
        self._log.append("delete()")
        return self._real.delete()


log = []
stack = LoggingReport(CachingReport(small), log)
stack.total()
stack.total()
print("\nproxies empilhados (registro -> cache -> real):", log, "| acertos de cache:", stack._real.hits)

# --- 5. o custo: um proxy por interface repete CADA método (e só delega) ---
print("\ncada método da interface precisa ser repetido em CADA proxy: 2 métodos x 3 proxies = 6 delegações; 20 métodos x 3 proxies = 60")
print("em Python, o __getattr__ generaliza isso: veja o exemplo seguinte")
