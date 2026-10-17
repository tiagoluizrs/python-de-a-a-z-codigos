"""Exercício 3: mixins cooperativos com super()."""


class Handler:
    """Base: ``handle(value)`` registra ``"Handler"`` em ``self.trace`` e
    devolve o valor inalterado. Cada instância tem sua lista ``trace``."""

    def __init__(self):
        self.trace = []

    def handle(self, value):
        self.trace.append("Handler")
        return value


class Strip:
    """Mixin: remove espaços das pontas do texto ANTES de passar adiante.

    Deve registrar ``"Strip"`` em ``self.trace``, transformar o valor e
    chamar ``super().handle(...)``.
    """

    def handle(self, value):
        raise NotImplementedError


class Upper:
    """Mixin: converte o texto para maiúsculas ANTES de passar adiante e
    registra ``"Upper"``."""

    def handle(self, value):
        raise NotImplementedError


class Exclaim:
    """Mixin: passa adiante e, DEPOIS, acrescenta ``"!"`` ao resultado.
    Registra ``"Exclaim"`` antes de chamar ``super()``."""

    def handle(self, value):
        raise NotImplementedError


class Pipeline(Strip, Upper, Exclaim, Handler):
    """Combina os mixins; a ordem das bases define a ordem do fluxo."""
