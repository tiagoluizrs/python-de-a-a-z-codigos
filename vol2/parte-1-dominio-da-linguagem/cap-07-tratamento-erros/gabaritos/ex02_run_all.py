"""Gabarito do exercício 2."""


def run_all(tasks):
    results, errors = [], []
    for task in tasks:
        try:
            results.append(task())
        except Exception as error:         # coleta, não interrompe
            errors.append(error)
    if errors:
        raise ExceptionGroup(f"{len(errors)} tarefas falharam", errors)
    return results


def count_by_type(group):
    counts = {}
    for item in group.exceptions:
        if isinstance(item, BaseExceptionGroup):      # recursão em grupos aninhados
            for name, amount in count_by_type(item).items():
                counts[name] = counts.get(name, 0) + amount
        else:
            name = type(item).__name__
            counts[name] = counts.get(name, 0) + 1
    return counts
