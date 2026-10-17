"""As anotações são dados: o Python as guarda e NÃO as verifica."""
import annotationlib
import inspect
import timeit
import typing
from annotationlib import Format


def add(a: int, b: int = 0) -> int:
    return a + b


print("anotações guardadas:", add.__annotations__)
print("add('a', 'b') =", add("a", "b"))              # roda: concatena textos, sem erro

# get_type_hints resolve nomes; inspect.get_annotations devolve o que está lá
print(typing.get_type_hints(add), inspect.get_annotations(add))


# Desde o 3.14 (PEP 649/749): a avaliação é ADIADA; referências adiantadas funcionam sem aspas
def build(name: str) -> Later:                       # Later ainda não existe aqui
    return Later(name)


try:
    build.__annotations__                            # avaliar agora: o nome ainda não existe
except NameError as error:
    print("antes de definir Later -> NameError:", error)


class Later:
    def __init__(self, name: str) -> None:
        self.name = name


print("depois de definir Later ->", build.__annotations__["return"], "|", build("x").name)


def early(x: Missing) -> None: ...                  # Missing nunca será definido


print("avaliar a anotação falha:", end=" ")
try:
    early.__annotations__
except NameError as error:
    print("NameError:", error)
print("FORWARDREF (sem falhar):", annotationlib.get_annotations(early, format=Format.FORWARDREF))
print("STRING:", annotationlib.get_annotations(early, format=Format.STRING))

# Custo: anotar uma função quase não custa em tempo de definição (3.14+: a anotação é compilada, não avaliada)
def make_plain():
    def f(a, b): return a

    return f


def make_annotated():
    def f(a: int, b: list[dict[str, tuple[int, ...]]]) -> dict[str, int]: return {}

    return f


n = 200_000
plain = min(timeit.repeat(make_plain, number=n, repeat=3)) / n
annotated = min(timeit.repeat(make_annotated, number=n, repeat=3)) / n
print(f"definir uma função: sem anotações {plain * 1e9:.0f} ns | com anotações complexas {annotated * 1e9:.0f} ns")
