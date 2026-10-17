"""Aninhado versus guard clauses (retorno antecipado)."""


def ship_nested(order):
    if order is not None:
        if order["paid"]:
            if order["items"]:
                if order["address"]:
                    return "shipped"
                else:
                    return "no address"
            else:
                return "empty"
        else:
            return "unpaid"
    else:
        return "no order"


def ship_guarded(order):
    if order is None:
        return "no order"
    if not order["paid"]:
        return "unpaid"
    if not order["items"]:
        return "empty"
    if not order["address"]:
        return "no address"
    return "shipped"


base = {"paid": True, "items": ["pen"], "address": "Rua A"}
cases = [None, {**base, "paid": False}, {**base, "items": []},
         {**base, "address": ""}, base]
for case in cases:
    assert ship_nested(case) == ship_guarded(case)
    print(ship_guarded(case))
