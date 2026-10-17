"""Carga em massa e desempenho: o que custa e o que não custa."""
import time

import sqlalchemy as sa
from sqlalchemy import insert, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "item"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    qty: Mapped[int] = mapped_column(default=0)


engine = sa.create_engine("sqlite://")
Base.metadata.create_all(engine)
N = 5_000
rows = [{"name": f"item-{i}", "qty": i} for i in range(N)]


def timed(label, func):
    with Session(engine) as session:
        session.execute(sa.delete(Item))
        session.commit()
        start = time.perf_counter()
        func(session)
        session.commit()
        elapsed = time.perf_counter() - start
        count = session.scalar(select(sa.func.count()).select_from(Item))
    print(f"  {label:<46} {elapsed * 1e3:8.1f} ms ({count:,} linhas)")
    return elapsed


print(f"inserir {N:,} linhas (SQLite em memória):")
loop = timed("laço de session.execute(insert(...)) por linha", lambda s: [s.execute(insert(Item).values(**r)) for r in rows])
timed("session.add_all([Item(...)]) (objetos ORM)", lambda s: s.add_all([Item(**r) for r in rows]))
fast = timed("session.execute(insert(Item), lista) (em lote)", lambda s: s.execute(insert(Item), rows))
print(f"  em lote foi {loop / fast:.0f}x mais rápido que o laço (o SQLAlchemy usa 'insertmanyvalues': vários VALUES por comando)")

# ler muitos objetos: yield_per transmite em lotes (memória constante)
with Session(engine) as session:
    session.execute(insert(Item), [{"name": f"n{i}", "qty": i} for i in range(50_000)])
    session.commit()
    start = time.perf_counter()
    total = sum(item.qty for item in session.scalars(select(Item).execution_options(yield_per=5_000)))
    print(f"yield_per=5000 sobre 55.000 linhas: soma {total:,} em {(time.perf_counter() - start) * 1e3:.0f} ms (sem carregar tudo de uma vez)")

# commit por linha
start = time.perf_counter()
with Session(engine) as session:
    for i in range(300):
        session.add(Item(name=f"c{i}"))
        session.commit()
print(f"300 commits, um por linha (SQLite em memória): {(time.perf_counter() - start) * 1e3:.0f} ms; em um arquivo, cada commit grava no disco (Capítulo 1)")
