"""Exercício 4: uma fábrica configurável com valores padrão validados (``functools.partial`` com mais cuidado)."""
import copy
import inspect


def factory_for(cls, **defaults):
    """Devolve ``make(**overrides)`` que cria ``cls(**{**defaults, **overrides})``.

    * cada chamada recebe CÓPIAS PROFUNDAS (``copy.deepcopy``) dos ``defaults`` (um padrão mutável, como uma lista, não pode ser
      compartilhado entre as instâncias); os ``overrides`` não são copiados;
    * nomes que ``cls.__init__`` não aceita, em ``defaults`` (na criação da fábrica) ou em ``overrides`` (na chamada):
      ``TypeError(f"{cls.__name__} não aceita o argumento {nome!r}")``; se o ``__init__`` tem ``**kwargs``, qualquer nome é aceito;
    * ``make.cls`` é a classe e ``make.defaults`` é uma CÓPIA dos padrões (alterá-la não afeta a fábrica)."""
    raise NotImplementedError
