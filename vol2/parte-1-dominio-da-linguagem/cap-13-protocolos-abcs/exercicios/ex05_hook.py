"""Exercício 5: __subclasshook__ e registro virtual."""
from abc import ABC


class Drawable(ABC):
    """Qualquer classe com um método ``draw`` é considerada ``Drawable``,
    sem herdar e sem registro (``__subclasshook__``).

    * ``issubclass(Qualquer, Drawable)`` é verdadeiro se ``Qualquer`` (ou uma
      de suas bases) define ``draw``;
    * ``draw`` precisa ser CHAMÁVEL (não vale um atributo ``draw = 1``);
    * ``issubclass(int, Drawable)`` é falso;
    * classes SEM ``draw`` podem ser declaradas manualmente com
      ``Drawable.register(Classe)``.
    """
