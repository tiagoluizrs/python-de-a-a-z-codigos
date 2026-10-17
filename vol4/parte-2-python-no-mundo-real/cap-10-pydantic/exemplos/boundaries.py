"""Validar nas FRONTEIRAS: API HTTP (Cap. 9), banco (Cap. 5), documentos (Cap. 7)."""
import httpx
import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


# 1. resposta de uma API: o JSON é "dict de qualquer coisa" até passar pelo modelo
class Repo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    stars: int = Field(ge=0)
    topics: list[str] = []


def handler(request):
    if request.url.path == "/ok":
        return httpx.Response(200, json=[{"name": "httpx", "stars": "12000", "lang": "py"}, {"name": "x", "stars": 3, "topics": ["a"]}])
    return httpx.Response(200, json=[{"name": "quebrado", "stars": -5}, {"nome": "sem name", "stars": 1}])


with httpx.Client(transport=httpx.MockTransport(handler), base_url="http://api.test") as client:
    repos = [Repo.model_validate(item) for item in client.get("/ok").json()]
    print("API válida:", [(r.name, r.stars) for r in repos], "(\"12000\" virou int; 'lang' extra ignorado)")
    try:
        [Repo.model_validate(item) for item in client.get("/bad").json()]
    except ValidationError as error:
        print("API mudou o contrato ->", error.error_count(), "erro(s):", [(e["loc"], e["type"]) for e in error.errors()])

# 2. ORM -> modelo de saída (não exponha a classe do banco)
class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(100))


class UserOut(BaseModel):                       # o que PODE sair: sem password_hash
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


engine = sa.create_engine("sqlite://")
Base.metadata.create_all(engine)
with Session(engine) as session:
    session.add(UserRow(name="Ana", password_hash="$2b$..."))
    session.commit()
    row = session.get(UserRow, 1)
    out = UserOut.model_validate(row)
    print("\nORM -> modelo de saída:", out.model_dump(), "| password_hash vazou?", "password_hash" in out.model_dump())

# 3. documento do MongoDB (Capítulo 7): o banco aceitava qualquer coisa; a validação na aplicação não
class ProductDoc(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku: str
    stock: int = Field(ge=0)
    tags: list[str] = []


docs = [{"sku": "A1", "stock": 5}, {"sku": "B2", "stock": "muitos"}, {"sku": "C3", "stock": 1, "tagz": ["x"]}]
good, bad = [], []
for index, doc in enumerate(docs):
    try:
        good.append(ProductDoc.model_validate(doc))
    except ValidationError as error:
        bad.append((index, [e["type"] for e in error.errors()]))
print("\ndocumentos do Mongo: válidos", [g.sku for g in good], "| inválidos (índice, erros):", bad)
print("regra: UM modelo de ENTRADA (o que aceito), um de SAÍDA (o que mostro) e a classe do banco separados; o Pydantic faz a ponte nas fronteiras.")
