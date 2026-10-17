"""Gabarito do exercício 6."""
from sqlalchemy.dialects import mysql, postgresql, sqlite


def upsert(session, model, values, key):
    if key not in values:
        raise KeyError(key)
    dialect = session.get_bind().dialect.name
    others = {k: v for k, v in values.items() if k != key}
    if dialect in ("sqlite", "postgresql"):
        insert = (sqlite if dialect == "sqlite" else postgresql).insert
        statement = insert(model).values(**values)
        statement = statement.on_conflict_do_update(index_elements=[key], set_={k: statement.excluded[k] for k in others})
        session.execute(statement)
    elif dialect in ("mysql", "mariadb"):
        statement = mysql.insert(model).values(**values)
        session.execute(statement.on_duplicate_key_update(**{k: statement.inserted[k] for k in others}))
    else:
        row = session.get(model, values[key])
        if row is None:
            session.add(model(**values))
        else:
            for column, value in others.items():
                setattr(row, column, value)
        session.flush()
