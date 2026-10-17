"""Ordenar texto com acentos: ponto de código, casefold, locale, chave NFD."""
import locale
import unicodedata

words = ["z", "é", "a", "E", "e", "b", "Z", "á"]
print(sorted(words))                       # por ponto de código
print(sorted(words, key=str.casefold))
print([f"{w}:U+{ord(w):04X}" for w in sorted(words)])


def accent_key(text):
    """Chave sem acentos e sem caixa, com desempate pelo texto original."""
    base = unicodedata.normalize("NFD", text.casefold())
    base = "".join(c for c in base if unicodedata.category(c) != "Mn")
    return (base, text)


names = ["Álvaro", "Zélia", "Ana", "Édson", "Eva", "ana", "Ângela"]
print(sorted(names))
print(sorted(names, key=str.casefold))
print(sorted(names, key=accent_key))

# locale: depende do sistema, é global ao processo e pode falhar
for candidate in ("pt_BR.UTF-8", "Portuguese_Brazil.1252", "pt_BR"):
    try:
        locale.setlocale(locale.LC_COLLATE, candidate)
        break
    except locale.Error:
        continue
else:
    candidate = None
print("locale usado:", candidate)
print(sorted(names, key=locale.strxfrm))
locale.setlocale(locale.LC_COLLATE, "C")    # volta ao padrão
print(sorted(names, key=locale.strxfrm))
