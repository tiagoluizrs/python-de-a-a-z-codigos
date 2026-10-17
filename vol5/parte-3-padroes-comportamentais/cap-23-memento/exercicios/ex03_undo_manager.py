"""Exercício 3: um gerenciador de desfazer/refazer genérico para qualquer objeto com ``snapshot()`` e ``restore()``."""
from typing import Protocol, runtime_checkable


@runtime_checkable
class Snapshottable(Protocol):
    """(Pronto, NÃO edite.) O que o gerenciador exige do alvo."""

    def snapshot(self): ...

    def restore(self, snapshot) -> None: ...


class UndoManager:
    """Cada ``checkpoint`` guarda o estado ATUAL do alvo, com um nome para o PASSO que vem a seguir (o que você vai fazer).

    * ``UndoManager(target, limit=50)``: ``target`` que não for um ``Snapshottable`` (``isinstance``): ``TypeError("alvo sem snapshot/restore")``; ``limit < 1``: ``ValueError("limite inválido")``;
    * ``checkpoint(label=None)``: guarda ``(label, target.snapshot())`` e APAGA o "refazer"; passa do limite: o checkpoint mais antigo é esquecido;
    * ``undo()``: sem nada para desfazer, ``LookupError("nada para desfazer")``; senão guarda o estado atual no "refazer" (com o MESMO nome), restaura o checkpoint mais recente e devolve o NOME dele;
    * ``redo()``: sem nada para refazer, ``LookupError("nada para refazer")``; senão guarda o estado atual de volta nos checkpoints, restaura o estado desfeito e devolve o nome do passo refeito;
    * ``goto(label)``: desfaz, um a um, até desfazer o passo MAIS RECENTE chamado ``label`` (o estado fica como estava ANTES dele; o "refazer" fica disponível); devolve quantos passos
      foram desfeitos; ``label`` inexistente: ``LookupError(f"checkpoint desconhecido: {label}")`` SEM alterar nada;
    * ``labels()``: os nomes dos checkpoints, do mais antigo ao mais recente; ``can_undo`` e ``can_redo``: propriedades booleanas."""

    def __init__(self, target, limit: int = 50):
        raise NotImplementedError

    def checkpoint(self, label: str | None = None) -> None:
        raise NotImplementedError

    def undo(self) -> str | None:
        raise NotImplementedError

    def redo(self) -> str | None:
        raise NotImplementedError

    def goto(self, label: str) -> int:
        raise NotImplementedError

    def labels(self) -> list[str | None]:
        raise NotImplementedError

    @property
    def can_undo(self) -> bool:
        raise NotImplementedError

    @property
    def can_redo(self) -> bool:
        raise NotImplementedError
