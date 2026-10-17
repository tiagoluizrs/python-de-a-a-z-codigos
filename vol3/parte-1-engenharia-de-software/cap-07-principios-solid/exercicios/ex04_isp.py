"""Exercício 4 (I): funções que dependem só do PAPEL de que precisam (os testes passam dublês com UM ou DOIS métodos)."""
from typing import Protocol


class Reader(Protocol):
    def get(self, user_id: int) -> dict | None: ...


class Lister(Protocol):
    def list_ids(self) -> list[int]: ...


class Deleter(Protocol):
    def delete(self, user_id: int) -> None: ...


def display_name(reader: Reader, user_id: int) -> str:
    """O nome de exibição: ``f"{first} {last}"`` com os campos ``first`` e ``last`` do dict de ``reader.get(user_id)``; se ``last`` for
    vazio ou ausente, só ``first``. Usuário inexistente (``None``): ``LookupError(f"usuário {user_id} não existe")``. Use APENAS
    ``reader.get``."""
    raise NotImplementedError


def purge_inactive(lister: Lister, reader: Reader, deleter: Deleter) -> list[int]:
    """Apaga (``deleter.delete(id)``) os usuários cujo dict tem ``active`` falso (ausente conta como falso), na ordem de
    ``lister.list_ids()``, e devolve os ids apagados. Use APENAS ``list_ids``, ``get`` e ``delete`` (um dublê só com esses três métodos
    deve bastar). Um id que aparece em ``list_ids`` mas cujo ``get`` devolve ``None`` é IGNORADO (já foi removido)."""
    raise NotImplementedError


def total_length(items) -> int:
    """A soma dos comprimentos (``len``) de todos os textos de ``items``, que pode ser QUALQUER iterável de textos (lista, tupla, gerador,
    arquivo aberto, conjunto...). Não use ``len(items)`` nem indexação nele: ele só precisa ser ``Iterable[str]``. Anote o parâmetro
    com ``collections.abc.Iterable[str]`` (o teste confere ``total_length.__annotations__``)."""
    raise NotImplementedError


def first_and_last(items) -> tuple:
    """``(primeiro, último)`` de ``items``, que aqui PRECISA ser uma sequência (acesso por índice e ``len``): anote com
    ``collections.abc.Sequence``. Vazia: ``ValueError("sequência vazia")``. Aceita lista, tupla e ``str``; NÃO precisa aceitar um gerador."""
    raise NotImplementedError
