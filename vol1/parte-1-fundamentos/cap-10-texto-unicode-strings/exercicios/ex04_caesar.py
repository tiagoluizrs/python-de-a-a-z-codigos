"""Exercício 4: cifra de César respeitando maiúsculas e minúsculas."""


def caesar(text: str, shift: int) -> str:
    """Desloque cada letra ASCII de ``text`` em ``shift`` posições.

    - maiúsculas continuam maiúsculas, minúsculas continuam minúsculas;
    - qualquer outro caractere (espaços, dígitos, pontuação, letras
      acentuadas, emoji) passa inalterado;
    - ``shift`` pode ser negativo ou maior que 26.

        caesar("Hello, World!", 3) == "Khoor, Zruog!"
        caesar("xyz", 3) == "abc"
        caesar("Ação", 1) == "Bçãp"   # só "A" e "o" mudam
        caesar(caesar("Python", 7), -7) == "Python"

    Dica: use ``str.maketrans`` e ``str.translate`` com
    ``string.ascii_lowercase`` e ``string.ascii_uppercase`` rotacionadas.
    """
    raise NotImplementedError
