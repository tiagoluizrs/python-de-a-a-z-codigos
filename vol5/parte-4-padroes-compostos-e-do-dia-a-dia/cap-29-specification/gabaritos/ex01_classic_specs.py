"""Gabarito do exercício 1."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    name: str
    age: int
    country: str
    tags: tuple = ()
    banned: bool | None = False


def _check(other):
    if not isinstance(other, Specification):
        raise TypeError("esperava uma Specification")


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate): ...

    @abstractmethod
    def describe(self): ...

    def failures(self, candidate):
        return [] if self.is_satisfied_by(candidate) else [self.describe()]

    def and_(self, other):
        _check(other)
        return AndSpec(self, other)

    def or_(self, other):
        _check(other)
        return OrSpec(self, other)

    def not_(self):
        return NotSpec(self)


class AgeAtLeast(Specification):
    def __init__(self, minimum):
        if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 0:
            raise ValueError("idade inválida")
        self.minimum = minimum

    def is_satisfied_by(self, user):
        return user.age >= self.minimum

    def describe(self):
        return f"idade >= {self.minimum}"


class FromCountry(Specification):
    def __init__(self, *codes):
        if not codes:
            raise ValueError("informe ao menos um país")
        self.codes = codes

    def is_satisfied_by(self, user):
        return user.country in self.codes

    def describe(self):
        return f"país em {self.codes}"


class HasTag(Specification):
    def __init__(self, tag):
        self.tag = tag

    def is_satisfied_by(self, user):
        return self.tag in user.tags

    def describe(self):
        return f"tem a tag {self.tag!r}"


class IsBanned(Specification):
    def is_satisfied_by(self, user):
        return bool(user.banned)

    def describe(self):
        return "está banido"


class Always(Specification):
    def is_satisfied_by(self, candidate):
        return True

    def describe(self):
        return "sempre"


class Never(Specification):
    def is_satisfied_by(self, candidate):
        return False

    def describe(self):
        return "nunca"


class AndSpec(Specification):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def is_satisfied_by(self, candidate):
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)

    def describe(self):
        return f"({self.left.describe()} E {self.right.describe()})"

    def failures(self, candidate):
        return self.left.failures(candidate) + self.right.failures(candidate)


class OrSpec(Specification):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def is_satisfied_by(self, candidate):
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)

    def describe(self):
        return f"({self.left.describe()} OU {self.right.describe()})"

    def failures(self, candidate):
        if self.is_satisfied_by(candidate):
            return []
        return self.left.failures(candidate) + self.right.failures(candidate)


class NotSpec(Specification):
    def __init__(self, inner):
        self.inner = inner

    def is_satisfied_by(self, candidate):
        return not self.inner.is_satisfied_by(candidate)

    def describe(self):
        return f"NÃO {self.inner.describe()}"


def all_of(*specs):
    if not specs:
        return Always()
    result = specs[0]
    for spec in specs[1:]:
        result = result.and_(spec)
    return result


def any_of(*specs):
    if not specs:
        return Never()
    result = specs[0]
    for spec in specs[1:]:
        result = result.or_(spec)
    return result


def filter_by(spec, candidates):
    return [c for c in candidates if spec.is_satisfied_by(c)]


def first_match(spec, candidates, default=None):
    for candidate in candidates:
        if spec.is_satisfied_by(candidate):
            return candidate
    return default
