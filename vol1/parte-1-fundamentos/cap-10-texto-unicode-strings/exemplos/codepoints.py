"""Pontos de código, ord/chr, categorias e unicodedata."""
import unicodedata as ud

for ch in ["A", "é", "你", "😀", " ", "\n", "٣", "²"]:
    print(f"{ch!r:8} U+{ord(ch):04X}  {ud.category(ch)}  "
          f"{ud.name(ch, '?')}")

print(chr(0x1F600), chr(233), "\N{GREEK SMALL LETTER LAMDA}")
print(ud.unidata_version)

# dígitos: três perguntas diferentes
for ch in ["7", "٣", "²", "½", "Ⅳ"]:
    print(repr(ch), ch.isdecimal(), ch.isdigit(), ch.isnumeric(),
          ud.numeric(ch, None))
print(int("٣٤"), "٣٤".isascii())

# o que é "letra"
print("ação".isalpha(), "ab1".isalnum(), "日本語".isalpha())
print("é".isidentifier(), "café".isidentifier(), "2a".isidentifier())
print(ud.block("é"), "|", ud.block("你"), "|", ud.block("😀"))
