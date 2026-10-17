"""Tipagem moderna (3.12 a 3.15), limpa sob `mypy --strict`."""
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from functools import wraps
from typing import (Final, Literal, NewType, Protocol, Self, TypedDict, NotRequired, TypeIs, assert_never, overload,
                    override, runtime_checkable)

# --- Aliases e NewType ---------------------------------------------------------
type Number = int | float                              # 'type' statement (3.12)
UserId = NewType("UserId", int)                        # tipo distinto, mesmo valor em execução
MAX_RETRIES: Final = 3                                 # constante: reatribuir é erro de tipo
Mode = Literal["r", "w", "a"]                          # só estes valores


def open_mode(mode: Mode) -> str:
    return {"r": "leitura", "w": "escrita", "a": "acréscimo"}[mode]


def load(user: UserId) -> str:
    return f"usuário {user}"


# --- Genéricos com a sintaxe do 3.12 (sem TypeVar manual) ------------------------------
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> Self:
        self._items.append(item)
        return self

    def pop(self) -> T:
        return self._items.pop()


def first[T](items: Sequence[T]) -> T | None:
    return items[0] if items else None


class Comparable(Protocol):
    def __lt__(self, other: Self, /) -> bool: ...


def biggest[C: Comparable](items: Iterable[C]) -> C:       # parâmetro de tipo com LIMITE
    return max(items)


# --- Protocol: tipagem estrutural -------------------------------------------------------
@runtime_checkable
class SupportsArea(Protocol):
    def area(self) -> float: ...


@dataclass
class Square:
    side: float

    def area(self) -> float:
        return self.side**2


def total_area(shapes: Iterable[SupportsArea]) -> float:
    return sum(shape.area() for shape in shapes)


# --- TypedDict -----------------------------------------------------------------------------
class Movie(TypedDict):
    title: str
    year: int
    rating: NotRequired[float]


def describe(movie: Movie) -> str:
    return f"{movie['title']} ({movie['year']})" + (f" nota {movie['rating']}" if "rating" in movie else "")


# --- Herança com @override e Self -----------------------------------------------------------
class Animal:
    def speak(self) -> str:
        return "..."


class Dog(Animal):
    @override
    def speak(self) -> str:
        return "au"


# --- Estreitamento: TypeIs e exaustividade ----------------------------------------------------
def is_str_list(values: Sequence[object]) -> TypeIs[Sequence[str]]:
    return all(isinstance(v, str) for v in values)


@dataclass
class Circle:
    radius: float


@dataclass
class Rect:
    width: float
    height: float


type Shape = Circle | Rect


def area(shape: Shape) -> float:
    match shape:
        case Circle(radius=r):
            return 3.14159 * r * r
        case Rect(width=w, height=h):
            return w * h
        case _:
            assert_never(shape)                        # se surgir uma variante nova, o verificador acusa


# --- overload: o tipo de retorno depende do argumento -------------------------------------------
@overload
def parse(value: str) -> int: ...
@overload
def parse(value: bytes) -> str: ...
def parse(value: str | bytes) -> int | str:
    return int(value) if isinstance(value, str) else value.decode()


# --- Decorador tipado: ParamSpec preserva a assinatura ---------------------------------------------
def logged[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


@logged
def power(base: float, exponent: int = 2) -> float:
    return base**exponent


if __name__ == "__main__":
    print(open_mode("w"), load(UserId(7)), Stack[int]().push(1).push(2).pop(), first([]), biggest([3, 9, 4]))
    print(total_area([Square(2), Square(3)]), describe({"title": "Dune", "year": 2021}), Dog().speak())
    print(area(Circle(1)), area(Rect(2, 3)), parse("42"), parse(b"abc"), power(2, 3), is_str_list(["a"]))
