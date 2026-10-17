"""Gabarito do exercício 3."""
import hmac


class Secret:
    __slots__ = ("_value",)

    def __init__(self, value):
        object.__setattr__(self, "_value", value)

    def reveal(self):
        return self._value

    def __repr__(self):
        return "Secret('**********')"

    __str__ = __repr__

    def __eq__(self, other):
        if not isinstance(other, Secret):
            return NotImplemented
        return hmac.compare_digest(self._value.encode(), other._value.encode())

    __hash__ = None

    def __bool__(self):
        return bool(self._value)

    def __reduce__(self):
        raise TypeError("Secret não pode ser serializado nem copiado")
