"""Exercício 3: atributos OBSERVÁVEIS: um descritor que avisa quem observa quando o valor muda."""


class observed:
    """Descritor COM dados para atributos de instância: ``price = observed(default=0)``.

    * o valor fica em ``instancia.__dict__["_" + nome]`` (o nome vem de ``__set_name__``); sem valor atribuído, ``__get__`` devolve ``default``;
    * ao ATRIBUIR um valor DIFERENTE do atual (``!=``), chama cada observador desta instância e deste atributo, na ordem em que foram registrados, com
      ``callback(instancia, nome, antigo, novo)`` DEPOIS de guardar o novo valor; atribuir um valor igual não avisa ninguém;
    * se um observador levantar exceção, a exceção sobe e o novo valor JÁ está guardado (os observadores seguintes não são chamados);
    * ``validate`` (opcional, ``observed(default=0, validate=f)``): uma função chamada com o novo valor ANTES de guardar; se levantar exceção, nada muda e ninguém
      é avisado;
    * lido pela classe, devolve o próprio descritor."""

    def __init__(self, default=None, validate=None):
        raise NotImplementedError

    def __set_name__(self, owner, name):
        raise NotImplementedError

    def __get__(self, obj, owner=None):
        raise NotImplementedError

    def __set__(self, obj, value):
        raise NotImplementedError


def watch(obj, name: str, callback):
    """Registra ``callback`` para o atributo observável ``name`` de ``obj`` (por INSTÂNCIA: outra instância da mesma classe não é afetada) e devolve ``callback``.
    ``name`` que não é um ``observed`` na classe: ``AttributeError(f"{name!r} não é observável")``; ``callback`` não chamável: ``TypeError``. Guarde os observadores
    em ``obj.__dict__["_watchers"]``, um dicionário ``{nome: [callbacks]}``."""
    raise NotImplementedError


def unwatch(obj, name: str, callback) -> None:
    """Remove ``callback``; não registrado: ``ValueError("não registrado")``."""
    raise NotImplementedError
