"""Gabarito do exercício 4."""


class Interner:
    def __init__(self):
        self._pool = {}
        self._calls = 0

    def intern(self, value):
        try:
            hash(value)
        except TypeError:
            raise TypeError(f"valor não hashable: {type(value).__name__}") from None
        self._calls += 1
        return self._pool.setdefault((type(value), value), value)

    def stats(self):
        return {"calls": self._calls, "unique": len(self._pool)}

    def clear(self):
        self._pool.clear()
        self._calls = 0

    def __len__(self):
        return len(self._pool)


def _intern_value(interner, value):
    if isinstance(value, str):
        return interner.intern(value)
    if isinstance(value, tuple) and all(isinstance(v, str) for v in value):
        return interner.intern(tuple(interner.intern(v) for v in value))
    return value


def dedupe_records(rows, interner=None):
    if interner is None:                      # não use `or`: um Interner vazio é falso (tem __len__)
        interner = Interner()
    return [{interner.intern(k): _intern_value(interner, v) for k, v in row.items()} for row in rows]


def distinct_objects(rows, key):
    return len({id(row[key]) for row in rows if key in row})


def duplication_report(rows):
    values: dict[str, list] = {}
    for row in rows:
        for key, value in row.items():
            if isinstance(value, str):
                values.setdefault(key, []).append(value)
    return {key: (len(vals), len(set(vals))) for key, vals in sorted(values.items())}
