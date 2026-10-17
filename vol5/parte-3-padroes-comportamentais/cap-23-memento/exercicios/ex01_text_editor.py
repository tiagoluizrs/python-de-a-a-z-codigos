"""Exercício 1: o Memento clássico: um editor que salva e restaura o próprio estado, e um zelador que só guarda."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EditorMemento:
    """(Pronto, NÃO edite.) O instantâneo opaco do editor: quem o guarda (o ``History``) não deve olhar os campos com ``_``."""

    _owner: object
    _text: str
    _cursor: int
    _selection: tuple | None


class Editor:
    """O originador. Estado: ``text`` (começa ``""``), ``cursor`` (começa ``0``) e ``selection`` (``None`` ou ``(início, fim)``).

    * ``type(chars)``: insere ``chars`` na posição do cursor, move o cursor para o fim do trecho inserido e LIMPA a seleção;
    * ``move(pos)``: move o cursor para ``pos`` (``0 <= pos <= len(text)``, senão ``IndexError``) e limpa a seleção;
    * ``select(start, end)``: ``0 <= start <= end <= len(text)`` (senão ``ValueError("seleção inválida")``); guarda a seleção e põe o cursor em ``end``;
    * ``delete_selection()``: sem seleção, ``ValueError("sem seleção")``; senão remove o trecho, põe o cursor em ``start`` e limpa a seleção;
    * ``save()``: devolve um ``EditorMemento`` (com ``self`` como dono) que guarda ``text``, ``cursor`` e ``selection``;
    * ``restore(memento)``: o argumento que não for um ``EditorMemento`` dá ``TypeError``; um memento de OUTRO editor dá ``ValueError("memento de outro editor")``; senão recoloca o estado."""

    def __init__(self):
        raise NotImplementedError

    def type(self, chars: str) -> None:
        raise NotImplementedError

    def move(self, pos: int) -> None:
        raise NotImplementedError

    def select(self, start: int, end: int) -> None:
        raise NotImplementedError

    def delete_selection(self) -> None:
        raise NotImplementedError

    def save(self) -> EditorMemento:
        raise NotImplementedError

    def restore(self, memento: EditorMemento) -> None:
        raise NotImplementedError


class History:
    """O zelador: guarda mementos e NUNCA lê os campos deles.

    * ``History(editor, limit=None)``: ``limit`` é o máximo de passos que podem ser desfeitos (os mais antigos são esquecidos); ``limit < 1``: ``ValueError("limite inválido")``;
    * ``do(action, *args)``: guarda o estado ANTES, apaga o "refazer", chama ``action(*args)`` e devolve o resultado; se ``action`` levantar uma exceção, o editor é RESTAURADO ao estado de antes,
      NADA entra no histórico e a exceção continua subindo;
    * ``undo()``: desfaz um passo e devolve ``True``; sem passos, devolve ``False``; ``redo()``: refaz um passo (``True``/``False``);
    * ``can_undo`` e ``can_redo``: propriedades booleanas."""

    def __init__(self, editor: Editor, limit: int | None = None):
        raise NotImplementedError

    def do(self, action, *args):
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
