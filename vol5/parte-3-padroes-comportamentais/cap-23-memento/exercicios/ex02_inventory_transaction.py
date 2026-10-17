"""Exercício 2: transações com rollback: o memento fica numa variável local de um gerenciador de contexto."""
from contextlib import contextmanager


class Inventory:
    """Um estoque com quantidades e etiquetas (listas!). O que é restaurado no rollback é o estado dos DOIS.

    * ``add(item, qty)``: ``qty`` precisa ser um inteiro ``> 0`` (``ValueError("quantidade inválida")``; ``bool`` NÃO vale); soma ao estoque;
    * ``remove(item, qty)``: mesma validação; item ausente ou ``qty`` maior que o estoque: ``ValueError(f"estoque insuficiente: {item}")``; se o estoque chega a ``0``, o item é APAGADO
      (da quantidade e das etiquetas);
    * ``label(item, text)``: item inexistente: ``LookupError(item)``; senão acrescenta ``text`` à lista de etiquetas do item;
    * ``quantity(item)``: a quantidade (``0`` se não existe); ``labels_of(item)``: uma CÓPIA da lista de etiquetas (``[]`` se não há);
    * ``transaction(dry_run=False)``: gerenciador de contexto. Ao entrar, guarda um instantâneo PROFUNDO do estado. Se o bloco levantar QUALQUER exceção (inclusive ``BaseException``),
      restaura o instantâneo, soma 1 a ``rollbacks`` e deixa a exceção subir. Se terminar bem: soma 1 a ``commits`` e mantém as mudanças. Com ``dry_run=True`` o estado é SEMPRE
      restaurado ao sair (``rollbacks`` sobe, ``commits`` não) e uma exceção, se houver, continua subindo.
      Transações ANINHADAS funcionam: a de dentro, ao falhar, desfaz só o que ela fez (a de fora decide se captura a exceção ou a deixa subir e desfaz tudo);
    * ``commits`` e ``rollbacks``: contadores, começam em ``0``."""

    def __init__(self):
        raise NotImplementedError

    def add(self, item: str, qty: int) -> None:
        raise NotImplementedError

    def remove(self, item: str, qty: int) -> None:
        raise NotImplementedError

    def label(self, item: str, text: str) -> None:
        raise NotImplementedError

    def quantity(self, item: str) -> int:
        raise NotImplementedError

    def labels_of(self, item: str) -> list[str]:
        raise NotImplementedError

    @contextmanager
    def transaction(self, dry_run: bool = False):
        raise NotImplementedError
        yield
