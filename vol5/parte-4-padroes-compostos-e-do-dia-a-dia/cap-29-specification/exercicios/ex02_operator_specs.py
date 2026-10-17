"""Exercício 2: a Specification com os operadores do Python: ``adulto & (local | vip) & ~banido``."""


class Spec:
    """Uma regra: um objeto que se chama como função (``spec(item)`` devolve um ``bool``) e se combina com operadores.

    * ``Spec(fn, description="?")``: ``fn`` que não for chamável: ``TypeError("fn precisa ser chamável")``; atributos ``fn`` e ``description``; ``spec(item)`` devolve ``bool(fn(item))``;
    * ``a & b``: satisfeita se as duas são, com CURTO-CIRCUITO (``b`` nem é chamada se ``a`` falha); descrição ``"(a e b)"``; ``a | b``: com curto-circuito (``b`` nem é chamada se ``a`` basta);
      descrição ``"(a ou b)"``; ``~a``: o contrário; descrição ``"não a"``. ``repr(spec)`` é a descrição;
    * o outro operando pode ser um ``Spec`` OU qualquer função chamável (que vira ``Spec(f, f.__name__)``); algo que não é chamável (``Spec & 3``): ``TypeError`` (devolva
      ``NotImplemented`` para o Python levantar o erro certo); o operador refletido (``funcao & spec``) também funciona;
    * as regras combinadas são NOVAS: ``a`` e ``b`` continuam funcionando sozinhas depois de ``a & b``."""

    def __init__(self, fn, description: str = "?"):
        raise NotImplementedError

    def __call__(self, item) -> bool:
        raise NotImplementedError

    def __and__(self, other):
        raise NotImplementedError

    def __rand__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError

    def __ror__(self, other):
        raise NotImplementedError

    def __invert__(self):
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError


def spec(description: str):
    """Um decorador: ``@spec("maior de idade")`` sobre ``def adult(u): ...`` devolve ``Spec(adult, "maior de idade")``."""
    raise NotImplementedError


def all_of(*specs) -> Spec:
    """A conjunção de todas (cada argumento: ``Spec`` ou função). Sem nenhuma: um ``Spec`` sempre verdadeiro, descrição ``"sempre"``; com uma só: ela mesma (como ``Spec``)."""
    raise NotImplementedError


def any_of(*specs) -> Spec:
    """A disjunção. Sem nenhuma: um ``Spec`` sempre falso, descrição ``"nunca"``; com uma só: ela mesma (como ``Spec``)."""
    raise NotImplementedError


def where(**conditions) -> Spec:
    """Uma regra de igualdade campo a campo: ``where(country="BR", vip=True)`` é satisfeita pelo item cujo campo ``country`` é ``"BR"`` E cujo ``vip`` é ``True``. O item pode ser um
    DICIONÁRIO (chaves) ou um OBJETO (atributos). Campo ausente: a condição é FALSA (não é um erro). Sem condições: sempre verdadeira. Descrição: ``"country == 'BR' e vip == True"``
    (as condições na ordem dada, unidas por ``" e "``; sem condições, ``"sempre"``)."""
    raise NotImplementedError


def filter_by(rule, items) -> list:
    """Os itens para os quais ``rule(item)`` é verdadeira, na ordem de entrada."""
    raise NotImplementedError
