"""Gabarito do exercício 2."""

ATOMIC = (int, float, complex, str, bytes, bool, type(None))


def my_deepcopy(obj, memo: dict | None = None):
    if memo is None:
        memo = {}
    if isinstance(obj, ATOMIC):
        return obj
    key = id(obj)
    if key in memo:              # já copiado (compartilhamento ou ciclo)
        return memo[key]

    if isinstance(obj, list):
        new: list = []
        memo[key] = new          # registra ANTES de recursar: quebra ciclos
        new.extend(my_deepcopy(item, memo) for item in obj)
        return new
    if isinstance(obj, dict):
        new_dict: dict = {}
        memo[key] = new_dict
        for k, v in obj.items():
            new_dict[my_deepcopy(k, memo)] = my_deepcopy(v, memo)
        return new_dict
    if isinstance(obj, set):
        new_set: set = set()
        memo[key] = new_set
        for item in obj:
            new_set.add(my_deepcopy(item, memo))
        return new_set
    if isinstance(obj, tuple):
        # Tupla é imutável: não dá para criar vazia e preencher depois,
        # então copiamos os itens primeiro e registramos no fim.
        items = tuple(my_deepcopy(item, memo) for item in obj)
        if key in memo:          # um ciclo através da tupla já a registrou
            return memo[key]
        if all(a is b for a, b in zip(items, obj)):
            items = obj          # nada mudou: reaproveita a tupla
        memo[key] = items
        return items
    raise TypeError(f"tipo não suportado: {type(obj).__name__}")
