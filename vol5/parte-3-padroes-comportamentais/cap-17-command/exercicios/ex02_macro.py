"""Exercício 2: comando composto (macro) ATÔMICO: ou tudo funciona, ou nada fica pela metade."""
from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class SetValue(Command):
    """(Pronto, NÃO edite.) ``SetValue(store, key, value)``: grava ``store[key] = value``; ``undo`` restaura o valor antigo ou apaga a chave se não existia."""

    _MISSING = object()

    def __init__(self, store: dict, key, value):
        self.store, self.key, self.value, self.old = store, key, value, SetValue._MISSING

    def execute(self):
        self.old = self.store.get(self.key, SetValue._MISSING)
        self.store[self.key] = self.value

    def undo(self):
        if self.old is SetValue._MISSING:
            self.store.pop(self.key, None)
        else:
            self.store[self.key] = self.old


class Fail(Command):
    """(Pronto, NÃO edite.) Levanta ``RuntimeError(message)`` ao executar; o ``undo`` registra a chamada em ``undone`` (para os testes)."""

    def __init__(self, message: str = "falhou"):
        self.message, self.undone = message, False

    def execute(self):
        raise RuntimeError(self.message)

    def undo(self):
        self.undone = True


class Macro(Command):
    """``Macro(*commands)``.

    * ``execute``: executa os comandos EM ORDEM. Se um deles levantar exceção, desfaz (``undo``) os que JÁ foram executados com sucesso, em ordem INVERSA, e
      relança a exceção original (o que falhou NÃO é desfeito, pois não terminou). Se um ``undo`` da compensação também falhar, ainda tenta os demais e a exceção
      original continua sendo a que sobe;
    * ``undo``: desfaz TODOS os comandos em ordem INVERSA (só faz sentido depois de um ``execute`` completo; antes disso, ``RuntimeError("macro não executada")``);
    * uma macro pode conter outras macros;
    * ``len(macro)``: quantos comandos diretos tem; ``Macro()`` vazia executa e desfaz sem fazer nada."""

    def __init__(self, *commands: Command):
        raise NotImplementedError

    def execute(self) -> None:
        raise NotImplementedError

    def undo(self) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


def run_all(commands: list[Command]) -> list[Command]:
    """Executa os ``commands`` como uma TRANSAÇÃO (use uma ``Macro``): devolve a lista dos comandos, se todos funcionaram; se algum falhar, os anteriores são
    desfeitos e a exceção sobe."""
    raise NotImplementedError
