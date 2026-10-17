"""O que o `with` faz: __enter__, o corpo, __exit__ (sempre)."""
import dis


class Tracer:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print(f"  enter {self.name}")
        return f"valor-de-{self.name}"          # vai para o `as`

    def __exit__(self, exc_type, exc, tb):
        print(f"  exit {self.name}: exc_type={getattr(exc_type, '__name__', None)}")
        return False                              # não suprime


print("1) caminho feliz")
with Tracer("A") as resource:
    print("  corpo, resource =", resource)

print("2) com exceção")
try:
    with Tracer("A"):
        raise ValueError("falha no corpo")
except ValueError as error:
    print("  a exceção continuou:", error)

print("3) dois gerenciadores: a saída é na ordem inversa")
with Tracer("A"), Tracer("B"):
    print("  corpo")

print("4) forma com parênteses (3.10+), útil para quebrar linhas")
with (
    Tracer("A") as first,
    Tracer("B") as second,
):
    print("  ", first, second)


# O equivalente manual (simplificado, PEP 343)
print("5) o mesmo, escrito à mão")
manager = Tracer("M")
value = manager.__enter__()
try:
    print("  corpo, value =", value)
except BaseException as error:
    if not manager.__exit__(type(error), error, error.__traceback__):
        raise
else:
    manager.__exit__(None, None, None)


def uses_with():
    with Tracer("X") as x:
        return x


print("6) bytecode do with")
dis.dis(uses_with)
