"""Gabarito do exercício 2."""


def _path(item):
    return ".".join(str(part) for part in item["loc"]) or "__root__"


def _message(item):
    message = item["msg"]
    if item["type"] == "value_error" and message.startswith("Value error, "):
        message = message[len("Value error, "):]
    return message


def errors_to_dict(error):
    result = {}
    for item in error.errors():
        result.setdefault(_path(item), []).append(_message(item))
    return result


def first_message(error):
    items = error.errors()
    text = f"{_path(items[0])}: {_message(items[0])}"
    extra = len(items) - 1
    if extra:
        text += f" (+{extra} {'erro' if extra == 1 else 'erros'})"
    return text
