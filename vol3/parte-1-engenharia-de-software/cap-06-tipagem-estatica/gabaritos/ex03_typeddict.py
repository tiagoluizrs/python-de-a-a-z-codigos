"""Gabarito do exercício 3."""
from collections.abc import Mapping
from typing import NotRequired, TypedDict


class Address(TypedDict):
    street: str
    city: str


class User(TypedDict):
    name: str
    age: int
    address: Address
    email: NotRequired[str]


def _text(data: Mapping[str, object], key: str, path: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise ValueError(path)
    return value


def parse_user(data: Mapping[str, object]) -> User:
    name = _text(data, "name", "name")
    age = data.get("age")
    if not isinstance(age, int) or isinstance(age, bool):
        raise ValueError("age")
    raw_address = data.get("address")
    if not isinstance(raw_address, Mapping):
        raise ValueError("address")
    address: Address = {"street": _text(raw_address, "street", "address.street"),
                        "city": _text(raw_address, "city", "address.city")}
    user: User = {"name": name, "age": age, "address": address}
    if "email" in data:
        user["email"] = _text(data, "email", "email")
    return user


def summary(user: User) -> str:
    text = f"{user['name']} ({user['age']}), {user['address']['city']}"
    return text + (f" <{user['email']}>" if "email" in user else "")
