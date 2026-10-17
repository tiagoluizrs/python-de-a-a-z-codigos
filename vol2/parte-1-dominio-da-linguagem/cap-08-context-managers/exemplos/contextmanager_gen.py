"""@contextmanager: um gerador com um único yield."""
from contextlib import contextmanager


@contextmanager
def tag(name):
    print(f"<{name}>")                    # entrada
    try:
        yield name                         # valor do `as`
    finally:
        print(f"</{name}>")                # saída: roda mesmo com exceção


with tag("p") as label:
    print("  texto dentro de", label)

try:
    with tag("div"):
        raise ValueError("falha")
except ValueError:
    print("exceção propagada, tag fechada")


# Tratar a exceção dentro do gerador a suprime (como `return True`)
@contextmanager
def ignore_value_errors():
    try:
        yield
    except ValueError as error:
        print("  suprimido:", error)


with ignore_value_errors():
    int("x")
print("seguiu")


# Sem try/finally, a limpeza NÃO roda se o corpo falhar
@contextmanager
def fragile():
    print("  abre")
    yield
    print("  fecha (só no caminho feliz)")


try:
    with fragile():
        raise KeyError("x")
except KeyError:
    print("  o 'fecha' nunca foi impresso")


# Os erros de projeto
@contextmanager
def no_yield():
    if False:
        yield


@contextmanager
def two_yields():
    yield 1
    yield 2


try:
    with no_yield():
        pass
except RuntimeError as error:
    print("RuntimeError:", error)
try:
    with two_yields():
        pass
except RuntimeError as error:
    print("RuntimeError:", error)

# Um gerenciador de gerador é de uso ÚNICO
manager = tag("once")
with manager:
    pass
try:
    with manager:
        pass
except (RuntimeError, AttributeError) as error:
    print("segunda vez:", type(error).__name__, "|", error)

# Também funciona como decorador (ContextDecorator)
@tag("section")
def render():
    print("  corpo da função")


render()
render()
