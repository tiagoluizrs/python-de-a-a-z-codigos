"""Gabarito do exercício 6."""
from collections.abc import Mapping
from typing import overload


@overload
def parse(value: str) -> int: ...
@overload
def parse(value: bytes) -> str: ...
@overload
def parse(value: None) -> None: ...
def parse(value: str | bytes | None) -> int | str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return int(value)
    return value.decode()


@overload
def get[T](mapping: Mapping[str, T], key: str) -> T | None: ...
@overload
def get[T, D](mapping: Mapping[str, T], key: str, default: D) -> T | D: ...
def get[T](mapping: Mapping[str, T], key: str, default: object = None) -> object:
    return mapping[key] if key in mapping else default
