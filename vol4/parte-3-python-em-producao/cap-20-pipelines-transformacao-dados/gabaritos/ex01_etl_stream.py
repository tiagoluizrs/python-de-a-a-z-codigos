"""Gabarito do exercício 1."""
import itertools


class Rejected(Exception):
    pass


def parse_line(line):
    parts = [p.strip() for p in line.rstrip("\r\n").split(",")]
    if len(parts) != 5:
        raise Rejected("colunas")
    event_id, user_id, product, qty, price = parts
    if not user_id:
        raise Rejected("user_id vazio")
    try:
        event_id_i, user_id_i, qty_i, price_f = int(event_id), int(user_id), int(qty), float(price)
    except ValueError:
        raise Rejected("número inválido") from None
    if qty_i <= 0:
        raise Rejected("quantidade não positiva")
    if price_f < 0:
        raise Rejected("preço negativo")
    return {"event_id": event_id_i, "user_id": user_id_i, "product": product.lower(), "qty": qty_i, "price": price_f,
            "total": round(qty_i * price_f, 2)}


def transform(lines, rejects, skip_header=True):
    seen = set()
    for number, line in enumerate(lines, start=1):
        if skip_header and number == 1:
            continue
        if not line.strip():
            continue
        try:
            record = parse_line(line)
            if record["event_id"] in seen:
                raise Rejected("event_id duplicado")
        except Rejected as reason:
            rejects.append((number, str(reason)))
            continue
        seen.add(record["event_id"])
        yield record


def batched(items, size):
    if size < 1:
        raise ValueError("size deve ser >= 1")
    iterator = iter(items)
    while batch := list(itertools.islice(iterator, size)):
        yield batch


def summarize(good_count, rejects):
    counts = {}
    for _, reason in rejects:
        counts[reason] = counts.get(reason, 0) + 1
    ordered = dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
    return {"loaded": good_count, "rejected": len(rejects), "reasons": ordered}
