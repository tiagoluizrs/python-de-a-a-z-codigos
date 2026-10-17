"""Exercício 1: comandos com desfazer/refazer sobre um editor de texto: ``Insert``, ``Delete`` e o histórico."""
from abc import ABC, abstractmethod


class Editor:
    """Guarda o ``text`` (``Editor(text="")``). Os comandos o alteram diretamente."""

    def __init__(self, text: str = ""):
        self.text = text


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class Insert(Command):
    """``Insert(editor, pos, text)``: insere ``text`` na posição ``pos``. ``pos`` fora de ``0 <= pos <= len(texto)`` (verificado em ``execute``, com o texto da hora):
    ``ValueError(f"posição inválida: {pos}")`` e NADA é alterado. ``undo`` remove exatamente o que foi inserido."""

    def __init__(self, editor: Editor, pos: int, text: str):
        raise NotImplementedError

    def execute(self) -> None:
        raise NotImplementedError

    def undo(self) -> None:
        raise NotImplementedError


class Delete(Command):
    """``Delete(editor, start, end)``: remove ``text[start:end]``. Exige ``0 <= start <= end <= len(texto)`` (verificado em ``execute``): senão
    ``ValueError(f"intervalo inválido: {start}-{end}")``. Guarda o trecho removido em ``execute`` para que ``undo`` o restaure na mesma posição.
    Executar de novo (``redo``) remove de novo o trecho que estiver ali."""

    def __init__(self, editor: Editor, start: int, end: int):
        raise NotImplementedError

    def execute(self) -> None:
        raise NotImplementedError

    def undo(self) -> None:
        raise NotImplementedError


class History:
    """O INVOCADOR. ``History(limit=None)``:

    * ``run(command)``: executa o comando; se der certo, guarda-o para desfazer e LIMPA a pilha de refazer; se ``execute`` levantar exceção, nada é guardado e a
      exceção sobe;
    * ``undo()``: desfaz o último comando executado (devolve ``True``); sem nada para desfazer, devolve ``False``;
    * ``redo()``: refaz o último desfeito (``True``) ou devolve ``False``;
    * ``can_undo`` e ``can_redo`` (propriedades booleanas);
    * ``limit``: se não for ``None``, só os ``limit`` comandos mais RECENTES ficam disponíveis para desfazer (os mais antigos são esquecidos); ``limit < 1``:
      ``ValueError("limit deve ser >= 1")``;
    * ``len(history)``: quantos comandos podem ser desfeitos agora."""

    def __init__(self, limit: int | None = None):
        raise NotImplementedError

    def run(self, command: Command) -> None:
        raise NotImplementedError

    def undo(self) -> bool:
        raise NotImplementedError

    def redo(self) -> bool:
        raise NotImplementedError

    @property
    def can_undo(self) -> bool:
        raise NotImplementedError

    @property
    def can_redo(self) -> bool:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
