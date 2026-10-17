"""Exercício 1: a Specification clássica: cada regra é um objeto; E, OU e NÃO são objetos também (e sabem explicar por que falharam)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """(Pronto, NÃO edite.) ``banned`` ``None`` quer dizer "não se sabe" (conta como NÃO banido)."""

    id: int
    name: str
    age: int
    country: str
    tags: tuple = ()
    banned: bool | None = False


class Specification(ABC):
    """A base. ``is_satisfied_by(candidate)`` e ``describe()`` são abstratos (cada regra implementa). Implemente, AQUI na base, os métodos de conveniência:

    * ``and_(other)``, ``or_(other)`` e ``not_()``: devolvem um ``AndSpec``, um ``OrSpec`` e um ``NotSpec``; ``other`` que não for uma ``Specification``: ``TypeError("esperava uma Specification")``;
    * ``failures(candidate)``: a lista das descrições (``describe()``) das regras FOLHA que explicam por que o candidato NÃO satisfaz esta regra: ``[]`` se satisfaz; para uma folha,
      ``[self.describe()]``. Os combinadores sobrescrevem (veja abaixo)."""

    @abstractmethod
    def is_satisfied_by(self, candidate) -> bool: ...

    @abstractmethod
    def describe(self) -> str: ...

    def failures(self, candidate) -> list[str]:
        raise NotImplementedError

    def and_(self, other: "Specification") -> "Specification":
        raise NotImplementedError

    def or_(self, other: "Specification") -> "Specification":
        raise NotImplementedError

    def not_(self) -> "Specification":
        raise NotImplementedError


class AgeAtLeast(Specification):
    """``AgeAtLeast(minimum)``: ``minimum`` precisa ser um ``int >= 0`` (``ValueError("idade inválida")``); satisfeita se ``user.age >= minimum``; ``describe()``: ``"idade >= 18"``."""

    def __init__(self, minimum: int):
        raise NotImplementedError


class FromCountry(Specification):
    """``FromCountry(*codes)``: ao menos um código (``ValueError("informe ao menos um país")``); satisfeita se ``user.country in codes``; ``describe()``: ``"país em ('BR', 'PT')"``
    (o ``repr`` da tupla de códigos)."""

    def __init__(self, *codes: str):
        raise NotImplementedError


class HasTag(Specification):
    """``HasTag(tag)``: satisfeita se ``tag in user.tags``; ``describe()``: ``"tem a tag 'vip'"`` (``repr`` do texto)."""

    def __init__(self, tag: str):
        raise NotImplementedError


class IsBanned(Specification):
    """Satisfeita se ``bool(user.banned)`` (``None`` não é banido); ``describe()``: ``"está banido"``."""


class Always(Specification):
    """Sempre satisfeita; ``describe()``: ``"sempre"``."""


class Never(Specification):
    """Nunca satisfeita; ``describe()``: ``"nunca"``."""


class AndSpec(Specification):
    """``AndSpec(left, right)``: satisfeita se as DUAS são; com CURTO-CIRCUITO (``right`` NÃO é avaliada se ``left`` falha); ``describe()``: ``"(esq E dir)"``;
    ``failures``: as falhas de ``left`` seguidas das de ``right`` (cada lado só conta o que realmente falhou)."""

    def __init__(self, left: Specification, right: Specification):
        raise NotImplementedError


class OrSpec(Specification):
    """``OrSpec(left, right)``: satisfeita se ALGUMA é, com curto-circuito (``right`` NÃO é avaliada se ``left`` basta); ``describe()``: ``"(esq OU dir)"``;
    ``failures``: ``[]`` se satisfeita; senão as falhas de ``left`` seguidas das de ``right``."""

    def __init__(self, left: Specification, right: Specification):
        raise NotImplementedError


class NotSpec(Specification):
    """``NotSpec(inner)``: satisfeita se ``inner`` NÃO é; ``describe()``: ``"NÃO " + inner.describe()``; ``failures``: ``[]`` se satisfeita; senão ``[self.describe()]``
    (a falha é a regra inteira "NÃO ...", sem abrir o ``inner``)."""

    def __init__(self, inner: Specification):
        raise NotImplementedError


def all_of(*specs: Specification) -> Specification:
    """Todas (``and_`` encadeado, da esquerda para a direita). Sem nenhuma: ``Always()``; com uma só: ela mesma (a MESMA instância)."""
    raise NotImplementedError


def any_of(*specs: Specification) -> Specification:
    """Alguma (``or_`` encadeado). Sem nenhuma: ``Never()``; com uma só: ela mesma."""
    raise NotImplementedError


def filter_by(spec: Specification, candidates) -> list:
    """Os candidatos que satisfazem ``spec``, na ordem de entrada."""
    raise NotImplementedError


def first_match(spec: Specification, candidates, default=None):
    """O primeiro candidato que satisfaz ``spec`` (para na primeira ocorrência, sem consumir o resto de um gerador) ou ``default``."""
    raise NotImplementedError
