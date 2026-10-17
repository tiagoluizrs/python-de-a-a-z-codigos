"""Gabarito do exercício 2."""


class Validator:
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name)          # estado na INSTÂNCIA

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    def validate(self, value):
        raise NotImplementedError


class Positive(Validator):
    def validate(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{self.public_name} deve ser positivo, recebi {value!r}")


class NonEmpty(Validator):
    def validate(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{self.public_name} não pode ser vazio")


class OneOf(Validator):
    def __init__(self, *choices):
        self.choices = choices

    def validate(self, value):
        if value not in self.choices:
            raise ValueError(f"{self.public_name} deve ser um de {self.choices}")
