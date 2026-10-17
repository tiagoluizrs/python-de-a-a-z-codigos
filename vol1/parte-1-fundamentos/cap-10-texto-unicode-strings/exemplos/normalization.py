"""Normalização: um mesmo texto, vários pontos de código."""
import unicodedata as ud

nfc = "é"                  # U+00E9
nfd = "e\u0301"            # e + acento agudo combinante
print(nfc, nfd, nfc == nfd, len(nfc), len(nfd))
print(nfc.encode(), nfd.encode())
print(ud.normalize("NFC", nfd) == nfc, ud.normalize("NFD", nfc) == nfd)

# efeitos práticos
names = {nfc: 1}
print(nfd in names, "ç".find("c"), "e\u0301".startswith("é"))
print(len("José"), len("Jose\u0301"), "Jose\u0301".upper())

# NFC vs NFKC
samples = ["ﬁ", "①", "ｱ", "Ⅳ", "x²", "\u00a0", "Å"]
for s in samples:
    print(repr(s), ascii(ud.normalize("NFC", s)),
          ascii(ud.normalize("NFKC", s)), ud.normalize("NFKD", s) == s)

# remover acentos: NFD e filtrar combinantes (Mn)
def strip_accents(text):
    decomposed = ud.normalize("NFD", text)
    return "".join(c for c in decomposed if ud.category(c) != "Mn")

print(strip_accents("Ação, coração e açaí"))
print(strip_accents("ø æ ß"))        # nem tudo decompõe!

# casefold vs lower
print("Straße".lower(), "Straße".casefold(), "STRASSE".casefold())
print("Straße".lower() == "STRASSE".lower(),
      "Straße".casefold() == "STRASSE".casefold())
print("İ".lower(), len("İ".lower()), "ß".upper(), "ǆ".title())
print("I".lower(), "ı".upper(), "ς".upper(), "Σ".lower())

# comparação robusta
def same_text(a, b):
    norm = lambda s: ud.normalize("NFC", s).casefold()
    return norm(a) == norm(b)

print(same_text("JOSÉ", "jose\u0301"))
