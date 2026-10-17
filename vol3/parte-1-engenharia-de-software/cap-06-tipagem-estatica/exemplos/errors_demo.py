"""Erros de tipo PROPOSITAIS: o programa roda, os verificadores reclamam."""
from dataclasses import dataclass
from typing import Optional, Protocol, TypedDict


def add(a: int, b: int) -> int:
    return a + b


def greet(name: str) -> str:
    return "olá, " + name


class User(TypedDict):
    name: str
    age: int


class Closeable(Protocol):
    def close(self) -> None: ...


class File:
    def close(self) -> None:
        pass


class Socket:
    def shutdown(self) -> None:
        pass


def close_all(items: list[Closeable]) -> None:
    for item in items:
        item.close()


def find(users: list[User], name: str) -> Optional[User]:
    for user in users:
        if user["name"] == name:
            return user
    return None


@dataclass
class Point:
    x: int
    y: int


def demo() -> None:
    """Cada linha abaixo tem um erro de tipo (a função nunca é chamada)."""
    add("1", 2)                               # argumento de tipo errado
    greet(None)                               # None não é str
    close_all([File(), Socket()])             # Socket não tem close()
    found = find([], "ana")
    print(found["age"])                       # pode ser None
    u: User = {"name": "ana"}                 # falta 'age'
    p = Point(1, "2")                         # y deve ser int
    x: int = "texto"                          # atribuição incompatível


def broken() -> int:
    return "oops"                             # retorno incompatível


def maybe(flag: bool) -> str:
    if flag:
        return "sim"                          # falta o caminho do False


if __name__ == "__main__":
    print("o módulo importa e roda; os erros estão em demo(), broken() e maybe()")
