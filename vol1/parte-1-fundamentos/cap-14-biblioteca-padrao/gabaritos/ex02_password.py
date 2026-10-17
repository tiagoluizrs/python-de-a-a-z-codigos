"""Gabarito do exercício 2: senhas com ``secrets``."""
import secrets
import string

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%&*?-_"


def generate_password(length: int = 16) -> str:
    if length < 8:
        raise ValueError("length must be at least 8")
    classes = (LOWER, UPPER, DIGITS, SYMBOLS)
    # Garante uma de cada classe...
    chars = [secrets.choice(c) for c in classes]
    # ...e completa o resto com o alfabeto inteiro
    alphabet = "".join(classes)
    chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
    # Embaralha com a fonte segura; senão os 4 primeiros seriam previsíveis
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def make_token(nbytes: int = 16) -> str:
    return secrets.token_urlsafe(nbytes)
