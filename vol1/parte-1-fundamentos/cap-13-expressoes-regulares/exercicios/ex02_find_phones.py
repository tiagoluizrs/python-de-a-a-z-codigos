"""Exercício 2: encontrar e normalizar telefones brasileiros."""


def find_phones(text: str) -> list[str]:
    """Encontre telefones em texto livre e devolva-os normalizados.

    Aceite, com ou sem ``+55``, DDD com ou sem parênteses, espaço ou
    hífen opcionais: celular (9 dígitos, começa com 9) e fixo (8
    dígitos, começa com 2 a 5). O DDD tem dois dígitos e não começa
    com 0. Normalize para ``+55`` + DDD + número, só dígitos.

    Exemplo::

        find_phones("Ligue (11) 98765-4321 ou 21 3456-7890")
        == ["+5511987654321", "+552134567890"]

    Cuidado: não case um pedaço de um número maior (``123456789012345``
    não contém telefone). Dica: lookarounds ``(?<!\\d)`` e ``(?!\\d)``.
    """
    raise NotImplementedError
