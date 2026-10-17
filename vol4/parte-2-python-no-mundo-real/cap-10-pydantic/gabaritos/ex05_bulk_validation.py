"""Gabarito do exercício 5."""
from pydantic import ValidationError


def _errors(error):
    return [{"loc": ".".join(str(p) for p in e["loc"]), "type": e["type"], "msg": e["msg"]} for e in error.errors()]


def validate_records(model, rows):
    valid, errors = [], []
    for index, row in enumerate(rows):
        try:
            valid.append(model.model_validate(row))
        except ValidationError as error:
            errors.append({"index": index, "errors": _errors(error)})
    return valid, errors


def validate_json_lines(model, text):
    valid, errors = [], []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            valid.append(model.model_validate_json(line))
        except ValidationError as error:
            errors.append({"index": number, "errors": _errors(error)})
    return valid, errors
