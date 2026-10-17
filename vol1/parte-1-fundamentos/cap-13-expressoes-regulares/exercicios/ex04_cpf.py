"""Exercício 4: validar CPF (formato com regex, dígitos em código)."""


def is_valid_cpf(value: str) -> bool:
    """Diga se ``value`` é um CPF com formato e dígitos válidos.

    Formatos aceitos: ``529.982.247-25`` ou ``52998224725`` (nada de
    formatação pela metade). Os dois últimos dígitos são verificadores:
    para cada um, multiplique os dígitos anteriores por pesos
    decrescentes (10..2 para o primeiro, 11..2 para o segundo), some,
    calcule ``(soma * 10) % 11`` e use 0 se der 10. CPFs com todos os
    dígitos iguais (``111.111.111-11``) são inválidos.
    """
    raise NotImplementedError


def mask_cpfs(text: str) -> str:
    """Troque cada CPF VÁLIDO em ``text`` por ``***.***.***-DD``.

    ``DD`` são os dois dígitos verificadores originais. CPFs inválidos
    e outros números ficam intactos. Dica: ``re.sub`` com função.
    """
    raise NotImplementedError
