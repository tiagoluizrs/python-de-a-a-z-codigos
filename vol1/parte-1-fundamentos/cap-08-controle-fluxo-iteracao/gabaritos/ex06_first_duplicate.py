"""Gabarito do exercício 6."""


def first_duplicate(items):
    seen = set()                       # busca em O(1) por item
    for index, item in enumerate(items):
        if item in seen:
            result = (item, index)
            break                      # achou: o else NÃO roda
        seen.add(item)
    else:
        result = None                  # terminou sem break
    return result
