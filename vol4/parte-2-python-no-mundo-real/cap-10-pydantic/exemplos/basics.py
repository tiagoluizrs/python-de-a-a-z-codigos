"""Modelos, coerção, restrições e erros."""
import datetime as dt

import pydantic
from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationError

print("pydantic", pydantic.VERSION)


class User(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=40)
    email: EmailStr | None = None
    born: dt.date | None = None
    tags: list[str] = []                       # default mutável é SEGURO aqui: cada instância recebe uma cópia


# 1. coerção: dados "sujos" (JSON, formulário, variável de ambiente) viram os tipos certos
user = User(id="7", name="Ana", born="2000-01-31", tags=("a", "b"))
print("coerção:", repr(user))
print("tipos:", type(user.id).__name__, type(user.born).__name__, type(user.tags).__name__)

# 2. tudo ou nada: TODOS os erros de uma vez, com o caminho de cada um
try:
    User(id="x", name="", email="nao-e-email", born="31/01/2000", tags=[1])
except ValidationError as error:
    print(f"\n{error.error_count()} erros de uma vez:")
    for item in error.errors():
        print(f"  {'.'.join(map(str, item['loc'])):<8} {item['type']:<22} {item['msg'][:60]}")

# 3. estrito: sem coerção
class Strict(BaseModel):
    model_config = ConfigDict(strict=True)
    n: int


try:
    Strict(n="1")
except ValidationError as error:
    print("\nstrict=True recusa '1' para int:", error.errors()[0]["type"])
print("o modo estrito também existe por campo: Field(strict=True) ou Annotated[int, Strict()]")

# 4. campos extras e imutabilidade
class Config(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    host: str
    port: int = 8000


print("\nextra='ignore' (padrão) descarta o que sobra; extra='forbid' acusa o erro de digitação:")
try:
    Config(host="h", prot=9000)
except ValidationError as error:
    print("  ", error.errors()[0]["type"], error.errors()[0]["loc"])
cfg = Config(host="h")
try:
    cfg.port = 1
except ValidationError as error:
    print("   frozen=True:", error.errors()[0]["type"])
print("   hash de um modelo frozen:", hash(cfg) is not None, "(pode ser chave de dicionário)")

# 5. aliases: o nome do JSON não precisa ser o do Python
class Item(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    item_id: int = Field(alias="itemId")
    unit_price: float = Field(alias="unitPrice")


item = Item.model_validate({"itemId": 1, "unitPrice": 9.5})
print("\nalias na entrada:", item, "| na saída com by_alias:", item.model_dump(by_alias=True))

# 6. validação sem criar o objeto, e o que NÃO é validado
print("\natribuição NÃO é revalidada por padrão:", end=" ")
user.id = "não é número"
print(repr(user.id), "(use validate_assignment=True em ConfigDict se quiser)")
