"""Gabarito do exercício 1."""


def summarize(title, /, *numbers, precision=2, **extras):
    total = sum(numbers)
    # sem números não há média: devolvemos None em vez de dividir por zero
    mean = round(total / len(numbers), precision) if numbers else None
    result = {
        "title": title,
        "count": len(numbers),
        "total": total,
        "mean": mean,
    }
    # os extras vêm por último
    result.update(extras)
    return result
