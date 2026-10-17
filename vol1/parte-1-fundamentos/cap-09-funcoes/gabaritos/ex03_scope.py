"""Gabarito do exercício 3."""

_last_id = 0


def next_id():
    # sem esta linha, a atribuição abaixo tornaria _last_id LOCAL em toda
    # a função, e a leitura em "+=" falharia antes de existir valor
    global _last_id
    _last_id += 1
    return _last_id


def reset_ids(start=0):
    global _last_id
    _last_id = start


def unbound_message():
    def broken():
        print(value)   # lê um local ainda sem valor
        value = 1

    try:
        broken()
    except UnboundLocalError as exc:
        return str(exc)
