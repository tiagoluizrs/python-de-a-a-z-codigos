"""Exercício 2: o MESMO roteiro do exercício 1, agora como uma função que recebe os passos (sem herança)."""
from dataclasses import dataclass, field


@dataclass
class Result:
    rows: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    @property
    def ok(self) -> int:
        return len(self.rows)


def make_importer(parse, save, *, validate=None, transform=None, before=None, after=None):
    """Devolve ``run(raw) -> Result`` com a MESMA ordem e as MESMAS regras do ``Importer.run`` do exercício 1 (``before``; ``parse``; por linha, ``validate`` e
    ``transform``; ``save(rows)`` uma vez; ``after(result)`` SEMPRE, inclusive quando ``parse`` ou ``save`` levantam exceção, que então sobe). Os passos opcionais
    (``validate``, ``transform``, ``before``, ``after``) valem ``None`` por padrão e são ignorados. ``parse`` ou ``save`` que não são chamáveis:
    ``TypeError("passo obrigatório precisa ser chamável")`` (na criação)."""
    raise NotImplementedError


def compose_steps(*steps):
    """Compõe funções de UMA linha em uma só (a saída de uma é a entrada da seguinte), para usar como ``transform``: ``compose_steps(f, g)(x) == g(f(x))``. Sem passos:
    a identidade. Um passo não chamável: ``TypeError``."""
    raise NotImplementedError


def validators(*rules):
    """Combina regras ``rule(row)`` (que levantam ``ValueError``) em UM ``validate``: executa as regras em ordem e para na PRIMEIRA que falhar (a exceção dela sobe).
    Sem regras: não faz nada."""
    raise NotImplementedError
