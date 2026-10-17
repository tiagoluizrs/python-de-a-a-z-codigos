"""Exercício 2: uma lanterna que aponta classes que talvez sejam um padrão desnecessário em Python."""
import ast
import textwrap
from dataclasses import dataclass


@dataclass(frozen=True)
class Hint:
    pattern: str     # "Strategy/Command", "Singleton", "Iterator" ou "Observer"
    where: str       # nome da classe
    line: int        # linha da classe (``class``), no texto depois de ``textwrap.dedent``


def pattern_hints(source: str) -> list[Hint]:
    """Percorre as classes de ``source`` (inclusive aninhadas) e devolve uma ``Hint`` por achado, ordenadas por ``(line, pattern)``:

    * ``"Strategy/Command"``: descontando ``__init__``, a classe tem EXATAMENTE um método, e ele é público (nome que não começa com ``_``)
      ou é ``__call__``; é o cheiro de "uma classe que poderia ser uma função" (classe sem métodos, ou com dois ou mais, não conta);
    * ``"Singleton"``: o corpo da classe atribui (``=`` ou com anotação) um nome ``_instance`` ou ``__instance``, OU a classe define ``__new__``;
    * ``"Iterator"``: a classe define ``__iter__`` E ``__next__`` (poderia ser um gerador);
    * ``"Observer"``: algum método da classe faz ``self.X = []`` (ou ``list()``, ou ``set()``) com ``X`` em
      ``{"observers", "listeners", "subscribers", "handlers", "callbacks"}``.
    Uma mesma classe pode gerar mais de uma ``Hint``."""
    raise NotImplementedError
