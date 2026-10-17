"""Observer, forma clássica (GoF): um objeto (o sujeito) avisa vários interessados (os observadores) quando muda, sem conhecê-los."""
import ast
import gc
import inspect
import textwrap
import weakref
from abc import ABC, abstractmethod


# --- 1. o problema: o sujeito conhece e chama cada interessado diretamente ---
class DashboardOld:
    def show(self, price):
        return f"painel: {price}"


class AlertOld:
    def check(self, price):
        return f"alerta! {price}" if price > 100 else None


class TickerOld:
    def __init__(self):
        self.dashboard, self.alert = DashboardOld(), AlertOld()      # acoplado a cada interessado

    def set_price(self, price):
        self.price = price
        return [self.dashboard.show(price), self.alert.check(price)]  # cada interessado novo EDITA esta classe


print("acoplado:", TickerOld().set_price(120))


# --- 2. a forma clássica: Subject (attach/detach/notify) e Observer (update) ---
class Observer(ABC):
    @abstractmethod
    def update(self, subject) -> None: ...


class Subject:
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)


class Ticker(Subject):
    def __init__(self):
        super().__init__()
        self._price = 0

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value
        self.notify()


class Dashboard(Observer):
    def __init__(self):
        self.lines = []

    def update(self, subject):
        self.lines.append(f"painel: {subject.price}")


class Alert(Observer):
    def __init__(self, limit):
        self.limit, self.fired = limit, []

    def update(self, subject):
        if subject.price > self.limit:
            self.fired.append(subject.price)


ticker = Ticker()
dash, alert = Dashboard(), Alert(100)
ticker.attach(dash)
ticker.attach(alert)
for p in (90, 120):
    ticker.price = p
print("\nobservers:", dash.lines, alert.fired, "| o Ticker não conhece nenhuma das duas classes")
ticker.detach(alert)
ticker.price = 130
print("depois de detach, o alerta não é avisado:", alert.fired, "| o painel continua:", dash.lines[-1])


# --- 3. as armadilhas, medidas ---
# (a) um observador que levanta exceção interrompe os seguintes
class Broken(Observer):
    def update(self, subject):
        raise RuntimeError("falhou")


t2 = Ticker()
after = Dashboard()
t2.attach(Broken())
t2.attach(after)
try:
    t2.price = 1
except RuntimeError:
    print("\n(a) o primeiro observador falhou e o segundo NÃO foi avisado:", after.lines)

# (b) remover um observador DURANTE a notificação pula o seguinte
class Quitter(Observer):
    def __init__(self, subject):
        self.subject = subject

    def update(self, subject):
        self.subject.detach(self)


t3 = Ticker()
first = Quitter(t3)
second, third = Dashboard(), Dashboard()
for o in (first, second, third):
    t3.attach(o)
t3.price = 5
print("(b) detach durante o notify: o 2º observador foi pulado:", second.lines, "| o 3º recebeu:", third.lines)

# (c) o sujeito mantém o observador VIVO (vazamento)
class Heavy(Observer):
    def update(self, subject):
        pass


t4 = Ticker()
heavy = Heavy()
ref = weakref.ref(heavy)
t4.attach(heavy)
del heavy
gc.collect()
print("(c) depois de apagar a última referência, o observador ainda existe?", ref() is not None, "(a lista do sujeito o segura: esquecer o detach vaza memória)")


# --- 4. a cerimônia ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nObserver + Subject:", measure([Observer, Subject]), "(sem contar o sujeito e os observadores concretos)")
