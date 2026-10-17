"""Gabarito 5: pipeline de logs; cada etapa consome e produz um item."""


def parse(lines):
    for line in lines:
        parts = line.split()
        if len(parts) != 3 or not parts[2].isdigit():
            continue            # linha em branco ou malformada
        level, service, ms = parts
        yield level, service, int(ms)


def only_levels(records, levels):
    for record in records:
        if record[0] in levels:
            yield record


def total_by_service(records):
    # único consumidor: acumula em um dict pequeno (um item por serviço)
    totals = {}
    for _, service, ms in records:
        count, total = totals.get(service, (0, 0))
        totals[service] = (count + 1, total + ms)
    return totals
