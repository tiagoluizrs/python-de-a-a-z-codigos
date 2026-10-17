"""Alvo do exercício 1."""
import re
import unicodedata


def slugify(text):
    """Transforma texto em um "slug" de URL: minúsculas, sem acentos, só letras e
    dígitos separados por um único hífen, sem hífen nas pontas."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower())
    return slug.strip("-") or "untitled"
