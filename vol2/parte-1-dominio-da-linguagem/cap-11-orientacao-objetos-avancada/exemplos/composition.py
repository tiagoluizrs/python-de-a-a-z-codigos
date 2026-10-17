"""Composição: "tem um" em vez de "é um" (a herança vem no Capítulo 12)."""


class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower

    def start(self):
        return f"motor de {self.horsepower} cv ligado"


class Car:
    def __init__(self, engine):
        self.engine = engine             # injeção de dependência

    def start(self):
        return f"Carro: {self.engine.start()}"


class ElectricEngine:
    def start(self):
        return "motor elétrico silencioso"


print(Car(Engine(120)).start())
print(Car(ElectricEngine()).start())     # troca a peça sem tocar em Car


# Delegação: expor só o que faz sentido de uma lista interna
class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def peek(self):
        return self._items[-1]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack({self._items!r})"


stack = Stack()
stack.push(1)
stack.push(2)
print(stack, stack.pop(), len(stack), hasattr(stack, "insert"))
print("uma subclasse de list herdaria insert, sort, extend...:",
      hasattr(type("S", (list,), {})(), "insert"))
