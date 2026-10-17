"""O MESMO código, seis bancos: SQL gerado, tipos e upsert por dialeto."""
import datetime as dt
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import String, select
from sqlalchemy.dialects import mysql, postgresql, sqlite
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from dburls import available_engines


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "sa_product"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(40))
    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2))
    at: Mapped[dt.datetime] = mapped_column(sa.DateTime(timezone=True))


engines = available_engines()
print("bancos disponíveis:", ", ".join(engines))
statement = select(Product).where(Product.price > 10).order_by(Product.id).limit(5).offset(10)
print("\nA mesma consulta, compilada por cada dialeto:")
for name, engine in engines.items():
    print(f"  {name:<11}", " ".join(str(statement.compile(engine)).split())[-62:])

print("\nO mesmo modelo e a mesma lógica, executados em cada banco:")
for name, engine in engines.items():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    moment = dt.datetime(2026, 10, 13, 12, 0, tzinfo=dt.UTC)
    with Session(engine) as session:
        session.add_all([Product(id=i, name=f"p{i}", price=Decimal("9.99") + i, at=moment) for i in range(1, 21)])
        session.commit()
        rows = session.scalars(select(Product).where(Product.price > 10).order_by(Product.id).limit(3).offset(2)).all()
        first = rows[0]
        print(f"  {name:<11} ids {[p.id for p in rows]} | price {type(first.price).__name__}({first.price}) | at.tzinfo = {first.at.tzinfo}")
    Base.metadata.drop_all(engine)

# upsert: aqui o código É específico do dialeto (o SQLAlchemy não tem upsert genérico)
print("\nUpsert, a parte específica do dialeto:")
values = {"id": 1, "name": "novo", "price": Decimal("1.00"), "at": dt.datetime(2026, 1, 1, tzinfo=dt.UTC)}
pg = postgresql.insert(Product).values(**values)
print("  postgresql:", " ".join(str(pg.on_conflict_do_update(index_elements=["id"], set_={"name": pg.excluded.name}).compile(dialect=postgresql.dialect())).split())[-70:])
my = mysql.insert(Product).values(**values)
print("  mysql     :", " ".join(str(my.on_duplicate_key_update(name=my.inserted.name).compile(dialect=mysql.dialect())).split())[-55:])
sl = sqlite.insert(Product).values(**values)
print("  sqlite    :", " ".join(str(sl.on_conflict_do_update(index_elements=["id"], set_={"name": sl.excluded.name}).compile(dialect=sqlite.dialect())).split())[-70:])
print("  oracle/mssql: sem insert-upsert nativo na API: use MERGE em text(), ou SELECT + INSERT/UPDATE na mesma transação")
for engine in engines.values():
    engine.dispose()
