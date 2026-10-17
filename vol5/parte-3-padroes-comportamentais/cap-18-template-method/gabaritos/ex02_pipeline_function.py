"""Gabarito do exercício 2."""
from dataclasses import dataclass, field


@dataclass
class Result:
    rows: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    @property
    def ok(self):
        return len(self.rows)


def make_importer(parse, save, *, validate=None, transform=None, before=None, after=None):
    if not callable(parse) or not callable(save):
        raise TypeError("passo obrigatório precisa ser chamável")

    def run(raw):
        result = Result()
        if before:
            before()
        try:
            for i, row in enumerate(parse(raw)):
                try:
                    if validate:
                        validate(row)
                except ValueError as error:
                    result.errors.append((i, str(error)))
                    continue
                result.rows.append(transform(row) if transform else row)
            save(result.rows)
        finally:
            if after:
                after(result)
        return result

    return run


def compose_steps(*steps):
    for step in steps:
        if not callable(step):
            raise TypeError("passo precisa ser chamável")

    def composed(value):
        for step in steps:
            value = step(value)
        return value

    return composed


def validators(*rules):
    def validate(row):
        for rule in rules:
            rule(row)

    return validate
