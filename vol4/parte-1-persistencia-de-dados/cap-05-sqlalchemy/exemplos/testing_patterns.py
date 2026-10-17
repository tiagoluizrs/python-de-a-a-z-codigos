"""Testar com banco: transação por teste, revertida no fim (rápido e isolado)."""
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "note"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]


# autocommit=False (modo moderno do sqlite3, Capítulo 1): sem ele o pysqlite não respeita SAVEPOINT e o rollback externo falha
engine = sa.create_engine("sqlite://", poolclass=sa.pool.StaticPool, connect_args={"autocommit": False})
Base.metadata.create_all(engine)


def one_test(name):
    """Equivalente a uma fixture do pytest: conexão + transação externa + sessão que vira SAVEPOINT."""
    connection = engine.connect()
    outer = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    session.add(Note(text=name))
    session.commit()                                       # "confirma" só o savepoint
    seen = session.scalars(select(Note.text)).all()
    session.close()
    outer.rollback()                                       # descarta TUDO que o teste fez
    connection.close()
    return seen


print("teste 1 viu:", one_test("do teste 1"))
print("teste 2 viu:", one_test("do teste 2"), "(o teste 1 não deixou resíduo)")
with Session(engine) as session:
    print("depois de tudo, o banco tem", session.scalar(select(sa.func.count()).select_from(Note)), "notas")
print("variante simples: SQLite em memória novo por teste (engine barato); para bancos reais, esta transação revertida evita recriar o esquema")
