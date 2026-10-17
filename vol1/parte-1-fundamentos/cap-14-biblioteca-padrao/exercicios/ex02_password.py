"""Exercício 2: gerador de senhas seguro com ``secrets``."""
import string

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%&*?-_"


def generate_password(length: int = 16) -> str:
    """Gere uma senha de ``length`` caracteres com pelo menos uma
    minúscula, uma maiúscula, um dígito e um símbolo.

    Regras:
    - ``length < 8`` levanta ``ValueError``.
    - Use SOMENTE o módulo ``secrets`` (nunca ``random``).
    - Dica: sorteie um caractere de cada classe, complete o resto com
      ``secrets.choice`` sobre todas as classes e embaralhe o resultado
      com ``secrets.SystemRandom().shuffle``.
    """
    raise NotImplementedError


def make_token(nbytes: int = 16) -> str:
    """Devolva um token aleatório seguro, seguro para URLs
    (``secrets.token_urlsafe``)."""
    raise NotImplementedError
