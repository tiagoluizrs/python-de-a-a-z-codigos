"""Gabarito do exercício 2."""


def _merge(sequences):
    result = []
    sequences = [list(seq) for seq in sequences if seq]
    while sequences:
        for seq in sequences:
            head = seq[0]
            # a cabeça só serve se não aparece na CAUDA de nenhuma lista
            if not any(head in other[1:] for other in sequences):
                break
        else:
            raise TypeError("inconsistent hierarchy")
        result.append(head)
        sequences = [[c for c in seq if c is not head] for seq in sequences]
        sequences = [seq for seq in sequences if seq]
    return result


def c3_linearization(cls):
    bases = list(cls.__bases__)
    if not bases:
        return [cls]
    return [cls] + _merge([c3_linearization(base) for base in bases] + [bases])
