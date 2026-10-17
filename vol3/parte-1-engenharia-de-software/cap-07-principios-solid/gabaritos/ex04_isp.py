"""Gabarito do exercício 4."""
from collections.abc import Iterable, Sequence
from typing import Protocol


class Reader(Protocol):
    def get(self, user_id: int) -> dict | None: ...


class Lister(Protocol):
    def list_ids(self) -> list[int]: ...


class Deleter(Protocol):
    def delete(self, user_id: int) -> None: ...


def display_name(reader: Reader, user_id: int) -> str:
    user = reader.get(user_id)
    if user is None:
        raise LookupError(f"usuário {user_id} não existe")
    return f"{user['first']} {user['last']}" if user.get("last") else user["first"]


def purge_inactive(lister: Lister, reader: Reader, deleter: Deleter) -> list[int]:
    removed = []
    for user_id in lister.list_ids():
        user = reader.get(user_id)
        if user is not None and not user.get("active"):
            deleter.delete(user_id)
            removed.append(user_id)
    return removed


def total_length(items: Iterable[str]) -> int:
    return sum(len(item) for item in items)


def first_and_last(items: Sequence) -> tuple:
    if len(items) == 0:
        raise ValueError("sequência vazia")
    return items[0], items[-1]
