"""Exercício 2: descritores de validação reutilizáveis."""


class Validator:
    """Base de descritores: guarde o valor na INSTÂNCIA, com ``__set_name__``.

    * ``__set_name__`` descobre o nome do atributo;
    * ``__get__`` devolve o descritor quando acessado pela classe
      (``obj is None``) e o valor guardado na instância caso contrário;
    * ``__set__`` chama ``self.validate(value)`` e só então guarda;
    * nenhuma instância pode interferir no valor de outra.
    """

    def validate(self, value):
        raise NotImplementedError


class Positive(Validator):
    """Aceita ``int``/``float`` > 0 (``bool`` NÃO vale); senão ``ValueError``
    cuja mensagem cita o nome do atributo."""


class NonEmpty(Validator):
    """Aceita ``str`` com algum caractere não branco; senão ``ValueError``."""


class OneOf(Validator):
    """``OneOf("a", "b")``: aceita só os valores listados; senão ``ValueError``."""

    def __init__(self, *choices):
        raise NotImplementedError
