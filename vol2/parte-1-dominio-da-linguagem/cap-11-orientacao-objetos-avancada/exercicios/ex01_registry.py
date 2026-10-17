"""Exercício 1: atributos de classe, classmethods e a armadilha da lista compartilhada."""


class Tracker:
    """Conta instâncias e guarda o histórico POR INSTÂNCIA.

    * ``Tracker(name)``; cada instância tem ``name`` e uma lista ``events``
      PRÓPRIA (a armadilha do atributo mutável de classe não pode ocorrer);
    * ``t.record("x")`` acrescenta o evento à lista da instância;
    * atributo de classe ``created`` conta quantas instâncias foram criadas;
    * ``Tracker.created_count()`` (classmethod) devolve esse número;
    * ``Tracker.reset_count()`` (classmethod) zera o contador;
    * ``Tracker.is_valid_name(texto)`` (staticmethod): nome não vazio e sem
      espaços nas pontas.
    """

    def __init__(self, name):
        raise NotImplementedError
