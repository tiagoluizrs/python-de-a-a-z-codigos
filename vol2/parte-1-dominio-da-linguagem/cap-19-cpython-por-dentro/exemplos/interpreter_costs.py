"""Quanto custam as operações básicas do interpretador (3.15)."""
import timeit

GLOBAL = 1


class Thing:
    attr = 1

    def method(self):
        return 1


def function():
    return 1


thing = Thing()
data = []
append = data.append


def measure(label, statement, setup="pass", number=2_000_000):
    seconds = min(timeit.repeat(statement, setup=setup, globals=globals(), number=number, repeat=5)) / number
    print(f"  {label:<38}{seconds * 1e9:7.1f} ns")


print("laço vazio e acessos:")
measure("pass", "pass")
measure("variável global (GLOBAL)", "GLOBAL")
measure("variável local (definida no setup)", "local", setup="local = 1")
measure("atributo de instância/classe (thing.attr)", "thing.attr")
measure("builtin len (len)", "len")
print("chamadas:")
measure("função Python vazia", "function()")
measure("método (thing.method())", "thing.method()")
measure("built-in (len(data))", "len(data)")
measure("data.append(1) (busca o método)", "data.append(1); data.pop()")
measure("app(1) com método guardado em local", "app(1); data.pop()", setup="app = data.append")
print("outras:")
measure("try/except sem exceção", "try:\n    pass\nexcept ValueError:\n    pass")
measure("try/except COM exceção", "try:\n    raise ValueError\nexcept ValueError:\n    pass", number=500_000)
measure("f-string", "f'{GLOBAL}'")
measure("isinstance(1, int)", "isinstance(1, int)")
