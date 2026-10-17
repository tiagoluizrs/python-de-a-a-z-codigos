"""Repository e Unit of Work (Capítulo 7 do Volume 3) sobre o SQLAlchemy, com um repositório falso para testes."""
from dataclasses import dataclass

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)


@dataclass
class User:                                              # o modelo de DOMÍNIO não conhece o SQLAlchemy
    id: int | None
    email: str


class SqlUserRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, user: User) -> User:
        row = UserRow(email=user.email)
        self.session.add(row)
        self.session.flush()
        return User(row.id, row.email)

    def by_email(self, email: str) -> User | None:
        row = self.session.scalars(select(UserRow).where(UserRow.email == email)).first()
        return User(row.id, row.email) if row else None


class SqlUnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.users = SqlUserRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.session.rollback()                          # sem commit() explícito, nada é gravado
        self.session.close()

    def commit(self):
        self.session.commit()


class FakeUnitOfWork:                                    # para testar a regra de negócio SEM banco
    def __init__(self):
        self.users = type("FakeRepo", (), {"data": {}, "add": lambda s, u: s.data.setdefault(u.email, u), "by_email": lambda s, e: s.data.get(e)})()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def commit(self):
        self.committed = True


def register(uow, email: str) -> User:                   # a regra de negócio: recebe QUALQUER unidade de trabalho
    with uow:
        if uow.users.by_email(email):
            raise ValueError(f"e-mail já cadastrado: {email}")
        user = uow.users.add(User(None, email))
        uow.commit()
        return user


if __name__ == "__main__":
    engine = sa.create_engine("sqlite://")
    Base.metadata.create_all(engine)
    uow = SqlUnitOfWork(sessionmaker(engine))
    print("registrado:", register(uow, "ana@x.com"))
    try:
        register(uow, "ana@x.com")
    except ValueError as error:
        print("duplicado:", error)
    with uow:
        uow.users.add(User(None, "nao-confirmado@x.com"))          # sem commit
    with uow:
        print("sem commit, não gravou:", uow.users.by_email("nao-confirmado@x.com"))
    fake = FakeUnitOfWork()
    register(fake, "bia@x.com")
    print("com o falso (sem banco):", fake.committed, list(fake.users.data))
