"""field(), valores padrão mutáveis, ordem dos campos, __post_init__, InitVar."""
from dataclasses import KW_ONLY, InitVar, dataclass, field
from typing import ClassVar

# 1) Padrão mutável é um erro (e uma proteção)
try:
    @dataclass
    class Bad:
        items: list = []
except ValueError as error:
    print("ValueError:", error)


@dataclass
class Cart:
    owner: str
    items: list[str] = field(default_factory=list)       # uma lista NOVA por instância
    tags: dict[str, int] = field(default_factory=dict)


a, b = Cart("ana"), Cart("bia")
a.items.append("x")
print(a, b, a.items is b.items)

# 2) Campos com padrão não podem vir antes dos sem padrão
try:
    @dataclass
    class WrongOrder:
        a: int = 0
        b: int
except TypeError as error:
    print("TypeError:", error)


# 3) kw_only resolve (3.10+)
@dataclass(kw_only=True)
class Config:
    host: str = "localhost"
    port: int


print(Config(port=8080))
try:
    Config("x", 1)
except TypeError as error:
    print("TypeError:", error)


@dataclass
class Mixed:
    id: int
    _: KW_ONLY
    note: str = ""                                      # só por nome, depois do marcador
    flag: bool = False


print(Mixed(1, note="ok"))


# 4) Opções de field()
@dataclass
class User:
    name: str
    password: str = field(repr=False)                    # fora do repr
    created: int = field(default=0, compare=False)       # fora do ==
    internal: list = field(default_factory=list, init=False)   # não está no __init__
    kind: ClassVar[str] = "user"                         # atributo de CLASSE: não é campo


u1, u2 = User("a", "123", created=1), User("a", "123", created=2)
print(u1, u1 == u2, u1.kind, "internal" in vars(u1))


# 5) __post_init__: validação e campos derivados
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("lados devem ser positivos")
        self.area = self.width * self.height


print(Rectangle(2, 3))
try:
    Rectangle(-1, 3)
except ValueError as error:
    print("ValueError:", error)


# 6) InitVar: parâmetro só do __init__, que NÃO vira campo
@dataclass
class Account:
    owner: str
    password: InitVar[str]
    hashed: str = field(init=False, repr=False)

    def __post_init__(self, password):
        self.hashed = f"hash({password})"


acct = Account("ana", "segredo")
print(acct, acct.hashed, hasattr(acct, "password"))
