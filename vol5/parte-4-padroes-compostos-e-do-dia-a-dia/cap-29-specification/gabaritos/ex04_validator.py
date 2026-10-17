"""Gabarito do exercício 4."""


class ValidationError(Exception):
    def __init__(self, errors):
        super().__init__("; ".join(errors))
        self.errors = list(errors)


class Rule:
    def __init__(self, check, message, when=None):
        self.check, self.message, self.when = check, message, when

    def error(self, item):
        if self.when is not None and not self.when(item):
            return None
        if self.check(item):
            return None
        return self.message(item) if callable(self.message) else self.message


class Validator:
    def __init__(self, rules=()):
        self.rules = list(rules)

    def add(self, rule):
        self.rules.append(rule)
        return self

    def validate(self, item):
        errors = (rule.error(item) for rule in self.rules)
        return [error for error in errors if error is not None]

    def is_valid(self, item):
        return not self.validate(item)

    def first_error(self, item):
        for rule in self.rules:
            error = rule.error(item)
            if error is not None:
                return error
        return None

    def ensure(self, item):
        errors = self.validate(item)
        if errors:
            raise ValidationError(errors)
        return item


def required(field):
    def check(item):
        value = item.get(field)
        return value is not None and not (isinstance(value, str) and not value.strip())

    return Rule(check, f"{field} é obrigatório")


def min_value(field, minimum):
    return Rule(lambda item: item.get(field) is None or item[field] >= minimum, f"{field} deve ser >= {minimum}")


def max_len(field, maximum):
    return Rule(lambda item: item.get(field) is None or len(item[field]) <= maximum, f"{field} deve ter no máximo {maximum} caracteres")
